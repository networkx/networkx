# This module uses material from the Wikipedia article Hopcroft--Karp algorithm
# <https://en.wikipedia.org/wiki/Hopcroft%E2%80%93Karp_algorithm>, accessed on
# January 3, 2015, which is released under the Creative Commons
# Attribution-Share-Alike License 3.0
# <http://creativecommons.org/licenses/by-sa/3.0/>. That article includes
# pseudocode, which has been translated into the corresponding Python code.
#
# Portions of this module use code from David Eppstein's Python Algorithms and
# Data Structures (PADS) library, which is dedicated to the public domain (for
# proof, see <http://www.ics.uci.edu/~eppstein/PADS/ABOUT-PADS.txt>).
"""Provides functions for computing maximum cardinality matchings and minimum
weight full matchings in a bipartite graph.

If you don't care about the particular implementation of the maximum matching
algorithm, simply use the :func:`maximum_matching`. If you do care, you can
import one of the named maximum matching algorithms directly.

For example, to find a maximum matching in the complete bipartite graph with
two vertices on the left and three vertices on the right:

>>> G = nx.complete_bipartite_graph(2, 3)
>>> left, right = nx.bipartite.sets(G)
>>> list(left)
[0, 1]
>>> list(right)
[2, 3, 4]
>>> nx.bipartite.maximum_matching(G)
{0: 2, 1: 3, 2: 0, 3: 1}

The dictionary returned by :func:`maximum_matching` includes a mapping for
vertices in both the left and right vertex sets.

Similarly, :func:`minimum_weight_full_matching` produces, for a complete
weighted bipartite graph, a matching whose cardinality is the cardinality of
the smaller of the two partitions, and for which the sum of the weights of the
edges included in the matching is minimal.

"""
import collections
import itertools as it

import networkx as nx
from networkx.algorithms.bipartite import sets as bipartite_sets
from networkx.algorithms.bipartite.matrix import biadjacency_matrix

__all__ = [
    "maximum_matching",
    "hopcroft_karp_matching",
    "eppstein_matching",
    "to_vertex_cover",
    "minimum_weight_full_matching",
    "maximum_envy_free_matching",
    "minimum_weight_envy_free_matching",
    "envy_free_matching_partition",
]

INFINITY = float("inf")


@nx._dispatchable
def hopcroft_karp_matching(G, top_nodes=None):
    """Returns the maximum cardinality matching of the bipartite graph `G`.

    A matching is a set of edges that do not share any nodes. A maximum
    cardinality matching is a matching with the most edges possible. It
    is not always unique. Finding a matching in a bipartite graph can be
    treated as a networkx flow problem.

    The functions ``hopcroft_karp_matching`` and ``maximum_matching``
    are aliases of the same function.

    Parameters
    ----------
    G : NetworkX graph

      Undirected bipartite graph

    top_nodes : container of nodes

      Container with all nodes in one bipartite node set. If not supplied
      it will be computed. But if more than one solution exists an exception
      will be raised.

    Returns
    -------
    matches : dictionary

      The matching is returned as a dictionary, `matches`, such that
      ``matches[v] == w`` if node `v` is matched to node `w`. Unmatched
      nodes do not occur as a key in `matches`.

    Raises
    ------
    AmbiguousSolution
      Raised if the input bipartite graph is disconnected and no container
      with all nodes in one bipartite set is provided. When determining
      the nodes in each bipartite set more than one valid solution is
      possible if the input graph is disconnected.

    Notes
    -----
    This function is implemented with the `Hopcroft--Karp matching algorithm
    <https://en.wikipedia.org/wiki/Hopcroft%E2%80%93Karp_algorithm>`_ for
    bipartite graphs.

    See :mod:`bipartite documentation <networkx.algorithms.bipartite>`
    for further details on how bipartite graphs are handled in NetworkX.

    See Also
    --------
    maximum_matching
    hopcroft_karp_matching
    eppstein_matching

    References
    ----------
    .. [1] John E. Hopcroft and Richard M. Karp. "An n^{5 / 2} Algorithm for
       Maximum Matchings in Bipartite Graphs" In: **SIAM Journal of Computing**
       2.4 (1973), pp. 225--231. <https://doi.org/10.1137/0202019>.

    """

    # First we define some auxiliary search functions.
    #
    # If you are a human reading these auxiliary search functions, the "global"
    # variables `leftmatches`, `rightmatches`, `distances`, etc. are defined
    # below the functions, so that they are initialized close to the initial
    # invocation of the search functions.
    def breadth_first_search():
        for v in left:
            if leftmatches[v] is None:
                distances[v] = 0
                queue.append(v)
            else:
                distances[v] = INFINITY
        distances[None] = INFINITY
        while queue:
            v = queue.popleft()
            if distances[v] < distances[None]:
                for u in G[v]:
                    if distances[rightmatches[u]] is INFINITY:
                        distances[rightmatches[u]] = distances[v] + 1
                        queue.append(rightmatches[u])
        return distances[None] is not INFINITY

    def depth_first_search(v):
        if v is not None:
            for u in G[v]:
                if distances[rightmatches[u]] == distances[v] + 1:
                    if depth_first_search(rightmatches[u]):
                        rightmatches[u] = v
                        leftmatches[v] = u
                        return True
            distances[v] = INFINITY
            return False
        return True

    # Initialize the "global" variables that maintain state during the search.
    left, right = bipartite_sets(G, top_nodes)
    leftmatches = {v: None for v in left}
    rightmatches = {v: None for v in right}
    distances = {}
    queue = collections.deque()

    # Implementation note: this counter is incremented as pairs are matched but
    # it is currently not used elsewhere in the computation.
    num_matched_pairs = 0
    while breadth_first_search():
        for v in left:
            if leftmatches[v] is None and depth_first_search(v):
                num_matched_pairs += 1

    # Strip the entries matched to `None`.
    leftmatches = {k: v for k, v in leftmatches.items() if v is not None}
    rightmatches = {k: v for k, v in rightmatches.items() if v is not None}

    # At this point, the left matches and the right matches are inverses of one
    # another. In other words,
    #
    #     leftmatches == {v, k for k, v in rightmatches.items()}
    #
    # Finally, we combine both the left matches and right matches.
    return dict(it.chain(leftmatches.items(), rightmatches.items()))


