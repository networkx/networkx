"""Floyd-Warshall algorithm for shortest paths."""

import networkx as nx

__all__ = [
    "floyd_warshall",
    "floyd_warshall_predecessor_and_distance",
    "reconstruct_path",
    "floyd_warshall_numpy",
    "floyd_warshall_tree",
]


@nx._dispatchable(edge_attrs="weight")
def floyd_warshall_numpy(G, nodelist=None, weight="weight"):
    """Find all-pairs shortest path lengths using Floyd's algorithm.

    This algorithm for finding shortest paths takes advantage of
    matrix representations of a graph and works well for dense
    graphs where all-pairs shortest path lengths are desired.
    The results are returned as a NumPy array, distance[i, j],
    where i and j are the indexes of two nodes in nodelist.
    The entry distance[i, j] is the distance along a shortest
    path from i to j. If no path exists the distance is Inf.

    Parameters
    ----------
    G : NetworkX graph

    nodelist : list, optional (default=G.nodes)
       The rows and columns are ordered by the nodes in nodelist.
       If nodelist is None then the ordering is produced by G.nodes.
       Nodelist should include all nodes in G.

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight.

    Returns
    -------
    distance : 2D numpy.ndarray
        A numpy array of shortest path distances between nodes.
        If there is no path between two nodes the value is Inf.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from(
    ...     [(0, 1, 5), (1, 2, 2), (2, 3, -3), (1, 3, 10), (3, 2, 8)]
    ... )
    >>> nx.floyd_warshall_numpy(G)
    array([[ 0.,  5.,  7.,  4.],
           [inf,  0.,  2., -1.],
           [inf, inf,  0., -3.],
           [inf, inf,  8.,  0.]])

    Notes
    -----
    Floyd's algorithm is appropriate for finding shortest paths in
    dense graphs or graphs with negative weights when Dijkstra's
    algorithm fails. This algorithm can still fail if there are negative
    cycles. It has running time $O(n^3)$ with running space of $O(n^2)$.

    Raises
    ------
    NetworkXError
        If nodelist is not a list of the nodes in G.
    """
    import numpy as np

    if nodelist is not None:
        if not (len(nodelist) == len(G) == len(set(nodelist))):
            raise nx.NetworkXError(
                "nodelist must contain every node in G with no repeats."
                "If you wanted a subgraph of G use G.subgraph(nodelist)"
            )

    # To handle cases when an edge has weight=0, we must make sure that
    # nonedges are not given the value 0 as well.
    A = nx.to_numpy_array(
        G, nodelist, multigraph_weight=min, weight=weight, nonedge=np.inf
    )
    n, m = A.shape
    np.fill_diagonal(A, 0)  # diagonal elements should be zero
    for i in range(n):
        # The second term has the same shape as A due to broadcasting
        A = np.minimum(A, A[i, :][np.newaxis, :] + A[:, i][:, np.newaxis])
    return A


