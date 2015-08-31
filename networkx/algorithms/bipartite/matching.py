# matching.py - bipartite graph maximum matching algorithms
#
# Copyright 2015 Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
#
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
"""Provides functions for computing a maximum cardinality matching in a
bipartite graph.

If you don't care about the particular implementation of the maximum matching
algorithm, simply use the :func:`maximum_matching`. If you do care, you can
import one of the named maximum matching algorithms directly.

For example, to find a maximum matching in the complete bipartite graph with
two vertices on the left and three vertices on the right:

>>> import networkx as nx
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

"""
import collections
import itertools

from networkx.algorithms.bipartite import sets as bipartite_sets

__all__ = ['maximum_matching', 'hopcroft_karp_matching', 'eppstein_matching',
           'to_vertex_cover']

INFINITY = float('inf')


def hopcroft_karp_matching(G):
    """Returns the maximum cardinality matching of the bipartite graph `G`.

    Parameters
    ----------
    G : NetworkX graph

      Undirected bipartite graph

    Returns
    -------
    matches : dictionary

      The matching is returned as a dictionary, `matches`, such that
      ``matches[v] == w`` if node ``v`` is matched to node ``w``. Unmatched
      nodes do not occur as a key in mate.

    Notes
    -----

    This function is implemented with the `Hopcroft--Karp matching algorithm
    <https://en.wikipedia.org/wiki/Hopcroft%E2%80%93Karp_algorithm>`_ for
    bipartite graphs.

    See Also
    --------

    eppstein_matching

    References
    ----------
    .. [1] John E. Hopcroft and Richard M. Karp. "An n^{5 / 2} Algorithm for
       Maximum Matchings in Bipartite Graphs" In: **SIAM Journal of Computing**
       2.4 (1973), pp. 225--231. <https://dx.doi.org/10.1137/0202019>.

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
    left, right = bipartite_sets(G)
    leftmatches = {v: None for v in left}
    rightmatches = {v: None for v in right}
    distances = {}
    queue = collections.deque()

    # Implementation note: this counter is incremented as pairs are matched but
    # it is currently not used elsewhere in the computation.
    num_matched_pairs = 0
    while breadth_first_search():
        for v in left:
            if leftmatches[v] is None:
                if depth_first_search(v):
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
    return dict(itertools.chain(leftmatches.items(), rightmatches.items()))


def eppstein_matching(G):
    """Returns the maximum cardinality matching of the bipartite graph `G`.

    Parameters
    ----------
    G : NetworkX graph

      Undirected bipartite graph

    Returns
    -------
    matches : dictionary

      The matching is returned as a dictionary, `matches`, such that
      ``matches[v] == w`` if node ``v`` is matched to node ``w``. Unmatched
      nodes do not occur as a key in mate.

    Notes
    -----

    This function is implemented with David Eppstein's version of the algorithm
    Hopcroft--Karp algorithm (see :func:`hopcroft_karp_matching`), which
    originally appeared in the `Python Algorithms and Data Structures library
    (PADS) <http://www.ics.uci.edu/~eppstein/PADS/ABOUT-PADS.txt>`_.

    See Also
    --------

    hopcroft_karp_matching

    """
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
            unlayered = {}
            for u in G:
                # TODO Why is extra inner loop necessary?
                for v in G[u]:
                    if v not in preds:
                        unlayered[v] = None
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


def _is_connected_by_alternating_path(G, v, matching, targets):
    """Returns ``True`` if and only if the vertex `v` is connected to one of
    the target vertices by an alternating path in `G`.

    An *alternating path* is a path in which every other edge is in the
    specified maximum matching (and the remaining edges in the path are not in
    the matching). An alternating path may have matched edges in the even
    positions or in the odd positions, as long as the edges alternate between
    'matched' and 'unmatched'.

    `G` is an undirected bipartite NetworkX graph.

    `v` is a vertex in `G`.

    `matching` is a dictionary representing a maximum matching in `G`, as
    returned by, for example, :func:`maximum_matching`.

    `targets` is a set of vertices.

    """
    # Get the set of matched edges and the set of unmatched edges. Only include
    # one version of each undirected edge (for example, include edge (1, 2) but
    # not edge (2, 1)).
    matched_edges = {(u, v) for u, v in matching.items() if u <= v}
    unmatched_edges = set(G.edges()) - matched_edges

    def _alternating_dfs(u, depth, along_matched=True):
        """Returns ``True`` if and only if `u` is connected to one of the
        targets by an alternating path.

        `u` is a vertex in the graph `G`.

        `depth` specifies the maximum recursion depth of the depth-first
        search.

        If `along_matched` is ``True``, this step of the depth-first search
        will continue only through edges in the given matching. Otherwise, it
        will continue only through edges *not* in the given matching.

        """
        # Base case 1: u is one of the target vertices. `u` is connected to one
        # of the target vertices by an alternating path of length zero.
        if u in targets:
            return True
        # Base case 2: we have exceeded are allowed depth. In this case, we
        # have looked at a path of length `n`, so looking any further won't
        # help.
        if depth < 0:
            return False
        # Determine which set of edges to look across.
        valid_edges = matched_edges if along_matched else unmatched_edges
        for v in G[u]:
            # Consider only those neighbors connected via a valid edge.
            if (u, v) in valid_edges or (v, u) in valid_edges:
                # Recursively perform a depth-first search starting from the
                # neighbor. Decrement the depth limit and switch which set of
                # vertices will be valid for next time.
                return _alternating_dfs(v, depth - 1, not along_matched)
        # If there are no more vertices to look through and we haven't yet
        # found a target vertex, simply say that no path exists.
        return False

    # Check for alternating paths starting with edges in the matching, then
    # check for alternating paths starting with edges not in the
    # matching. Initiate the depth-first search with the current depth equal to
    # the number of nodes in the graph.
    return (_alternating_dfs(v, len(G), along_matched=True)
            or _alternating_dfs(v, len(G), along_matched=False))


def _connected_by_alternating_paths(G, matching, targets):
    """Returns the set of vertices that are connected to one of the target
    vertices by an alternating path in `G`.

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
    # TODO This can be parallelized.
    return {v for v in G if _is_connected_by_alternating_path(G, v, matching,
                                                              targets)}


def to_vertex_cover(G, matching):
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

    Returns
    -------

    vertex_cover : :class:`set`

      The minimum vertex cover in `G`.

    Notes
    -----

    This function is implemented using the procedure guaranteed by `Konig's
    theorem
    <http://en.wikipedia.org/wiki/K%C3%B6nig%27s_theorem_%28graph_theory%29>`_,
    which proves an equivalence between a maximum matching and a minimum vertex
    cover in bipartite graphs.

    Since a minimum vertex cover is the complement of a maximum independent set
    for any graph, one can compute the maximum independent set of a bipartite
    graph this way:

    >>> import networkx as nx
    >>> G = nx.complete_bipartite_graph(2, 3)
    >>> matching = nx.bipartite.maximum_matching(G)
    >>> vertex_cover = nx.bipartite.to_vertex_cover(G, matching)
    >>> independent_set = set(G) - vertex_cover
    >>> print(list(independent_set))
    [2, 3, 4]

    """
    # This is a Python implementation of the algorithm described at
    # <https://en.wikipedia.org/wiki/K%C3%B6nig%27s_theorem_%28graph_theory%29#Proof>.
    L, R = bipartite_sets(G)
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
