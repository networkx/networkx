"""Shortest Path and path length using Bounded Source Shortest Path (BMSSP) algorithm"""

import heapq

import networkx as nx

__all__ = [
    "single_source_bmssp_path",
    "single_source_bmssp_path_length",
    "multi_source_bmssp_path",
    "multi_source_bmssp_path_length",
    "bmssp",
]


@nx._dispatchable(edge_attrs="weight")
def single_source_bmssp_path(G, source, target, weight="weight", precision=0):
    """Returns the shortest weighted path in G from source to target

    Uses BMSSP algorithm to compute the shortest path length
    between two nodes in a graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
        starting node for the path

    target : node label
        ending node for path

    weight : string or function
        If this is a string, then edge weight will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such edge attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    precision : int, optional (default=0)
        Decimal precision for weight calculations. If edge weights are
        integers, precision=0 is sufficient. For floating-point weights,
        use higher precision to avoid rounding errors.

        Examples:
            - precision=0: weights like 1, 2, 3 (integers)
            - precision=2: weights like 1.25, 3.50 (2 decimal places)
            - precision=6: weights like 0.123456 (6 decimal places)

        Note: If precision is less than the actual decimal places in
        weights, the result will be rounded. For example, if weight is
        1.25 and precision=1, the returned distance will be rounded to
        1 decimal place (e.g., 1.3).

    Returns
    -------
    path : list
        List of nodes in a shortest path

    Raises
    ------
    NetworkXNotImplemented
        If `G` is undirected. BMSSP algorithm only supports directed graphs.

    NodeNotFound
        If `source` is not in `G`.

    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> G = nx.DiGraph(nx.path_graph(5))
    >>> print(single_source_bmssp_path(G, 0, 4))
    [0, 1, 2, 3, 4]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    The weight function can be used to include node weights.

    >>> def func(u, v, d):
    ...     node_u_wt = G.nodes[u].get("node_weight", 1)
    ...     node_v_wt = G.nodes[v].get("node_weight", 1)
    ...     edge_wt = d.get("weight", 1)
    ...     return node_u_wt / 2 + node_v_wt / 2 + edge_wt

    In this example we take the average of start and end node
    weights of an edge and add it to the weight of the edge.

    The function :func:`bmssp` computes both path and length-of-path
    if you need both, use that.
    """
    if source not in G:
        raise nx.NodeNotFound(f"Node {source} not found in graph")
    if target not in G:
        raise nx.NodeNotFound(f"Node {target} not found in graph")
    _, paths = bmssp(G, {source}, target=target, weight=weight, precision=precision)
    if target not in paths:
        raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
    return paths[target]


@nx._dispatchable(edge_attrs="weight")
def single_source_bmssp_path_length(G, source, target, weight="weight", precision=0):
    """Returns the shortest weighted path length in G from source to target.

    Uses bmssp algorithm to compute the shortest weighted path length
    between two nodes in a Graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
        starting node for path

    target : node label
        ending node for path

    weight : string or function
        If this is a string, then edge weights will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such edge attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    precision : int, optional (default=0)
        Decimal precision for weight calculations. If edge weights are
        integers, precision=0 is sufficient. For floating-point weights,
        use higher precision to avoid rounding errors.

        Examples:
            - precision=0: weights like 1, 2, 3 (integers)
            - precision=2: weights like 1.25, 3.50 (2 decimal places)
            - precision=6: weights like 0.123456 (6 decimal places)

        Note: If precision is less than the actual decimal places in
        weights, the result will be rounded. For example, if weight is
        1.25 and precision=1, the returned distance will be rounded to
        1 decimal place (e.g., 1.3).

    Returns
    -------
    length : number
        Shortest path length

    Raises
    ------
    NetworkXNotImplemented
        If `G` is undirected. BMSSP algorithm only supports directed graphs.

    NodeNotFound
        If `source` is not in `G`.

    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> G = nx.DiGraph(nx.path_graph(5))
    >>> single_source_bmssp_path_length(G, 0, 4)
    4.0

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    The function :func:`bmssp` computes both path length and path
    if you need both, use that.
    """
    if source not in G:
        raise nx.NodeNotFound(f"Node {source} not found in graph")
    if target not in G:
        raise nx.NodeNotFound(f"Node {target} not found in graph")
    if source == target:
        return 0
    length, _ = bmssp(G, {source}, target=target, weight=weight, precision=precision)
    if target not in length:
        raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
    return length[target]


