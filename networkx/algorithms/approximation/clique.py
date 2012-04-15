# -*- coding: utf-8 -*-
"""
Cliques.
"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   All rights reserved.
#   BSD license.
__all__ = ["clique_removal"]
__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
from networkx.algorithms.approximation import ramsey

def clique_removal(graph):
    """ Repeatedly remove cliques from the graph.

    Results in a `O(|V|/(\log |V|)^2)` approximation of maximum clique
    & independent set. Returns the largest independent set found, along
    with found maximal cliques.

    Parameters
    ----------
    graph : NetworkX graph
        Undirected graph

    Returns
    -------
    max_ind_cliques : (set, list) tuple
        Maximal independent set and list of maximal cliques (sets) in the graph.

    References
    ----------
    .. [1] Boppana, R., & Halldórsson, M. M. (1992).
        Approximating maximum independent sets by excluding subgraphs.
        BIT Numerical Mathematics, 32(2), 180–196. Springer.
    """
    graph = graph.copy()
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

    maxiset = max(isets)
    return maxiset, cliques