@nx._dispatchable
def eppstein_matching(G, top_nodes=None):
    """Returns the maximum cardinality matching of the bipartite graph `G`.

    Parameters
    ----------
    G : NetworkX graph

      Undirected bipartite graph

    top_nodes : container

      Container with all nodes in one bipartite node set. If not supplied
      it will be computed. But if more than one solution exists an exception
      will be raised.

    Returns
    -------
    matches : dictionary

      The matching is returned as a dictionary, `matching`, such that
      ``matching[v] == w`` if node `v` is matched to node `w`. Unmatched
      nodes do not occur as a key in `matching`.

    Raises
    ------
    AmbiguousSolution
      Raised if the input bipartite graph is disconnected and no container
      with all nodes in one bipartite set is provided. When determining
      the nodes in each bipartite set more than one valid solution is
      possible if the input graph is disconnected.

    Notes
    -----
    This function is implemented with David Eppstein's version of the algorithm
    Hopcroft--Karp algorithm (see :func:`hopcroft_karp_matching`), which
    originally appeared in the `Python Algorithms and Data Structures library
    (PADS) <http://www.ics.uci.edu/~eppstein/PADS/ABOUT-PADS.txt>`_.

    See :mod:`bipartite documentation <networkx.algorithms.bipartite>`
    for further details on how bipartite graphs are handled in NetworkX.

    See Also
    --------
    hopcroft_karp_matching

    """
    # Due to its original implementation, a directed graph is needed
    # so that the two sets of bipartite nodes can be distinguished
    left, right = bipartite_sets(G, top_nodes)
    G = nx.DiGraph(G.edges(left))
    # initialize greedy matching (redundant, but faster than full search)
    matching = {}
    for u in G:
        for v in G[u]:
            if v not in matching:
                matching[v] = u
                break
    while True:
        # structure residual graph into layers
        # pred[u] gives the neighbor in the previous layer for u in U
        # preds[v] gives a list of neighbors in the previous layer for v in V
        # unmatched gives a list of unmatched vertices in final layer of V,
        # and is also used as a flag value for pred[u] when u is in the first
        # layer
        preds = {}
        unmatched = []
        pred = {u: unmatched for u in G}
        for v in matching:
            del pred[matching[v]]
        layer = list(pred)

        # repeatedly extend layering structure by another pair of layers
        while layer and not unmatched:
            newLayer = {}
            for u in layer:
                for v in G[u]:
                    if v not in preds:
                        newLayer.setdefault(v, []).append(u)
            layer = []
            for v in newLayer:
                preds[v] = newLayer[v]
                if v in matching:
                    layer.append(matching[v])
                    pred[matching[v]] = v
                else:
                    unmatched.append(v)

        # did we finish layering without finding any alternating paths?
        if not unmatched:
            # TODO - The lines between --- were unused and were thus commented
            # out. This whole commented chunk should be reviewed to determine
            # whether it should be built upon or completely removed.
            # ---
            # unlayered = {}
            # for u in G:
            #     # TODO Why is extra inner loop necessary?
            #     for v in G[u]:
            #         if v not in preds:
            #             unlayered[v] = None
            # ---
            # TODO Originally, this function returned a three-tuple:
            #
            #     return (matching, list(pred), list(unlayered))
            #
            # For some reason, the documentation for this function
            # indicated that the second and third elements of the returned
            # three-tuple would be the vertices in the left and right vertex
            # sets, respectively, that are also in the maximum independent set.
            # However, what I think the author meant was that the second
            # element is the list of vertices that were unmatched and the third
            # element was the list of vertices that were matched. Since that
            # seems to be the case, they don't really need to be returned,
            # since that information can be inferred from the matching
            # dictionary.

            # All the matched nodes must be a key in the dictionary
            for key in matching.copy():
                matching[matching[key]] = key
            return matching

        # recursively search backward through layers to find alternating paths
        # recursion returns true if found path, false otherwise
        def recurse(v):
            if v in preds:
                L = preds.pop(v)
                for u in L:
                    if u in pred:
                        pu = pred.pop(u)
                        if pu is unmatched or recurse(pu):
                            matching[v] = u
                            return True
            return False

        for v in unmatched:
            recurse(v)


