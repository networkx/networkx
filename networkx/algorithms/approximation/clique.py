"""Functions for computing large cliques and maximum independent sets."""

import networkx as nx
from networkx.algorithms.approximation import ramsey
from networkx.utils import not_implemented_for

__all__ = [
    "clique_removal",
    "max_clique",
    "large_clique_size",
    "maximum_independent_set",
]


class LinearTimeMaximiumIndependentSet:
    """A class for the approximate maximum independent set problem.

    This class is a helper for the `maximum_independent_set` function.
    The class should not normally be used directly.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Notes
    -----
    This implementation temporarily modifies G by removing self-loops.
    These changes are reverted after finding the approximate maximum
    independent set.

    Attributes
    ----------
    G : NetworkX graph
        The undirected graph received as input
    H : NetworkX graph
        The undirected graph being operated on
    max_degree : int
        The maximum degree of H
    nodes_by_degree : dict of dicts
        The ordered set of nodes for each degree up to max_degree
    independent_set : dict
        The ordered set of independent nodes, equivalent to nodes_by_degree[0]
    twos: dict
        The ordered set of nodes a degree-two reduction can be applied on
        Note that this is *not* equivalent to nodes_by_degree[2]
    removed_paths : list
        The list of paths of temporarily removed nodes
    """

    def __init__(self, G):
        """Initialize the class. Self-loop edges are temporarily removed."""
        self.G = G

        # note: no edge or node data is copied
        self.H = H = nx.Graph(G.edges)
        H.add_nodes_from(G)
        if H.order() == 0:
            return

        self.removed_paths = []
        self.inserted_edges = []

        # Remove self-loops
        H.remove_edges_from(nx.selfloop_edges(H))

        # Construct degree data structure
        self.max_degree = max((d for v, d in H.degree), default=0)
        # note: use dict as an ordered set
        self.nodes_by_degree = {d: {} for d in range(max(self.max_degree, 2) + 1)}
        for v, d in H.degree:
            self.nodes_by_degree[d][v] = True
        self.independent_set = self.nodes_by_degree[0]
        self.twos = self.nodes_by_degree[2].copy()

    def reduce_degree(self, v):
        """Reduce degree of v and update data structures accordingly."""
        d = self.H.degree[v]
        if d == 3:
            self.twos[v] = True
        elif d == 2:
            self.twos.pop(v, None)

        self.nodes_by_degree[d].pop(v)
        self.nodes_by_degree[d - 1][v] = True

    def remove_node(self, v):
        """Remove v from data structures and update all neighbors of v."""
        for u in self.H[v]:
            self.reduce_degree(u)

        d = self.H.degree[v]
        self.nodes_by_degree[d].pop(v)
        if d == 2:
            self.twos.pop(v, None)

        self.H.remove_node(v)

    def degree_one_reduction(self):
        """Apply the degree-one reduction by removing the neighbor of a degree-one node."""
        u = nx.utils.arbitrary_element(self.nodes_by_degree[1])
        # note: only take the single node that exists
        v = nx.utils.arbitrary_element(self.H[u])
        self.remove_node(v)

    def longest_degree_two_path(self, v):
        """Find the longest path consisting of only degree-two nodes that includes v.
        Using only degree-two nodes forces the path in both directions until it either
        reaches its end or reconnects to v, finding a cycle. Returns whether a cycle
        was found, the path and the first nodes found that are not in the path."""
        u1, u2 = self.H[v]

        # Build forwards path
        path1 = [v]
        pred = v
        while self.H.degree[u1] == 2:
            if u1 == v:
                # Cycle found
                return True, path1, ()
            path1.append(u1)
            a, b = self.H[u1]
            u1, pred = a if a != pred else b, u1

        # Build backwards path
        path2 = []
        pred = v
        while self.H.degree[u2] == 2:
            path2.append(u2)
            a, b = self.H[u2]
            u2, pred = a if a != pred else b, u2

        path2.reverse()
        path = path2 + path1
        return False, path, (u2, u1)

    def degree_two_path_reduction(self):
        """Apply the degree-two path reduction as described in [1]_."""
        u, _ = self.twos.popitem()

        is_cycle, P, ends = self.longest_degree_two_path(u)
        if is_cycle:
            self.remove_node(u)
            return

        # Get first nodes not in path
        v, w = ends

        if v == w:
            # Fig. 4(a)
            self.remove_node(v)
            return

        if len(P) % 2 == 1:
            if self.H.has_edge(v, w):
                # Fig. 4(b)
                self.remove_node(v)
                self.remove_node(w)
            elif len(P) > 1:
                # Fig. 4(c)
                v1 = P[0]

                # Also remove v1 as a further reduction on v1 is useless
                self.twos.pop(v1, None)
                for vi in P[1:]:
                    self.twos.pop(vi, None)
                    self.nodes_by_degree[2].pop(vi)
                self.H.remove_nodes_from(P[1:])
                self.removed_paths.append(P[1:])

                self.H.add_edge(v1, w)
        else:
            # Figs. 4(d) and 4(e)
            if self.H.has_edge(v, w):
                # Fig. 4(d)
                self.reduce_degree(v)
                self.reduce_degree(w)
            else:
                # Fig. 4(e)
                self.H.add_edge(v, w)

            for vi in P:
                self.twos.pop(vi, None)
                self.nodes_by_degree[2].pop(vi)
            self.H.remove_nodes_from(P)
            self.removed_paths.append(P)

    def max_degree_reduction(self):
        """Apply the inexact reduction of removing a node with the highest degree."""
        u = nx.utils.arbitrary_element(self.nodes_by_degree[self.max_degree])
        self.remove_node(u)

    def maximum_independent_set(self):
        """Find an approximate maximum independent set in linear time with Reducing-Peeling."""
        if self.H.order() == 0:
            return set()

        # Reducing-Peeling
        while self.nodes_by_degree[1] or self.twos or self.max_degree >= 3:
            if self.nodes_by_degree[1]:
                self.degree_one_reduction()
            elif self.twos:
                self.degree_two_path_reduction()
            else:
                self.max_degree_reduction()
            while not self.nodes_by_degree[self.max_degree]:
                self.max_degree -= 1

        # Add removed nodes to solution if possible
        for P in reversed(self.removed_paths):
            for v in P:
                if all(nbr not in self.independent_set for nbr in self.G[v]):
                    self.independent_set[v] = True

        # Extend independent set to be maximal
        selfloops = nx.selfloop_edges(self.G)
        self.G.remove_edges_from(selfloops)
        max_independent_set = set(
            nx.algorithms.maximal_independent_set(self.G, self.independent_set)
        )
        self.G.add_edges_from(selfloops)

        return max_independent_set


