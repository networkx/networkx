# -*- coding: utf-8 -*-
"""
Algorithm to find a maximum independent set.

"""
#    Peng Feifei <pengff@ios.ac.cn>
#    All rights reserved.
#    BSD license.

import networkx as nx
import exact_maximum_clique
__author__ = """Peng Feifei (pengff@ios.ac.cn)"""
__all__ = ['maximum_independent_set']

def maximum_independent_set(G):
    """Finds a maximum clique set for the graph G.

    Independent set or stable set is a set of vertices in a graph, no two of
    which are adjacent. That is, it is a set I of vertices such that for every
    two vertices in I, there is no edge connecting the two. Equivalently, each
    edge in the graph has at most one endpoint in I. The size of an independent
    set is the number of vertices it contains.

    A maximum independent set is a largest independent set for a given graph G
    and its size is denoted α(G). The problem of finding such a set is called
    the maximum independent set problem and is an NP-hard optimization problem.
    As such, it is unlikely that there exists an efficient algorithm for finding
    a maximum independent set of a graph.

    http://en.wikipedia.org/wiki/Independent_set_(graph_theory)

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    iset : Set
        The maximum independent set

    Notes
    -----
    Maximum independent set algorithm is based on [1]:

    References
    ----------
    .. [1] Carraghan R, Pardalos P M. An exact algorithm for the 
           maximum clique problem[J]. Operations Research Letters, 1990, 9(6): 375-382.

    """
    cgraph = nx.complement(G)
    iset=exact_maximum_clique.maxclique_set(cgraph)
    return iset