def _is_connected_by_alternating_path(G, v, matched_edges, unmatched_edges, targets):
    """Returns True if and only if the vertex `v` is connected to one of
    the target vertices by an alternating path in `G`.

    An *alternating path* is a path in which every other edge is in the
    specified maximum matching (and the remaining edges in the path are not in
    the matching). An alternating path may have matched edges in the even
    positions or in the odd positions, as long as the edges alternate between
    'matched' and 'unmatched'.

    `G` is an undirected bipartite NetworkX graph.

    `v` is a vertex in `G`.

    `matched_edges` is a set of edges present in a maximum matching in `G`.

    `unmatched_edges` is a set of edges not present in a maximum
    matching in `G`.

    `targets` is a set of vertices.

    """

    def _alternating_dfs(u, along_matched=True):
        """Returns True if and only if `u` is connected to one of the
        targets by an alternating path.

        `u` is a vertex in the graph `G`.

        If `along_matched` is True, this step of the depth-first search
        will continue only through edges in the given matching. Otherwise, it
        will continue only through edges *not* in the given matching.

        """
        visited = set()
        # Follow matched edges when depth is even,
        # and follow unmatched edges when depth is odd.
        initial_depth = 0 if along_matched else 1
        stack = [(u, iter(G[u]), initial_depth)]
        while stack:
            parent, children, depth = stack[-1]
            valid_edges = matched_edges if depth % 2 else unmatched_edges
            try:
                child = next(children)
                if child not in visited:
                    if (parent, child) in valid_edges or (child, parent) in valid_edges:
                        if child in targets:
                            return True
                        visited.add(child)
                        stack.append((child, iter(G[child]), depth + 1))
            except StopIteration:
                stack.pop()
        return False

    # Check for alternating paths starting with edges in the matching, then
    # check for alternating paths starting with edges not in the
    # matching.
    return _alternating_dfs(v, along_matched=True) or _alternating_dfs(
        v,
        along_matched=False,
    )


