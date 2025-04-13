"""Functions for computing dominating sets in a graph."""

import math
from heapq import heappop, heappush
from itertools import chain, count

import networkx as nx
from networkx.utils import arbitrary_element

from ..utils import not_implemented_for

__all__ = [
    "dominating_set",
    "is_dominating_set",
    "connected_dominating_set",
    "is_connected_dominating_set",
]


@nx._dispatchable
def dominating_set(G, start_with=None):
    r"""Finds a dominating set for the graph G.

    A *dominating set* for a graph with node set *V* is a subset *D* of
    *V* such that every node not in *D* is adjacent to at least one
    member of *D* [1]_.

    Parameters
    ----------
    G : NetworkX graph

    start_with : node (default=None)
        Node to use as a starting point for the algorithm.

    Returns
    -------
    D : set
        A dominating set for G.

    Notes
    -----
    This function is an implementation of algorithm 7 in [2]_ which
    finds some dominating set, not necessarily the smallest one.

    See also
    --------
    is_dominating_set

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Dominating_set

    .. [2] Abdol-Hossein Esfahanian. Connectivity Algorithms.
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf

    """
    all_nodes = set(G)
    if start_with is None:
        start_with = arbitrary_element(all_nodes)
    if start_with not in G:
        raise nx.NetworkXError(f"node {start_with} is not in G")
    dominating_set = {start_with}
    dominated_nodes = set(G[start_with])
    remaining_nodes = all_nodes - dominated_nodes - dominating_set
    while remaining_nodes:
        # Choose an arbitrary node and determine its undominated neighbors.
        v = remaining_nodes.pop()
        undominated_nbrs = set(G[v]) - dominating_set
        # Add the node to the dominating set and the neighbors to the
        # dominated set. Finally, remove all of those nodes from the set
        # of remaining nodes.
        dominating_set.add(v)
        dominated_nodes |= undominated_nbrs
        remaining_nodes -= undominated_nbrs
    return dominating_set


@nx._dispatchable
def is_dominating_set(G, nbunch):
    """Check if `nbunch` is a dominating set for `G`.

    A *dominating set* for a graph with node set *V* is a subset *D* of
    *V* such that every node not in *D* is adjacent to at least one
    member of *D* [1]_.

    Parameters
    ----------
    G : NetworkX graph

    nbunch : iterable
        An iterable of nodes in the graph `G`.

    See also
    --------
    dominating_set

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Dominating_set

    """
    testset = {n for n in nbunch if n in G}
    nbrs = set(chain.from_iterable(G[n] for n in testset))
    return len(set(G) - testset - nbrs) == 0


@not_implemented_for("directed")
@nx._dispatchable
def connected_dominating_set(G):
    """Return a connected dominating set.

    A *dominating set* for a graph *G* with node set *V* is a subset *D* of
    *V* such that every node not in *D* is adjacent to at least one
    member of *D* [1]_. A *connected dominating set* is a dominating
    set *C* that induces a connected subgraph of *G* [2]_.

    Parameters
    ----------
    G : NewtorkX graph
        Undirected connected graph.

    Returns
    -------
    connected_dominating_set : set
        A dominating set of nodes which induces a connected subgraph of G.

    Examples
    ________
    >>> G = nx.Graph(
    ...     [
    ...         (1, 2),
    ...         (1, 3),
    ...         (1, 4),
    ...         (1, 5),
    ...         (1, 6),
    ...         (2, 7),
    ...         (3, 8),
    ...         (4, 9),
    ...         (5, 10),
    ...         (6, 11),
    ...         (7, 12),
    ...         (8, 12),
    ...         (9, 12),
    ...         (10, 12),
    ...         (11, 12),
    ...     ]
    ... )
    >>> nx.connected_dominating_set(G)
    {1, 2, 3, 4, 5, 6, 7}

    Raises
    ------
    NetworkXNotImplemented
        If G is directed.

    Notes
    -----
    This function implements Algorithm 1 in its basic version as described
    in [3]_. The idea behind the algorithm is the following: grow a tree *T*,
    starting from the vertex of maximum degree. At each step we pick a vertex
    *v* in *T* with maximal number of white neighbors and "scan it." Scanning
    a vertex add edges to *T* from *v* to all its neighbors not in *T*. In the
    end we find a spanning tree *T*, and pick the nonleaf nodes as the connected
    dominating set. Initially all vertices colored white. When we scan a vertex
    (color it black), we mark all its neighbors that are not in *T* and and add
    them to *T* (color them gray). Thus, marked nodes that have not been scanned
    are leaves in *T* (gray nodes). All unmarked nodes are white. The algorithm
    continues scanning marked nodes, until all the vertices are marked (gray or
    black). The set of scanned nodes (black nodes) will form the connected
    dominating set.
    Runtime complexity of this implementation is $O(|E|*log|V|)$ (amortized).

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Dominating_set
    .. [2] https://en.wikipedia.org/wiki/Connected_dominating_set
    .. [3] Guha, S. and Khuller, S.
           *Approximation Algorithms for Connected Dominating Sets*,
           Algorithmica, 20, 374-387, 1998.

    """
    if len(G) == 0 or not nx.is_connected(G):
        return set()

    if not nx.is_connected(G):
        raise nx.NetworkXError("G must be a connected graph")

    if len(G) == 1:
        return set(G)

    G_succ = G._adj  # For speed-up

    push = heappush
    pop = heappop

    # Keep track of the number of white nodes adjacent to each vertex
    white_degree = {v: G.degree[v] for v in G}

    # Initially all nodes are white
    white_nodes = set(G)

    # We want a max-heap of the white-degree using heapq, which is a min-heap
    # So we store the negative of the white-degree
    gray_nodes = []

    # This will be the CDS
    black_nodes = set()

    # Use the count c to avoid comparing nodes (may not be able to)
    c = count()

    def _update(node):
        white_nodes.remove(node)
        push(gray_nodes, (-white_degree[node], next(c), node))
        for nbr in G_succ[node]:
            white_degree[nbr] -= 1

    # Find node with highest degree
    max_deg_node = max(G, key=G.degree)
    _update(max_deg_node)

    while white_nodes:
        (neg_deg, _, u) = pop(gray_nodes)
        # Check if u's white-degree changed while in the heap
        if -neg_deg > white_degree[u]:
            push(gray_nodes, (-white_degree[u], next(c), u))
            continue
        # Color all u's white neighbors gray
        for v in G_succ[u]:
            if v in white_nodes:
                _update(v)
        black_nodes.add(u)

    return black_nodes


@not_implemented_for("directed")
@nx._dispatchable
def is_connected_dominating_set(G, nbunch):
    """Check if `nbunch` is a connected dominating set for `G`.

    A *dominating set* for a graph *G* with node set *V* is a subset *D* of
    *V* such that every node not in *D* is adjacent to at least one
    member of *D* [1]_. A *connected dominating set* is a dominating
    set *C* that induces a connected subgraph of *G* [2]_.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph.

    nbunch : iterable
        An iterable of nodes in the graph `G`.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Dominating_set
    .. [2] https://en.wikipedia.org/wiki/Connected_dominating_set

    """
    return nx.is_dominating_set(G, nbunch) and nx.is_connected(nx.subgraph(G, nbunch))
