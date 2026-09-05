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

    heuristic : function
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
    return a path that is suboptimal when epsilon is greater than 1.
    This Epsilon value gaurentees that the path is at least as good as
    the optimal path + epsilon.
    The path is accessable through the extract_path function.


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

    >>> def heuristic(u, v):  # Euclidean distance between nodes
    ...     return math.sqrt(
    ...         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
    ...         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
    ...     )

    >>> # A* search for comparison
    >>> path = nx.astar_path(G, source, target, heuristic)
    >>> weight = nx.path_weight(G, path, "weight")
    >>> path, weight
    ([42, 32, 19, 72, 49, 29, 31, 94, 35, 25], 1.29129785933092)

    >>> search = ada_star(G, source, target, heuristic=heuristic)
    >>> search.compute_or_improve_path(epsilon=2)
    >>> path = search.extract_path()
    >>> weight = nx.path_weight(G, path, "weight")
    >>> path, weight
    ([42, 32, 24, 40, 59, 4, 66, 27, 35, 25], 1.4679609830956495)

    >>> search.compute_or_improve_path(epsilon=1.2)
    >>> path = search.extract_path()
    >>> weight = nx.path_weight(G, path, "weight")
    >>> path, weight
    ([42, 32, 24, 12, 59, 4, 1, 27, 35, 25], 1.3335657361796027)

    >>> search.compute_or_improve_path(epsilon=1)
    >>> path = search.extract_path()
    >>> weight = nx.path_weight(G, path, "weight")
    >>> path, weight
    ([42, 32, 19, 72, 49, 29, 31, 94, 35, 25], 1.29129785933092)

    >>> search.update_graph([[49, 97, 0]])  # set weight between 49 and 97 to 0
    >>> search.compute_or_improve_path(epsilon=1)
    >>> path = search.extract_path()
    >>> weight = nx.path_weight(G, path, "weight")
    >>> path, weight
    ([42, 32, 19, 72, 49, 29, 31, 94, 35, 25], 1.29129785933092)
    """

    def __init__(
        self,
        G,
        source,
        target,
        *,
        heuristic=None,
        weight="weight",
        initial_epsilon=1000,
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

        self.heuristic = heuristic
        self.OPEN = {}
        self.G = G
        self.weight = _weight_function(self.G, weight)

        # estimate g[n] of the cost from each state to the goal
        self.state_to_goal_est = {n: math.inf for n in G.nodes()}

        # one-step lookahead cost, is 0 if n is the goal, otherwise,
        # is the minimum of the cost between n and its neighbours plus
        # the estimate of the cost of the neighbour to the goal

        self.one_step_lookahead_cost = {n: math.inf for n in G.nodes()}
        self.one_step_lookahead_cost[self.target] = 0.0

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
        >>> import math

        >>> G = nx.random_geometric_graph(100, 0.20, seed=896803)
        >>> for u, v, w in G.edges(data=True):  # Euclidean distance between nodes
        ...     w["weight"] = math.sqrt(
        ...         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
        ...         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
        ...     )
        >>> source, target = 42, 25

        >>> def heuristic(u, v):  # Euclidean distance between nodes
        ...     return math.sqrt(
        ...         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
        ...         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
        ...     )

        >>> # A* search for comparison
        >>> path = nx.astar_path(G, source, target, heuristic)
        >>> weight = nx.path_weight(G, path, "weight")
        >>> path, weight
        ([42, 32, 19, 72, 49, 29, 31, 94, 35, 25], 1.29129785933092)

        >>> search = ada_star(G, source, target, heuristic=heuristic)
        >>> search.compute_or_improve_path(epsilon=2)
        >>> path = search.extract_path()
        >>> weight = nx.path_weight(G, path, "weight")
        >>> path, weight
        ([42, 32, 24, 40, 59, 4, 66, 27, 35, 25], 1.4679609830956495)

        >>> search.compute_or_improve_path(epsilon=1.2)
        >>> path = search.extract_path()
        >>> weight = nx.path_weight(G, path, "weight")
        >>> path, weight
        ([42, 32, 24, 12, 59, 4, 1, 27, 35, 25], 1.3335657361796027)

        >>> search.compute_or_improve_path(epsilon=1)
        >>> path = search.extract_path()
        >>> weight = nx.path_weight(G, path, "weight")
        >>> path, weight
        ([42, 32, 19, 72, 49, 29, 31, 94, 35, 25], 1.29129785933092)
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
            if not self.OPEN:
                v = [math.inf, math.inf]
                u = None

            else:
                u = min(self.OPEN, key=self.OPEN.get)
                v = self.OPEN[u]

            if (v >= self._key(self.source)) and self.one_step_lookahead_cost[
                self.source
            ] == self.state_to_goal_est[self.source]:
                break
            self.OPEN.pop(u)
            self.visited.add(u)

            if self.state_to_goal_est[u] > self.one_step_lookahead_cost[u]:
                self.state_to_goal_est[u] = self.one_step_lookahead_cost[u]
                self.CLOSED.add(u)
                for un in self.G[u]:
                    self._update_state(un)
            else:
                self.state_to_goal_est[u] = float("inf")
                for un in self.G[u]:
                    self._update_state(un)
                self._update_state(u)

    def update_graph(self, changes):
        """Update the graph with new edge weights

        Updates the graph with new edge weights. The algorithm will use
        previous work to find a new path in the updated graph.

        Parameters
        ----------
        changes : list of changes, each change is a list of [node1, node2, new_weight]

        Returns
        -------
        None

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

        >>> def heuristic(u, v):  # Euclidean distance between nodes
        ...     return math.sqrt(
        ...         (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
        ...         + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
        ...     )

        >>> # A* search for comparison
        >>> path = nx.astar_path(G, source, target, heuristic)
        >>> weight = nx.path_weight(G, path, "weight")
        >>> path, weight
        ([42, 32, 19, 72, 49, 29, 31, 94, 35, 25], 1.29129785933092)

        >>> search = ada_star(G, source, target, heuristic=heuristic)
        >>> search.compute_or_improve_path(epsilon=1)
        >>> path = search.extract_path()
        >>> weight = nx.path_weight(G, path, "weight")
        >>> path, weight
        ([42, 32, 19, 72, 49, 29, 31, 94, 35, 25], 1.29129785933092)

        >>> search.update_graph([[49, 97, 0]])  # set weight between 49 and 97 to 0
        >>> search.compute_or_improve_path(epsilon=1)
        >>> path = search.extract_path()
        >>> weight = nx.path_weight(G, path, "weight")
        >>> path, weight
        ([42, 32, 19, 72, 49, 29, 31, 94, 35, 25], 1.29129785933092)
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
        suboptimal by the at most the epsilon given in the
        compute_or_improve_path function.

        Returns
        -------
        list of nodes in the path

        Raises
        ------
        NetworkXNoPath
            If no path exists between source and target.

        """

        path = [self.source]
        source = self.source

        while True:
            neighbours = self.G[source].keys()
            # find neighbour with lowest g value
            try:
                source = min(
                    neighbours,
                    key=lambda x: self.state_to_goal_est[x]
                    + self.weight(source, x, self.G[source][x]),
                )
            except:
                raise nx.NetworkXNoPath(
                    f"No path exists between {self.source} and {self.target}"
                )

            path.append(source)
            if source == self.target:
                break

        if path[-1] != self.target:
            raise nx.NetworkXNoPath(
                f"No path exists between {self.source} and {self.target}"
            )

        return list(path)

    def _update_state(self, n):
        if n != self.target:
            self.one_step_lookahead_cost[n] = float("inf")
            for nbr in self.G[n]:
                self.one_step_lookahead_cost[n] = min(
                    self.one_step_lookahead_cost[n],
                    self.state_to_goal_est[nbr] + self.weight(n, nbr, self.G[n][nbr]),
                )

        if n in self.OPEN:
            self.OPEN.pop(n)

        if self.state_to_goal_est[n] != self.one_step_lookahead_cost[n]:
            if n not in self.CLOSED:
                self.OPEN[n] = self._key(n)
            else:
                self.INCONS[n] = 0

    def _key(self, n):
        # return the key of a state
        # the key of a state is a list of two floats, (k1, k2)
        if self.state_to_goal_est[n] > self.one_step_lookahead_cost[n]:
            return [
                self.one_step_lookahead_cost[n]
                + (self.epsilon * self.heuristic(self.source, n)),
                self.one_step_lookahead_cost[n],
            ]
        return [
            self.state_to_goal_est[n] + self.heuristic(self.source, n),
            self.state_to_goal_est[n],
        ]