def _connected_by_alternating_paths(G, matching, targets):
    """Returns the set of vertices that are connected to one of the target
    vertices by an alternating path in `G` or are themselves a target.

    An *alternating path* is a path in which every other edge is in the
    specified maximum matching (and the remaining edges in the path are not in
    the matching). An alternating path may have matched edges in the even
    positions or in the odd positions, as long as the edges alternate between
    'matched' and 'unmatched'.

    `G` is an undirected bipartite NetworkX graph.

    `matching` is a dictionary representing a maximum matching in `G`, as
    returned by, for example, :func:`maximum_matching`.

    `targets` is a set of vertices.

    """
    # Get the set of matched edges and the set of unmatched edges. Only include
    # one version of each undirected edge (for example, include edge (1, 2) but
    # not edge (2, 1)). Using frozensets as an intermediary step we do not
    # require nodes to be orderable.
    edge_sets = {frozenset((u, v)) for u, v in matching.items()}
    matched_edges = {tuple(edge) for edge in edge_sets}
    unmatched_edges = {
        (u, v) for (u, v) in G.edges() if frozenset((u, v)) not in edge_sets
    }

    return {
        v
        for v in G
        if v in targets
        or _is_connected_by_alternating_path(
            G,
            v,
            matched_edges,
            unmatched_edges,
            targets,
        )
    }


@nx._dispatchable
def to_vertex_cover(G, matching, top_nodes=None):
    """Returns the minimum vertex cover corresponding to the given maximum
    matching of the bipartite graph `G`.

    Parameters
    ----------
    G : NetworkX graph

      Undirected bipartite graph

    matching : dictionary

      A dictionary whose keys are vertices in `G` and whose values are the
      distinct neighbors comprising the maximum matching for `G`, as returned
      by, for example, :func:`maximum_matching`. The dictionary *must*
      represent the maximum matching.

    top_nodes : container

      Container with all nodes in one bipartite node set. If not supplied
      it will be computed. But if more than one solution exists an exception
      will be raised.

    Returns
    -------
    vertex_cover : :class:`set`

      The minimum vertex cover in `G`.

    Raises
    ------
    AmbiguousSolution
      Raised if the input bipartite graph is disconnected and no container
      with all nodes in one bipartite set is provided. When determining
      the nodes in each bipartite set more than one valid solution is
      possible if the input graph is disconnected.

    Notes
    -----
    This function is implemented using the procedure guaranteed by `Konig's
    theorem
    <https://en.wikipedia.org/wiki/K%C3%B6nig%27s_theorem_%28graph_theory%29>`_,
    which proves an equivalence between a maximum matching and a minimum vertex
    cover in bipartite graphs.

    Since a minimum vertex cover is the complement of a maximum independent set
    for any graph, one can compute the maximum independent set of a bipartite
    graph this way:

    >>> G = nx.complete_bipartite_graph(2, 3)
    >>> matching = nx.bipartite.maximum_matching(G)
    >>> vertex_cover = nx.bipartite.to_vertex_cover(G, matching)
    >>> independent_set = set(G) - vertex_cover
    >>> print(list(independent_set))
    [2, 3, 4]

    See :mod:`bipartite documentation <networkx.algorithms.bipartite>`
    for further details on how bipartite graphs are handled in NetworkX.

    """
    # This is a Python implementation of the algorithm described at
    # <https://en.wikipedia.org/wiki/K%C3%B6nig%27s_theorem_%28graph_theory%29#Proof>.
    L, R = bipartite_sets(G, top_nodes)
    # Let U be the set of unmatched vertices in the left vertex set.
    unmatched_vertices = set(G) - set(matching)
    U = unmatched_vertices & L
    # Let Z be the set of vertices that are either in U or are connected to U
    # by alternating paths.
    Z = _connected_by_alternating_paths(G, matching, U)
    # At this point, every edge either has a right endpoint in Z or a left
    # endpoint not in Z. This gives us the vertex cover.
    return (L - Z) | (R & Z)


#: Returns the maximum cardinality matching in the given bipartite graph.
#:
#: This function is simply an alias for :func:`hopcroft_karp_matching`.
maximum_matching = hopcroft_karp_matching


