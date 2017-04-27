# -*- coding: utf-8 -*-
"""
Cliques.
"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   All rights reserved.
#   BSD license.
import networkx as nx
from networkx.algorithms.approximation import ramsey
__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
__all__ = ["clique_removal","max_clique"]

def max_clique(G):
    r"""Find the Maximum Clique

    Finds the `O(|V|/(log|V|)^2)` apx of maximum clique/independent set
    in the worst case.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    clique : set
        The apx-maximum clique of the graph

    Notes
    ------
    A clique in an undirected graph G = (V, E) is a subset of the vertex set
    `C \subseteq V`, such that for every two vertices in C, there exists an edge
    connecting the two. This is equivalent to saying that the subgraph
    induced by C is complete (in some cases, the term clique may also refer
    to the subgraph).

    A maximum clique is a clique of the largest possible size in a given graph.
    The clique number `\omega(G)` of a graph G is the number of
    vertices in a maximum clique in G. The intersection number of
    G is the smallest number of cliques that together cover all edges of G.

    http://en.wikipedia.org/wiki/Maximum_clique

    References
    ----------
    .. [1] Boppana, R., & Halldórsson, M. M. (1992).
        Approximating maximum independent sets by excluding subgraphs.
        BIT Numerical Mathematics, 32(2), 180–196. Springer.
        doi:10.1007/BF01994876
    """
    if G is None:
        raise ValueError("Expected NetworkX graph!")

    # finding the maximum clique in a graph is equivalent to finding
    # the independent set in the complementary graph
    cgraph = nx.complement(G)
    iset, _ = clique_removal(cgraph)
    return iset

def clique_removal(G):
    """ Repeatedly remove cliques from the graph.

    Results in a `O(|V|/(\log |V|)^2)` approximation of maximum clique
    & independent set. Returns the largest independent set found, along
    with found maximal cliques.

    Parameters
    ----------
    G : NetworkX graph
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
    graph = G.copy(with_data=False)
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
    # Determine the largest independent set as measured by cardinality.
    maxiset = max(isets, key=len)
    return maxiset, cliques
