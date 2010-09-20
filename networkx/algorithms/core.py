"""
Find the k-cores of a graph.

The k-core is found by recursively pruning nodes with degrees less than k. 
"""
__author__ = "\n".join(['Dan Schult (dschult@colgate.edu)',
                        'Jason Grout (jason-sage@creativetrax.com)',
                        'Aric Hagberg (hagberg@lanl.gov)'])
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__all__ = ['core_number','k_core','find_cores']

import networkx as nx

def core_number(G):
    """Return the core number for each vertex.
    
    The core number of a node is the largest value k of a k-core that 
    contains the node.

    A k-core is a maximal subgraph that contains nodes of degree k or more.

    Parameters
    ----------
    G : NetworkX graph 
       A graph or directed graph
  
    Returns
    -------
    core_number : dictionary 
       A dictionary keyed by node to the core number. 

    Raises
    ------
    NetworkXError
        The k-core is not defined for graphs with self loops or parallel edges.

    Notes
    -----
    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the degree is defined to be the in-degree + out-degree 
    of a node.

    References
    ----------
    .. [1] An O(m) Algorithm for Cores Decomposition of Networks
       Vladimir Batagelj and Matjaz Zaversnik, 2003
       http://arxiv.org/abs/cs.DS/0310049 
    """
    if G.is_multigraph():
        raise nx.NetworkXError(
                'MultiGraph and MultiDiGraph types not supported.')

    if G.number_of_selfloops()>0:
        raise nx.NetworkXError(
                'Input graph has self loops; the core number is not defined',
                'Consider using G.remove_edges_from(G.selfloop_edges())')

    if G.is_directed():
        import itertools
        def neighbors(v):
            return itertools.chain.from_iterable([G.predecessors_iter(v),
                                                  G.successors_iter(v)])
    else:
        neighbors=G.neighbors_iter
    degrees=G.degree()
    # sort nodes by degree
    nodes=sorted(degrees,key=degrees.get)
    bin_boundaries=[0]
    curr_degree=0
    for i,v in enumerate(nodes):
        if degrees[v]>curr_degree:
            bin_boundaries.extend([i]*(degrees[v]-curr_degree))
            curr_degree=degrees[v]
    node_pos = dict((v,pos) for pos,v in enumerate(nodes))
    # initial guesses for core is degree
    core=degrees
    nbrs=dict((v,set(neighbors(v))) for v in G)
    for v in nodes:
        for u in nbrs[v]:
            if core[u] > core[v]:
                nbrs[u].remove(v)
                pos=node_pos[u]
                bin_start=bin_boundaries[core[u]]
                node_pos[u]=bin_start
                node_pos[nodes[bin_start]]=pos
                nodes[bin_start],nodes[pos]=nodes[pos],nodes[bin_start]
                bin_boundaries[core[u]]+=1
                core[u]-=1
    return core

find_cores=core_number

def k_core(G,k=None):
    """Return k-core of G.

    A k-core is a maximal subgraph that contains nodes of degree k or more.

    Parameters
    ----------
    G : NetworkX graph 
       A graph or directed graph

    k : int, optional
       The order of the core.  If not specified return the main core.
  
    Returns
    -------
    G : NetworkX graph
       The k-core subgraph

    Raises
    ------
    NetworkXError
        The k-core is not defined for graphs with self loops or parallel edges.

    Notes
    -----
    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the degree is defined to be the in-degree + out-degree 
    of a node.

    References
    ----------
    .. [1] An O(m) Algorithm for Cores Decomposition of Networks
       Vladimir Batagelj and Matjaz Zaversnik,  2003
       http://arxiv.org/abs/cs.DS/0310049 
    """
    core_number=nx.core_number(G)
    if k is None:
        k=max(core_number.values()) # main core
    nodes=(n for n in core_number if core_number[n]>=k)
    return G.subgraph(nodes)
