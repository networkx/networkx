# -*- coding: utf-8 -*-
"""
Compute the shortest paths and path lengths between nodes in the graph.
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

import networkx as nx

def shortest_path(G,source=None,target=None,weighted=False):
    """Compute shortest paths in the graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Starting node for path.  
       If not specified compute shortest paths for all connected node pairs.

    target : node, optional 
       Ending node for path.  
       If not specified compute shortest paths for every node reachable 
       from the source.

    weighted : bool, optional
       If True consider weighted edges when finding shortest path.

    Returns
    -------
    path: list or dictionary
        If the source and target are both specified return a single list
        of nodes in a shortest path.
        If only the source is specified return a dictionary keyed by
        targets with a list of nodes in a shortest path.
        If neither the source or target is specified return a dictionary 
        of dictionaries with path[source][target]=[list of nodes in path].

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print nx.shortest_path(G,source=0,target=4)
    [0, 1, 2, 3, 4]
    >>> p=nx.shortest_path(G,source=0) # target not specified
    >>> p[4]
    [0, 1, 2, 3, 4]
    >>> p=nx.shortest_path(G) # source,target not specified
    >>> p[0][4]
    [0, 1, 2, 3, 4]

    Notes
    -----
    There may be more than one shortest path between a source and target.
    This returns only one of them.

    If weighted=True and the graph has no 'weight' edge attribute
    the value 1 will be used.
    """
    if source is None:
        if target is None:
            if weighted:
                paths=nx.all_pairs_dijkstra_path(G)
            else:
                paths=nx.all_pairs_shortest_path(G)
        else:
            raise nx.NetworkXError(\
                "Target given but no source specified.")
    else: # source specified
        if target is None:
            if weighted:
                paths=nx.single_source_dijkstra_path(G,source)
            else:
                paths=nx.single_source_shortest_path(G,source)
        else:
            # shortest source-target path
            if weighted:
                paths=nx.dijkstra_path(G,source,target)
            else:
                paths=nx.bidirectional_shortest_path(G,source,target)

    return paths


def shortest_path_length(G,source=None,target=None,weighted=False):
    """Compute shortest path lengths in the graph.
    
    This function can compute the single source shortest path
    lengths by specifying only the source or all pairs shortest
    path lengths by specifying neither the source or target.

    Parameters
    ----------
    G : NetworkX graph

    source : node, optional
       Starting node for path.  
       If not specified compute shortest pats lenghts for all 
       connected node pairs.

    target : node, optional 
       Ending node for path.  
       If not specified compute shortest path lenghts for every 
       node reachable from the source.

    weighted : bool, optional
       If True consider weighted edges when finding shortest path length.

    Returns
    -------
    length : number, or container of numbers
        If the source and target are both specified return a
        single number for the shortest path.
        If only the source is specified return a dictionary keyed by
        targets with a the shortest path as keys.
        If neither the source or target is specified return a dictionary 
        of dictionaries with length[source][target]=value.

    Raises
    ------
    NetworkXError
        If no path exists between source and target.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print nx.shortest_path_length(G,source=0,target=4)
    4
    >>> p=nx.shortest_path_length(G,source=0) # target not specified
    >>> p[4]
    4
    >>> p=nx.shortest_path_length(G) # source,target not specified
    >>> p[0][4]
    4

    Notes
    -----
    If weighted=True and the graph has no 'weight' edge attribute
    the value 1 will be used.

    """
    if source is None:
        if target is None:
            if weighted:
                paths=nx.all_pairs_dijkstra_path_length(G)
            else:
                paths=nx.all_pairs_shortest_path_length(G)
        else:
            raise nx.NetworkXError(\
                "Target given but no source specified.")
    else: # source specified
        if target is None:
            if weighted:
                paths=nx.single_source_dijkstra_path_length(G,source)
            else:
                paths=nx.single_source_shortest_path_length(G,source)
        else:
            # shortest source-target path
            if weighted:
                paths=nx.dijkstra_path_length(G,source,target)
            else:
                p=nx.bidirectional_shortest_path(G,source,target)
                if p is False:
                    raise nx.NetworkXError(\
                        "No path from %s to %s."%(source,target))
                paths=len(p)-1
    return paths

        

def average_shortest_path_length(G,weighted=False):
    """ Return the average shortest path length.

    The average shortest path length is the sum of path lengths d(u,v)
    between all pairs of nodes (assuming the length is zero if v is
    not reachable from v) normalized by n*(n-1) where n is the number
    of nodes in G.

    Parameters
    ----------
    G : NetworkX graph

    weighted : bool, optional, default=False 
       If True use edge weights on path. 

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print nx.average_shortest_path_length(G)
    2.0

    Notes
    -----
    If weighted=True and the graph has no 'weight' edge attribute
    the value 1 will be used.

    """
    if weighted:
        path_length=nx.single_source_dijkstra_path_length
    else:
        path_length=nx.single_source_shortest_path_length
    avg=0.0
    for n in G:
        l=path_length(G,n).values()
        avg+=float(sum(l))/len(l)
    return avg/(len(G)-1)
        

