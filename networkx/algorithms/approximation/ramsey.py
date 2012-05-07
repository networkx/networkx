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

def ramsey_R2(graph):
    r"""Approximately computes the Ramsey number `R(2;s,t)` for graph.

    Parameters
    ----------
    graph : NetworkX graph
        Undirected graph

    Returns
    -------
    max_pair : (set, set) tuple
        Maximum clique, Maximum independent set.
    """
    if not graph:
        return (set([]), set([]))

    node = next(graph.nodes_iter())
    nbrs = nx.all_neighbors(graph, node)
    nnbrs = nx.non_neighbors(graph, node)
    c_1, i_1 = ramsey_R2(graph.subgraph(nbrs))
    c_2, i_2 = ramsey_R2(graph.subgraph(nnbrs))

    c_1.add(node)
    i_2.add(node)
    return (max([c_1, c_2]), max([i_1, i_2]))