@nx._dispatchable(edge_attrs="weight")
def multi_source_bmssp_path(G, sources, weight="weight", precision=0):
    """Find shortest weighted paths in G from a given set of source
    nodes.

    Compute shortest path between any of the source nodes and all other
    reachable nodes for a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty set of nodes
        Starting nodes for paths. If this is just a set containing a
        single node, then all paths computed by this function will start
        from that node. If there are two or more nodes in the set, the
        computed paths may begin from any one of the start nodes.

    weight : string or function
        If this is a string, then edge weights will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such edge attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    precision : int, optional (default=0)
        Decimal precision for weight calculations. If edge weights are
        integers, precision=0 is sufficient. For floating-point weights,
        use higher precision to avoid rounding errors.

        Examples:
            - precision=0: weights like 1, 2, 3 (integers)
            - precision=2: weights like 1.25, 3.50 (2 decimal places)
            - precision=6: weights like 0.123456 (6 decimal places)

        Note: If precision is less than the actual decimal places in
        weights, the result will be rounded. For example, if weight is
        1.25 and precision=1, the returned distance will be rounded to
        1 decimal place (e.g., 1.3).

    Returns
    -------
    path : dictionary
        Dictionary of shortest paths keyed by target.

    Examples
    --------
    >>> G = nx.DiGraph(nx.path_graph(5))
    >>> path = multi_source_bmssp_path(G, {0})
    >>> path[1]
    [0, 1]
    >>> path[3]
    [0, 1, 2, 3]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    Raises
    ------
    NetworkXNotImplemented
        If `G` is undirected. BMSSP algorithm only supports directed graphs.

    ValueError
        If `sources` is empty.
    NodeNotFound
        If any of `sources` is not in `G`.

    """
    if not sources:
        raise ValueError("Sources must not be empty")
    for s in sources:
        if s not in G:
            raise nx.NodeNotFound(f"Node {s} not found in graph")
    _, paths = bmssp(G, sources, weight=weight, precision=precision)
    return paths


@nx._dispatchable(edge_attrs="weight")
def multi_source_bmssp_path_length(G, sources, weight="weight", precision=0):
    """Find shortest weighted path lengths in G from a given set of
    source nodes.

    Compute the shortest path length between any of the source nodes and
    all other reachable nodes for a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty set of nodes
        Starting nodes for paths. If this is just a set containing a
        single node, then all paths computed by this function will start
        from that node. If there are two or more nodes in the set, the
        computed paths may begin from any one of the start nodes.

    weight : string or function
        If this is a string, then edge weights will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    precision : int, optional (default=0)
        Decimal precision for weight calculations. If edge weights are
        integers, precision=0 is sufficient. For floating-point weights,
        use higher precision to avoid rounding errors.

        Examples:
            - precision=0: weights like 1, 2, 3 (integers)
            - precision=2: weights like 1.25, 3.50 (2 decimal places)
            - precision=6: weights like 0.123456 (6 decimal places)

        Note: If precision is less than the actual decimal places in
        weights, the result will be rounded. For example, if weight is
        1.25 and precision=1, the returned distance will be rounded to
        1 decimal place (e.g., 1.3).

    Returns
    -------
    length : dict
        Dict keyed by node to shortest path length to nearest source.

    Examples
    --------
    >>> G = nx.DiGraph(nx.path_graph(5))
    >>> length = multi_source_bmssp_path_length(G, {0})
    >>> for node in [0, 1, 2, 3, 4]:
    ...     print(f"{node}: {length[node]}")
    0: 0
    1: 1.0
    2: 2.0
    3: 3.0
    4: 4.0

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    Raises
    ------
    NetworkXNotImplemented
        If `G` is undirected. BMSSP algorithm only supports directed graphs.

    ValueError
        If `sources` is empty.
    NodeNotFound
        If any of `sources` is not in `G`.

    """
    if not sources:
        raise ValueError("Sources must not be empty")
    for s in sources:
        if s not in G:
            raise nx.NodeNotFound(f"Node {s} not found in graph")
    length, _ = bmssp(G, sources, weight=weight, precision=precision)
    return length