@nx._dispatchable(edge_attrs="weight")
def floyd_warshall_tree(G, weight="weight"):
    r"""Find all-pairs shortest path lengths using a Tree-based
    modification of Floyd's algorithm.

    This variant implements the Tree algorithm of Brodnik, Grgurovic and Pozar.
    It differs from the classical Floyd Warshall algorithm by using a shortest
    path tree rooted at each intermediate vertex w. For every w, the algorithm
    builds a tree ``OUT_w`` of shortest paths for the current iteration and
    scans the tree in depth first order. If an update at a vertex v cannot
    improve any distance, the algorithm skips the entire subtree below v,
    since none of its nodes can produce a shorter path, as proved in [1]_.

    Parameters
    ----------
    G : NetworkX graph

    weight : string, optional (default= 'weight')
        Edge data key corresponding to the edge weight.

    Returns
    -------
    predecessor, distance : dict and dict-of-dict
        Predecessor is a dict keyed by node to the predecessor node in
        the shortest path. The distance output is a dict keyed by source
        node to a dict keyed by target node to the distance value of the
        shortest path between the source and target.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from(
    ...     [
    ...         ("s", "u", 10),
    ...         ("s", "x", 5),
    ...         ("u", "v", 1),
    ...         ("u", "x", 2),
    ...         ("v", "y", 1),
    ...         ("x", "u", 3),
    ...         ("x", "v", 5),
    ...         ("x", "y", 2),
    ...         ("y", "s", 7),
    ...         ("y", "v", 6),
    ...     ]
    ... )
    >>> predecessors, distances = nx.floyd_warshall_tree(G)
    >>> nx.reconstruct_path("s", "v", predecessors)
    ['s', 'x', 'u', 'v']

    Notes
    -----
    Floyd's algorithm is appropriate for finding shortest paths
    in dense graphs or graphs with negative weights when Dijkstra's algorithm
    fails.  This algorithm can still fail if there are negative cycles.
    It has worst case running time $O(|V|^3)$ with running space of $O(|V|^2)$.

    For complete directed graphs with independent edge weights drawn from the
    uniform distribution on [0, 1], the expected running time is
    $O(|V|^2 (\log |V|)^2)$, as shown in [1]_.

    See Also
    --------
    floyd_warshall_predecessor_and_distance
    floyd_warshall
    floyd_warshall_numpy

    References
    ----------
    .. [1] Brodnik, Andrej, Marko Grgurovic, and Rok Pozar.
       "Modifications of the Floyd-Warshall algorithm with
       nearly quadratic expected-time."
       Ars Math. Contemp. 22, no. 1 (2022).
       https://doi.org/10.26493/1855-3974.2467.497
    """
    from collections import defaultdict

    # dictionary-of-dictionaries representation for dist and pred
    # use some defaultdict magick here
    # for dist the default is the floating point inf value
    inf = float("inf")
    dist = defaultdict(lambda: defaultdict(lambda: inf))
    for u in G:
        dist[u][u] = 0
    pred = defaultdict(dict)
    # initialize path distance dictionary to be the adjacency matrix
    # also set the distance to self to 0 (zero diagonal)
    undirected = not G.is_directed()
    for u, v, d in G.edges(data=True):
        e_weight = d.get(weight, 1.0)
        dist[u][v] = min(e_weight, dist[u][v])
        pred[u][v] = u
        if undirected:
            dist[v][u] = min(e_weight, dist[v][u])
            pred[v][u] = v

    # dont check for those w, `from` which `no` path exists
    for w, pred_w in pred.items():
        # out_w will store the adjacency list of the OUT_W tree of the paper,
        # it is a tree, parent --> list of children
        out_w = {parent: [] for parent in G}
        for v, parent in pred_w.items():  # w to v path exist
            if v == w:
                continue
            out_w[parent].append(v)

        # dfs order dict and skip dict in practical improvements in the paper
        stack = [w]
        dfs_dict = {}  # {node: next node in dfs order}
        skip_dict = {}  # {node: next node after subtree is skipped}

        node = None
        while stack:
            next_node = stack.pop()
            dfs_dict[node] = next_node
            if stack:
                skip_dict[next_node] = stack[-1]
            stack.extend(out_w[next_node])
            node = next_node

        dist_w = dist[w]  # for speed
        # main inner loop starts here
        for u in G:
            if u == w:  # small optimization
                continue
            dist_u = dist[u]
            dist_uw = dist_u[w]
            if dist_uw == inf:  # small optimization
                continue

            # note: we skip v=w as relaxation would always fail
            v = dfs_dict[w]
            while v is not None:
                dist_uwv = dist_uw + dist_w[v]
                if dist_u[v] > dist_uwv:
                    dist_u[v] = dist_uwv
                    # update/new entries to be created in pred[u]
                    pred[u][v] = pred_w[v]  # v must be in pred_w as checked above
                    v = dfs_dict.get(v, None)
                else:
                    v = skip_dict.get(v, None)

    return dict(pred), dict(dist)


