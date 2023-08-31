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
    s_start : node
        Starting node for the path

    s_goal : node
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
    >>> random.seed(1)
    >>> G = nx.random_geometric_graph(100, 0.20, seed=896803)
    >>> for u, v, w in G.edges(data=True):  # Euclidean distance between nodes
    ...     w["weight"] = np.sqrt(
    ...         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
    ...         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
    ...     )

    >>> s_start, s_goal = 42, 25
    >>> def heursistic(u, v):  # Euclidean distance between nodes
    ...     return np.sqrt(
    ...         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
    ...         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
    ...     )

    >>> # A* search for comparison
    >>> start_time = time.time()
    >>> path = nx.astar_path(G, s_start, s_goal, heursistic)
    >>> print("A* time: ", time.time() - start_time)
    A* time:  0.00012803077697753906
    >>> print("A* path: ", path)
    A* path:  [42, 32, 19, 72, 49, 29, 31, 94, 35, 25]

    >>> #create search object
    >>> search = ada_star(s_start, s_goal, G, heursistic)

    >>> #compute first suboptimal path epsilon = 2
    >>> start_time = time.time()
    >>> search.compute_or_improve_path(epsilon=2)
    >>> path = search.extract_path()
    >>> print("ADA* epsilon = 2 time: ", time.time() - start_time)
    ADA* epsilon = 2 time:  0.0009984970092773438
    >>> print("epsilon = 2 path: ", path)
    epsilon = 2 path:  [42, 32, 24, 40, 59, 4, 66, 27, 35, 25]
    >>> print("epsilon = 2 path_weight: ", nx.path_weight(G, search.extract_path(), "weight"))
    epsilon = 2 path_weight:  1.4679609830956495

    >>> #compute second (better) suboptimal path
    >>> search.compute_or_improve_path(epsilon=1.2)
    >>> path = search.extract_path()
    >>> print("epsilon = 1.2 path: ", path)
    epsilon = 1.2 path:  [42, 32, 24, 12, 59, 4, 1, 27, 35, 25]
    >>> print("epsilon = 1.2 path_weight: ", nx.path_weight(G, path, "weight"))
    epsilon = 1.2 path_weight:  1.3335657361796027

    >>> #compute third (best) suboptimal path
    >>> search.compute_or_improve_path(epsilon=1)
    >>> path = search.extract_path()
    >>> print("epsilon = 1 path: ", path)
    epsilon = 1 path:  [42, 32, 19, 72, 49, 29, 31, 94, 35, 25]
    >>> print("epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))
    epsilon = 1 path_weight:  1.29129785933092

    >>> #change graph edge weight
    >>> print("changing graph weight for edge (49, 97)")
    changing graph weight for edge (49, 97)
    >>> search.update_graph([[49, 97, 0]]) #add edge between 77 and 15 with weight 0
    >>> search.compute_or_improve_path(epsilon=1)
    >>> path = search.extract_path()
    >>> print("changed epsilon = 1 path: ", path)
    changed epsilon = 1 path:  [42, 32, 19, 72, 49, 97, 11, 31, 94, 35, 25]
    >>> print("changed epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))
    changed epsilon = 1 path_weight:  1.1428811257616596

    """

    def __init__(
        self, s_start, s_goal, G, heuristic=None, weight="weight",
        initial_epsilon=1000
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

        if s_start not in G or s_goal not in G:
            msg = f"Either source {s_start} or target {s_goal} is not in G"
            raise nx.NodeNotFound(msg)

        self.s_start, self.s_goal = s_start, s_goal
        if heuristic is None:
        # The default heuristic is h=0 - same as Dijkstra's algorithm
            def heuristic(u, v):
                return 0
        self.heursistic = heuristic
        
        self.weight = weight
        self.G = G
        self.g, self.rhs, self.OPEN = {}, {}, {}

        # estimate g[s] of the cost from each state to the goal
        self.g = {s: math.inf for s in G.nodes()}

        # one-step lookahead cost, rhs[s], 0 is s is the goal, otherwise,
        # is the minimum of the following sum:
        # The cost between s and its neighbours plus the g value
        # of that neighbour
        self.rhs = {s: math.inf for s in G.nodes()}

        self.rhs[self.s_goal] = 0.0
        self.epsilon = initial_epsilon

        # initialize OPEN, CLOSED, INCONS
        self.OPEN[self.s_goal] = self.__key__(self.s_goal)
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
        >>> #create search object
        >>> search = ada_star(s_start, s_goal, G, heursistic)

        >>> #compute first suboptimal path epsilon = 2
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
                self.OPEN[state] = self.__key__(state)
            self.INCONS = {}
            for state in self.OPEN:
                # update keys
                self.OPEN[state] = self.__key__(state)
            self.CLOSED = set()

        while True:
            s, v = self.__smallest_key__()
            if (not self.__key_lt__(v, self.__key__(self.s_start))) and \
                  self.rhs[self.s_start] == self.g[self.s_start]:
                break
            self.OPEN.pop(s)
            self.visited.add(s)

            if self.g[s] > self.rhs[s]:
                self.g[s] = self.rhs[s]
                self.CLOSED.add(s)
                for sn in self.__get_neighbor__(s):
                    self.__update_state__(sn)
            else:
                self.g[s] = float("inf")
                for sn in self.__get_neighbor__(s):
                    self.__update_state__(sn)
                self.__update_state__(s)

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
            >>> s_start, s_goal = 42, 25
            >>> def heursistic(u, v): #Euclidean distance between nodes
            >>> return np.sqrt((G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0])**2 + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1])**2)

            >>> #change graph edge weight
            >>> print("changing graph weight for edge (49, 97)")
            changing graph weight for edge (49, 97)
            >>> search.update_graph([[49, 97, 0]]) #add edge between 77 and 15 with weight 0
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
            self.__update_state__(change[0])
            self.__update_state__(change[1])
        # move states from INCONS to OPEN
        for state in self.INCONS:
            self.OPEN[state] = self.__key__(state)
        self.INCONS = {}
        for state in self.OPEN:
            # update keys
            self.OPEN[state] = self.__key__(state)
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

        path = [self.s_start]
        s = self.s_start

        while True:  # TODO raise exception if no path exists
            neighbours = self.__get_neighbor__(s)
            # find neighbour with lowest g value
            s = min(neighbours, key=lambda x: self.g[x] + self.__cost__(s, x))
            path.append(s)
            if s == self.s_goal:
                break

        return list(path)

    def __update_state__(self, s):
        if s != self.s_goal:
            self.rhs[s] = float("inf")
            for x in self.__get_neighbor__(s):
                self.rhs[s] = min(self.rhs[s], self.g[x] + self.__cost__(s, x))

        if s in self.OPEN:
            self.OPEN.pop(s)

        if self.g[s] != self.rhs[s]:
            if s not in self.CLOSED:
                self.OPEN[s] = self.__key__(s)
            else:
                self.INCONS[s] = 0

    def __key__(self, s):
        # return the key of a state
        # the key of a state is a list of two floats, (k1, k2)
        if self.g[s] > self.rhs[s]:
            return [
                self.rhs[s] + (self.epsilon * self.heursistic(self.s_start, s)),
                self.rhs[s],
            ]
        return [self.g[s] + self.heursistic(self.s_start, s), self.g[s]]

    def __key_lt__(self, key1: list, key2: list):
        # compare two keys
        # return the higher of two keys, by prioritizing the first element and
        # then the second element
        if key1[0] < key2[0]:
            return True
        if key1[0] == key2[0] and key1[1] < key2[1]:
            return True
        return False

    def __smallest_key__(self):
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

    def __cost__(self, s, s_prime):
        return self.G[s][s_prime][self.weight]

    def __get_neighbor__(self, s):
        return self.G[s].keys()


# if __name__ == "__main__":
    # import numpy as np

    # random.seed(1)
    # G = nx.random_geometric_graph(100, 0.20, seed=896803)
    # for u, v, w in G.edges(data=True):  # Euclidean distance between nodes
    #     w["weight"] = np.sqrt(
    #         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
    #         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
    #     )
    # s_start, s_goal = 42, 25

    # def heursistic(u, v):  # Euclidean distance between nodes
    #     return np.sqrt(
    #         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
    #         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
    #     )

    # # A* search for comparison
    # start_time = time.time()
    # path = nx.astar_path(G, s_start, s_goal, heursistic)
    # print("A* time: ", time.time() - start_time)
    # print("A* path: ", path)

    # # create search object
    # search = ada_star(s_start, s_goal, G, heursistic)

    # # compute first suboptimal path epsilon = 2
    # start_time = time.time()
    # search.compute_or_improve_path(epsilon=2)
    # path = search.extract_path()
    # print("ADA* epsilon = 2 time: ", time.time() - start_time)
    # print("epsilon = 2 path: ", path)
    # print(
    #     "epsilon = 2 path_weight: ", nx.path_weight(G, search.extract_path(), "weight")
    # )

    # # compute second (better) suboptimal path
    # search.compute_or_improve_path(epsilon=1.2)
    # path = search.extract_path()
    # print("epsilon = 1.2 path: ", path)
    # print("epsilon = 1.2 path_weight: ", nx.path_weight(G, path, "weight"))

    # # compute third (best) suboptimal path
    # search.compute_or_improve_path(epsilon=1)
    # path = search.extract_path()
    # print("epsilon = 1 path: ", path)
    # print("epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))

    # # change graph edge weight
    # print("changing graph weight for edge (49, 97)")
    # search.update_graph([[49, 97, 0]])  # add edge between 77 and 15 with weight 0
    # search.compute_or_improve_path(epsilon=1)
    # path = search.extract_path()
    # print("changed epsilon = 1 path: ", path)
    # print("changed epsilon = 1 path_weight: ", nx.path_weight(G, path, "weight"))