@nx._dispatchable(edge_attrs="weight")
def bmssp(G, sources, target=None, weight="weight", precision=0):
    """Uses BMSSP algorithm to find shortest weighted paths

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty iterable of nodes
        Starting nodes for paths. If this is just an iterable containing
        a single node, then all paths computed by this function will
        start from that node. If there are two or more nodes in this
        iterable, the computed paths may begin from any one of the start
        nodes.

    target : node label, optional
        Ending node for path. If provided, algorithm may terminate early
        once target is reached.

    weight : string or function
        If this is a string, then edge weights will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such edge attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    precision : int, optional (default=0)
        Decimal precision for weight calculations. If edge weights are
        integers, precision=0 is sufficient. For floating-point weights,
        use higher precision to avoid rounding errors.

        Examples:
            - precision=0: weights like 1, 2, 3 (integers)
            - precision=2: weights like 1.25, 3.50 (2 decimal places)
            - precision=6: weights like 0.123456 (6 decimal places)

        Note: If precision is less than the actual decimal places in
        weights, the result will be rounded. For example, if weight is
        1.25 and precision=1, the returned distance will be rounded to
        1 decimal place (e.g., 1.3).

    Returns
    -------
    distance : dictionary
        A mapping from node to shortest distance to that node from one
        of the source nodes.

    paths : dictionary
        A mapping from node to shortest path to that node from one of
        the source nodes.

    Raises
    ------
    NetworkXNotImplemented
        If `G` is undirected. BMSSP algorithm only supports directed graphs.

    NodeNotFound
        If any of `sources` is not in `G`.

    See Also
    --------
    single_source_bmssp_path
    multi_source_bmssp_path

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_edge(0, 1, weight=1)
    >>> G.add_edge(1, 2, weight=2)
    >>> G.add_edge(0, 2, weight=4)
    >>> distances, paths = bmssp(G, {0})
    >>> distances[2]
    3.0
    >>> paths[2]
    [0, 1, 2]

    References
    ----------
    .. [1] Makowski, Connor, Willem Guter, Tim Russell, Timothy Russell,
       Austin Saragih, and Lucas Castro. "BMSSPy: A Python Package and
       Empirical Comparison of Bounded Multi-Source Shortest Path Algorithm."
       MIT Center for Transportation & Logistics Research Paper No. 2025/034,
       November 19, 2025. https://doi.org/10.2139/ssrn.5777186

    """
    # Validate graph is directed
    if not G.is_directed():
        raise nx.NetworkXNotImplemented("BMSSP algorithm only supports directed graphs")
    # Validate sources
    sources = set(sources)
    if not sources:
        raise ValueError("Sources must not be empty")
    for s in sources:
        if s not in G:
            raise nx.NodeNotFound(f"Node {s} not found in graph")
    # Get weight function
    weight_fn = _get_weight_function(G, weight)
    # Build adjacency list with edge weights and IDs
    n = G.number_of_nodes()
    m = G.number_of_edges()
    # Create node index mapping
    node_list = list(G.nodes())
    node_to_idx = {node: idx for idx, node in enumerate(node_list)}
    idx_to_node = dict(enumerate(node_list))
    # Calculate parameters
    counter = _find_counter(n, precision)
    edge_adj_val = _find_edge_adj_val(n, m, precision)
    # Build adjacency list: adj[u] = [(v, weight, edge_id), ...]
    adj = [[] for _ in range(n)]
    edge_id = 0
    for u, v, data in G.edges(data=True):
        wt = weight_fn(u, v, data)
        if wt is None:
            continue
        if wt < 0:
            raise ValueError("BMSSP algorithm does not support negative weights")
        u_idx = node_to_idx[u]
        v_idx = node_to_idx[v]
        edge_id += edge_adj_val
        adj[u_idx].append((v_idx, wt, edge_id))
    # Initialize distance and predecessor arrays
    dist = [INF] * n
    cdist = [INF] * n  # Clean distance (without tie-breaker adjustments)
    predecessor = [-1] * n
    # Initialize sources
    source_indices = [node_to_idx[s] for s in sources]
    for src_idx in source_indices:
        dist[src_idx] = 0
        cdist[src_idx] = 0
    # Get algorithm parameters
    k = _find_k(n)
    t = _find_t(n)
    l = _find_l(n, t)
    # Run BMSSP
    target_idx = node_to_idx[target] if target is not None else None
    _bmssp_recursive(
        l,
        INF,
        source_indices,
        n,
        k,
        t,
        adj,
        dist,
        cdist,
        predecessor,
        counter,
        target_idx,
    )
    # Build result dictionaries
    distance_result = {}
    paths_result = {}
    for idx in range(n):
        node = idx_to_node[idx]
        if dist[idx] < INF:
            # Round distance to original precision
            distance_result[node] = round(cdist[idx], precision)
            # Reconstruct path
            paths_result[node] = _reconstruct_path(idx, predecessor, idx_to_node)
    return distance_result, paths_result


