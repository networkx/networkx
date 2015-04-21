# -*- coding: utf-8 -*-
"""
Graph diameter, radius, eccentricity and other properties.
"""
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Dan Schult(dschult@colgate.edu)'])
#    Copyright (C) 2004-2015 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['eccentricity', 'diameter', 'radius', 'periphery', 'center']

import networkx

def eccentricity(G, v=None, sp=None):
    """Return the eccentricity of nodes in G.

    The eccentricity of a node v is the maximum distance from v to
    all other nodes in G.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    v : node, optional
       Return value of specified node       

    sp : dict of dicts, optional       
       All pairs shortest path lengths as a dictionary of dictionaries

    Returns
    -------
    ecc : dictionary
       A dictionary of eccentricity values keyed by node.
    """
#    nodes=
#    nodes=[]
#    if v is None:                # none, use entire graph 
#        nodes=G.nodes()
#    elif v in G:               # is v a single node
#        nodes=[v]
#    else:                      # assume v is a container of nodes
#        nodes=v
    order=G.order()

    e={}
    for n in G.nbunch_iter(v):
        if sp is None:
            length=networkx.single_source_shortest_path_length(G,n)
            L = len(length)
        else:
            try:
                length=sp[n]
                L = len(length)
            except TypeError:
                raise networkx.NetworkXError('Format of "sp" is invalid.')
        if L != order:
            msg = "Graph not connected: infinite path length"
            raise networkx.NetworkXError(msg)
            
        e[n]=max(length.values())

    if v in G:
        return e[v]  # return single value
    else:
        return e


def diameter(G, e=None):
    """Return the diameter of the graph G.

    The diameter is the maximum eccentricity.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    d : integer
       Diameter of graph

    See Also
    --------
    eccentricity
    """
    if e is None:
        e=eccentricity(G)
    return max(e.values())

def periphery(G, e=None):
    """Return the periphery of the graph G. 

    The periphery is the set of nodes with eccentricity equal to the diameter. 

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    p : list
       List of nodes in periphery
    """
    if e is None:
        e=eccentricity(G)
    diameter=max(e.values())
    p=[v for v in e if e[v]==diameter]
    return p


def radius(G, e=None):
    """Return the radius of the graph G.

    The radius is the minimum eccentricity.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    r : integer
       Radius of graph
    """
    if e is None:
        e=eccentricity(G)
    return min(e.values())

def center(G, e=None):
    """Return the center of the graph G. 

    The center is the set of nodes with eccentricity equal to radius. 

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    c : list
       List of nodes in center
    """
    if e is None:
        e=eccentricity(G)
    # order the nodes by path length
    radius=min(e.values())
    p=[v for v in e if e[v]==radius]
    return p

