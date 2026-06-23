"""Reachability queries on directed graphs via Pruned Landmark Labeling (PLL).

``has_path`` answers a single reachability query with an O(V + E) traversal, paid
again on every call.  This module instead builds a reusable index once and then
answers each query from precomputed 2-hop labels in roughly label-size time.  It
is build for graphs that are queried for reachability many times (dependency,
provenance or citation graphs, etc.).

The graph is first condensed to its DAG of strongly connected components, so the
labeling is built on an acyclic graph and the resulting 2-hop cover is complete:
a query is answered entirely from the labels, including negative (unreachable)
answers, with no graph traversal at query time.
"""

from collections import deque

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["pll_reachability_index", "PLLReachability"]


@not_implemented_for("undirected")
@nx._dispatchable
def pll_reachability_index(G):
    """Build a Pruned Landmark Labeling reachability index for ``G``.

    The returned index answers reachability queries (``is_reachable(s, t)``) from
    precomputed 2-hop labels.

    Parameters
    ----------
    G : NetworkX DiGraph
        A directed graph.

    Returns
    -------
    PLLReachability
        An index object exposing ``is_reachable(source, target)``.

    Raises
    ------
    NetworkXNotImplemented
        If ``G`` is undirected.

    Examples
    --------
    >>> G = nx.DiGraph([(0, 1), (1, 2), (2, 3), (3, 1)])
    >>> index = nx.pll_reachability_index(G)
    >>> index.is_reachable(0, 3)
    True
    >>> index.is_reachable(3, 0)
    False
    >>> index.is_reachable(1, 3)  # 1, 2, 3 form a cycle
    True

    Notes
    -----
    ``G`` is condensed to its DAG of strongly connected components, so reachability
    is preserved (``u`` reaches ``v`` iff they share a component, or ``u``'s
    component reaches ``v``'s in the DAG).  Labels are built on that DAG with a
    pruned BFS from each component in importance order, yielding a complete 2-hop
    cover; an empty label intersection is therefore a definitive "not reachable".

    References
    ----------
    .. [1] CHAO ZHANG, ANGELA BONIFATI, and M. TAMER ÖZSU. "Indexing Techniques for
    Graph Reachability Queries".

    See Also
    --------
    has_path
    descendants
    transitive_closure
    """
    return PLLReachability(G)


class PLLReachability:
    """A Pruned Landmark Labeling reachability index for a directed graph.

    Construct via :func:`pll_reachability_index`.  The index stores, for each
    strongly connected component, two small hub sets (``Lout`` and ``Lin``) that
    together form a complete 2-hop cover, so ``is_reachable`` is answered from the
    labels alone.

    Attributes
    ----------
    comp : dict
        Maps each node of the original graph to its strongly-connected-component id.
    """

    def __init__(self, G):
        # Condense to the SCC DAG: reachability(u, v) holds iff comp[u] == comp[v]
        # or comp[u] reaches comp[v] in the (acyclic) condensation.
        self.C = nx.condensation(G)
        self.comp = self.C.graph["mapping"]
        dag = self.C

        # Importance order: degree-product heuristic, most important first.
        order = sorted(
            dag.nodes(),
            key=lambda v: (dag.in_degree(v) + 1) * (dag.out_degree(v) + 1),
            reverse=True,
        )

        # Lout[x]: hubs reachable from x.  Lin[x]: hubs that reach x.
        # Query(s, t): Lout[s] and Lin[t] share a hub.
        self.Lout = {v: set() for v in dag.nodes()}
        self.Lin = {v: set() for v in dag.nodes()}
        Lout, Lin = self.Lout, self.Lin

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

    def is_reachable(self, source, target):
        """Return ``True`` if ``target`` is reachable from ``source``.

        Parameters
        ----------
        source, target : nodes
            Nodes of the graph the index was built from.

        Returns
        -------
        bool
            ``True`` if there is a directed path from ``source`` to ``target``
            (a node is reachable from itself), ``False`` otherwise.

        Raises
        ------
        NodeNotFound
            If ``source`` or ``target`` is not in the graph.

        Examples
        --------
        >>> G = nx.path_graph(4, create_using=nx.DiGraph)
        >>> index = nx.pll_reachability_index(G)
        >>> index.is_reachable(0, 3)
        True
        >>> index.is_reachable(3, 0)
        False
        """
        if source not in self.comp:
            raise nx.NodeNotFound(f"Source {source!r} is not in G")
        if target not in self.comp:
            raise nx.NodeNotFound(f"Target {target!r} is not in G")
        cs, ct = self.comp[source], self.comp[target]
        if cs == ct:
            return True  # same strongly connected component -> mutually reachable
        a, b = self.Lout[cs], self.Lin[ct]
        if len(a) > len(b):
            a, b = b, a
        return any(h in b for h in a)  # label-only; empty intersection -> False

    def label_stats(self):
        """Return basic size statistics of the index (DAG size, average label size)."""
        sizes = [len(s) for s in self.Lout.values()] + [
            len(s) for s in self.Lin.values()
        ]
        total = sum(sizes)
        return {
            "dag_nodes": self.C.number_of_nodes(),
            "total_label_entries": total,
            "avg_label_size": total / max(1, len(sizes)),
        }