@nx._dispatchable(edge_attrs="weight")
def floyd_warshall_predecessor_and_distance(G, weight="weight"):
    """Find all-pairs shortest path lengths using Floyd's algorithm.

    Parameters
    ----------
    G : NetworkX graph

    weight: string, optional (default= 'weight')
       Edge data key corresponding to the edge weight.

    Returns
    -------
    predecessor,distance : dictionaries
       Dictionaries, keyed by source and target, of predecessors and distances
       in the shortest path.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from(
    ...     [
    ...         ("s", "u", 10),
    ...         ("s", "x", 5),
    ...         ("u", "v", 1),
    ...         ("u", "x", 2),
    ...         ("v", "y", 1),
    ...         ("x", "u", 3),
    ...         ("x", "v", 5),
    ...         ("x", "y", 2),
    ...         ("y", "s", 7),
    ...         ("y", "v", 6),
    ...     ]
    ... )
    >>> predecessors, _ = nx.floyd_warshall_predecessor_and_distance(G)
    >>> print(nx.reconstruct_path("s", "v", predecessors))
    ['s', 'x', 'u', 'v']

    Notes
    -----
    Floyd's algorithm is appropriate for finding shortest paths
    in dense graphs or graphs with negative weights when Dijkstra's algorithm
    fails.  This algorithm can still fail if there are negative cycles.
    It has running time $O(n^3)$ with running space of $O(n^2)$.

    See Also
    --------
    floyd_warshall
    floyd_warshall_numpy
    all_pairs_shortest_path
    all_pairs_shortest_path_length
    """
    from collections import defaultdict

    # dictionary-of-dictionaries representation for dist and pred
    # use some defaultdict magick here
    # for dist the default is the floating point inf value
    dist = defaultdict(lambda: defaultdict(lambda: float("inf")))
    for u in G:
        dist[u][u] = 0
    pred = defaultdict(dict)
    # initialize path distance dictionary to be the adjacency matrix
    # also set the distance to self to 0 (zero diagonal)
    undirected = not G.is_directed()
    for u, v, d in G.edges(data=True):
        e_weight = d.get(weight, 1.0)
        dist[u][v] = min(e_weight, dist[u][v])
        pred[u][v] = u
        if undirected:
            dist[v][u] = min(e_weight, dist[v][u])
            pred[v][u] = v
    for w in G:
        dist_w = dist[w]  # save recomputation
        for u in G:
            dist_u = dist[u]  # save recomputation
            for v in G:
                d = dist_u[w] + dist_w[v]
                if dist_u[v] > d:
                    dist_u[v] = d
                    pred[u][v] = pred[w][v]
    return dict(pred), dict(dist)


@nx._dispatchable(graphs=None)
def reconstruct_path(source, target, predecessors):
    """Reconstruct a path from source to target using the predecessors
    dict as returned by floyd_warshall_predecessor_and_distance

    Parameters
    ----------
    source : node
       Starting node for path

    target : node
       Ending node for path

    predecessors: dictionary
       Dictionary, keyed by source and target, of predecessors in the
       shortest path, as returned by floyd_warshall_predecessor_and_distance

    Returns
    -------
    path : list
       A list of nodes containing the shortest path from source to target

       If source and target are the same, an empty list is returned

    Notes
    -----
    This function is meant to give more applicability to the
    floyd_warshall_predecessor_and_distance function

    See Also
    --------
    floyd_warshall_predecessor_and_distance
    """
    if source == target:
        return []
    prev = predecessors[source]
    curr = prev[target]
    path = [target, curr]
    while curr != source:
        curr = prev[curr]
        path.append(curr)
    return list(reversed(path))


@nx._dispatchable(edge_attrs="weight")
def floyd_warshall(G, weight="weight"):
    """Find all-pairs shortest path lengths using Floyd's algorithm.

    Parameters
    ----------
    G : NetworkX graph

    weight: string, optional (default= 'weight')
       Edge data key corresponding to the edge weight.


    Returns
    -------
    distance : dict
       A dictionary,  keyed by source and target, of shortest paths distances
       between nodes.

    Examples
    --------
    >>> from pprint import pprint
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from(
    ...     [(0, 1, 5), (1, 2, 2), (2, 3, -3), (1, 3, 10), (3, 2, 8)]
    ... )
    >>> fw = nx.floyd_warshall(G, weight="weight")
    >>> results = {a: dict(b) for a, b in fw.items()}
    >>> pprint(results)
    {0: {0: 0, 1: 5, 2: 7, 3: 4},
     1: {0: inf, 1: 0, 2: 2, 3: -1},
     2: {0: inf, 1: inf, 2: 0, 3: -3},
     3: {0: inf, 1: inf, 2: 8, 3: 0}}

    Notes
    -----
    Floyd's algorithm is appropriate for finding shortest paths
    in dense graphs or graphs with negative weights when Dijkstra's algorithm
    fails.  This algorithm can still fail if there are negative cycles.
    It has running time $O(n^3)$ with running space of $O(n^2)$.

    See Also
    --------
    floyd_warshall_predecessor_and_distance
    floyd_warshall_numpy
    all_pairs_shortest_path
    all_pairs_shortest_path_length
    """
    # could make this its own function to reduce memory costs
    return floyd_warshall_predecessor_and_distance(G, weight=weight)[1]
