"""
Find and manipulate the k-cores of a graph

"""
__author__ = """Dan Schult(dschult@colgate.edu)\nJason Grout(jason-sage@creativetrax.com)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['find_cores']

def find_cores(G,with_labels=True):
    """Return the core number for each vertex.

    See: arXiv:cs.DS/0310049 by Batagelj and Zaversnik

    If with_labels is True a dict is returned keyed by node to the core number.
    If with_labels is False a list of the core numbers is returned.
    """
    # compute the degrees of each vertex
    degrees=G.degree(with_labels=True)
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
    if with_labels:
        return core
    else:
        return core.values()

