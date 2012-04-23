# -*- coding: utf-8 -*-
"""
Shortest path algorithms for unweighted graphs.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2010 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['bidirectional_shortest_path',
           'single_source_shortest_path',
           'single_source_shortest_path_length',
           'all_pairs_shortest_path',
           'all_pairs_shortest_path_length',
           'predecessor']


import networkx as nx

def single_source_shortest_path_length(G,source,cutoff=None):
    """Compute the shortest path lengths from source to all reachable nodes.

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

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> length=nx.single_source_shortest_path_length(G,0)
    >>> length[4]
    4
    >>> print(length)
    {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

    See Also
    --------
    shortest_path_length
    """
    seen={}                  # level (number of hops) when seen in BFS
    level=0                  # the current level
    nextlevel={source:1}  # dict of nodes to check at next level
    while nextlevel:
        thislevel=nextlevel  # advance to next level
        nextlevel={}         # and start a new list (fringe)
        for v in thislevel:
            if v not in seen:
                seen[v]=level # set the level of vertex v
                nextlevel.update(G[v]) # add neighbors of v
        if (cutoff is not None and cutoff <= level):  break
        level=level+1
    return seen  # return all path lengths as dictionary


def all_pairs_shortest_path_length(G,cutoff=None):
    """ Compute the shortest path lengths between all nodes in G.

    Parameters
    ----------
    G : NetworkX graph

    cutoff : integer, optional
        depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    lengths : dictionary
        Dictionary of shortest path lengths keyed by source and target.

    Notes
    -----
    The dictionary returned only has keys for reachable node pairs.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> length=nx.all_pairs_shortest_path_length(G)
    >>> print(length[1][4])
    3
    >>> length[1]
    {0: 1, 1: 0, 2: 1, 3: 2, 4: 3}

    """
    paths={}
    for n in G:
        paths[n]=single_source_shortest_path_length(G,n,cutoff=cutoff)
    return paths




def bidirectional_shortest_path(G,source,target):
    """Return a list of nodes in a shortest path between source and target.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       starting node for path

    target : node label
       ending node for path

    Returns
    -------
    path: list
       List of nodes in a path from source to target.

    Raises
    ------
    NetworkXNoPath
       If no path exists between source and target.

    See Also
    --------
    shortest_path

    Notes
    -----
    This algorithm is used by shortest_path(G,source,target).
    """
    # call helper to do the real work
    results=_bidirectional_pred_succ(G,source,target)
    pred,succ,w=results

    # build path from pred+w+succ
    path=[]
    # from w to target
    while w is not None:
        path.append(w)
        w=succ[w]
    # from source to w
    w=pred[path[0]]
    while w is not None:
        path.insert(0,w)
        w=pred[w]

    return path

def _bidirectional_pred_succ(G, source, target):
    """Bidirectional shortest path helper.

       Returns (pred,succ,w) where
       pred is a dictionary of predecessors from w to the source, and
       succ is a dictionary of successors from w to the target.
    """
    # does BFS from both source and target and meets in the middle
    if target == source:
        return ({target:None},{source:None},source)

    # handle either directed or undirected
    if G.is_directed():
        Gpred=G.predecessors_iter
        Gsucc=G.successors_iter
    else:
        Gpred=G.neighbors_iter
        Gsucc=G.neighbors_iter

    # predecesssor and successors in search
    pred={source:None}
    succ={target:None}

    # initialize fringes, start with forward
    forward_fringe=[source]
    reverse_fringe=[target]

    while forward_fringe and reverse_fringe:
        if len(forward_fringe) <= len(reverse_fringe):
            this_level=forward_fringe
            forward_fringe=[]
            for v in this_level:
                for w in Gsucc(v):
                    if w not in pred:
                        forward_fringe.append(w)
                        pred[w]=v
                    if w in succ:  return pred,succ,w # found path
        else:
            this_level=reverse_fringe
            reverse_fringe=[]
            for v in this_level:
                for w in Gpred(v):
                    if w not in succ:
                        succ[w]=v
                        reverse_fringe.append(w)
                    if w in pred:  return pred,succ,w # found path

    raise nx.NetworkXNoPath("No path between %s and %s." % (source, target))


def single_source_shortest_path(G,source,cutoff=None):
    """Compute shortest path between source
    and all other nodes reachable from source.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    lengths : dictionary
        Dictionary, keyed by target, of shortest paths.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> path=nx.single_source_shortest_path(G,0)
    >>> path[4]
    [0, 1, 2, 3, 4]

    Notes
    -----
    The shortest path is not necessarily unique. So there can be multiple
    paths between the source and each target node, all of which have the
    same 'shortest' length. For each target node, this function returns
    only one of those paths.

    See Also
    --------
    shortest_path
    """
    level=0                  # the current level
    nextlevel={source:1}       # list of nodes to check at next level
    paths={source:[source]}  # paths dictionary  (paths to key from source)
    if cutoff==0:
        return paths
    while nextlevel:
        thislevel=nextlevel
        nextlevel={}
        for v in thislevel:
            for w in G[v]:
                if w not in paths:
                    paths[w]=paths[v]+[w]
                    nextlevel[w]=1
        level=level+1
        if (cutoff is not None and cutoff <= level):  break
    return paths


def all_pairs_shortest_path(G,cutoff=None):
    """ Compute shortest paths between all nodes.

    Parameters
    ----------
    G : NetworkX graph

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    lengths : dictionary
        Dictionary, keyed by source and target, of shortest paths.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> path=nx.all_pairs_shortest_path(G)
    >>> print(path[0][4])
    [0, 1, 2, 3, 4]

    See Also
    --------
    floyd_warshall()

    """
    paths={}
    for n in G:
        paths[n]=single_source_shortest_path(G,n,cutoff=cutoff)
    return paths




def predecessor(G,source,target=None,cutoff=None,return_seen=None):
    """ Returns dictionary of predecessors for the path from source to all nodes in G.


    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    target : node label, optional
       Ending node for path. If provided only predecessors between
       source and target are returned

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.


    Returns
    -------
    pred : dictionary
        Dictionary, keyed by node, of predecessors in the shortest path.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> print(G.nodes())
    [0, 1, 2, 3]
    >>> nx.predecessor(G,0)
    {0: [], 1: [0], 2: [1], 3: [2]}

    """
    level=0                  # the current level
    nextlevel=[source]       # list of nodes to check at next level
    seen={source:level}      # level (number of hops) when seen in BFS
    pred={source:[]}         # predecessor dictionary
    while nextlevel:
        level=level+1
        thislevel=nextlevel
        nextlevel=[]
        for v in thislevel:
            for w in G[v]:
                if w not in seen:
                    pred[w]=[v]
                    seen[w]=level
                    nextlevel.append(w)
                elif (seen[w]==level):# add v to predecessor list if it
                    pred[w].append(v) # is at the correct level
        if (cutoff and cutoff <= level):
            break

    if target is not None:
        if return_seen:
            if not target in pred: return ([],-1)  # No predecessor
            return (pred[target],seen[target])
        else:
            if not target in pred: return []  # No predecessor
            return pred[target]
    else:
        if return_seen:
            return (pred,seen)
        else:
            return pred

