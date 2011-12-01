# -*- coding: utf-8 -*-
"""
Flow Hierarchy.
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__authors__ = "\n".join(['Ben Edwards (bedwards@cs.unm.edu)'])
__all__ = ['flow_hierarchy']

def flow_hierarchy(G,weight=None):
    """Returns the flow hierarchy of a directed network `G'.

    Flow hierarchy is defined as the fraction of edges not participating
    in cycles in a directed graph.[1].

    Parameters
    ----------
    G : NetworkX DiGraph or MultiDiGraph
        Graph to be analyzed.
    weight : key,optional (default=None)
        Value for weights on nodes. If None defaults to 1

    Returns
    -------
    h : float
       flow heirarchy value for the network

    Notes
    -----
    In [1] they use an algorithm which repeatedly exponentiates the link
    adjacency matrix and then looks for zeros on the diagonal. This has a
    running time of O(m^(log(m)). However, an edge is in a cycle iff it is
    in a strongly connected component, which can be found in O(m) time using
    Tarjan's algorithm
    
    References
    ----------
    .. [1] Luo, J.; Magee, C.L. (2011),
    Detecting evolving patterns of self-organizing networks by flow
    hierarchy measurement, Complexity, Volume 16 Issue 6 53-61

    """
    if not G.is_directed():
        raise nx.NetworkXError("G must be a digraph in flow_heirarchy")
    cG = nx.condensation_multigraph(G)
    return cG.size(weight=weight)/float(G.size(weight=weight))
    