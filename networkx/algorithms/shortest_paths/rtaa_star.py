# Real-Time Adaptive A* pathfinding algorithm for NetworkX
# Based on: Koenig & Likhachev (2006) - RTAA*
# Contributed by the open-source community.

"""Shortest paths and path lengths using the Real-Time Adaptive A* (RTAA*) algorithm."""

__all__ = ['rtaa_star_path', 'rtaa_star_path_length']

import heapq
from math import sqrt
from networkx.exception import NetworkXNoPath, NodeNotFound
from networkx.utils import not_implemented_for

def _rtaa_star_search(G, source, target, heuristic=None, weight='weight',
                      lookahead=None, move_limit=1, landmarks=None):
    """
    Internal function that executes the enhanced RTAA* algorithm and returns a tuple (path, cost).
    """
    # Validate that source and target are in the graph
    if source not in G:
        raise NodeNotFound(f"Source {source} is not in the graph")
    if target not in G:
        raise NodeNotFound(f"Target {target} is not in the graph")
    if source == target:
        return [source], 0
    
    # Validate that all landmarks exist in the graph
    if landmarks:
        if isinstance(landmarks, (list, tuple, set)):
            for node in landmarks:
                if node not in G:
                    raise NodeNotFound(f"Landmark {node} is not in the graph")
                
    # Function to retrieve edge weight (attribute or function)
    if callable(weight):
        weight_func = weight
    else:
        def weight_func(u, v):
            data = G.get_edge_data(u, v, default={})
            return data.get(weight, 1)  # assume weight 1 if attribute is missing

    # Euclidean distance function (if coordinates available, else 0)
    def euclidean_distance(u, v):
        # Try to extract node coordinates (from 'pos' attribute or tuple)
        def get_coords(node):
            # If the node is directly a numeric tuple (e.g., (x, y))
            if isinstance(node, tuple) and len(node) >= 2 and all(isinstance(c, (int, float)) for c in node):
                return node
            # If the node has position attributes in the graph
            if node in G.nodes:
                data = G.nodes[node]
                if 'pos' in data:
                    return data['pos']
                if 'x' in data and 'y' in data:
                    return (data['x'], data['y'])
            return None
        pu, pv = get_coords(u), get_coords(v)
        if pu is None or pv is None:
            return 0  # no coordinates found, return 0 (admissible zero heuristic)
        # Euclidean distance between u and v
        return sqrt(sum((a - b) ** 2 for a, b in zip(pu, pv)))

    # Landmark selection and preprocessing (if requested)
    landmark_distances = {}  # maps each landmark to computed distances
    if landmarks:
        # Determine list of nodes to be used as landmarks
        if isinstance(landmarks, int):
            num_landmarks = landmarks
            landmark_list = []
            # Simple strategy: use source and target, and possibly distant nodes
            if num_landmarks >= 1:
                landmark_list.append(source)
            if num_landmarks >= 2:
                landmark_list.append(target)
            # If more landmarks are requested, choose distant nodes (using BFS/Dijkstra from source or target)
            if num_landmarks >= 3:
                # Find the farthest node from the source (in terms of path distance)
                # Perform a Dijkstra/BFS from the source
                dist_map = {source: 0}
                open_heap = [(0, source)]
                while open_heap:
                    d, node = heapq.heappop(open_heap)
                    if d != dist_map[node]:
                        continue
                    for nbr in G[node]:
                        new_d = d + weight_func(node, nbr)
                        if new_d < dist_map.get(nbr, float('inf')):
                            dist_map[nbr] = new_d
                            heapq.heappush(open_heap, (new_d, nbr))
                # Farthest node found
                farthest = max(dist_map, key=lambda x: dist_map[x] if dist_map[x] != float('inf') else -1)
                if farthest not in landmark_list:
                    landmark_list.append(farthest)
            if num_landmarks >= 4:
                # Find the farthest node from the target
                dist_map = {target: 0}
                open_heap = [(0, target)]
                while open_heap:
                    d, node = heapq.heappop(open_heap)
                    if d != dist_map[node]:
                        continue
                    for nbr in G[node]:
                        new_d = d + weight_func(node, nbr)
                        if new_d < dist_map.get(nbr, float('inf')):
                            dist_map[nbr] = new_d
                            heapq.heappush(open_heap, (new_d, nbr))
                farthest2 = max(dist_map, key=lambda x: dist_map[x] if dist_map[x] != float('inf') else -1)
                if farthest2 not in landmark_list:
                    landmark_list.append(farthest2)
            # Limit to the requested number
            landmark_list = landmark_list[:num_landmarks]
        else:
            # Explicit list of landmarks provided
            landmark_list = list(landmarks)
        # Compute distances from each selected landmark to all nodes (using Dijkstra)
        for L in landmark_list:
            distances = {L: 0}
            open_heap = [(0, L)]
            while open_heap:
                d, node = heapq.heappop(open_heap)
                if d != distances[node]:
                    continue
                for nbr in G[node]:
                    new_d = d + weight_func(node, nbr)
                    if new_d < distances.get(nbr, float('inf')):
                        distances[nbr] = new_d
                        heapq.heappush(open_heap, (new_d, nbr))
            landmark_distances[L] = distances

    # Cache of base heuristic (geometric + ALT) for each node
    base_h_cache = {}
    def base_heuristic(n):
        # Use cache to avoid repeated calculations
        if n in base_h_cache:
            return base_h_cache[n]
        # Geometric heuristic (Euclidean or custom)
        if heuristic is not None:
            h_val = heuristic(n, target)
        else:
            h_val = euclidean_distance(n, target)
        # Landmark heuristic (ALT) - takes the largest difference |d(L, target) - d(L, n)|
        if landmark_distances:
            h_alt = 0
            for L, dist_map in landmark_distances.items():
                if target in dist_map:
                    dLt = dist_map[target]
                    dLn = dist_map.get(n, float('inf'))
                    if dLn == float('inf'):
                        # if n is not reachable from L, skip this landmark
                        continue
                    diff = abs(dLt - dLn)
                    if diff > h_alt:
                        h_alt = diff
            if h_alt > h_val:
                h_val = h_alt
        base_h_cache[n] = h_val
        return h_val

    # Dictionary for the current adaptive heuristic values (updated during execution)
    adapt_h = {target: 0}
    # Final result: constructed path and total cost
    path = [source]
    path_cost = 0.0

    # Determine expansion limit (lookahead); None/0 means full search
    expansion_limit = float('inf') if not lookahead or lookahead <= 0 else lookahead

    # Current state of the agent (starting at source)
    current = source
    # Main loop of RTAA*: continues until the goal is reached
    while current != target:
        # Set up A* search structure from the current state
        open_heap = []  # heap of open nodes (f, order, node tuples)
        closed_set = set()  # set of nodes expanded in this iteration
        g = {current: 0.0}  # costs from current to each node
        parent = {current: None}  # predecessors for reconstructing the path
        # Insert current node into the frontier
        f_start = adapt_h.get(current, base_heuristic(current))
        heapq.heappush(open_heap, (f_start, 0, current))
        expansions = 0
        s_bar = None
        found_goal = False

        # Limited A* search (expand at most expansion_limit nodes)
        while open_heap and expansions < expansion_limit:
            f_val, _, node = heapq.heappop(open_heap)
            if node in closed_set:
                continue  # already expanded (ignore duplicate entries)
            closed_set.add(node)
            # Check if the heap entry is outdated (can occur if g/h values were improved later)
            if f_val != g[node] + adapt_h.get(node, base_heuristic(node)):
                continue  # ignore if a better cost for this node was found
            # If the goal is reached during the search, we can exit
            if node == target:
                found_goal = True
                s_bar = node
                break
            # Expand neighbors of the current node
            expansions += 1
            for nbr in G[node]:
                if nbr in closed_set:
                    continue
                new_cost = g[node] + weight_func(node, nbr)
                if new_cost < g.get(nbr, float('inf')):
                    g[nbr] = new_cost
                    parent[nbr] = node
                    f_nbr = new_cost + adapt_h.get(nbr, base_heuristic(nbr))
                    heapq.heappush(open_heap, (f_nbr, expansions, nbr))
            # If expansion limit reached, set s_bar (best of frontier)
            if expansions >= expansion_limit:
                if open_heap:
                    s_bar = open_heap[0][2]  # node with smallest f remaining in the frontier
                else:
                    s_bar = node
                break

        # If the search ended without finding a path and the frontier is empty (graph disconnected)
        if not found_goal and not open_heap and s_bar is None:
            raise NetworkXNoPath(f"No path to {target} from {source}")

        # Special case: if no nodes remain in frontier and goal was not found, then no path exists
        if s_bar is None:
            # (This can happen if open_heap became empty exactly at the break, indicating failure)
            raise NetworkXNoPath(f"No path to {target} from {source}")

        # Update adaptive heuristics for all nodes expanded in this iteration using s_bar as reference
        # (Ensures admissibility and monotonicity)
        h_s_bar = adapt_h.get(s_bar, base_heuristic(s_bar))
        g_s_bar = g.get(s_bar, float('inf'))
        for s in closed_set:
            if s == s_bar:
                continue  # do not update s_bar itself (it was not expanded)
            # New heuristic value calculated
            new_h = g_s_bar + h_s_bar - g[s]
            # Ensure not to decrease the existing heuristic
            current_h = adapt_h.get(s, base_heuristic(s))
            if new_h < current_h:
                new_h = current_h
            # Keep goal node with zero heuristic
            adapt_h[s] = 0 if s == target else new_h

        # Move the agent: follow the path toward s_bar (or part of it, depending on move_limit)
        if found_goal:
            # If the goal was found during the search, reconstruct the full path to it
            node = target
            segment = []
            while node is not None:
                segment.append(node)
                node = parent.get(node)
            segment.reverse()  # now it runs from current to target
            # Add to the final path (ignoring the repeated current node)
            path.extend(segment[1:])
            path_cost += g[target]  # g[target] is the total cost from current to target
            current = target
            break  # goal reached, exit the main loop
        else:
            # Goal not reached yet, continue toward s_bar
            # Reconstruct path from current state to s_bar via parents
            node = s_bar
            segment = []
            while node is not None:
                segment.append(node)
                node = parent.get(node)
            segment.reverse()  # path from current to s_bar
            if segment[0] != current:
                segment.insert(0, current)
            # Define how many steps to move (move_limit)
            steps = move_limit if move_limit and move_limit > 0 else 1
            if steps > len(segment) - 1:
                steps = len(segment) - 1  # do not surpass s_bar
            # Walk through the segment nodes, one at a time
            for i in range(1, steps + 1):
                next_node = segment[i]
                path.append(next_node)
                # add edge cost (current -> next_node)
                path_cost += weight_func(current, next_node)
                current = next_node
            # Main loop continues with the current state updated
    # Return the complete path and its total cost
    return path, path_cost

