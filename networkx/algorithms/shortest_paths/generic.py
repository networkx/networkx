# -*- coding: utf-8 -*-
"""
Shortest paths.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['shortest_path', 
           'shortest_path_length',
           'average_shortest_path_length']


import networkx
#use deque only if networkx requires python 2.4
#from collections import deque 
import heapq


def shortest_path(G,source=None,target=None,weighted=False):
    """Compute the shortest path.

    There may be more than one shortest path.  This returns only one.
    
    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Starting node for path

    target : node, optional 
       Ending node for path 

    weighted : bool, optional
       If True consider weighted edges when finding shortest path.

    Returns
    -------

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print nx.shortest_path(G,0,4)
    [0, 1, 2, 3, 4]

    """
    if source is None:
        if target is None:
            if weighted:
                paths=networkx.all_pairs_dijkstra_path(G)
            else:
                paths=networkx.all_pairs_shortest_path(G)
        else:
            raise networkx.NetworkXError("Target given but no source specified.")
    else: # source specified
        if target is None:
            if weighted:
                paths=networkx.single_source_dijkstra_path(G,source)
            else:
                paths=networkx.single_source_shortest_path(G,source)
        else:
            # shortest source-target path
            if weighted:
                paths=networkx.dijkstra_shortest_path(G,source,target)
            else:
                paths=networkx.bidirectional_shortest_path(G,source,target)

    return paths


def shortest_path_length(G,source=None,target=None,weighted=False):
    """Compute the shortest path length.

    Raise an exception if no path exists.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Starting node for path

    target : node, optional 
       Ending node for path 

    weighted : bool, optional
       If True consider weighted edges when finding shortest path.

    Returns
    -------
   
    Raises
    ------
    NetworkXError
        If no path exists between source and target.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print nx.shortest_path_length(G,0,4)
    4
    
    Notes
    -----

    """
    if source is None:
        if target is None:
            if weighted:
                paths=networkx.all_pairs_dijkstra_path_length(G)
            else:
                paths=networkx.all_pairs_shortest_path_length(G)
        else:
            raise networkx.NetworkXError("Target given but no source specified.")
    else: # source specified
        if target is None:
            if weighted:
                paths=networkx.single_source_dijkstra_path_length(G,source)
            else:
                paths=networkx.single_source_shortest_path_length(G,source)
        else:
            # shortest source-target path
            if weighted:
                paths=networkx.dijkstra_shortest_path_length(G,source,target)
            else:
                p=networkx.bidirectional_shortest_path(G,source,target)
                if p is False:
                    raise networkx.NetworkXError("no path from %s to %s"%(source,target))
                paths=len(p)-1
    return paths

        

def average_shortest_path_length(G,weighted=False):
    """ Return the average shortest path length.

    Parameters
    ----------
    G : NetworkX graph

    weighted : bool, optional, default=False 
       If True use edge weights on path. 

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> print nx.average_shortest_path_length(G)
    1.25

    """
    if weighted:
        path_length=networkx.single_source_dijkstra_path_length
    else:
        path_length=networkx.single_source_shortest_path_length
    avg=0.0
    for n in G:
        l=path_length(G,n).values()
        avg+=float(sum(l))/len(l)
    return avg/len(G)
        