@nx._dispatchable(edge_attrs="weight")
def minimum_weight_full_matching(G, top_nodes=None, weight="weight"):
    r"""Returns a minimum weight full matching of the bipartite graph `G`.

    Let :math:`G = ((U, V), E)` be a weighted bipartite graph with real weights
    :math:`w : E \to \mathbb{R}`. This function then produces a matching
    :math:`M \subseteq E` with cardinality

    .. math::
       \lvert M \rvert = \min(\lvert U \rvert, \lvert V \rvert),

    which minimizes the sum of the weights of the edges included in the
    matching, :math:`\sum_{e \in M} w(e)`, or raises an error if no such
    matching exists.

    When :math:`\lvert U \rvert = \lvert V \rvert`, this is commonly
    referred to as a perfect matching; here, since we allow
    :math:`\lvert U \rvert` and :math:`\lvert V \rvert` to differ, we
    follow Karp [1]_ and refer to the matching as *full*.

    Parameters
    ----------
    G : NetworkX graph

      Undirected bipartite graph

    top_nodes : container

      Container with all nodes in one bipartite node set. If not supplied
      it will be computed.

    weight : string, optional (default='weight')

       The edge data key used to provide each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    matches : dictionary

      The matching is returned as a dictionary, `matches`, such that
      ``matches[v] == w`` if node `v` is matched to node `w`. Unmatched
      nodes do not occur as a key in `matches`.

    Raises
    ------
    ValueError
      Raised if no full matching exists.

    ImportError
      Raised if SciPy is not available.

    Notes
    -----
    The problem of determining a minimum weight full matching is also known as
    the rectangular linear assignment problem. This implementation defers the
    calculation of the assignment to SciPy.

    References
    ----------
    .. [1] Richard Manning Karp:
       An algorithm to Solve the m x n Assignment Problem in Expected Time
       O(mn log n).
       Networks, 10(2):143-152, 1980.
    """
    import numpy as np
    import scipy as sp

    left, right = nx.bipartite.sets(G, top_nodes)
    U = list(left)
    V = list(right)
    # We explicitly create the biadjacency matrix having infinities
    # where edges are missing (as opposed to zeros, which is what one would
    # get by using toarray on the sparse matrix).
    weights_sparse = biadjacency_matrix(
        G,
        row_order=U,
        column_order=V,
        weight=weight,
        format="coo",
    )
    weights = np.full(weights_sparse.shape, np.inf)
    weights[weights_sparse.row, weights_sparse.col] = weights_sparse.data
    left_matches = sp.optimize.linear_sum_assignment(weights)
    d = {U[u]: V[v] for u, v in zip(*left_matches)}
    # d will contain the matching from edges in left to right; we need to
    # add the ones from right to left as well.
    d.update({v: u for u, v in d.items()})
    return d


def _M_alternating_sequence(G, M, *, top_nodes=None):
    r"""Return an M-alternating-sequence of a bipartite graph `G` with
    regard to a matching `M`.

    An *M-alternating-sequence* is a sequence of pairwise disjoint subsets of nodes X_0 - Y_1 - X_1 - Y_2 - X_2 - ...
    When `M` is a maximum matching, the M-alternating-sequence calculated using it has some useful properties for
    finding envy free bipartite matching, this is proved in the article.

    Two sets are calculated with the following recursive definition:

    X_0 = nodes in G unmatched by M.
    for i>=1:
        Latex:
            Y_i = :math:`N_{G\M}(X_{i-1})\\`
            X_i = :math:`N_M(Y_i)`
        English:
            Y_i -> neighbors of X_{i-1} that were not matched by M
                   group-subtracting all the previous Y_k's we've seen
            X_i -> neighbors of Y_i that were matched by M

    The iterative pattern stops when either Y_k or X_k are an empty set for a
    certain k, forever staying an empty set. From k onward the alternating sequence
    is proven to always stop in the article.

    Two tuples containing sets of nodes are returned - tuple(X_subsets), tuple(Y_subsets).

    >>> G = nx.complete_bipartite_graph(3,3)
    >>> M = nx.bipartite.hopcroft_karp_matching(G)
    >>> _M_alternating_sequence(G, M)
    ((), ())

    >>> G = nx.Graph([(0,3),(0,4),(1,4),(2,4)])
    >>> M = {0:3, 3:0, 1:4, 4:1}
    >>> _M_alternating_sequence(G, M)
    (({2}, {1}), ({4},))

    >>> G = nx.Graph([(0,3),(1,3),(1,4),(2,4)])
    >>> M = {0:3,3:0,4:1,1:4}
    >>> _M_alternating_sequence(G, M)
    (({2}, {1}, {0}), ({4}, {3}))

    >>> G = nx.Graph([(0,3),(1,3),(1,4),(2,4)])
    >>> M = {0:3,3:0,4:1,1:4}
    >>> _M_alternating_sequence(G, M)
    (({2}, {1}, {0}), ({4}, {3}))

    >>> G = nx.Graph([(0,6),(1,6),(1,7),(2,6),(2,8),(3,9),(3,6),(4,8),(4,7),(5,9)])
    >>> M = {0:6,6:0,1:7,7:1,2:8,8:2,3:9,9:3}
    >>> _M_alternating_sequence(G, M)
    (({4, 5}, {1, 2, 3}, {0}), ({8, 9, 7}, {6}))

    """
    X, Y = nx.bipartite.sets(G, top_nodes=top_nodes)
    X_0 = set(X) - set(M.keys())
    if len(X_0) == 0:
        return (), ()

    X_subsets = [X_0]
    Y_subsets = []

    Y_subgroups_accumulate = set()

    while len(X_subsets) == 1 or (len(X_subsets[-1]) != 0 and len(Y_subsets[-1]) != 0):
        Y_current = {
            nbr
            for n in X_subsets[-1]
            for nbr in G[n]
            if nbr not in Y_subgroups_accumulate
            if M.get(n) != nbr
            if M.get(nbr) != n
        }
        if len(Y_current) == 0:
            break
        X_current = {
            nbr
            for n in Y_current
            for nbr in G[n]
            if M.get(n) == nbr and M.get(nbr) == n
        }
        if len(X_current) == 0:
            break

        Y_subsets.append(Y_current)
        X_subsets.append(X_current)

        Y_subgroups_accumulate.update(Y_current)

    return tuple(X_subsets), tuple(Y_subsets)