@not_implemented_for('multigraph')  
def rtaa_star_path(G, source, target, heuristic=None, weight='weight',
                   lookahead=None, move_limit=1, landmarks=None):
    """Return a list of nodes in a path between source and target using the Real-Time Adaptive A* (RTAA*) algorithm.

    This algorithm searches for a path incrementally, making it suitable for real-time scenarios where only a limited search can be done per step.
    It uses adaptive heuristics (which can incorporate landmarks) to ensure that the search remains efficient and optimal.

    Parameters
    ----------
    G : NetworkX graph
        The input graph.

    source : node
        Starting node for the path.

    target : node
        Ending node for the path.

    heuristic : function, optional (default=None)
        Heuristic function used to estimate the distance from a node to the target.
        The function takes two nodes as arguments and must return a number. If None, a default heuristic of Euclidean distance (if node positions are available) or 0 is used.

    weight : string or function, optional (default="weight")
        If a string, use this edge attribute as the edge weight. If no such attribute exists, the edge weight is assumed to be 1.
        If a function, it must accept three arguments (u, v, d) where u and v are node identifiers and d is the edge attribute dictionary; it must return a number representing the weight of the edge.

    lookahead : int, optional (default=None)
        The maximum number of node expansions allowed in each A* search iteration (the lookahead depth).
        If None or 0, the algorithm performs a full A* search to the goal in each iteration.

    move_limit : int, optional (default=1)
        The number of steps (edges) to move along the computed path in each iteration before replanning.
        After moving this many steps (or if the target is reached sooner), the algorithm repeats the A* search from the new current position.

    landmarks : int or iterable, optional (default=None)
        If an int, specifies the number of landmark nodes to use for the ALT heuristic (A*, Landmarks, and Triangle inequality). Up to that many landmarks will be chosen, including the source, target, and other distant nodes, to improve the heuristic estimate.
        If an iterable of nodes is given, those nodes are used as landmarks. If None, no landmark heuristic is used.

    Returns
    -------
    path : list
        List of nodes in the path from source to target.

    Raises
    ------
    NodeNotFound
        If `source` or `target` is not in the graph `G`.
    NetworkXNoPath
        If no path exists between source and target.

    See Also
    --------
    rtaa_star_path_length : Compute the path length (total cost) using RTAA*.
    astar_path : A* algorithm for shortest path.
    dijkstra_path : Dijkstra’s algorithm for shortest path.

    Notes
    -----
    Real-Time Adaptive A* (RTAA*) [1]_ is a real-time heuristic search algorithm that plans in small increments. It updates the heuristic values of expanded nodes after each limited search (adaptive heuristic), which guides subsequent searches more effectively. This behavior allows it to handle large graphs by constraining the search space (via the `lookahead`) and still eventually finding an optimal path if the heuristic is admissible.

    References
    ----------
    .. [1] Sven Koenig, Maxim Likhachev, "Real-Time Adaptive A*", Proceedings of the International Joint Conference on Autonomous Agents and Multiagent Systems (AAMAS 2006), pp. 281-288, 2006.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(5)
    >>> nx.rtaa_star_path(G, 0, 4)
    [0, 1, 2, 3, 4]
    """
    path, cost = _rtaa_star_search(G, source, target, heuristic, weight, lookahead, move_limit, landmarks)
    return path