def _maximum_independent_set_clique_removal(G):
    iset, _ = clique_removal(G)
    return iset


def _maximum_independent_set_lineartime(G):
    return LinearTimeMaximiumIndependentSet(G).maximum_independent_set()


ALGORITHMS = {
    "clique_removal": _maximum_independent_set_clique_removal,
    "lineartime": _maximum_independent_set_lineartime,
}


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def maximum_independent_set(G, method=None):
    r"""Find an approximate maximum independent set.

    Independent set or stable set is a set of vertices in a graph, no two of
    which are adjacent. That is, it is a set I of vertices such that for every
    two vertices in I, there is no edge connecting the two. Equivalently, each
    edge in the graph has at most one endpoint in I. The size of an independent
    set is the number of vertices it contains [1]_.

    A maximum independent set is a largest independent set for a given graph G
    and its size is denoted $\\alpha(G)$. The problem of finding such a set is called
    the maximum independent set problem and is an NP-hard optimization problem.
    As such, it is unlikely that there exists an efficient algorithm for finding
    a maximum independent set of a graph.

    The approximation algorithm is specified with the `method` keyword argument.
    Whereas the ``"clique_removal"`` method results in a $O(|V|/(\log |V|)^2)$
    approximation of the maximum independent set in the worst case, there is no
    such guarantee for the ``"lineartime"`` method.

    * ``"clique_removal"`` [2]_ computes the approximate maximum independent set
      by repeatedly removing cliques from a copy of *G*. The implementation may
      suffer from recursion depth issues for large graphs. Use this if you desire
      accurate results and only work with small graphs.

    * ``"lineartime"`` [3]_ (runtime :math:`O(|V|+|E|)`) computes the approximate
      maximum independent set by applying reduction rules to the graph, relying
      on a heuristic if no exact reduction can be performed. Use this if you can
      tolerate inaccurate results or work with large graphs.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    method : string, optional (default = 'clique_removal')
        The algorithm to use to approximate the maximum independent set.
        Supported options: 'clique_removal', 'lineartime'.
        Other inputs produce a ValueError.

    Returns
    -------
    iset : set
        The approximate maximum independent set

    Examples
    --------
    >>> G = nx.path_graph(10)
    >>> nx.approximation.maximum_independent_set(G)
    {0, 2, 4, 6, 9}

    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or is a multigraph.

    ValueError
        If the specified `method` is not supported.

    Notes
    -----
    Both supported methods ignore self-loops, since independent sets are
    not conventionally defined with such edges.

    References
    ----------
    .. [1] `Wikipedia: Independent set (graph theory)
        <https://en.wikipedia.org/wiki/Independent_set_(graph_theory)>`_
    .. [2] Boppana, R., & Halldórsson, M. M. (1992).
       Approximating maximum independent sets by excluding subgraphs.
       BIT Numerical Mathematics, 32(2), 180–196. Springer.
    .. [3] Chang, Lijun, Wei Li, and Wenjie Zhang.
       "Computing a Near-Maximum Independent Set in Linear Time by Reducing-Peeling."
       Proceedings of the 2017 ACM International Conference on Management of Data (2017): 1181–96.
       https://www.researchgate.net/profile/Wei-Li-291/publication/316849563_Computing_A_Near-Maximum_Independent_Set_in_Linear_Time_by_Reducing-Peeling/.
    """
    if method is None:
        method = "clique_removal"

    try:
        algo = ALGORITHMS[method]
    except KeyError as e:
        raise ValueError(f"{method} is not a valid choice for an algorithm.") from e

    return algo(G)


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def max_clique(G, method=None):
    r"""Find an approximate maximum clique in G.

    Returns an approximation of the maximum clique by finding the approximate
    maximum independent set of the complement of G.

    A clique in an undirected graph G = (V, E) is a subset of the vertex set
    :math:`C \subseteq V` such that for every two vertices in C there exists an edge
    connecting the two. This is equivalent to saying that the subgraph
    induced by C is complete (in some cases, the term clique may also refer
    to the subgraph) [1]_.

    A maximum clique is a clique of the largest possible size in a given graph.
    The clique number `\omega(G)` of a graph G is the number of
    vertices in a maximum clique in G. The intersection number of
    G is the smallest number of cliques that together cover all edges of G.

    The approximation algorithm is specified with the `method` keyword argument.
    Whereas the ``"clique_removal"`` method results in a $O(|V|/(\log |V|)^2)$
    approximation of the maximum clique in the worst case, there is no such
    guarantee for the ``"lineartime"`` method.

    * ``"clique_removal"`` [2]_ computes the approximate maximum clique by
      repeatedly removing cliques from the complement of *G*. The implementation
      may suffer from recursion depth issues for large graphs. Use this if you
      desire accurate results and only work with small graphs.

    * ``"lineartime"`` [3]_ (runtime :math:`O(|V|+|E|)`) computes the approximate
      maximum clique by applying reduction rules to the complement of *G*, relying
      on a heuristic if no exact reduction can be performed. Use this if you can
      tolerate inaccurate results or work with large graphs.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    clique : set
        The approximate maximum clique of the graph

    Examples
    --------
    >>> G = nx.path_graph(10)
    >>> nx.approximation.max_clique(G)
    {8, 9}

    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or is a multigraph.

    Notes
    -----
    Both supported methods ignore self-loops, since cliques are not conventionally
    defined with such edges.

    References
    ----------
    .. [1] `Wikipedia: Clique (graph theory)
        <https://en.wikipedia.org/wiki/Clique_(graph_theory)>`_
    .. [2] Boppana, R., & Halldórsson, M. M. (1992).
       Approximating maximum independent sets by excluding subgraphs.
       BIT Numerical Mathematics, 32(2), 180–196. Springer.
    .. [3] Chang, Lijun, Wei Li, and Wenjie Zhang.
       "Computing a Near-Maximum Independent Set in Linear Time by Reducing-Peeling."
       Proceedings of the 2017 ACM International Conference on Management of Data (2017): 1181–96.
       https://www.researchgate.net/profile/Wei-Li-291/publication/316849563_Computing_A_Near-Maximum_Independent_Set_in_Linear_Time_by_Reducing-Peeling/.

    """
    # finding the maximum clique in a graph is equivalent to finding
    # the independent set in the complementary graph
    cgraph = nx.complement(G)
    return maximum_independent_set(cgraph, method)


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def clique_removal(G):
    r"""Repeatedly remove cliques from the graph.

    Results in a $O(|V|/(\log |V|)^2)$ approximation of maximum clique
    and independent set. Returns the largest independent set found, along
    with found maximal cliques.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    max_ind_cliques : (set, list) tuple
        2-tuple of Maximal Independent Set and list of maximal cliques (sets).

    Examples
    --------
    >>> G = nx.path_graph(10)
    >>> nx.approximation.clique_removal(G)
    ({0, 2, 4, 6, 9}, [{0, 1}, {2, 3}, {4, 5}, {6, 7}, {8, 9}])

    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or is a multigraph.

    References
    ----------
    .. [1] Boppana, R., & Halldórsson, M. M. (1992).
        Approximating maximum independent sets by excluding subgraphs.
        BIT Numerical Mathematics, 32(2), 180–196. Springer.
    """
    graph = G.copy()
    c_i, i_i = ramsey.ramsey_R2(graph)
    cliques = [c_i]
    isets = [i_i]
    while graph:
        graph.remove_nodes_from(c_i)
        c_i, i_i = ramsey.ramsey_R2(graph)
        if c_i:
            cliques.append(c_i)
        if i_i:
            isets.append(i_i)
    # Determine the largest independent set as measured by cardinality.
    maxiset = max(isets, key=len)
    return maxiset, cliques


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def large_clique_size(G):
    """Find the size of a large clique in a graph.

    A *clique* is a subset of nodes in which each pair of nodes is
    adjacent. This function is a heuristic for finding the size of a
    large clique in the graph.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    k: integer
       The size of a large clique in the graph.

    Examples
    --------
    >>> G = nx.path_graph(10)
    >>> nx.approximation.large_clique_size(G)
    2

    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or is a multigraph.

    Notes
    -----
    This implementation is from [1]_. Its worst case time complexity is
    :math:`O(n d^2)`, where *n* is the number of nodes in the graph and
    *d* is the maximum degree.

    This function is a heuristic, which means it may work well in
    practice, but there is no rigorous mathematical guarantee on the
    ratio between the returned number and the actual largest clique size
    in the graph.

    References
    ----------
    .. [1] Pattabiraman, Bharath, et al.
       "Fast Algorithms for the Maximum Clique Problem on Massive Graphs
       with Applications to Overlapping Community Detection."
       *Internet Mathematics* 11.4-5 (2015): 421--448.
       <https://doi.org/10.1080/15427951.2014.986778>

    See also
    --------

    :func:`networkx.algorithms.approximation.clique.max_clique`
        A function that returns an approximate maximum clique with a
        guarantee on the approximation ratio.

    :mod:`networkx.algorithms.clique`
        Functions for finding the exact maximum clique in a graph.

    """
    degrees = G.degree

    def _clique_heuristic(G, U, size, best_size):
        if not U:
            return max(best_size, size)
        u = max(U, key=degrees)
        U.remove(u)
        N_prime = {v for v in G[u] if degrees[v] >= best_size}
        return _clique_heuristic(G, U & N_prime, size + 1, best_size)

    best_size = 0
    nodes = (u for u in G if degrees[u] >= best_size)
    for u in nodes:
        neighbors = {v for v in G[u] if degrees[v] >= best_size}
        best_size = _clique_heuristic(G, neighbors, 1, best_size)
    return best_size