def _get_weight_function(G, weight):
    """Return a function that returns the weight of an edge.

    Parameters
    ----------
    G : NetworkX graph
        The graph for which weight function is needed.

    weight : string or function
        If string, edge weights are accessed via this edge attribute key.
        If function, it should accept (u, v, data) and return a number.

    Returns
    -------
    weight_fn : function
        A function that takes (u, v, data) and returns the edge weight.
        For multigraphs, returns the minimum weight among parallel edges.
    """
    if callable(weight):
        return weight
    if G.is_multigraph():

        def weight_fn(u, v, data):
            return min(d.get(weight, 1) for d in data.values())

        return weight_fn

    def weight_fn(u, v, data):
        return data.get(weight, 1)

    return weight_fn


INF = float("inf")


def _find_k(n):
    """Find parameter k for BMSSP algorithm.

    Computes k = floor(log(n)^(1/3)), which determines the branching
    factor and pivot selection threshold in the BMSSP algorithm.

    Parameters
    ----------
    n : int
        Number of nodes in the graph.

    Returns
    -------
    k : int
        The computed parameter k, minimum value is 1.
    """
    if n <= 1:
        return 1
    log_n = 0
    while n > 1:
        n //= 2
        log_n += 1
    # Binary search for cube root of log_n
    l, r = 1, log_n
    while r - l > 1:
        m = (r - l) // 2 + l
        if m * m * m > log_n:
            r = m - 1
        else:
            l = m
    if r * r * r <= log_n:
        return r
    return l


def _find_t(n):
    """Find parameter t for BMSSP algorithm.

    Computes t = floor(log(n)^(2/3)), which determines the recursion
    depth scaling factor in the BMSSP algorithm.

    Parameters
    ----------
    n : int
        Number of nodes in the graph.

    Returns
    -------
    t : int
        The computed parameter t, minimum value is 1.
    """
    if n <= 1:
        return 1
    log_n = 0
    n_copy = n
    while n_copy > 1:
        n_copy //= 2
        log_n += 1
    # Binary search for cube root of log_n^2
    l, r = 1, log_n
    while r - l > 1:
        m = (r - l) // 2 + l
        if m * m * m > log_n * log_n:
            r = m - 1
        else:
            l = m
    if r * r * r <= log_n * log_n:
        return r
    return l


def _find_l(n, t):
    """Find recursion depth l for BMSSP algorithm.

    Computes l = ceil(log(n) / t), which determines the maximum
    recursion depth in the BMSSP algorithm.

    Parameters
    ----------
    n : int
        Number of nodes in the graph.

    t : int
        The t parameter from _find_t.

    Returns
    -------
    l : int
        The computed recursion depth, returns 0 if n <= 1 or t <= 0.
    """
    if n <= 1 or t <= 0:
        return 0
    log_n = 0
    n_copy = n
    while n_copy > 1:
        n_copy //= 2
        log_n += 1
    return (log_n + t - 1) // t  # Ceiling division


def _find_counter(n, precision=6):
    """Calculate counter value for tie-breaking in distance comparisons.

    The counter value is used to break ties between paths of equal
    weight, ensuring deterministic path selection.

    Parameters
    ----------
    n : int
        Number of nodes in the graph.

    precision : int, optional (default=6)
        Decimal precision for weight calculations.

    Returns
    -------
    counter : float
        A small positive value used for tie-breaking.
    """
    temp = (10 ** (precision + 1)) * (2 * n + 1)
    return 1.0 / temp


def _find_edge_adj_val(n, m, precision=6):
    """Calculate edge adjustment value for unique edge identification.

    The edge adjustment value ensures each edge has a unique identifier
    in distance calculations, which helps in deterministic path reconstruction.

    Parameters
    ----------
    n : int
        Number of nodes in the graph.

    m : int
        Number of edges in the graph.

    precision : int, optional (default=6)
        Decimal precision for weight calculations.

    Returns
    -------
    edge_adj_val : float
        A small positive value unique to each edge.
    """
    temp = (10 ** (precision + 1)) * (2 * n + 1) * (2 * m + 1)
    return 1.0 / temp


