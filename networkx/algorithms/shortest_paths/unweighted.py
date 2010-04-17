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
           'predecessor', 
           'floyd_warshall']

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
    >>> print length
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
    >>> print length[1][4]
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

    See Also
    --------
    shortest_path

    Notes
    -----
    This algorithm is used by shortest_path(G,source,target).
    """
    # call helper to do the real work
    results=_bidirectional_pred_succ(G,source,target)
    if results is False:
        return False  # no path from source to target
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
    if source is None or target is None:
        raise NetworkXException(\
            "Bidirectional shortest path called without source or target")
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



    return False  # no path found


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
    There may be more than one shortest path between the
    source and target nodes. This function returns only one
    of them.

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
    >>> print path[0][4]
    [0, 1, 2, 3, 4]

    See Also
    --------
    floyd_warshall()

    """
    paths={}
    for n in G:
        paths[n]=single_source_shortest_path(G,n,cutoff=cutoff)
    return paths        


def floyd_warshall_array(G):
    """The Floyd-Warshall algorithm for all pairs shortest paths.
 

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    distance,pred : dictionaries
       A dictionary, keyed by source and target, of shortest path
       distance and predecessors in the shortest path.

    Notes
    ------
    This differs from floyd_warshall only in the types of the return
    values.  Thus, path[i,j] gives the predecessor at j on a path from
    i to j.  A value of None indicates that no path exists.  A
    predecessor of i indicates the beginning of the path.  The
    advantage of this implementation is that, while running time is
    O(n^3), running space is O(n^2).

    This algorithm handles negative weights.
    """

    # A weight that's more than any path weight
    HUGE_VAL = 1
    for u,v,d in G.edges(data=True):
        HUGE_VAL += abs(d)

    dist = {}
    dist_prev = {}
    pred = {}
    pred_prev = {}
    for i in G:
        dist[i] = {}
        dist_prev[i] = {}
        pred[i] = {}
        pred_prev[i] = {}
        inbrs=G[i]
        for j in G:
            dist[i][j] = 0              # arbitrary, just create slot
            pred[i][j] = 0              # arbitrary, just create slot
            if i == j:
                dist_prev[i][j] = 0
                pred_prev[i][j] = -1
            elif j in inbrs:
                val = inbrs[j]
                dist_prev[i][j] = val
                pred_prev[i][j] = i
            else:
                # no edge, distinct vertices
                dist_prev[i][j] = HUGE_VAL
                pred_prev[i][j] = -1    # None, but has to be numerically comparable
    for k in G:
        for i in G:
            for j in G:
                dist[i][j] = min(dist_prev[i][j], dist_prev[i][k] + dist_prev[k][j])
                if dist_prev[i][j] <= dist_prev[i][k] + dist[k][j]:
                    pred[i][j] = pred_prev[i][j]
                else:
                    pred[i][j] = pred_prev[k][j]
        tmp = dist_prev
        dist_prev = dist
        dist = tmp

        tmp = pred_prev
        pred_prev = pred
        pred = tmp
    # The last time through the loop, we exchanged for nothing, so
    # return the prev versions, since they're really the current
    # versions.
    return dist_prev, pred_prev
######################################################################

def floyd_warshall(G):
    """The Floyd-Warshall algorithm for all pairs shortest paths.
    
    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    distance,pred : dictionaries
       A dictionary, keyed by source and target, of shortest path
       distance and predecessors in the shortest path.

    Notes
    -----
    This algorithm is most appropriate for dense graphs.
    The running time is O(n^3), and running space is O(n^2)
    where n is the number of nodes in G.  

    See Also
    --------
    all_pairs_shortest_path()
    all_pairs_shortest_path_length()

    """
    huge=1e30000 # sentinal value
    # dictionary-of-dictionaries representation for dist and pred
    dist={} 
    # initialize path distance dictionary to be the adjacency matrix
    # but with sentinal value "huge" where there is no edge
    # also set the distance to self to 0 (zero diagonal)
    pred={}
    # initialize predecessor dictionary 
    for u in G:
        dist[u]={}
        pred[u]={}
        unbrs=G[u]
        for v in G:
            if v in unbrs:
                dist[u][v]=unbrs[v].get('weight',1)
                pred[u][v]=u
            else:
                dist[u][v]=huge
                pred[u][v]=None 
        dist[u][u]=0  # set 0 distance to self

    for w in G.nodes():
        for u in G.nodes():
            for v in G.nodes():
                if dist[u][v] > dist[u][w] + dist[w][v]:
                    dist[u][v] = dist[u][w] + dist[w][v]
                    pred[u][v] = pred[w][v]
    return dist,pred


def predecessor(G,source,target=None,cutoff=None,return_seen=None):
    """ Returns dictionary of predecessors for the path from source to all
    nodes in G.  


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
    >>> print G.nodes()
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

