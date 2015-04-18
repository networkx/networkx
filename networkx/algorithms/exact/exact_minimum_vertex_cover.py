# -*- coding: utf-8 -*-
"""
Algorithm to find a minimum vertex cover.

"""
#    Peng Feifei <pengff@ios.ac.cn>
#    All rights reserved.
#    BSD license.

import networkx as nx
import exact_maximum_independent_set
__author__ = """Peng Feifei (pengff@ios.ac.cn)"""
__all__ = ['min_vertex_cover']

def min_vertex_cover(G):
    """Finds a minimum vertex cover for the graph G.

    Given an undirected graph `G = (V, E)`,find a minimum 
    subset of V such that each edge in E is incident to at least 
    one vertex in the subset.

	http://en.wikipedia.org/wiki/Vertex_cover

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    iset : Set
        The minimum vertex cover

    Notes
    -----
    Minimum vertex cover algorithm is based on [1]:

    References
    ----------
    .. [1] Carraghan R, Pardalos P M. An exact algorithm for the 
           maximum clique problem[J]. Operations Research Letters, 1990, 9(6): 375-382.

    """
    iset=exact_maximum_independent_set.maximum_independent_set(G)
    return list(set(G.nodes()).difference(set(iset)))
