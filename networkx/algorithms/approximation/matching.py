# -*- coding: utf-8 -*-
"""
**************
Graph Matching
**************

Given a graph G = (V,E), a matching M in G is a set of pairwise non-adjacent
edges; that is, no two edges share a common vertex.

http://en.wikipedia.org/wiki/Matching_(graph_theory)
"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   All rights reserved.
#   BSD license.
import networkx as nx
__all__ = ["min_maximal_matching"]
__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""

def min_maximal_matching(graph):
    """Returns a set of edges such that no two edges share a common endpoint
    and every edge not in the set shares some common endpoint in the set.

    Parameters
    ----------
    graph : NetworkX graph
      Undirected graph

    Returns
    -------
    min_maximal_matching : set
      Returns a set of edges such that no two edges share a common endpoint
      and every edge not in the set shares some common endpoint in the set.
      Cardinality will be 2*OPT in the worst case.

    References
    ----------
    .. [1] Vazirani, Vijay Approximation Algorithms (2001)
    """
    return nx.maximal_matching(graph)
