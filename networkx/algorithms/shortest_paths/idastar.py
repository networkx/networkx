"""Shortest paths and path lengths using the IDA* ("Iterative Deepening A star") algorithm."""

import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function

__all__ = ["idastar_path", "idastar_path_length"]


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def idastar_path(G, source, target, heuristic=None, weight="weight"):
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

    def search(node, g_cost, threshold, path, explored):
        """Recursive depth-first search with f-cost threshold."""

        f_cost = g_cost + heuristic(node, target)
        if f_cost > threshold:
            return f_cost, None  # Return the new threshold as a cutoff value

        if node == target:
            return f_cost, path + [node]  # Found the target, end search and return path

        # If the node passes both validations then it's neither the
        # target node nor above the threshold value, so it's added
        # to the explored set

        # Declare minimum threshold to infinite, that way, if
        # in the end the threshold is infinite we can verify
        # the path is impossible
        min_threshold = float("inf")
        explored.add(node)

        # List for storing all the node's neighbours to later analyse the most promising one
        neighbors = []
        for neighbor, w in G_succ[node].items():
            if neighbor in explored:
                continue

            cost = weight(node, neighbor, w)
            if cost is None:
                continue

            # Calculate the cost of the neighbor and add to the neighbors list
            next_g_cost = g_cost + cost
            # Calculate f(n) of the neighbor and store the data in the neighbors list
            f_cost_neighbor = next_g_cost + heuristic(neighbor, target)
            neighbors.append((neighbor, next_g_cost, f_cost_neighbor))  # Store f-cost

        # Sort the neighbors list in ascending order
        # of it's f-cost, sorting the most promising
        # nodes in the first positions of the list
        neighbors.sort(key=lambda n: n[2])

        # Get first node in list, which is the
        # most promising neighbor of the node
        for neighbor, next_g_cost, f_cost_neighbor in neighbors:
            result_threshold, result_path = search(
                neighbor, next_g_cost, threshold, path + [node], explored
            )
            if result_path is not None:
                return (
                    result_threshold,
                    result_path,
                )  # Target found, end search and return path

            min_threshold = min(min_threshold, result_threshold)

        # Remove explored node from set so that the
        # algorithm only keeps track of the nodes that
        # fit in the optimal path
        explored.remove(node)
        return min_threshold, None  # Return the updated threshold and no path

    # IDA* main loop
    # Threshold is equal to the heuristic of the cost of the
    # source node to the target since the cost to go from the
    # start node to itself is 0.
    threshold = heuristic(source, target)
    while True:
        # Set that stores the explored nodes
        # along the way of the path finding
        explored = set()
        threshold, path = search(source, 0, threshold, [], explored)
        if path is not None:  # Path found
            return path

        if threshold == float("inf"):  # Path from source to target doesn't exist
            raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def idastar_path_length(G, source, target, heuristic=None, weight="weight"):
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
