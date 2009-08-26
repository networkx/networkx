# -*- coding: utf-8 -*-
"""
Shortest paths, diameter, radius, eccentricity, and related methods.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['eccentricity', 'diameter', 'radius', 'periphery', 'center']

import networkx
from networkx.algorithms.traversal.path \
    import single_source_shortest_path_length

def eccentricity(G, v=None, sp=None, with_labels=False):
    """Return the eccentricity of node v in G (or all nodes if v is None).

    The eccentricity is the maximum of shortest paths to all other nodes. 

    The optional keyword sp must be a dict of dicts of
    shortest_path_length keyed by source and target.
    That is, sp[v][t] is the length from v to t.
       
    If with_labels=True 
    return dict of eccentricities keyed by vertex.
    """
    nodes=[]
    if v is None:                # none, use entire graph 
        nodes=G.nodes() 
    elif isinstance(v, list):  # check for a list
        nodes=v
    else:                      # assume it is a single value
        nodes=[v]
    order=G.order()

    e={}
    for v in nodes:
        if sp is None:
            length=single_source_shortest_path_length(G,v)
        else:
            length=sp[v]
        try:
            assert len(length)==order
        except:
            raise networkx.NetworkXError,\
                  "Graph not connected: infinite path length"
            
        e[v]=max(length.values())

    if with_labels:
        return e
    else:
        if len(e)==1: return e.values()[0] # return single value
        return e.values()

def diameter(G, e=None):
    """Return the diameter of the graph G.

    The diameter is the maximum of all pairs shortest path.
    """
    if e is None:
        e=eccentricity(G,with_labels=True)
    return max(e.values())

def periphery(G, e=None):
    """Return the periphery of the graph G. 

    The periphery is the set of nodes with eccentricity equal to the diameter. 
    """
    if e is None:
        e=eccentricity(G,with_labels=True)
    diameter=max(e.values())
    p=[v for v in e if e[v]==diameter]
    return p


def radius(G, e=None):
    """Return the radius of the  graph G.

    The radius is the minimum of all pairs shortest path.
       """
    if e is None:
        e=eccentricity(G,with_labels=True)
    return min(e.values())

def center(G, e=None):
    """Return the center of graph G.

    The center is the set of nodes with eccentricity equal to radius. 
    """
    if e is None:
        e=eccentricity(G,with_labels=True)
    # order the nodes by path length
    radius=min(e.values())
    p=[v for v in e if e[v]==radius]
    return p

