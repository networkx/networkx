# -*- coding: utf-8 -*-
"""
Weakly connected components.
"""
__authors__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)'
                         'Christopher Ellison'])
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['number_weakly_connected_components', 
           'weakly_connected_components',
           'weakly_connected_component_subgraphs',
           'is_weakly_connected' 
           ]

import networkx as nx

def weakly_connected_components(G):
    """Return weakly connected components of G.
    """
    if not G.is_directed():
        raise nx.NetworkXError("""Not allowed for undirected graph G. 
              Use connected_components() """)
    seen={}
    components=[]
    for v in G:
        if v not in seen:
            c=_single_source_shortest_unipath_length(G,v)
            components.append(list(c.keys()))
            seen.update(c)
    components.sort(key=len,reverse=True)
    return components


def number_weakly_connected_components(G):
    """Return the number of connected components in G.
    For directed graphs only. 
    """
    return len(weakly_connected_components(G))

def weakly_connected_component_subgraphs(G):
    """Return weakly connected components as subgraphs.
    """
    wcc=weakly_connected_components(G)
    graph_list=[]
    for c in wcc:
        graph_list.append(G.subgraph(c))
    return graph_list

def is_weakly_connected(G):
    """Test directed graph for weak connectivity.

    Parameters
    ----------
    G : NetworkX Graph
       A directed graph.

    Returns
    -------
    connected : bool
      True if the graph is weakly connected, False otherwise.

    See Also
    --------
    strongly_connected_components

    Notes
    -----
    For directed graphs only. 
    """
    if not G.is_directed():
        raise nx.NetworkXError("""Not allowed for undirected graph G.
              See is_connected() for connectivity test.""")

    if len(G)==0:
        raise nx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(weakly_connected_components(G)[0])==len(G)

def _single_source_shortest_unipath_length(G,source,cutoff=None):
    """Compute the shortest path lengths from source to all reachable nodes.

    The direction of the edge between nodes is ignored.
    
    For directed graphs only.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    lengths : dictionary
        Dictionary of shortest path lengths keyed by target.
    """
    # namespace speedups
    Gsucc = G.succ
    Gpred = G.pred

    seen={}                  # level (number of hops) when seen in BFS
    level=0                  # the current level
    nextlevel={source:1}  # dict of nodes to check at next level
    while nextlevel:
        thislevel=nextlevel  # advance to next level
        nextlevel={}         # and start a new list (fringe)
        for v in thislevel:
            if v not in seen:
                seen[v]=level # set the level of vertex v
                nextlevel.update(Gsucc[v]) # add successors of v
                nextlevel.update(Gpred[v]) # add predecessors of v
        if (cutoff is not None and cutoff <= level):  break
        level=level+1
    return seen  # return all path lengths as dictionary
