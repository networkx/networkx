"""Shortest paths and path lengths using the A* ("A star") algorithm."""

from heapq import heappop, heappush
from itertools import count

import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function
from networkx.utils import py_random_state

__all__ = ["astar_path", "astar_path_length", "alt_heuristic"]


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def astar_path(G, source, target, heuristic=None, weight="weight", *, cutoff=None):
    """Returns a list of nodes in a shortest path between source and target
    using the A* ("A-star") algorithm.

    There may be more than one shortest path.  This returns only one.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    heuristic : function
       A function to evaluate the estimate of the distance
       from the a node to the target.  The function takes
       two nodes arguments and must return a number.
       If the heuristic is inadmissible (if it might
       overestimate the cost of reaching the goal from a node),
       the result may not be a shortest path.
       The algorithm does not support updating heuristic
       values for the same node due to caching the first
       heuristic calculation per node.

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

    cutoff : float, optional
       If this is provided, the search will be bounded to this value. I.e. if
       the evaluation function surpasses this value for a node n, the node will not
       be expanded further and will be ignored. More formally, let h'(n) be the
       heuristic function, and g(n) be the cost of reaching n from the source node. Then,
       if g(n) + h'(n) > cutoff, the node will not be explored further.
       Note that if the heuristic is inadmissible, it is possible that paths
       are ignored even though they satisfy the cutoff.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> print(nx.astar_path(G, 0, 4))
    [0, 1, 2, 3, 4]
    >>> G = nx.grid_graph(dim=[3, 3])  # nodes are two-tuples (x,y)
    >>> nx.set_edge_attributes(G, {e: e[1][0] * 2 for e in G.edges()}, "cost")
    >>> def dist(a, b):
    ...     (x1, y1) = a
    ...     (x2, y2) = b
    ...     return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    >>> print(nx.astar_path(G, (0, 0), (2, 2), heuristic=dist, weight="cost"))
    [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    See Also
    --------
    shortest_path, dijkstra_path

    """
    if source not in G:
        raise nx.NodeNotFound(f"Source {source} is not in G")

    if target not in G:
        raise nx.NodeNotFound(f"Target {target} is not in G")

    if heuristic is None:
        # The default heuristic is h=0 - same as Dijkstra's algorithm
        def heuristic(u, v):
            return 0

    weight = _weight_function(G, weight)

    G_succ = G._adj  # For speed-up (and works for both directed and undirected graphs)

    # The queue stores priority, node, cost to reach, and parent.
    # Uses Python heapq to keep in priority order.
    # Add a counter to the queue to prevent the underlying heap from
    # attempting to compare the nodes themselves. The hash breaks ties in the
    # priority and is guaranteed unique for all nodes in the graph.
    c = count()
    queue = [(0, next(c), source, 0, None)]

    # Maps enqueued nodes to distance of discovered paths and the
    # computed heuristics to target. We avoid computing the heuristics
    # more than once and inserting the node into the queue too many times.
    enqueued = {}
    # Maps explored nodes to parent closest to the source.
    explored = {}

    while queue:
        # Pop the smallest item from queue.
        _, __, curnode, dist, parent = heappop(queue)

        if curnode == target:
            path = [curnode]
            node = parent
            while node is not None:
                path.append(node)
                node = explored[node]
            path.reverse()
            return path

        if curnode in explored:
            # Do not override the parent of starting node
            if explored[curnode] is None:
                continue

            # Skip bad paths that were enqueued before finding a better one
            qcost, h = enqueued[curnode]
            if qcost < dist:
                continue

        explored[curnode] = parent

        for neighbor, w in G_succ[curnode].items():
            cost = weight(curnode, neighbor, w)
            if cost is None:
                continue
            ncost = dist + cost
            if neighbor in enqueued:
                qcost, h = enqueued[neighbor]
                # if qcost <= ncost, a less costly path from the
                # neighbor to the source was already determined.
                # Therefore, we won't attempt to push this neighbor
                # to the queue
                if qcost <= ncost:
                    continue
            else:
                h = heuristic(neighbor, target)

            if cutoff and ncost + h > cutoff:
                continue

            enqueued[neighbor] = ncost, h
            heappush(queue, (ncost + h, next(c), neighbor, ncost, curnode))

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def astar_path_length(
    G, source, target, heuristic=None, weight="weight", *, cutoff=None
):
    """Returns the length of the shortest path between source and target using
    the A* ("A-star") algorithm.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    heuristic : function
       A function to evaluate the estimate of the distance
       from the a node to the target.  The function takes
       two nodes arguments and must return a number.
       If the heuristic is inadmissible (if it might
       overestimate the cost of reaching the goal from a node),
       the result may not be a shortest path.
       The algorithm does not support updating heuristic
       values for the same node due to caching the first
       heuristic calculation per node.

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

    cutoff : float, optional
       If this is provided, the search will be bounded to this value. I.e. if
       the evaluation function surpasses this value for a node n, the node will not
       be expanded further and will be ignored. More formally, let h'(n) be the
       heuristic function, and g(n) be the cost of reaching n from the source node. Then,
       if g(n) + h'(n) > cutoff, the node will not be explored further.
       Note that if the heuristic is inadmissible, it is possible that paths
       are ignored even though they satisfy the cutoff.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    See Also
    --------
    astar_path

    """
    if source not in G or target not in G:
        msg = f"Either source {source} or target {target} is not in G"
        raise nx.NodeNotFound(msg)

    weight = _weight_function(G, weight)
    path = astar_path(G, source, target, heuristic, weight, cutoff=cutoff)
    return sum(weight(u, v, G[u][v]) for u, v in zip(path[:-1], path[1:]))


