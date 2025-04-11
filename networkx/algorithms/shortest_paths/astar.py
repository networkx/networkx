"""Shortest paths and path lengths using the A* ("A star") algorithm."""

from heapq import heappop, heappush
from itertools import count

import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function

__all__ = ["astar_path", "astar_path_length", "idastar_path", "idastar_path_length"]


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


"""Shortest paths and path lengths using the IDA* ("Iterative Deepening A star") algorithm."""


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def idastar_path(G, source, target, heuristic=None, weight="weight"):
    """Returns a list of nodes in a shortest path between source and target
    using the Iterative Deepening A* (IDA*) algorithm.

    There may be more than one shortest path. This function only returns one.

    Parameters
    ----------
    G : NetworkX graph
        A graph (directed or undirected) representing the structure to search.

    source : node
        Starting node for path.

    target : node
        Ending node for path.

    heuristic : function, optional
        A function to estimate the cost from a node to the target. It must take
        two node arguments and return a number. If not provided, the default is
        a zero heuristic, making IDA* equivalent to iterative-deepening Dijkstra.

    weight : string or function, optional (default='weight')
        If a string, it is interpreted as the edge attribute used as the edge
        weight. If a function, it must accept exactly three positional arguments:
        the two endpoints of an edge and the dictionary of edge attributes for
        that edge. It must return a numeric value or None to hide the edge.

    Returns
    -------
    path : list
        List of nodes representing the path from source to target.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    NetworkXNodeNotFound
        If either source or target is not in the graph.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.idastar_path(G, 0, 4)
    [0, 1, 2, 3, 4]

    >>> import math
    >>> G = nx.grid_graph(dim=[3, 3])
    >>> def dist(a, b):
    ...     (x1, y1) = a
    ...     (x2, y2) = b
    ...     return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    >>> nx.set_edge_attributes(G, 1, "cost")
    >>> nx.idastar_path(G, (0, 0), (2, 2), heuristic=dist, weight="cost")
    [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]

    Notes
    -----
    The algorithm performs a series of depth-first searches with increasing
    cost thresholds defined by f(n) = g(n) + h(n), where g(n) is the path cost
    from the source and h(n) is the heuristic estimate to the goal. The threshold
    is a max cost value the algorithm uses to analyse only the nodes that are below
    that value, if no nodes are below the threshold, the algorithm will expand the most
    promising one with the least cost above the threshold

    Edge weights must be non-negative numbers. The weight function can be used
    to filter edges by returning None.

    This function is suitable for graphs with large search spaces where memory
    efficiency is important or memory capacity is reduced, as it uses depth-first
    search and avoids storing all frontier nodes, keeping track of only the nodes
    that construct the path and removing the ones that do not.

    See Also
    --------
    astar_path, dijkstra_path, shortest_path
    """
    if source not in G:
        raise nx.NodeNotFound(f"Source {source} is not in G")

    if target not in G:
        raise nx.NodeNotFound(f"Target {target} is not in G")

    if heuristic is None:
        # Default heuristic is h=0, equivalent to Dijkstra's algorithm
        def heuristic(u, v):
            return 0

    weight = _weight_function(G, weight)
    G_succ = G._adj  # For speed-up (works for both directed and undirected graphs)

    # Threshold is equal to the heuristic of the cost of the
    # source node to the target since the cost to go from the
    # start node to itself is 0.
    threshold = heuristic(source, target)

    # IDA* main loop
    while True:
        explored = set()
        # Declare minimum threshold to infinite, that way, if
        # in the end the threshold is infinite we can verify
        # the path is impossible
        min_threshold = float("inf")
        stack = [(source, 0, 0, [source])]

        # Secondary loop to iterate through the stack of nodes
        while stack:
            # Get first node in stack, which in the
            # first ireteration is the source node
            node, g_cost, _, path = stack.pop()
            f_cost = g_cost + heuristic(node, target)

            if f_cost > threshold:
                min_threshold = min(min_threshold, f_cost)
                continue

            if node == target:
                return path  # Target found, end search and return path

            # If the node passes both validations then it's neither the
            # target node nor above the threshold value, so it's added
            # to the explored set
            explored.add(node)

            # List of all the neighbours to later analyse the most promising one
            neighbors = []

            for neighbor, w in G_succ[node].items():
                if neighbor in explored:
                    continue

                cost = weight(node, neighbor, w)
                if cost is None:
                    continue

                # Calculate the cost of the neighbor and add to the neighbors list
                next_g_cost = g_cost + cost
                # Calculate f(n) of the neighbour and store the data in the neighbors array
                f_cost_neighbor = next_g_cost + heuristic(neighbor, target)
                # Store f-cost and path + current neighbor
                neighbors.append(
                    (neighbor, next_g_cost, f_cost_neighbor, path + [neighbor])
                )

            neighbors.sort(key=lambda n: n[2])

            # Add neighbors to the stack in reverse order (LIFO)
            # so that most promising nodes are analysed first
            stack.extend(reversed(neighbors))
            # Remove explored node from set so that the
            # algorithm only keeps track of the nodes that
            # fit in the optimal path
            explored.remove(node)
        if min_threshold == float("inf"):
            raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")

        # Declare the new threshold for the next iteration
        threshold = min_threshold


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def idastar_path_length(G, source, target, heuristic=None, weight="weight"):
    """Returns the length of the shortest path between source and target using
    the Iterative Deepening A* (IDA*) algorithm.

    The function first finds the shortest path using the IDA* algorithm, then
    calculates the total length (sum of edge weights) of the path.

    Parameters
    ----------
    G : NetworkX graph
        A graph (directed or undirected) representing the structure to search.

    source : node
        Starting node for path.

    target : node
        Ending node for path.

    heuristic : function, optional
            A function to estimate the cost from a node to the target. It must take
            two node arguments and return a number. If not provided, the default is
            a zero heuristic, making IDA* equivalent to iterative-deepening Dijkstra.

    weight : string or function, optional (default='weight')
        If a string, it is interpreted as the edge attribute used as the edge
        weight. If a function, it must accept exactly three positional arguments:
        the two endpoints of an edge and the dictionary of edge attributes for
        that edge. It must return a numeric value or None to hide the edge.

    Returns
    -------
    length : float
        The total length (sum of edge weights) of the shortest path from source
        to target, as found by the IDA* algorithm.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    NetworkXNodeNotFound
        If either source or target is not in the graph.

    See Also
    --------
    idastar_path
    """
    # Validate if source and target are in the graph received
    if source not in G or target not in G:
        msg = f"Either source {source} or target {target} is not in G"
        raise nx.NodeNotFound(msg)

    # Get the graph node weights
    weight = _weight_function(G, weight)
    path = idastar_path(G, source, target, heuristic, weight)
    # Calculate the optimal path by calling the IDA* algorithm and
    # calculate the sum of the costs of all the nodes in the path
    # returned
    return sum(weight(u, v, G[u][v]) for u, v in zip(path[:-1], path[1:]))
