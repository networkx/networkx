"""Reachability queries on directed graphs via Pruned Landmark Labeling (PLL).

``has_path`` answers a single reachability query with an O(V + E) traversal, paid
again on every call. This module instead builds a reusable reachability graph
once, and then answers each query from that graph without traversing the original
graph. A fixed graph queried for
reachability many times (dependency, provenance or citation graphs, etc.).

The reachability graph returned by :func:`pll_reachability_graph` encodes a 2-hop
labeling as edges. The original graph is condensed to its DAG of strongly
connected components, and for each component ``c`` an edge ``c -> h`` records that
hub ``h`` is reachable from ``c`` (``h`` in ``c``'s out-label) and an edge
``h -> c`` records that ``c`` is reachable from hub ``h`` (``h`` in ``c``'s
in-label). Two nodes are reachable iff their components share a hub, i.e. the
out-neighbours of one meet the in-neighbours of the other. The node-to-component
map is stored on the returned graph as ``H.graph["mapping"]``, as
:func:`~networkx.algorithms.components.condensation` does.

"""

from collections import deque

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["pll_reachability_graph", "is_reachable"]


@not_implemented_for("undirected")
@nx._dispatchable(returns_graph=True)
def pll_reachability_graph(G):
    """Build a reachability graph for ``G`` using Pruned Landmark Labeling.

    The returned graph encodes a 2-hop reachability cover as edges, so that
    reachability between two nodes of ``G`` can be answered with
    :func:`is_reachable` without traversing ``G``.

    Parameters
    ----------
    G : NetworkX DiGraph
        A directed graph.

    Returns
    -------
    H : NetworkX DiGraph
        A reachability graph whose nodes are the strongly-connected-component ids
        of ``G``. An edge ``c -> h`` means hub ``h`` is reachable from component
        ``c``; an edge ``h -> c`` means ``c`` is reachable from hub ``h``. The
        node-to-component mapping is stored as ``H.graph["mapping"]``.

    Raises
    ------
    NetworkXNotImplemented
        If ``G`` is undirected.

    Examples
    --------
    >>> G = nx.DiGraph([(0, 1), (1, 2), (2, 3), (3, 1)])
    >>> H = nx.pll_reachability_graph(G)
    >>> nx.is_reachable(H, 0, 3)
    True
    >>> nx.is_reachable(H, 3, 0)
    False

    Notes
    -----
    ``G`` is condensed to its DAG of strongly connected components, so
    reachability is preserved (``u`` reaches ``v`` iff they share a component, or
    ``u``'s component reaches ``v``'s in the DAG). Labels are built on that DAG
    with a pruned BFS from each component in importance order, yielding a complete
    2-hop cover.

    References
    ----------
    .. [1] CHAO ZHANG, ANGELA BONIFATI, and M. TAMER ÖZSU. "Indexing Techniques for
    Graph Reachability Queries".

    See Also
    --------
    is_reachable
    has_path
    condensation
    """
    dag = nx.condensation(G)
    mapping = dag.graph["mapping"]

    # importance order: degree-product heuristic, most important first
    order = sorted(
        dag.nodes(),
        key=lambda v: (dag.in_degree(v) + 1) * (dag.out_degree(v) + 1),
        reverse=True,
    )

    # Lout[c]: hubs reachable from c. Lin[c]: hubs that reach c.
    Lout = {v: set() for v in dag.nodes()}
    Lin = {v: set() for v in dag.nodes()}

    def covered(s, t):
        a, b = Lout[s], Lin[t]
        if len(a) > len(b):
            a, b = b, a
        return any(h in b for h in a)

    succ, pred = dag._succ, dag._pred
    for v in order:
        # forward pruned BFS: v becomes a hub in Lin[u] for u reachable from v
        seen = {v}
        dq = deque((v,))
        while dq:
            u = dq.popleft()
            if covered(v, u):  # already 2-hop covered -> prune this branch
                continue
            Lin[u].add(v)
            for w in succ[u]:
                if w not in seen:
                    seen.add(w)
                    dq.append(w)
        # backward pruned BFS: v becomes a hub in Lout[u] for u that reach v
        seen = {v}
        dq = deque((v,))
        while dq:
            u = dq.popleft()
            if covered(u, v):
                continue
            Lout[u].add(v)
            for w in pred[u]:
                if w not in seen:
                    seen.add(w)
                    dq.append(w)

    # write the labels into a DiGraph: the edges *are* the labels
    H = nx.DiGraph()
    H.add_nodes_from(dag.nodes())
    for c in dag.nodes():
        for h in Lout[c]:
            H.add_edge(c, h)  # c -> h : h in Lout[c]
        for h in Lin[c]:
            H.add_edge(h, c)  # h -> c : h in Lin[c]
    H.graph["mapping"] = mapping
    return H


def is_reachable(H, source, target):
    """Return ``True`` if ``target`` is reachable from ``source``.

    Answers a reachability query from a reachability graph ``H`` produced by
    :func:`pll_reachability_graph`, without traversing the original graph.

    Parameters
    ----------
    H : NetworkX DiGraph
        A reachability graph from :func:`pll_reachability_graph` (it must carry
        the ``H.graph["mapping"]`` node-to-component map).
    source, target : nodes
        Nodes of the original graph ``H`` was built from.

    Returns
    -------
    bool
        ``True`` if there is a directed path from ``source`` to ``target`` in the
        original graph (a node is reachable from itself), ``False`` otherwise.

    Raises
    ------
    NodeNotFound
        If ``source`` or ``target`` is not in the original graph.

    Examples
    --------
    >>> G = nx.path_graph(4, create_using=nx.DiGraph)
    >>> H = nx.pll_reachability_graph(G)
    >>> nx.is_reachable(H, 0, 3)
    True
    >>> nx.is_reachable(H, 3, 0)
    False
    """
    mapping = H.graph["mapping"]
    if source not in mapping:
        raise nx.NodeNotFound(f"Source {source!r} is not in G")
    if target not in mapping:
        raise nx.NodeNotFound(f"Target {target!r} is not in G")
    cs, ct = mapping[source], mapping[target]
    if cs == ct:
        return True  # same strongly connected component -> mutually reachable
    # reachable iff the components share a hub: out-neighbours of cs meet
    # in-neighbours of ct
    return bool(H._succ[cs].keys() & H._pred[ct].keys())