def envy_free_matching_partition(G, *, M=None, top_nodes=None):
    r"""Return a unique EFM (Envy Free Matching) partition of bipartite graph `G`.

    An EFM partition of a bipartite graph with bipartite sets X,Y is a unique partition of X - X_L, X_S and Y - X_L, X_S.
    This unique partition is proven to have the following properties:
    1. Every matching that matches all the nodes in X_L and is contained in G[X_L,Y_L] (all edges are between X_L and Y_L)
    is an envy-free matching.
    2. Every envy-free matching in `G` is contained in G[X_L,Y_L].

    Due to these properties we can say that X_L and Y_L are the "*good*" nodes and X_S and Y_S are the "*bad*" nodes,
    because - in the context of finding envy-free matchings, we will only find them in X_L and Y_L.

    Parameters
    ----------
    G:  NetworkX graph
      Undirected bipartite graph

    M: dict
      dictionary that represents a maximum matching in `G`.
      If M is none, the function will calculate a maximum matching.

    top_nodes: list
      if graph is not all connected top_nodes is the set of the top nodes in
      the bipartite graph `G`.

    Returns
    -------
    EFM: tuple of sets
      The partition returns as a tuple of 4 sets of nodes:
      `(X_L, X_S, Y_L, Y_S)` where X_L and Y_L are the "good nodes" of G
      while X_S and Y_S are the "bad nodes" of G where no envy-free matching
      exists according to THM 1.3 in the article.

    Examples
    --------
    Example 1: Perfect matching

    >>> G = nx.complete_bipartite_graph(3, 3)
    >>> M = nx.bipartite.hopcroft_karp_matching(G)
    >>> nx.bipartite.envy_free_matching_partition(G, M=M)
    ({0, 1, 2}, set(), {3, 4, 5}, set())

    Where there exists a perfect matching the maximum cardinality
    envy free matching is the perfect matching.

    Example 2: Non-empty envy-free matching

    >>> G = nx.Graph([(0, 3), (0, 4), (1, 4), (2, 4)])
    >>> M = {0: 3, 3: 0, 1: 4, 4: 1}
    >>> nx.bipartite.envy_free_matching_partition(G, M=M)
    ({0}, {1, 2}, {3}, {4})

    Here the graph contains a non-empty envy-free matching so X_L and Y_L are not empty.

    Example 3: Odd path

    >>> G = nx.Graph([(0, 3), (1, 3), (1, 4), (2, 4)])
    >>> M = {0: 3, 3: 0, 4: 1, 1: 4}
    >>> nx.bipartite.envy_free_matching_partition(G, M=M)
    (set(), {0, 1, 2}, set(), {3, 4})

    Like presented in the article, odd path contains an empty envy-free matching
    so X_L and Y_L are empty in the partition.

    Example 4: Y-path-saturated graph

    >>> G = nx.Graph(
    ...     [(0, 6), (1, 6), (1, 7), (2, 6), (2, 8), (3, 9), (3, 6), (4, 8), (4, 7), (5, 9)]
    ... )
    >>> M = {0: 6, 6: 0, 1: 7, 7: 1, 2: 8, 8: 2, 3: 9, 9: 3}
    >>> nx.bipartite.envy_free_matching_partition(G, M=M)
    (set(), {0, 1, 2, 3, 4, 5}, set(), {8, 9, 6, 7})

    Like presented in the article [1], Y-path-saturated graph contains an empty
    envy-free matching so X_L and Y_L are empty in the partition.

    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications
    to Fair Division", by Elad Aigner-Horev and Erel Segal-Halevi (2022),
    https://arxiv.org/abs/1901.09527
    Algorithm 1: Finding the EFM partition of a bipartite graph.
    """
    if M is None:
        M = maximum_matching(G, top_nodes=top_nodes)
    X, Y = nx.bipartite.sets(G, top_nodes=top_nodes)
    X_subsets, Y_subsets = _M_alternating_sequence(G, M, top_nodes=top_nodes)
    X_S = set(it.chain.from_iterable(X_subsets))
    Y_S = set(it.chain.from_iterable(Y_subsets))
    return set(X) - X_S, X_S, set(Y) - Y_S, Y_S


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def maximum_envy_free_matching(G, *, top_nodes=None):
    r"""Return an envy-free matching of maximum cardinality of the bipartite graph `G`

    A matching in a bipartite graph with bipartite sets X and Y is called envy-free,
    if no unmatched node in X is adjacent to a matched node in Y.

    An envy-free bipartite matching has *maximum cardinality* if it is the largest (has the most edges) possible matching
    that is still envy-free.
    There can be multiple different envy-free matching of maximum cardinality, this function returns *one* of them.

    There are graphs which don't have any possible envy-free matching or synonmously,
    their largest envy-free bipartite matching is empty.

    Envy-Free bipartite matches can be used for matching between people to "things" in a fair way.
    For example, they can be used for House Allocation Problems.

    Illustration: A real estate agent has a group of buyers seeking to purchase a house and a group of houses for sale,
    each buyer indicated houses they are interested in. The real estate agent wants to maximize the amount of people
    that get a house and avoid making customers that didn't get a house jealous by giving other customers houses they
    were interested in.

    this problem can be modeled to a bipartite graph with the buyers set (X), houses set(Y) and edges
    between X and Y indicating a buyer being interested in a house (binary "yes" or "no"). Using networkx, you can construct a bipartite graph
    as described, and call "maximum_envy_free_matching" on it to receive a matching of buyers to houses, guarenteed to
    be fair (This can produce an empty matching - meaning fairness can't be achieved in this case).


    Parameters
    ----------
    G : NetworkX graph
      Undirected bipartite graph

    top_nodes : container
      If graph is not connected `top_nodes` is the set of the top nodes in
      the bipartite graph `G`.

    Returns
    -------
    Matching: dictionary
        A Maximum cardinality envy-free matching is returned as a dictionary.

    Examples
    --------
    Example 1: Perfect matching

    >>> G = nx.complete_bipartite_graph(3, 3)
    >>> nx.bipartite.maximum_envy_free_matching(G)
    {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}

    Where there exists a perfect matching the maximum envy free matching is
    the perfect matching.

    Example 2: Non-empty envy-free matching

    >>> G = nx.Graph([(0, 3), (0, 4), (1, 4), (2, 4)])
    >>> nx.bipartite.maximum_envy_free_matching(G)
    {0: 3, 3: 0}

    Example 3: Odd path

    >>> G = nx.Graph([(0, 3), (1, 3), (1, 4), (2, 4)])
    >>> nx.bipartite.maximum_envy_free_matching(G)
    {}

    Like presented in the article, an odd path contains an empty envy-free matching
    so the returned matching is empty.

    Example 4: Y-path-saturated graph

    >>> G = nx.Graph(
    ...     [(0, 6), (1, 6), (1, 7), (2, 6), (2, 8), (3, 9), (3, 6), (4, 8), (4, 7), (5, 9)]
    ... )
    >>> nx.bipartite.maximum_envy_free_matching(G)
    {}

    Like presented in the article [1]_, Y-path-saturated graph contains an empty
    envy-free matching so X_L and Y_L are empty in the partition.

    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications
    to Fair Division", by Elad Aigner-Horev and Erel Segal-Halevi (2022),
    https://arxiv.org/abs/1901.09527
    Algorithm 1: Finding the EFM partition of a bipartite graph.
    """
    M = maximum_matching(G, top_nodes=top_nodes)
    partition = envy_free_matching_partition(G, M=M, top_nodes=top_nodes)
    un = partition[1].union(partition[3])
    return {node: M[node] for node in M if node not in un and M[node] not in un}


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def minimum_weight_envy_free_matching(G, *, top_nodes=None):
    r"""Returns a minimum weight maximum cardinality envy-free matching of the bipartite graph `G`

    A matching in a bipartite graph with bipartite sets X and Y is called envy-free,
    if no unmatched node in X is adjacent to a matched node in Y.

    An envy-free bipartite matching has *maximum cardinality* if it is the largest (has the most edges) possible matching
    that is still envy-free.
    This function returns an envy-free bipartite matching with the least cost (sum of edge weights) out of the maximum cardinality matchings.

    There can be multiple different envy-free matching of maximum cardinality and minimum weight, this function returns *one* of them.

    Weighted Envy-Free bipartite matches can be used for matching between people to "things" in a fair way considering cardinal preferences.
    For example, they can be used for the Rental harmony problem.

    Illustration: A group of people that want to rent an apartament as roomates want to find a pairing of roomate to room and minimize cost for each one.
    Each roomate assign an amount he's willing to pay for a certain room.

    this problem can be modeled to a bipartite graph with the roomates set (X), rooms set(Y) and edges
    between X and Y indicating a roomate interested in a room and the edge weight meaning the amount of money he's willing to pay.
    Using networkx, you can construct a bipartite graph
    as described, and call "minimum_weight_envy_free_matching" on it to receive a matching of roomates to rooms, guarenteed to
    be fair (This can produce an empty matching - meaning fairness can't be achieved in this case).



    Parameters
    ----------
    G : NetworkX graph
      Undirected bipartite graph.

    top_nodes : container
      If graph is not connected `top_nodes` is the set of the top nodes
      in the bipartite graph `G`.

    Returns
    -------
    Matching: dictionary
      A minimum weight maximum cardinality matching is returned as a dictionary.

    Examples
    --------
    Example 1: K 3,3 with weights

    >>> G = nx.Graph()
    >>> edges = [
    ...     (0, 3, 250),
    ...     (0, 4, 148),
    ...     (0, 5, 122),
    ...     (1, 3, 175),
    ...     (1, 4, 135),
    ...     (1, 5, 150),
    ...     (2, 3, 150),
    ...     (2, 4, 125),
    ... ]
    >>> G.add_weighted_edges_from(edges)
    >>> nx.bipartite.minimum_weight_envy_free_matching(G)
    {0: 5, 1: 4, 2: 3, 5: 0, 4: 1, 3: 2}

    Where there exists a perfect matching the maximum envy free matching is a
    perfect matching and this is the minimum weight perfect matching.

    Example 2: Non-empty envy-free matching

    >>> G = nx.Graph()
    >>> edges = [(0, 4, 5), (1, 4, 1), (2, 5, 3), (2, 7, 9), (3, 6, 3), (3, 7, 7)]
    >>> G.add_weighted_edges_from(edges)
    >>> nx.bipartite.minimum_weight_envy_free_matching(G, top_nodes=[0, 1, 2, 3])
    {2: 5, 3: 6, 5: 2, 6: 3}

    References
    ----------
    .. [1] "Envy-free Matchings in Bipartite Graphs and their Applications
    to Fair Division", by Elad Aigner-Horev and Erel Segal-Halevi (2022),
    https://arxiv.org/abs/1901.09527
    Algorithm 1: Finding the EFM partition of a bipartite graph.
    """
    M = maximum_matching(G, top_nodes=top_nodes)
    partition = envy_free_matching_partition(G, M=M, top_nodes=top_nodes)
    union_partition = partition[0].union(partition[2])
    return minimum_weight_full_matching(G.subgraph(union_partition))