def _reconstruct_path(dest_idx, predecessor, idx_to_node):
    """Reconstruct the shortest path from predecessor array.

    Traces back from the destination node to the source using the
    predecessor array built during the BMSSP algorithm.

    Parameters
    ----------
    dest_idx : int
        Index of the destination node.

    predecessor : list
        Array where predecessor[i] is the index of the predecessor
        of node i in the shortest path, or -1 if no predecessor.

    idx_to_node : dict
        Mapping from node indices to original node labels.

    Returns
    -------
    path : list
        List of nodes representing the shortest path from source
        to destination.
    """
    path = []
    current = dest_idx
    while current != -1:
        path.append(idx_to_node[current])
        current = predecessor[current]
    path.reverse()
    return path


def _is_pivot(root, forest, k):
    """Check if a node is a pivot in the shortest path forest.

    A node is considered a pivot if it has at least k descendants
    (including itself) in the tight-edge forest.

    Parameters
    ----------
    root : int
        Index of the node to check.

    forest : dict
        Dictionary mapping node indices to lists of their children
        in the tight-edge forest.

    k : int
        Threshold for pivot selection.

    Returns
    -------
    is_pivot : bool
        True if the node has at least k descendants, False otherwise.
    """
    stack = [root]
    seen = set()
    cnt = 0
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        cnt += 1
        if cnt >= k:
            return True
        if u in forest:
            for v in forest[u]:
                stack.append(v)
    return False


def _find_pivots(B, S, n, adj, dist, cdist, predecessor, counter, k):
    """Find pivot nodes using bounded Bellman-Ford exploration.

    This function performs a bounded exploration from source nodes to
    identify pivot nodes that will be used as recursive subproblem roots.

    Parameters
    ----------
    B : float
        Distance bound for exploration.

    S : list
        List of source node indices.

    n : int
        Total number of nodes in the graph.

    adj : list of lists
        Adjacency list where adj[u] contains tuples (v, weight, edge_id).

    dist : list
        Current distance array (with tie-breaker adjustments).

    cdist : list
        Clean distance array (without tie-breaker adjustments).

    predecessor : list
        Predecessor array for path reconstruction.

    counter : float
        Tie-breaking counter value.

    k : int
        Parameter k for pivot selection threshold.

    Returns
    -------
    pivots : list
        List of pivot node indices.

    W : list
        List of node indices within the distance bound B.
    """
    # Phase 1: Bounded Bellman-Ford
    W = set(S)
    W_prev = set(S)
    for i in range(k):
        W_curr = set()
        for u in W_prev:
            if dist[u] >= B:
                continue
            for v, wt, edge_id in adj[u]:
                temp = cdist[u] + wt + counter + edge_id
                if temp <= dist[v]:
                    dist[v] = temp
                    predecessor[v] = u
                    cdist[v] = cdist[u] + wt + counter
                    if temp < B:
                        W_curr.add(v)
        W.update(W_curr)
        if len(W) > k * len(S):
            return list(S), list(W)
        if not W_curr:
            break
        W_prev = W_curr
    # Phase 2: Build tight-edge forest
    forest = {u: [] for u in W}
    indeg = {u: 0 for u in W}
    for v in W:
        u = predecessor[v]
        if u != -1 and u in W:
            forest[u].append(v)
            indeg[v] += 1
    # Phase 3: Pivot selection
    P = []
    for u in S:
        if u not in W:
            continue
        if indeg.get(u, 0) != 0:
            continue
        if _is_pivot(u, forest, k):
            P.append(u)
    return P, list(W)


