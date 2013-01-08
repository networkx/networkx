# -*- coding: utf-8 -*-
"""
************
Vertex Cover
************

Given an undirected graph `G = (V, E)` and a function w assigning nonnegative
weights to its vertices, find a minimum weight subset of V such that each edge
in E is incident to at least one vertex in the subset.

http://en.wikipedia.org/wiki/Vertex_cover
"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   All rights reserved.
#   BSD license.
from networkx.utils import *
__all__ = ["min_weighted_vertex_cover"]
__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""

@not_implemented_for('directed')
def min_weighted_vertex_cover(G, weight=None):
    r"""2-OPT Local Ratio for Minimum Weighted Vertex Cover

    Find an approximate minimum weighted vertex cover of a graph.

    Parameters
    ----------
    G : NetworkX graph
      Undirected graph

    weight : None or string, optional (default = None)
        If None, every edge has weight/distance/cost 1. If a string, use this
        edge attribute as the edge weight. Any edge attribute not present
        defaults to 1.

    Returns
    -------
    min_weighted_cover : set
      Returns a set of vertices whose weight sum is no more than 2 * OPT.

    Notes
    -----
    Local-Ratio algorithm for computing an approximate vertex cover.
    Algorithm greedily reduces the costs over edges and iteratively
    builds a cover. Worst-case runtime is `O(|E|)`.

    References
    ----------
    .. [1] Bar-Yehuda, R., & Even, S. (1985). A local-ratio theorem for
       approximating the weighted vertex cover problem.
       Annals of Discrete Mathematics, 25, 27–46
       http://www.cs.technion.ac.il/~reuven/PDF/vc_lr.pdf
    """
    weight_func = lambda nd: nd.get(weight, 1)
    cost = dict((n, weight_func(nd)) for n, nd in G.nodes(data=True))

    # while there are edges uncovered, continue
    for u,v in G.edges_iter():
        # select some uncovered edge
        min_cost = min([cost[u], cost[v]])
        cost[u] -= min_cost
        cost[v] -= min_cost

    return set(u for u in cost if cost[u] == 0)
