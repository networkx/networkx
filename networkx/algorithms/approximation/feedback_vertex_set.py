"""Approximation for minimal feedback vertex set."""
#    Copyright (C) 2016 by
#    James Clough <james.clough91@gmail.com>
#    All rights reserved.
#    BSD license.

__author__ = "\n".join(["James Clough (james.clough91@gmail.com)"])

__all__ = ['feedback_vertex_set']

import networkx as nx
from networkx.utils.decorators import *

@not_implemented_for('directed')
@not_implemented_for('multigraph')
def feedback_vertex_set(G, vertex_weights=None):
    """ Returns a feedback vertex set (FVS) for graph G
    
    A feedback vertex set is a set of vertices which, if removed from G, make it acyclic.
    
    This function finds an approximation for the minimal feedback vertex set.
    The set is minimal in the sense of minimising the weights of the vertices in the set.
    These weights can be specified, or otherwise are left as 1 for each vertex.
    The algorithm, cited below, is a 2-approximation meaning that the total weight of
    the FVS is guaranteed to be within a factor of 2 of the true minimum.
    Finding the true minimum FVS is an NP-hard problem.
    
    Parameters
    ----------
    G : graph
        A NetworkX Graph

    vertex_weights: dict
        A dictionary specifying weights for each vertex.
        If None, assume all weights are 1.
        
    Returns
    -------
    F: list
        The vertices in the FVS
    
    Raises
    ------
    NetworkXNotImplemented
        If G is directed or a multigraph
        
    NetworkXError
        If vertex_weights is not fully specified
    
    Notes
    -----
    This is an implementation of the algorithm in the Bafna et. al. paper cited below.
    
    References
    ----------
    * V. Bafna, P. Berman, T. Fujito, 
    "A 2-approximation algorithm for the undirected feedback vertex set problem",
    SIAM J. Discrete Math., Vol. 12, No. 3, pp. 289-297, (1999)
    """

    G_original = G.copy()
    if vertex_weights is None:
        vertex_weights = {u:1. for u in G.nodes()}
    else:
        for u in G.nodes():
            if u not in vertex_weights:
                raise nx.NetworkXError("Vertex %s missing from vertex_weights" % u)

    F = []
    stack = []
    for u in list(G.nodes()):
        if vertex_weights[u] == 0:
            G.remove_node(u)
            F.append(u)

    G = _cleanup(G)
    while G.number_of_nodes() > 0:
        C_nodes = _find_semidisjoint_cycle(G)
        if C_nodes:
            # we have a semidisjoint cycle
            min_w_in_C = min([vertex_weights[u] for u in C_nodes])
            vertex_weights = {u:vertex_weights[u] - min_w_in_C for u in G.nodes()}
            # some stuff in square brackets I don't understand
        else:
            # there are no semidisjoint cycles left
            min_w_in_C = min([(vertex_weights[u] / (G.degree(u)-1)) for u in G.nodes()])
            vertex_weights = {u:vertex_weights[u] - (min_w_in_C * (G.degree(u)-1)) for u in G.nodes()}
        for u in list(G.nodes()):
            if vertex_weights[u] == 0:
                G.remove_node(u)
                F.append(u)
                stack.append(u)
        G = _cleanup(G)
    while len(stack) > 0:
        u = stack.pop()
        F_u = [v for v in F if v!=u]
        if _check_fvs(G_original.copy(), F_u):
            F.remove(u)
    return F


def _check_fvs(G, F):
    """ Check whether vertex set F is a feedback vertex set for graph G

    """
    for u in F:
        G.remove_node(u)
    if len(nx.cycle_basis(G)) == 0:
        return True
    else:
        return False


def _cleanup(G):
    """ While any vertex has degree of 1 or 0, remove it and any incident edges

    """
    if G.number_of_nodes() == 0:
        return G
    while (G.number_of_nodes() > 0) and (min(dict(nx.degree(G)).values()) <= 1):
        for u in list(G.nodes()):
            if G.degree(u) <= 1:
                G.remove_node(u)
    return G

def _find_semidisjoint_cycle(G):
    """ Return list of nodes in semidisjoint cycle C in G, or False otherwise

    A cycle C is semidisjoint if for every vertex u in C, the degree of u
    equals 2 with at most one exception.
    """
    C_basis = nx.cycle_basis(G)
    for C in C_basis:
        if _check_cycle_semidisjoint(G, C):#
            return C
    return False
    

def _check_cycle_semidisjoint(G, C):
    """ Given a cycle of edges, C, in graph G, check that C is semidisjoint

    """
    num_extra_edges = 0
    for u in C:
        if G.degree(u) > 2:
            num_extra_edges += 1
    if num_extra_edges > 1:
        return False
    else:
        return True

