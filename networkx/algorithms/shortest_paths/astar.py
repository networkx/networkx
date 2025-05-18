"""Shortest paths and path lengths using the A* ("A star") algorithm."""

import heapq
import math
from functools import cache, lru_cache
from heapq import heappop, heappush
from itertools import count

import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function
from networkx.exception import NetworkXNoPath
from networkx.utils.decorators import not_implemented_for

__all__ = ["astar_path", "astar_path_length", "bidirectional_astar"]


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

    push = heappush
    pop = heappop
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
        _, __, curnode, dist, parent = pop(queue)

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
            push(queue, (ncost + h, next(c), neighbor, ncost, curnode))

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


# === Bidirectional A* Search ===


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def bidirectional_astar(
    G,
    source,
    target,
    heuristic=None,
    weight="weight",
    max_nodes_expanded=None,
    max_heuristic_distance=None,
    greedy=False,
):
    """Returns a shortest path between source and target using Bidirectional A*.

    This implementation performs two simultaneous A* searches—one forward from the
    source, one backward from the target—until the frontiers meet.

    Parameters
    ----------
    G : NetworkX graph

    source : node
        Starting node for path

    target : node
        Ending node for path

    heuristic : function, optional
        A function to estimate the distance from a node to the target.
        Takes two node arguments and returns a float. If None, defaults
        to Euclidean heuristic for 2D grid graphs.

    weight : string or function, default="weight"
        Edge weight specification. If a string, edge weights are accessed
        via `G[u][v][weight]`. If a function, it should accept arguments
        (u, v, edge_data) and return a numeric cost.

    max_nodes_expanded : int, optional
        If set, defines a maximum number of nodes to expand. When exceeded,
        switches to greedy mode to finish faster.

    max_heuristic_distance : float, optional
        If set, the algorithm aborts if estimated heuristic distance
        between source and target exceeds this threshold.

    greedy : bool, default=False
        If True, the algorithm uses only the heuristic (Greedy Best-First Search),
        ignoring accumulated cost. Provides faster execution at the cost of
        path optimality.

    Returns
    -------
    total_cost : float
        The total weight of the path found.

    path : list
        List of nodes representing the computed path from source to target.

    stats : dict
        Dictionary with profiling statistics:
        - nodes_expanded_forward
        - nodes_expanded_backward
        - total_nodes_expanded
        - explored_percent

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    Notes
    -----
    This implementation prioritizes performance in large graphs.
    If `greedy=True`, the path may not be optimal.

    """
    if source not in G:
        raise NodeNotFound(f"Source {source} is not in G")
    if target not in G:
        raise NodeNotFound(f"Target {target} is not in G")
    if source == target:
        return (0, [source], {"total_nodes_expanded": 1})

    # Default heuristic: Euclidean distance between 2D grid coordinates
    @cache
    def _euclidean_heuristic(u, v):
        try:
            x1, y1 = u
            x2, y2 = v
            return math.hypot(x2 - x1, y2 - y1)
        except (TypeError, ValueError):
            return 0

    if heuristic is None:
        heuristic = _euclidean_heuristic

    def h_forward(n):
        return heuristic(n, target)

    def h_backward(n):
        return heuristic(n, source)

    weight_fn = _weight_function(G, weight)

    dist = [{}, {}]
    pred = [{}, {}]
    seen = [{source: 0}, {target: 0}]
    fringe = [[], []]
    counter = count()
    visited_nodes = [set(), set()]
    frontier_sizes = []

    heapq.heappush(
        fringe[0],
        ((h_forward(source) if greedy else h_forward(source)), next(counter), source),
    )
    heapq.heappush(
        fringe[1],
        ((h_backward(target) if greedy else h_backward(target)), next(counter), target),
    )

    neighbors = [G._succ, G._pred] if G.is_directed() else [G._adj, G._adj]
    meeting_node = None

    while fringe[0] and fringe[1]:
        f_cost_0 = fringe[0][0][0]
        f_cost_1 = fringe[1][0][0]
        direction = 0 if f_cost_0 <= f_cost_1 else 1

        f_cost, _, curr = heapq.heappop(fringe[direction])
        if curr in dist[direction]:
            continue

        dist[direction][curr] = seen[direction][curr]
        visited_nodes[direction].add(curr)

        if curr in seen[1 - direction]:
            meeting_node = curr
            break

        if (
            max_heuristic_distance is not None
            and heuristic(source, target) > max_heuristic_distance
        ):
            raise NetworkXNoPath("Path exceeds max heuristic distance.")

        if (
            max_nodes_expanded is not None
            and (len(visited_nodes[0]) + len(visited_nodes[1])) > max_nodes_expanded
        ):
            greedy = True  # force fast greedy fallback

        frontier_sizes.append((len(fringe[0]), len(fringe[1])))

        for nbr, edata in neighbors[direction][curr].items():
            cost = (
                weight_fn(curr, nbr, edata)
                if direction == 0
                else weight_fn(nbr, curr, edata)
            )
            if cost is None:
                continue
            new_cost = dist[direction][curr] + (0 if greedy else cost)
            if nbr in dist[direction]:
                continue
            if nbr not in seen[direction] or new_cost < seen[direction][nbr]:
                seen[direction][nbr] = new_cost
                pred[direction][nbr] = curr
                heuristic_cost = h_forward(nbr) if direction == 0 else h_backward(nbr)
                total_cost = heuristic_cost if greedy else new_cost + heuristic_cost
                heapq.heappush(fringe[direction], (total_cost, next(counter), nbr))

    if meeting_node is None:
        raise NetworkXNoPath(f"No path between {source} and {target}.")

    forward_path = []
    node = meeting_node
    while node in pred[0]:
        forward_path.append(node)
        node = pred[0][node]
    forward_path.append(node)
    forward_path.reverse()

    backward_path = []
    node = meeting_node
    while node in pred[1]:
        backward_path.append(node)
        node = pred[1][node]
    backward_path.append(node)

    forward_path.pop()
    full_path = forward_path + backward_path

    stats = {
        "nodes_expanded_forward": len(visited_nodes[0]),
        "nodes_expanded_backward": len(visited_nodes[1]),
        "total_nodes_expanded": len(visited_nodes[0]) + len(visited_nodes[1]),
        "explored_percent": (len(visited_nodes[0]) + len(visited_nodes[1]))
        / G.number_of_nodes()
        * 100,
    }

    total_cost = 0
    for i in range(len(full_path) - 1):
        u, v = full_path[i], full_path[i + 1]
        total_cost += G[u][v].get(weight, 1)

    return (total_cost, full_path, stats)
