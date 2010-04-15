"""
Find the k-cores of a graph.
The k-core is found by recursively pruning nodes with degrees less than k. 
"""
__author__ = "\n".join(['Dan Schult(dschult@colgate.edu)',
                        'Jason Grout(jason-sage@creativetrax.com)'])
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['find_cores']

def find_cores(G):
    """Return the core number for each vertex.
    
    Parameters
    ----------
    G : NetworkX graph
       A graph
  
    Returns
    -------
    core_number : dictionary 
       A ditionary keyed by node to the core number. 

    References
    ----------
    .. [1] An O(m) Algorithm for Cores Decomposition of Networks
       Vladimir Batagelj and Matjaz Zaversnik,  2003
       http://arxiv.org/abs/cs.DS/0310049 
    """
    # compute the degrees of each vertex
    degrees=G.degree()
    # sort verticies by degree
    verts= sorted( degrees.keys(), key=lambda x: degrees[x])
    bin_boundaries=[0]
    curr_degree=0
    for i,v in enumerate(verts):
        if degrees[v]>curr_degree:
            bin_boundaries.extend([i]*(degrees[v]-curr_degree))
            curr_degree=degrees[v]
    vert_pos = dict((v,pos) for pos,v in enumerate(verts))
    # Set up initial guesses for core and lists of neighbors.
    core= degrees
    nbrs=dict((v,set(G.neighbors(v))) for v in G)
    # form vertex core building up from smallest
    for v in verts:
        for u in nbrs[v]:
            if core[u] > core[v]:
                nbrs[u].remove(v)
                pos=vert_pos[u]
                bin_start=bin_boundaries[core[u]]
                vert_pos[u]=bin_start
                vert_pos[verts[bin_start]]=pos
                verts[bin_start],verts[pos]=verts[pos],verts[bin_start]
                bin_boundaries[core[u]]+=1
                core[u] -= 1
    return core

