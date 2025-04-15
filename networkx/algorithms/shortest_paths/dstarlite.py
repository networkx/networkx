"""Dynamic shortest paths and path lengths using the D* Lite ("D star Lite") algorithm."""

import heapq

import networkx as nx

__all__ = [
    "new_dstar_lite_instance",
    "d_star_modify_edge",
    "d_star_recalculate_path",
    "d_star_get_path_cost",
    "d_star_get_path_length",
]


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def new_dstar_lite_instance(G, source, target, heuristic=None, weight="weight"):
    """
    Initializes a new instance of the D* Lite algorithm for a NetworkX graph.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        The search graph containing nodes and weighted edges.
    source : hashable
        The starting node for the path.
    target : hashable
        The target node for the path.
    heuristic : function(u, v) -> float, optional
        The heuristic function to estimate the distance between two nodes.
        Default is a zero heuristic (equivalent to Dijkstra's algorithm).
    weight : str, optional
        The edge attribute that represents the weights. Default is 'weight'.

    Returns
    -------
    DStarLite
        A configured instance of the D* Lite algorithm ready for operations.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> edges = [
    ...     ("A", "B", 1),
    ...     ("B", "C", 2),
    ...     ("A", "D", 4),
    ...     ("D", "C", 1),
    ...     ("C", "E", 3),
    ...     ("B", "E", 5),
    ... ]
    >>> for u, v, w in edges:
    ...     G.add_edge(u, v, weight=w)
    >>> dstar = new_dstar_lite_instance(G, "A", "E", weight="weight")
    >>>
    >>> print(dstar.get_path())
    ['A', 'B', 'C', 'E']
    >>> print(dstar.get_path_cost())
    6
    >>>
    >>> newGraph = d_star_modify_edge(dstar, "B", "C", 10)
    >>> d_star_recalculate_path(dstar)
    ['A', 'B', 'E']
    >>> print(dstar.get_path_cost())
    6
    """
    return DStarLite(G, source, target, heuristic, weight)


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def d_star_modify_edge(instance, u, v, new_weight, weight="weight"):
    """
    Dynamically modifies the weight of an edge and updates the path.

    Parameters
    ----------
    weight
    instance : DStarLite
        The active instance of the algorithm.
    u : hashable
        The source node of the edge.
    v : hashable
        The target node of the edge.
    new_weight : float
        The new weight/cost of the edge.

    Returns
    -------
    nx.Graph or nx.DiGraph
        The updated graph containing the modified edge.
    """
    return instance.modify_edge(u, v, new_weight)


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def d_star_recalculate_path(instance, weight="weight"):
    """
    Recalculates the shortest path after modifications in the graph.

    Parameters
    ----------
    weight
    instance : DStarLite
        The active instance of the algorithm.

    Returns
    -------
    list or None
        A list of nodes representing the path, or None if no path exists.
    """
    instance.compute_shortest_path()
    return instance.get_path()


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def d_star_get_path_cost(instance, weight="weight"):
    """
    Returns the total cost of the last computed path.

    This function calls the `get_path_cost()` method of the given DStarLite instance
    to obtain the sum of the weights along the currently computed shortest path.
    If no path exists, it returns infinity.

    Parameters
    ----------
    weight
    instance : DStarLite
        The active instance of the D* Lite algorithm.

    Returns
    -------
    int or float
        The total cost of the path (i.e., the sum of the edge weights), or infinity if no path exists.
    """
    return instance.get_path_cost()


@nx._dispatchable(edge_attrs="weight", preserve_node_attrs="heuristic")
def d_star_get_path_length(instance, weight="weight"):
    """
    Returns the length (number of edges) of the last computed path.

    This function calls the `get_path_length()` method of the given DStarLite instance
    to obtain the number of edges in the currently computed shortest path.
    If no path exists, it returns infinity.

    Parameters
    ----------
    weight
    instance : DStarLite
        The active instance of the D* Lite algorithm.

    Returns
    -------
    int or float
        The number of edges in the path, or infinity if no path exists.
    """
    return instance.get_path_length()


# --------------------------------------------------------------------------------------
# Fundamental Data Structures
# --------------------------------------------------------------------------------------


