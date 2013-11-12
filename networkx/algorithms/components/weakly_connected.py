# -*- coding: utf-8 -*-
"""Weakly connected components.
"""
#    Copyright (C) 2004-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx as nx
from networkx.utils.decorators import not_implemented_for
__authors__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)'
                         'Christopher Ellison'])
__all__ = ['number_weakly_connected_components',
           'weakly_connected_components',
           'weakly_connected_component_subgraphs',
           'is_weakly_connected'
           ]

@not_implemented_for('undirected')
def weakly_connected_components(G):
    """Generate weakly connected components of G.
    """
    seen={}
    for v in G:
        if v not in seen:
            c=_single_source_shortest_unipath_length(G,v)
            yield list(c.keys())
            seen.update(c)

@not_implemented_for('undirected')
def number_weakly_connected_components(G):
    """Return the number of connected components in G.
    For directed graphs only.
    """
    return len(list(weakly_connected_components(G)))

@not_implemented_for('undirected')
def weakly_connected_component_subgraphs(G, copy=True):
    """Generate weakly connected components as subgraphs.

    Parameters
    ----------
    G : NetworkX Graph
       A directed graph.

    copy : bool
        If copy is True, graph, node, and edge attributes are copied to the
        subgraphs.
    """
    for comp in weakly_connected_components(G):
        if copy:
            yield G.subgraph(comp).copy()
        else:
            yield G.subgraph(comp)

@not_implemented_for('undirected')
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
    if len(G)==0:
        raise nx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(list(weakly_connected_components(G))[0])==len(G)

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
    nextlevel = set([source]) # set of nodes to check at next level
    while nextlevel:
        thislevel=nextlevel  # advance to next level
        nextlevel = set()         # and start a new list (fringe)
        for v in thislevel:
            if v not in seen:
                seen[v]=level # set the level of vertex v
                nextlevel.update(Gsucc[v]) # add successors of v
                nextlevel.update(Gpred[v]) # add predecessors of v
        if (cutoff is not None and cutoff <= level):  break
        level=level+1
    return seen  # return all path lengths as dictionary