@not_implemented_for('multigraph')
def rtaa_star_path_length(G, source, target, heuristic=None, weight='weight',
                          lookahead=None, move_limit=1, landmarks=None):
    """Return the length (total weight) of a path between source and target using the Real-Time Adaptive A* (RTAA*) algorithm.

    The length is the sum of the weights of the edges in the path found by the algorithm.

    Parameters
    ----------
    G : NetworkX graph
        The input graph.

    source : node
        Starting node for the path.

    target : node
        Ending node for the path.

    heuristic : function, optional (default=None)
        Heuristic function used to estimate the distance from a node to the target (see `rtaa_star_path`).

    weight : string or function, optional (default="weight")
        Weight attribute or function (see `rtaa_star_path` for details).

    lookahead : int, optional (default=None)
        Maximum number of node expansions per iteration (see `rtaa_star_path`).

    move_limit : int, optional (default=1)
        Number of steps to move per iteration (see `rtaa_star_path`).

    landmarks : int or iterable, optional (default=None)
        Landmarks for ALT heuristic (see `rtaa_star_path`).

    Returns
    -------
    length : number
        Total cost of the path from source to target.

    Raises
    ------
    NodeNotFound
        If `source` or `target` is not in the graph `G`.
    NetworkXNoPath
        If no path exists between source and target.

    """
    path, cost = _rtaa_star_search(G, source, target, heuristic, weight, lookahead, move_limit, landmarks)
    return cost
