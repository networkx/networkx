import math

import networkx as nx

from networkx.algorithms.shortest_paths.weighted import _weight_function

__all__ = ["ada_star"]

class ada_star:
    """A dynamic anytime path planning algorithm.

    Class is responsible for the implementation of the Dynamic Anytime
    A* algorithm. This algorithm returns a path from a start state to a
    goal state. The algorithm is able to return a suboptimal path in a
    short amount of time. The algorithm is able to iteratively improve
    the path over time by calling the compute_or_improve_path function.
    The algorithm is also able to cope with dynamic environments by
    calling the update_graph function, which updates the graph with new
    weights. The algorithm makes use of previous work done when there
    are changes to the graph.

    Creates a search object, which can be used to find a path from a
    start state to a goal state in a graph. The search object can be
    used to iteratively improve the path over time, as well as being
    called to update the graph with new weights. The search object, will
    then use previous work to find a new path in the updated graph

    Parameters
    ----------
    source : node
        Starting node for the path

    target : node
        Goal node for the path

    G : networkx graph
        Graph to find the path in

    heursistic : function
        A function to evaluate the estimate of the distance
    from the a node to the target.  The function takes
    two node labels as arguments and must return a number.
    If the heuristic is inadmissible (if it might
    overestimate the cost of reaching the goal from a node),
    the result may not be a shortest path.

    weight : string, default='weight'
        The edge weights will be accessed via the edge attribute with
    this key (that is, the weight of the edge joining `u` to `v`
    will be ``G.edges[u, v][weight]``). If no such edge attribute
    exists, the weight of the edge is assumed to be one.

    initial_epsilon : float, default=1000
        The suboptimality bound, epsilon >= 1. The algorithm will
    return a path that is suboptimal by this bound. The algorithm
    will return a path that is suboptimal by this bound. The path
    is accessable through the extract_path function.


    Methods
    -------
    compute_or_improve_path(epsilon)
        Compute or improve the path from the start state to the goal state.

    update_graph(changes)
        Update the graph with new edge weights

    extract_path()
        Extract the path based on current potentially suboptimal solution.


    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.
    NodeNotFound
        If either source or target is not in G.

    See Also
    --------
    shortest_path, astar_path, dijkstra_path

    References
    ----------
    [1] Likhachev, Maxim, David I. Ferguson, Geoffrey J. Gordon, Anthony
    Stentz, and Sebastian Thrun. "Anytime dynamic A*: An anytime,
    replanning algorithm." In ICAPS, vol. 5, pp. 262-271. 2005.

    Examples
    --------
    >>> import math
    >>> G = nx.random_geometric_graph(100, 0.20, seed=896803)
    >>> for u, v, w in G.edges(data=True):  # Euclidean distance between nodes
    ...     w["weight"] = math.sqrt(
    ...         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
    ...         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
    ...     )

    >>> source, target = 42, 25
    >>> def heursistic(u, v):  # Euclidean distance between nodes
    ...     return math.sqrt(
    ...         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
    ...         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
    ...     )
    >>> path = nx.astar_path(G, source, target, heursistic)
    >>> print("A* path: ", path)
    A* path:  [42, 32, 19, 72, 49, 29, 31, 94, 35, 25]

    >>> search = ada_star(source, target, G, heursistic)
    >>> search.compute_or_improve_path(epsilon=2)
    >>> path = search.extract_path()
    >>> print("epsilon = 2 path: ", path)
    epsilon = 2 path:  [42, 32, 24, 40, 59, 4, 66, 27, 35, 25]
    >>> print("epsilon = 2 path_weight: ", nx.path_weight(G, search.extract_path(), "weight"))
    epsilon = 2 path_weight:  1.4679609830956495

    >>> search.compute_or_improve_path(epsilon=1.2)
    >>> path = search.extract_path()
    >>> print("epsilon = 1.2 path: ", path)
    epsilon = 1.2 path:  [42, 32, 24, 12, 59, 4, 1, 27, 35, 25]
    >>> print("epsilon = 1.2 path_weight: ", nx.path_weight(G, path, "weight"))
    epsilon = 1.2 path_weight:  1.3335657361796027

    >>> search.compute_or_improve_path(epsilon=1)
    >>> path = search.extract_path()
    >>> print("epsilon = 1 path: ", path)
    epsilon = 1 path:  [42, 32, 19, 72, 49, 29, 31, 94, 35, 25]
    >>> print("epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))
    epsilon = 1 path_weight:  1.29129785933092

    >>> search.update_graph([[49, 97, 0]]) #add edge between 77 and 15 with weight 0
    >>> search.compute_or_improve_path(epsilon=1)
    >>> path = search.extract_path()
    >>> print("changed epsilon = 1 path: ", path)
    changed epsilon = 1 path:  [42, 32, 19, 72, 49, 97, 11, 31, 94, 35, 25]
    >>> print("changed epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))
    changed epsilon = 1 path_weight:  1.1428811257616596

    """

    def __init__(
        self, source, target, G, heuristic=None, weight="weight", initial_epsilon=1000
    ):
        """initializer for ADA* algorithm

        Returns a search object, which can be used to find a path from a
        start state to a goal state in a graph. The search object can be
        used to iteratively improve the path over time, as well as being
        called to update the graph with new weights. The search object, will
        then use previous work to find a new path in the updated graph.


        Raises
        ------
        NetworkXNoPath
            If no path exists between source and target.

        NodeNotFound
            If either source or target is not in G.

        """

        if type(G) == nx.MultiDiGraph or type(G) == nx.MultiGraph:
            raise nx.NetworkXNotImplemented("MultiGraph and MultiDiGraph not supported")

        if source not in G or target not in G:
            msg = f"Either source {source} or target {target} is not in G"
            raise nx.NodeNotFound(msg)

        self.source, self.target = source, target
        if heuristic is None:
            # The default heuristic is h=0 - same as Dijkstra's algorithm
            def heuristic(u, v):
                return 0

        self.heursistic = heuristic

        self.G = G
        self.g, self.rhs, self.OPEN = {}, {}, {}

        self.weight = _weight_function(self.G, weight)

        # estimate g[n] of the cost from each state to the goal
        self.g = {n: math.inf for n in G.nodes()}

        # one-step lookahead cost, rhs[n], 0 is n is the goal, otherwise,
        # is the minimum of the following sum:
        # The cost between n and its neighbours plus the g value
        # of that neighbour
        self.rhs = {n: math.inf for n in G.nodes()}

        self.rhs[self.target] = 0.0
        self.epsilon = initial_epsilon

        # initialize OPEN, CLOSED, INCONS
        self.OPEN[self.target] = self._key(self.target)
        self.CLOSED, self.INCONS = set(), {}

        # keep track of visited states
        self.visited = set()
        # flag to check if the algorithm is being called for the first time
        self.initialize = True
        # compute first suboptimal path
        self.compute_or_improve_path(self.epsilon)

    def compute_or_improve_path(self, epsilon):
        """Compute or improve the path from the start state to the goal state.

        Compute or improve a path from the start state to the goal state.
        Takes a suboptimality bound as input, and calculates a path that is
        suboptimal by that bound. The path is accessable through the
        extract_path function.


        Parameters
        ----------

        epsilon : float
            The suboptimality bound, epsilon >= 1

        :return: None

        Examples
        --------
        create search object
        >>> search = ada_star(source, target, G, heursistic)

        compute first suboptimal path epsilon = 2
        >>> search.compute_or_improve_path(epsilon=2)
        >>> path = search.extract_path()
        >>> print("epsilon = 2 path: ", path)
        epsilon = 2 path:  [42, 32, 24, 40, 59, 4, 66, 27, 35, 25]
        >>> search.compute_or_improve_path(epsilon=1)
        >>> path = search.extract_path()
        >>> print("epsilon = 1 path: ", path)
        epsilon = 1 path:  [42, 32, 19, 72, 49, 29, 31, 94, 35, 25]

        """
        if self.initialize:
            self.epsilon = epsilon
            self.initialize = False

        else:  # Do not update INCONS and OPEN on first call
            self.epsilon = epsilon
            # move states from INCONS to OPEN
            for state in self.INCONS:
                self.OPEN[state] = self._key(state)
            self.INCONS = {}
            for state in self.OPEN:
                # update keys
                self.OPEN[state] = self._key(state)
            self.CLOSED = set()

        while True:
            u, v = self._smallest_key()
            if (not self._key_lt(v, self._key(self.source))) and self.rhs[
                self.source
            ] == self.g[self.source]:
                break
            self.OPEN.pop(u)
            self.visited.add(u)

            if self.g[u] > self.rhs[u]:
                self.g[u] = self.rhs[u]
                self.CLOSED.add(u)
                for un in self._get_neighbor(u):
                    self._update_state(un)
            else:
                self.g[u] = float("inf")
                for un in self._get_neighbor(u):
                    self._update_state(un)
                self._update_state(u)

    def update_graph(self, changes):
        """Update the graph with new edge weights

        Updates the graph with new edge weights. The algorithm will use
        previous work to find a new path in the updated graph.

        Parameters
        ---------
        changes : list of changes, each change is a list of [node1, node2, new_weight]

        Returns
        ---------
        None

        Examples
        --------

            >>> import numpy as np
            >>> import networkx as nx
            >>> from networkx.algorithms.shortest_paths.ada_star import ada_star
            >>> random.seed(1)
            >>> G = nx.random_geometric_graph(100, 0.20, seed=896803)
            >>> for (u, v, w) in G.edges(data=True): #Euclidean distance between nodes
            ...     w['weight'] = np.sqrt((G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0])**2 + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1])**2)
            >>> source, target = 42, 25
            >>> def heursistic(u, v): #Euclidean distance between nodes
            >>> return np.sqrt((G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0])**2 + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1])**2)

            >>> search.update_graph([[49, 97, 0]]) #add edge between 49 and 97 with weight 0
            >>> search.compute_or_improve_path(epsilon=1)
            >>> path = search.extract_path()
            >>> print("changed epsilon = 1 path: ", path)
            changed epsilon = 1 path:  [42, 32, 19, 72, 49, 97, 11, 31, 94, 35, 25]
            >>> print("changed epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))
            changed epsilon = 1 path_weight:  1.1428811257616596

        """
        for change in changes:
            self.G[change[0]][change[1]][self.weight] = change[2]
            self.G[change[1]][change[0]][self.weight] = change[2]
            self._update_state(change[0])
            self._update_state(change[1])
        # move states from INCONS to OPEN
        for state in self.INCONS:
            self.OPEN[state] = self._key(state)
        self.INCONS = {}
        for state in self.OPEN:
            # update keys
            self.OPEN[state] = self._key(state)
        self.CLOSED = set()

    def extract_path(self):
        """Extract the path based on current potentially suboptimal solution.

        Returns a path from the start state to the goal state. The path is
        suboptimal by the bound given in the compute_or_improve_path function.

        Returns
        -------
        list of nodes in the path

        Raises
        -------
        NetworkXNoPath
            If no path exists between source and target.

        """

        path = [self.source]
        source = self.source

        while True:  # TODO raise exception if no path exists
            neighbours = self._get_neighbor(source)
            # find neighbour with lowest g value
            try:
                source = min(
                    neighbours, key=lambda x: self.g[x] + self._cost(source, x)
                )
            except:
                raise nx.NetworkXNoPath(
                    f"No path exists between {self.source} and {self.target}"
                )

            path.append(source)
            if source == self.target:
                break

        return list(path)

    def _update_state(self, n):
        if n != self.target:
            self.rhs[n] = float("inf")
            for nbr in self._get_neighbor(n):
                self.rhs[n] = min(self.rhs[n], self.g[nbr] + self._cost(n, nbr))

        if n in self.OPEN:
            self.OPEN.pop(n)

        if self.g[n] != self.rhs[n]:
            if n not in self.CLOSED:
                self.OPEN[n] = self._key(n)
            else:
                self.INCONS[n] = 0

    def _key(self, n):
        # return the key of a state
        # the key of a state is a list of two floats, (k1, k2)
        if self.g[n] > self.rhs[n]:
            return [
                self.rhs[n] + (self.epsilon * self.heursistic(self.source, n)),
                self.rhs[n],
            ]
        return [self.g[n] + self.heursistic(self.source, n), self.g[n]]

    def _key_lt(self, key1: list, key2: list):
        # compare two keys
        # return the higher of two keys, by prioritizing the first element and
        # then the second element
        if key1[0] < key2[0]:
            return True
        if key1[0] == key2[0] and key1[1] < key2[1]:
            return True
        return False

    def _smallest_key(self):
        # return the smallest key, smallest being the one with the lowest first element as priority,
        # if the first elements are equal, the one with the lowest second element is chosen

        min_primary = math.inf
        min_secondary = math.inf
        min_index = None
        for key, value in self.OPEN.items():
            if value[0] <= min_primary:
                min_primary = value[0]
                min_index = key
                if value[1] < min_secondary:
                    min_secondary = value[1]
                    min_index = key

        return min_index, [min_primary, min_secondary]

    def _cost(self, n, nbr):
        return self.weight(n, nbr, self.G[n][nbr])

    # self.G[n][nbr][self.weight]

    def _get_neighbor(self, n):
        return self.G[n].keys()


