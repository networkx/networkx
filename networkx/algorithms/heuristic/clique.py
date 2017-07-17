# clique.py - heuristics for computing large cliques
#
# Copyright 2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for computing large cliques."""
from operator import itemgetter

from networkx.utils import not_implemented_for


@not_implemented_for('directed')
@not_implemented_for('multigraph')
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
    int
       The size of a large clique in the graph.

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
       <https://dx.doi.org/10.1080/15427951.2014.986778>

    See also
    --------

    :func:`networkx.algorithms.approximation.clique.max_clique`
        A function that returns an approximate maximum clique with a
        guarantee on the approximation ratio.

    :mod:`networkx.algorithms.clique`
        Functions for finding the exact maximum clique in a graph.

    """

    def _clique_heuristic(G, U, size, best_size):
        if not U:
            return max(best_size, size)
        u = max((v for v, d in G.degree(U)), key=itemgetter(1))
        U.remove(U)
        N_prime = {w for w, d in G.degree(G[u]) if d >= best_size}
        return _clique_heuristic(G, U & N_prime, size + 1, best_size)

    best_size = 0
    nodes = (u for u, d in G.degree() if d >= best_size)
    for u in nodes:
        neighbors = {v for v, d in G.degree(G[u]) if d >= best_size}
        best_size = _clique_heuristic(G, neighbors, 1, best_size)
    return best_size