def _base_case(B, x, adj, dist, cdist, predecessor, counter, k):
    """Base case: Dijkstra-like exploration from a single source.

    Performs a bounded Dijkstra exploration from source node x,
    terminating after processing k+1 nodes or exhausting the heap.

    Parameters
    ----------
    B : float
        Distance bound for exploration.

    x : int
        Source node index.

    adj : list of lists
        Adjacency list where adj[u] contains tuples (v, weight, edge_id).

    dist : list
        Current distance array (with tie-breaker adjustments).

    cdist : list
        Clean distance array (without tie-breaker adjustments).

    predecessor : list
        Predecessor array for path reconstruction.

    counter : float
        Tie-breaking counter value.

    k : int
        Maximum number of nodes to complete before early termination.

    Returns
    -------
    B_new : float
        Updated distance bound after exploration.

    S : list
        List of completed node indices.
    """
    S = []
    B_new = B
    heap = [(dist[x], x)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        # Early termination at k+1 nodes
        if len(S) >= k:
            B_new = d
            break
        S.append(u)
        for v, wt, edge_id in adj[u]:
            d_new = cdist[u] + wt + counter + edge_id
            if d_new <= dist[v] and d_new < B:
                dist[v] = d_new
                predecessor[v] = u
                cdist[v] = cdist[u] + wt + counter
                heapq.heappush(heap, (d_new, v))
    return B_new, S


def _bmssp_recursive(
    l, B, S, n, k, t, adj, dist, cdist, predecessor, counter, target_idx=None
):
    """Recursive BMSSP (Bounded Multi-Source Shortest Path) algorithm.

    This is the core recursive function that implements the BMSSP algorithm.
    It divides the problem into subproblems using pivot selection and
    processes them recursively.

    Parameters
    ----------
    l : int
        Current recursion depth level.

    B : float
        Distance bound for this recursive call.

    S : list
        List of source node indices for this subproblem.

    n : int
        Total number of nodes in the graph.

    k : int
        Branching factor parameter.

    t : int
        Recursion depth scaling parameter.

    adj : list of lists
        Adjacency list where adj[u] contains tuples (v, weight, edge_id).

    dist : list
        Current distance array (with tie-breaker adjustments).

    cdist : list
        Clean distance array (without tie-breaker adjustments).

    predecessor : list
        Predecessor array for path reconstruction.

    counter : float
        Tie-breaking counter value.

    target_idx : int, optional
        Index of target node for early termination. If provided and
        target is reached, algorithm terminates early.

    Returns
    -------
    B_comp : float
        Completion bound - all nodes with distance less than B_comp
        have been fully processed.

    completed : list
        List of node indices that have been fully processed.
    """
    # Base case
    if l == 0:
        return _base_case(B, S[0], adj, dist, cdist, predecessor, counter, k)
    # Find pivots
    P, W = _find_pivots(B, S, n, adj, dist, cdist, predecessor, counter, k)
    # Data structure D (min-heap)
    D = []
    D_set = set()
    for p in P:
        heapq.heappush(D, (dist[p], p))
        D_set.add(p)
    B_comp = B
    for p in P:
        B_comp = min(B_comp, dist[p])
    U = []  # Completed nodes
    # Work budget - use n to ensure all nodes can be processed
    budget = max(n, k)
    for i in range(min(l * t, 30)):
        budget *= 2
    while D:
        # Pull smallest
        B_curr, x = heapq.heappop(D)
        if x in D_set:
            D_set.discard(x)
        S_curr = [x]
        # Recursive call
        B_new, U_curr = _bmssp_recursive(
            l - 1,
            B_curr,
            S_curr,
            n,
            k,
            t,
            adj,
            dist,
            cdist,
            predecessor,
            counter,
            target_idx,
        )
        B_comp = min(B_comp, B_new)
        # Add completed nodes
        U.extend(U_curr)
        # Check if target reached
        if target_idx is not None and target_idx in U_curr:
            break
        # Relax edges with two-window handling
        K = []  # For BatchPrepend
        for u in U_curr:
            for v, wt, edge_id in adj[u]:
                d_new = cdist[u] + wt + counter + edge_id
                if d_new <= dist[v]:
                    dist[v] = d_new
                    predecessor[v] = u
                    cdist[v] = cdist[u] + wt + counter
                    # Two-window handling
                    if B_curr <= d_new < B:
                        if v not in D_set:
                            heapq.heappush(D, (d_new, v))
                            D_set.add(v)
                    elif B_comp <= d_new < B_curr:
                        K.append((d_new, v))
        # BatchPrepend
        for d_v, v in K:
            if v not in D_set:
                heapq.heappush(D, (d_v, v))
                D_set.add(v)
        for x in S_curr:
            if B_comp <= dist[x] < B_curr:
                if x not in D_set:
                    heapq.heappush(D, (dist[x], x))
                    D_set.add(x)
    # Final completion
    B_comp = min(B_comp, B)
    completed = list(U)
    for u in W:
        if dist[u] < B_comp and u not in completed:
            completed.append(u)
    return B_comp, completed
