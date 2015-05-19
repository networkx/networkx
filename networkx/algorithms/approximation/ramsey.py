# -*- coding: utf-8 -*-
"""
Ramsey numbers.
"""
#   Copyright (C) 2011 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   All rights reserved.
#   BSD license.
import networkx as nx
__all__ = ["ramsey_R2"]
__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""

def ramsey_R2(G):
    r"""Approximately computes the Ramsey number `R(2;s,t)` for graph.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    max_pair : (set, set) tuple
        Maximum clique, Maximum independent set.
    """
    if not G:
        return (set([]), set([]))

    node = next(G.nodes_iter())
    nbrs = nx.all_neighbors(G, node)
    nnbrs = nx.non_neighbors(G, node)
    c_1, i_1 = ramsey_R2(G.subgraph(nbrs))
    c_2, i_2 = ramsey_R2(G.subgraph(nnbrs))

    c_1.add(node)
    i_2.add(node)

    # max here should based on size of sets/lists
    max_c = c_1
    if len(c_2) > len(c_1):
        max_c = c2

    max_i = i_1
    if len(i_2) > len(i_1):
        max_i = i2

    return (max_c, max_i)