@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def alt_heuristic(G, k=8, weight="length", method="farthest", seed=None):
    """Returns an ALT (A*, Landmarks, Triangle inequality) heuristic for graph `G`.

    It selects `k` landmark nodes and computes shortest-path distances between every
    node and each landmark (one Dijkstra sweep per landmark, two on directed graphs).
    The returned function ``h(u,v)`` us a lower bound on the shortest-path distance
    from ``u`` to ``v`` obtained from the triangle inequality, and can be passed
    directly as the ``heuristic`` argument of :func:`astar_path` or :func:`astar_path_length`.

    The heuristic is admissible (it never overestimates the true distance) and consistent,
    so A* retains its optimality guarantee. The one-time preprocessing cost is amortized over
    repeated shortest-path queries on the same graph.

    Parameters
    ----------
    G : NetworkX graph

    k : int, optional (default=8)
        Number of landmarks to select. Larger values give tighter bounds at the cost of more
        preprocessing time and ``O(k * n)`` memory (``O(2 * k * n)`` for directed graphs).
        Values greater than ``len(G)`` are capped.

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

    method : string, optional (default="farthest")
        Landmark selection strategy. ``"farthest"`` greedily selects landmarks that are
        far apart: the first landmark is chosen uniformly at random and each subsequent
        landmark maximizes the shortest-path distance to its nearest already-selected landmark.
        ``"random"`` selects `k` landmarks uniformly at random.

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    heuristic : callable
        A function ``h(u,v)`` that returns a lower bound on the shortest-path distance from
        ``u`` to ``v`` in `G`. The function is admissible and consistent. Suitable for the
        ``heuristic`` argument of :func:`astar_path` or :func:`astar_path_length`.

    Raises
    ------
    NetworkXError
        If `k` is less than 1.

    NetworkXPointlessConcept
        If `G` is empty.

    ValueError
        If `method` is not ``"farthest"`` or ``"random"``.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> h = nx.alt_heuristic(G, k=2, seed=10)
    >>> nx.astar_path(G, 0, 4, heuristic=h)
    [0, 1, 2, 3, 4]
    >>> h(0, 4)
    4

    Notes
    -----
    For each landmark :math:`\ell` with precomputed distances, the triangle inequality yields
    two lower bounds on the distance :math:`d(u, v)`:

    .. math::

        d(u, v) \geq |d(u, \ell) - d(v, \ell)|
        \qquad
        d(u, v) \geq |d(\ell, u) - d(\ell, v)|

    The heuristic returns the maximum of these bounds over all landmarks, or 0 if no landmark
    yields a finite bound (for example, across disconnected components).

    All shortest-path queries answered with this heuristic must use the same `weight` attribute
    that was used to build it; using a different weight may make the heuristic inadmissible and
    A* may return suboptimal paths.

    References
    ----------
    ..  [1] Goldberg, Andrew V., and Chris Harrelson. "Computing the shortest path: A search
    meets graph theory." In SODA, vol. 5, pp. 156-165. 2005.
    https://www.cs.princeton.edu/courses/archive/spr06/cos423/Handouts/GH05.pdf
    """

    if k < 1:
        raise nx.NetworkXError(f"Number of landmarks k={k} must be at least 1.")
    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            "ALT heuristic is undefined for empty graphs."
        )
    if method not in {"farthest", "random"}:
        raise ValueError(
            f"Unknown landmark selection method: {method}, must be 'farthest' or 'random'."
        )

    k = min(k, len(G))

    inf = float("inf")
    nodes = list(G)

    # Select landmarks and compute distances *from* each landmark.
    if method == "random":
        landmarks = seed.sample(nodes, k)
        dist_from = [
            nx.single_source_dijkstra_path_length(G, landmark, weight=weight)
            for landmark in landmarks
        ]
    elif method == "farthest":
        # Greedy farthest-point selection. Unreachable nodes are at distance infinity from each landmark,
        # so they are selected first, placing landmarks in every component.
        landmarks = [seed.choice(nodes)]
        dist_from = [
            nx.single_source_dijkstra_path_length(G, landmarks[0], weight=weight)
        ]
        nearest = {v: dist_from[0].get(v, inf) for v in nodes}
        while len(landmarks) < k:
            chosen = set(landmarks)
            farthest = max(
                (v for v in nodes if v not in chosen), key=nearest.__getitem__
            )
            landmarks.append(farthest)
            dists = nx.single_source_dijkstra_path_length(G, farthest, weight=weight)
            dist_from.append(dists)
            for v, d in dists.items():
                if d < nearest[v]:
                    nearest[v] = d

    # Distances *to* each landmark. On undirected graphs these equal the distances from each landmark,
    # so the same tables are reused.
    if G.is_directed():
        dist_to = [
            nx.single_source_dijkstra_path_length(
                G.reverse(copy=False), landmark, weight=weight
            )
            for landmark in landmarks
        ]
    else:
        dist_to = dist_from

    def heuristic(u, v):
        best = 0
        for d_from, d_to in zip(dist_from, dist_to):
            u_to, v_to = d_to.get(u, inf), d_to.get(v, inf)
            if u_to < inf and v_to < inf and u_to - v_to > best:
                best = u_to - v_to
            u_from, v_from = d_from.get(u, inf), d_from.get(v, inf)
            if u_from < inf and v_from < inf and v_from - u_from > best:
                best = v_from - u_from
        return best

    return heuristic
