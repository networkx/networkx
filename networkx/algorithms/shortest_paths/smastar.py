"""
Adapted implementation of the SMA* (Simplified Memory-Bounded A*) algorithm for NetworkX.

Originally inspired by existing pathfinding algorithms in the NetworkX library.
In compliance with the original BSD 3-Clause License, copyright notices and
appropriate attribution must be retained. See the official repository:
    https://github.com/networkx/networkx
"""

import math
from heapq import heappop, heappush
from itertools import count

import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function

__all__ = ["sma_star_path", "sma_star_path_length"]


def euclidean_heuristic(G, u, v):
    """
    Computes the Euclidean heuristic between two nodes.

    Assumes nodes have 'x' and 'y' attributes. If not,
    returns 0 to maintain admissibility.

    Parameters
    ----------
    G : networkx.Graph
        The graph containing the nodes.
    u : node
        Source node.
    v : node
        Target node.

    Returns
    -------
    float
        Euclidean distance between u and v or 0 if attributes are missing.
    """
    try:
        x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
        x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
        return math.hypot(x2 - x1, y2 - y1)
    except KeyError:
        return 0


def sma_star_path(
    G, source, target, heuristic=None, weight="weight", memory_limit=10000
):
    """
    Returns the shortest path between 'source' and 'target' using the SMA* algorithm.

    Parameters
    ----------
    G : networkx.Graph or networkx.DiGraph
        Graph on which to perform the search.
    source : node
        Starting node.
    target : node
        Goal node.
    heuristic : callable, optional
        Heuristic function h(u, v) estimating the cost between nodes.
        Defaults to Euclidean distance if not provided.
    weight : string or callable, optional
        Edge data key corresponding to the edge weight (default: "weight").
    memory_limit : int, optional
        Maximum number of nodes to keep in memory (default: 10000).

    Returns
    -------
    list
        List of nodes representing the shortest path.

    Raises
    ------
    nx.NodeNotFound
        If 'source' or 'target' is not in the graph.
    nx.NetworkXNoPath
        If no path exists between 'source' and 'target'.
    """
    if source not in G:
        raise nx.NodeNotFound(f"Source {source} is not in G")
    if target not in G:
        raise nx.NodeNotFound(f"Target {target} is not in G")

    if heuristic is None:

        def heuristic(u, v):
            return euclidean_heuristic(G, u, v)

    push, pop = heappush, heappop
    weight_fn = _weight_function(G, weight)
    G_succ = G._adj
    counter = count()

    queue = [(0, next(counter), source, 0, None)]
    best_cost = {source: 0}
    came_from = {}

    while queue:
        if len(queue) > memory_limit:
            queue.sort(reverse=True, key=lambda x: x[0])
            queue.pop(0)

        f, _, current, g, parent = pop(queue)

        if g > best_cost.get(current, float("inf")):
            continue

        if parent is not None:
            came_from[current] = parent

        if current == target:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        for neighbor, edge_attr in G_succ[current].items():
            cost = weight_fn(current, neighbor, edge_attr)
            if cost is None:
                continue
            new_cost = g + cost

            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                h = heuristic(neighbor, target)
                push(queue, (new_cost + h, next(counter), neighbor, new_cost, current))

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")


def sma_star_path_length(
    G, source, target, heuristic=None, weight="weight", memory_limit=10000
):
    """
    Returns the total cost of the shortest path found by SMA*.

    Parameters
    ----------
    G : networkx.Graph or networkx.DiGraph
        Graph on which to perform the search.
    source : node
        Starting node.
    target : node
        Goal node.
    heuristic : callable, optional
        Heuristic function used.
    weight : string or callable, optional
        Edge data key corresponding to the edge weight.
    memory_limit : int, optional
        Maximum number of nodes to keep in memory (default: 10000).

    Returns
    -------
    float
        Total cost of the computed path.
    """
    path = sma_star_path(G, source, target, heuristic, weight, memory_limit)
    return sum(
        _weight_function(G, weight)(u, v, G[u][v]) for u, v in zip(path[:-1], path[1:])
    )