if __name__ == "__main__":
    import math

    # random.seed(1)
    G = nx.random_geometric_graph(100, 0.20, seed=896803)
    for u, v, w in G.edges(data=True):  # Euclidean distance between nodes
        w["weight"] = math.sqrt(
            (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
            + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
        )
    source, target = 42, 25

    def heursistic(u, v):  # Euclidean distance between nodes
        return math.sqrt(
            (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
            + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
        )

    # A* search for comparison
    path = nx.astar_path(G, source, target, heursistic)
    print("A* path: ", path)

    # create search object
    search = ada_star(source, target, G, heursistic)

    # compute first suboptimal path epsilon = 2
    search.compute_or_improve_path(epsilon=2)
    path = search.extract_path()
    print("epsilon = 2 path: ", path)
    print(
        "epsilon = 2 path_weight: ", nx.path_weight(G, search.extract_path(), "weight")
    )

    # compute second (better) suboptimal path
    search.compute_or_improve_path(epsilon=1.2)
    path = search.extract_path()
    print("epsilon = 1.2 path: ", path)
    print("epsilon = 1.2 path_weight: ", nx.path_weight(G, path, "weight"))

    # compute third (best) suboptimal path
    search.compute_or_improve_path(epsilon=1)
    path = search.extract_path()
    print("epsilon = 1 path: ", path)
    print("epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))

    # change graph edge weight
    print("changing graph weight for edge (49, 97)")
    search.update_graph([[49, 97, 0]])  # add edge between 77 and 15 with weight 0
    search.compute_or_improve_path(epsilon=1)
    path = search.extract_path()
    print("changed epsilon = 1 path: ", path)
    print("changed epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))


# import math

# AG1 = nx.random_geometric_graph(100, 0.20, seed=896803)
# for u, v, w in AG1.edges(data=True):  # Euclidean distance between nodes
#     w["weight"] = math.sqrt(
#         (AG1.nodes[v]["pos"][0] - AG1.nodes[u]["pos"][0]) ** 2
#         + (AG1.nodes[v]["pos"][1] - AG1.nodes[u]["pos"][1]) ** 2
#     )

# source, target = 42, 25


# search = ada_star(source, target, AG1, None, "weight", initial_epsilon=2)
# path = search.extract_path()
# print("epsilon = 2 path: ", path)
# # assert path == [42, 32, 19, 72, 49, 29, 31, 94, 35, 25]

# search.compute_or_improve_path(epsilon=1.2)
# path = search.extract_path()
# print("epsilon = 1.2 path: ", path)

# search.compute_or_improve_path(epsilon=1)
# path = search.extract_path()
# print("epsilon = 1 path: ", path)