class PriorityQueue:
    """
    An optimized priority queue for D* Lite supporting:
      - O(1) priority updates.
      - Lazy removal of obsolete items.
      - Access to the smallest element without removal.

    Attributes
    ----------
    heap : list
        Internal storage using a heap structure.
    entry_map : dict
        A fast mapping from items to their entries in the heap.
    count : int
        A version counter to break ties in priority.
    """

    def __init__(self):
        """Initializes an empty priority queue."""
        self.heap = []
        self.entry_map = {}
        self.count = 0

    def push(self, item, priority):
        """
        Inserts or updates an item in the priority queue with a new priority.

        Parameters
        ----------
        item : hashable
            The item to be inserted.
        priority : tuple(float, float)
            The priority (k1, k2) calculated by D* Lite.
        """
        if item in self.entry_map:
            self.remove(item)
        entry = [priority, self.count, item]
        heapq.heappush(self.heap, entry)
        self.entry_map[item] = entry
        self.count += 1

    def remove(self, item):
        """
        Lazily removes an item by marking its entry as invalid.

        Parameters
        ----------
        item : hashable
            The item to remove.
        """
        if item in self.entry_map:
            entry = self.entry_map.pop(item)
            entry[-1] = None  # Invalidate the entry without modifying the heap

    def pop(self):
        """
        Removes and returns the item with the smallest priority, cleaning up invalid entries.

        Returns
        -------
        hashable
            The next valid item with the smallest priority.

        Raises
        ------
        KeyError
            If the priority queue is empty.
        """
        while self.heap:
            priority, _, item = heapq.heappop(self.heap)
            if item is not None:
                del self.entry_map[item]
                return item
        raise KeyError("Priority queue is empty")

    def empty(self):
        """Checks whether the priority queue is empty."""
        return not self.entry_map

    def top_key(self):
        """
        Returns the smallest current key without modifying the queue.

        Returns
        -------
        tuple(float, float)
            The priority (k1, k2) of the top valid item, or (inf, inf) if the queue is empty.
        """
        while self.heap:
            priority, _, item = self.heap[0]
            if item is None:
                heapq.heappop(self.heap)
            else:
                return priority
        return float("inf"), float("inf")


# --------------------------------------------------------------------------------------
# Core Implementation of D* Lite
# --------------------------------------------------------------------------------------


