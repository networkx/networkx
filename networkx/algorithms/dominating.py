"""Functions for computing dominating sets in a graph."""

import math
from heapq import heappop, heappush
from itertools import chain

import networkx as nx
from networkx.utils import arbitrary_element

from ..utils import not_implemented_for

__all__ = [
    "dominating_set",
    "is_dominating_set",
    "connected_dominating_set",
    "is_connected_dominating_set",
    "interval_graph_min_connected_dominating_set",
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
    r"""Checks if `nbunch` is a dominating set for `G`.

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
    r"""Returns a connected dominating set.

    A *dominating set* for a graph *G* with node set *V* is a subset *D* of
    *V* such that every node not in *D* is adjacent to at least one
    member of *D* [1]_. A *connected dominating set* is a dominating
    set *C* that induces a connected subgraph of *G* [2]_.
    
    Parameters
    ----------
    G : NewtorkX graph
        Undirected graph.

    Returns
    -------
    black_nodes : set
        Returns a dominating set of nodes which induce a connected subgraph of G.

    Examples
    ________
    >>> G = nx.Graph([ \
        (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), \
        (2, 7), (3, 8), (4, 9), (5, 10), (6, 11), \
        (7, 12), (8, 12), (9, 12), (10, 12), (11, 12) \
    ])
    >>> nx.guha_khuller_single_scan_connected_dominating_set(G)
    {1, 2, 3, 4, 5, 6, 7}

    Raises
    ------
    NetworkXNotImplemented
        If G is directed.

    Notes
    -----
    This function implements Algorithm 1 in its basic version as specified
    in [3]_.
    Runtime complexity of the algorithm is $O(|E|)$.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Dominating_set
    .. [2] https://en.wikipedia.org/wiki/Connected_dominating_set
    .. [3] Guha, S. and Khuller, S.
           *Approximation Algorithms for Connected Dominating Sets*,
           Algorithmica, 20, 374-387, 1998.
    
    """
    if len(G) == 0 or nx.is_connected(G) == False:
        return set()

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

    def _update(node):
        white_nodes.remove(node)
        push(gray_nodes, (-white_degree[node], node))
        for nbr, _ in G_succ[node].items():
            white_degree[nbr] -= 1

    # Find node with highest degree
    max_deg_node = max(G, key=G.degree)
    _update(max_deg_node)

    while white_nodes:
        (neg_deg, u) = pop(gray_nodes)
        # Check if u's white-degree changed while in the heap
        if -neg_deg > white_degree[u]:
            push(gray_nodes, (-white_degree[u], u))
            continue
        # Color all u's white neighbors gray
        for v, _ in G_succ[u].items():
            if v in white_nodes:
                _update(v)
        black_nodes.add(u)

    return black_nodes


@not_implemented_for("directed")
@nx._dispatchable
def is_connected_dominating_set(G, nbunch):
    r"""Checks if `nbunch` is a connected dominating set for `G`.

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
    if nx.is_dominating_set(G, nbunch) == False:
        return False
    SG = nx.subgraph(G, nbunch)
    return nx.is_connected(SG)


@not_implemented_for("directed")
@nx._dispatchable
def interval_graph_min_connected_dominating_set(G):
    r"""Returns a minimum connected dominating set of an interval graph `G`.

    A *dominating set* for a graph *G* with node set *V* is a subset *D* of
    *V* such that every node not in *D* is adjacent to at least one
    member of *D* [1]_. A *connected dominating set* is a dominating
    set *C* that induces a connected subgraph of *G* [2]_. A minimum
    connected dominating set is a connected dominating set with the
    smallest possible cardinality among all connected dominating sets of *G*.

    An *interval graph* *G* is an undirected graph formed from a set of
    intervals on the real line, with a vertex for each interval and an
    edge between vertices whose intervals intersect. It is the intersection
    graph of the intervals [3]_.

    Parameters
    ----------
    G : NetworkX graph
        Undirected interval graph as specified in [4]_.

    Returns
    -------
    min_dom_set: set
        A connected dominating set with minimal cardinality.

    Examples
    --------
    >>> intervals = [
            (30, 37), (52, 53), (24, 26),
            (64, 66), (7, 31), (38, 40),
            (9, 18), (37, 64), (15, 21)
        ]
    >>> G = nx.interval_graph(intervals)
    >>> nx.interval_graph_min_connected_dominating_set(G)
    {(7, 31), (30, 37), (37, 64)}

    Raises
    ------
    :exc:`TypeError`
        If `G` is not an a valid interval graph as specified in [4]_.

    Notes
    -----
    This function is an implementation of the algorithm in [5]_.
    Runtime complexity of the algorithm is $O(|E| + |V|)$.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Dominating_set
    .. [2] https://en.wikipedia.org/wiki/Connected_dominating_set
    .. [3] https://en.wikipedia.org/wiki/Interval_graph
    .. [4] https://networkx.org/documentation/stable/reference/generated/networkx.generators.interval_graph.interval_graph
    .. [5] Ramalingam, G. and Rangan, C.Pandu
           *A unified approach to domination problems of interval graphs*,
           Information Processing Letters, Volume 27, Issue 5, 28 April 1988,
           Pages 271-274.

    """
    # Convert the interval graph to a numbered graph
    intervals = list(G.nodes)
    intervals = sorted(intervals, key=lambda pair: pair[1])

    ints_to_nums = {intervals[i - 1]: i for i in range(1, len(intervals) + 1)}
    nums_to_ints = {ints_to_nums[i]: i for i in intervals}

    H = nx.Graph()
    for e in G.edges:
        H.add_edge(ints_to_nums[e[0]], ints_to_nums[e[1]])

    n = H.number_of_nodes()

    # True if G is the null graph, G has a single node or G is disconnected
    if n == 0:
        return {}

    # The lowest numbered node in each node's neighborhood
    low = {i: min(i, min(H.adj[i])) for i in H.nodes}

    # MCDSs
    MCD = [set()]

    # Main loop
    for i in range(1, n + 1):
        if low[i] == 1:
            MCD.append({i})
            continue

        min_size = math.inf
        min_j = -1
        for j in H.adj[i]:
            if j < i and low[j] < low[i] and MCD[j] and len(MCD[j]) < min_size:
                min_size = len(MCD[j])
                min_j = j

        if min_j == -1:
            MCD.append(set())
        else:
            MCD.append(MCD[min_j] | {i})

    # Post-processing
    maxlow = max([low[i] for i in range(low[n], n + 1)])
    L = [MCD[i] for i in range(maxlow, n + 1) if MCD[i]]

    min_dom_set_numbered = min(L, key=len)
    min_dom_set = {nums_to_ints[i] for i in min_dom_set_numbered}
    return min_dom_set