class DStarLite:
    """
    Implementation of the D* Lite algorithm for dynamic graph shortest path problems.

    Attributes
    ----------
    G : nx.Graph or nx.DiGraph
        A local copy of the input graph.
    source : hashable
        The current starting node.
    target : hashable
        The fixed target node.
    weight : str
        The edge attribute representing weights.
    heuristic : function
        The heuristic function used to guide the search.
    g_score : dict
        The known actual cost of reaching the target from each node.
    rhs : dict
        The one-step lookahead cost for each node (right-hand side value).
    queue : PriorityQueue
        A priority queue of nodes to be processed.
    k_m : float
        Accumulated offset used to adjust priorities after changes.
    last_path : list or None
        The last computed shortest path.
    """

    def __init__(self, G, source, target, heuristic=None, weight="weight"):
        # Validate that source and target exist in the graph.
        if source not in G:
            G.add_node(source)
        if target not in G:
            G.add_node(target)

        self.G = G.copy()  # Make a local copy to avoid side effects.
        self.source = source
        self.target = target
        self.weight = weight
        self.heuristic = heuristic if heuristic else (lambda u, v: 0)

        """Initialize costs: all nodes start with infinite cost except the target. """
        self.g_score = {n: float("inf") for n in self.G.nodes}
        self.rhs = {n: float("inf") for n in self.G.nodes}
        self.rhs[self.target] = 0

        self.queue = PriorityQueue()
        self.k_m = 0
        self.last_path = None

        self._validate_edge_weights()
        self.queue.push(self.target, self.compute_key(self.target))
        self.compute_shortest_path()

    def _validate_edge_weights(self):
        """
        Ensures all edges have a 'weight' attribute.
        """
        for u, v, data in self.G.edges(data=True):
            if self.weight not in data:
                data[self.weight] = 1  # Safe default value.

    def compute_key(self, u):
        """
        Computes the priority key for node u.

        Formula
        -------
        key = (min(g(u), rhs(u)) + h(u, target) + k_m, min(g(u), rhs(u)))

        Parameters
        ----------
        u : hashable
            The node for which the key is computed.

        Returns
        -------
        tuple(float, float)
            The computed key.
        """
        g_rhs_min = min(self.g_score[u], self.rhs[u])
        h = self.heuristic(u, self.target)
        return g_rhs_min + h + self.k_m, g_rhs_min

    def update_vertex(self, u):
        """
        Updates the rhs value for node u and its position in the priority queue.

        Parameters
        ----------
        u : hashable
            The node to update.
        """
        if u != self.target:
            # Compute rhs as the minimum cost from all successors.
            successors = list(self.G.neighbors(u))
            costs = [
                self.g_score[v] + self.G[u][v][self.weight]
                for v in successors
                if self.G.has_edge(u, v)
            ]
            self.rhs[u] = min(costs) if costs else float("inf")
        if u in self.queue.entry_map:
            self.queue.remove(u)
        if self.g_score[u] != self.rhs[u]:  # Node is inconsistent.
            self.queue.push(u, self.compute_key(u))

    def compute_shortest_path(self):
        """
        Executes the main search loop of D* Lite to propagate cost changes until
        either an optimal path is found or it is determined that no path exists.

        For directed graphs, propagation is performed using the predecessors.
        """
        while not self.queue.empty():
            current_key = self.queue.top_key()
            start_key = self.compute_key(self.source)
            if (
                self.rhs[self.source] == self.g_score[self.source]
                and current_key >= start_key
            ):
                break
            u = self.queue.pop()
            if self.g_score[u] > self.rhs[u]:
                self.g_score[u] = self.rhs[u]
                for v in self.G.predecessors(u):
                    self.update_vertex(v)
            else:
                self.g_score[u] = float("inf")
                for v in self.G.predecessors(u):
                    self.update_vertex(v)
                self.update_vertex(u)
        if self.rhs[self.source] == float("inf"):
            self.last_path = None  # No path exists to the target.
        else:
            self.generate_path()

    def generate_path(self):
        """
        Reconstructs the path from source to target using the pre-computed rhs values.

        Strategy:
        1. Greedily navigate from the source toward the target by choosing the successor with the lowest expected cost.
        2. Use rhs + edge weight for local decisions (no new search is required).
        3. Detect cycles to avoid infinite loops.

        Returns
        -------
        None
            The computed path is stored in 'self.last_path'. If no path exists, it is set to None.
        """
        path = []
        current = self.source
        visited = set()
        while current != self.target:
            if current in visited:
                self.last_path = None
                return
            visited.add(current)
            path.append(current)
            next_node = None
            min_cost = float("inf")
            for neighbor in self.G.successors(current):
                if not self.G.has_edge(current, neighbor):
                    continue
                if self.rhs[neighbor] == float("inf"):
                    continue
                try:
                    edge_weight = self.G[current][neighbor][self.weight]
                    cost = self.rhs[neighbor] + edge_weight
                except KeyError:
                    continue
                if cost < min_cost:
                    min_cost = cost
                    next_node = neighbor
            if next_node is None:
                self.last_path = None
                return
            current = next_node
        path.append(current)
        self.last_path = path

    def modify_edge(self, u, v, new_weight):
        """
        Dynamically updates the weight of the edge (u, v) and reprocesses the affected nodes.

        Parameters
        ----------
        u : hashable
            The source node of the edge.
        v : hashable
            The target node of the edge.
        new_weight : float
            The new weight to assign to the edge.

        Returns
        -------
        nx.Graph or nx.DiGraph
            The updated graph.
        """
        if not self.G.has_edge(u, v):
            self.G.add_edge(u, v, **{self.weight: new_weight})
        else:
            self.G[u][v][self.weight] = new_weight
        self.update_vertex(u)
        if not self.G.is_directed():
            self.update_vertex(v)
        self.compute_shortest_path()
        return self.G

    def get_path(self):
        """
        Returns a safe copy of the last computed path.

        Returns
        -------
        list or None
            The shortest path as a list of nodes, or None if no path exists.
        """
        return self.last_path.copy() if self.last_path else None

    def get_path_length(self):
        """
        Returns the number of edges in the last computed path, or infinity if there is no path.

        Returns
        -------
        int or float
            The path length.
        """
        return len(self.last_path) - 1 if self.last_path else float("inf")

    def get_path_cost(self):
        """
        Returns the total cost of the last computed path as the sum of the edge weights.

        If no path exists, returns infinity.

        Returns
        -------
        int or float
            The total cost of the path, or infinity if there is no computed path.
        """
        if self.last_path is None:
            return float("inf")
        return sum(
            self.G[u][v]["weight"] for u, v in zip(self.last_path, self.last_path[1:])
        )
