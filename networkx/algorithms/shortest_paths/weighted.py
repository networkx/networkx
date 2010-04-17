# -*- coding: utf-8 -*-
"""
Shortest path algorithms for weighed graphs.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['dijkstra_path', 
           'dijkstra_path_length', 
           'bidirectional_dijkstra',
           'single_source_dijkstra_path', 
           'single_source_dijkstra_path_length',
           'all_pairs_dijkstra_path', 
           'all_pairs_dijkstra_path_length',
           'single_source_dijkstra', 
           'dijkstra_predecessor_and_distance']


import heapq
import networkx as nx

def dijkstra_path(G,source,target):
    """Returns the shortest path from source to target in a weighted
    graph G.  

    Parameters
    ----------
    G : NetworkX graph

    source : node 
       Starting node

    target : node 
       Ending node

    Returns
    -------
    path : list
       List of nodes in a shortest path.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print nx.dijkstra_path(G,0,4)
    [0, 1, 2, 3, 4]

    Notes
    ------
    Uses a bidirectional version of Dijkstra's algorithm.
    Edge weight attributes must be numerical.

    See Also
    --------
    bidirectional_dijkstra()
    """
#    (length,path)=bidirectional_dijkstra(G,source,target) # faster, needs test
#     return path
    (length,path)=single_source_dijkstra(G,source)
    try:
        return path[target]
    except KeyError:
        raise nx.NetworkXError, \
              "node %s not reachable from %s"%(source,target)


def dijkstra_path_length(G,source,target):
    """Returns the shortest path length from source to target in a weighted
    graph G.  


    Parameters
    ----------
    G : NetworkX graph, weighted

    source : node label
       starting node for path

    target : node label
       ending node for path 

    Returns
    -------
    length : number
        Shortest path length.
       
    Raises
    ------
    NetworkXError
        If no path exists between source and target.

    Examples
    --------
    >>> G=nx.path_graph(5) # a weighted graph by default
    >>> print nx.dijkstra_path_length(G,0,4)
    4
    
    Notes
    -----
    Edge weight attributes must be numerical.

    See Also
    --------
    bidirectional_dijkstra()

    """

#    (length,path)=bidirectional_dijkstra(G,source,target) # faster, needs test
#    return length
    (length,path)=single_source_dijkstra(G,source)
    try:
        return length[target]
    except KeyError:
        raise nx.NetworkXError, \
              "node %s not reachable from %s"%(source,target)



def bidirectional_dijkstra(G, source, target):
    """Dijkstra's algorithm for shortest paths using bidirectional search. 

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node.

    target : node
       Ending node.

    Returns
    -------
    length : number
        Shortest path length.

    Returns a tuple of two dictionaries keyed by node.
    The first dicdtionary stores distance from the source.
    The second stores the path from the source to that node.

    Raise an exception if no path exists.


    Raises
    ------
    NetworkXError
        If no path exists between source and target.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> length,path=nx.bidirectional_dijkstra(G,0,4)
    >>> print length
    4
    >>> print path
    [0, 1, 2, 3, 4]
    
    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    In practice  bidirectional Dijkstra is much more than twice as fast as 
    ordinary Dijkstra.

    Ordinary Dijkstra expands nodes in a sphere-like manner from the
    source. The radius of this sphere will eventually be the length 
    of the shortest path. Bidirectional Dijkstra will expand nodes 
    from both the source and the target, making two spheres of half 
    this radius. Volume of the first sphere is pi*r*r while the  
    others are 2*pi*r/2*r/2, making up half the volume. 
    
    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems). 

    See Also
    --------
    shortest_path
    shortest_path_length
    """
    if source is None or target is None:
        raise NetworkXException(
            "Bidirectional Dijkstra called with no source or target")
    if source == target: return (0, [source])
    #Init:   Forward             Backward
    dists =  [{},                {}]# dictionary of final distances
    paths =  [{source:[source]}, {target:[target]}] # dictionary of paths 
    fringe = [[],                []] #heap of (distance, node) tuples for extracting next node to expand
    seen =   [{source:0},        {target:0} ]#dictionary of distances to nodes seen 
    #initialize fringe heap
    heapq.heappush(fringe[0], (0, source)) 
    heapq.heappush(fringe[1], (0, target))
    #neighs for extracting correct neighbor information
    if G.is_directed():
        neighs = [G.successors_iter, G.predecessors_iter]
    else:
        neighs = [G.neighbors_iter, G.neighbors_iter]
    #variables to hold shortest discovered path
    #finaldist = 1e30000
    finalpath = []
    dir = 1
    while fringe[0] and fringe[1]:
        # choose direction 
        # dir == 0 is forward direction and dir == 1 is back
        dir = 1-dir
        # extract closest to expand
        (dist, v )= heapq.heappop(fringe[dir]) 
        if v in dists[dir]:
            # Shortest path to v has already been found 
            continue
        # update distance
        dists[dir][v] = dist #equal to seen[dir][v]
        if v in dists[1-dir]:
            # if we have scanned v in both directions we are done 
            # we have now discovered the shortest path
            return (finaldist,finalpath)
        for w in neighs[dir](v):
            if(dir==0): #forward
                vwLength = dists[dir][v] + G[v][w].get('weight',1)
            else: #back, must remember to change v,w->w,v
                vwLength = dists[dir][v] + G[w][v].get('weight',1)
            
            if w in dists[dir]:
                if vwLength < dists[dir][w]:
                    raise ValueError,\
                        "Contradictory paths found: negative weights?"
            elif w not in seen[dir] or vwLength < seen[dir][w]:
                # relaxing        
                seen[dir][w] = vwLength
                heapq.heappush(fringe[dir], (vwLength,w)) 
                paths[dir][w] = paths[dir][v]+[w]
                if w in seen[0] and w in seen[1]:
                    #see if this path is better than than the already
                    #discovered shortest path
                    totaldist = seen[0][w] + seen[1][w] 
                    if finalpath == [] or finaldist > totaldist:
                        finaldist = totaldist
                        revpath = paths[1][w][:]
                        revpath.reverse()
                        finalpath = paths[0][w] + revpath[1:]
    return False


#def dijkstra(G,source,target):
#    return bidirectional_dijkstra(G,source,target)


def single_source_dijkstra_path(G,source):
    """Compute shortest path between source
    and all other reachable nodes for a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path. 

    Returns
    -------
    paths : dictionary
       Dictionary of shortest path lengths keyed by target.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> path=nx.single_source_dijkstra_path(G,0)
    >>> path[4]
    [0, 1, 2, 3, 4]

    Notes
    -----
    Edge weight attributes must be numerical.

    See Also
    --------
    single_source_dijkstra()

    """
    (length,path)=single_source_dijkstra(G,source)
    return path


def single_source_dijkstra_path_length(G,source):
    """Compute shortest path length between source
    and all other reachable nodes for a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    Returns
    -------
    paths : dictionary
       Dictionary of shortest paths keyed by target.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> length=nx.single_source_dijkstra_path_length(G,0)
    >>> length[4]
    4
    >>> print length
    {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

    Notes
    -----
    Edge data must be numerical values for XGraph and XDiGraphs.


    See Also
    --------
    single_source_dijkstra()

    """
    (length,path)=single_source_dijkstra(G,source)
    return length


def single_source_dijkstra(G,source,target=None,cutoff=None ):
    """Compute shortest paths and lengths in a weighted graph G.

    Uses Dijkstra's algorithm for shortest paths. 

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    target : node label, optional
       Ending node for path 

    cutoff : integer or float, optional
       Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    distance,path : dictionaries
       Returns a tuple of two dictionaries keyed by node.
       The first dicdtionary stores distance from the source.
       The second stores the path from the source to that node.


    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> length,path=nx.single_source_dijkstra(G,0)
    >>> print length[4]
    4
    >>> print length
    {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
    >>> path[4]
    [0, 1, 2, 3, 4]

    Notes
    ---------
    Distances are calculated as sums of weighted edges traversed.
    Edges must hold numerical values for Graph and DiGraphs.

    Based on the Python cookbook recipe (119466) at 
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/119466

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems). 
    
    See Also
    --------
    single_source_dijkstra_path()
    single_source_dijkstra_path_length()
    
    """
    if source==target: return (0, [source])
    dist = {}  # dictionary of final distances
    paths = {source:[source]}  # dictionary of paths
    seen = {source:0} 
    fringe=[] # use heapq with (distance,label) tuples 
    heapq.heappush(fringe,(0,source))
    while fringe:
        (d,v)=heapq.heappop(fringe)
        if v in dist: continue # already searched this node.
        dist[v] = d
        if v == target: break
        #for ignore,w,edgedata in G.edges_iter(v,data=True):
        #is about 30% slower than the following
        if G.is_multigraph():
            edata=[]
            for w,keydata in G[v].items():
                edata.append((w,
                             {'weight':min((dd.get('weight',1)
                                            for k,dd in keydata.iteritems()))}))
        else:
            edata=G[v].iteritems()


        for w,edgedata in edata:
            vw_dist = dist[v] + edgedata.get('weight',1)
            if cutoff is not None:
                if vw_dist>cutoff: 
                    continue
            if w in dist:
                if vw_dist < dist[w]:
                    raise ValueError,\
                          "Contradictory paths found: negative weights?"
            elif w not in seen or vw_dist < seen[w]:
                seen[w] = vw_dist
                heapq.heappush(fringe,(vw_dist,w))
                paths[w] = paths[v]+[w]
    return (dist,paths)

def dijkstra_predecessor_and_distance(G,source):
    """Compute shorest path length and predecessors on shortest paths
    in weighted graphs.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    Returns
    -------
    pred,distance : dictionaries
       Returns two dictionaries representing a list of predecessors 
       of a node and the distance to each node.

    Notes
    -----
    The list of predecessors contains more than one element only when
    there are more than one shortest paths to the key node.
    """
    push=heapq.heappush
    pop=heapq.heappop
    dist = {}  # dictionary of final distances
    pred = {source:[]}  # dictionary of predecessors
    seen = {source:0} 
    fringe=[] # use heapq with (distance,label) tuples 
    push(fringe,(0,source))
    while fringe:
        (d,v)=pop(fringe)
        if v in dist: continue # already searched this node.
        dist[v] = d
        if G.is_multigraph():
            edata=(  (w,min(edgedata.values())) 
                     for w,edgedata in G[v].iteritems() )
        else:
            edata=G[v].iteritems()
        for w,edgedata in edata:
            vw_dist = dist[v] + edgedata.get('weight',1)
            if w in dist:
                if vw_dist < dist[w]:
                    raise ValueError,\
                          "Contradictory paths found: negative weights?"
            elif w not in seen or vw_dist < seen[w]:
                seen[w] = vw_dist
                push(fringe,(vw_dist,w))
                pred[w] = [v]
            elif vw_dist==seen[w]:
                pred[w].append(v)
    return (pred,dist)

def all_pairs_dijkstra_path_length(G):
    """ Compute shortest path lengths between all nodes in a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    distance : dictionary
       Dictionary, keyed by source and target, of shortest path lengths.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> length=nx.all_pairs_dijkstra_path_length(G)
    >>> print length[1][4]
    3
    >>> length[1]
    {0: 1, 1: 0, 2: 1, 3: 2, 4: 3}

    Notes
    -----
    The dictionary returned only has keys for reachable node pairs.
    """
    paths={}
    for n in G:
        paths[n]=single_source_dijkstra_path_length(G,n)
    return paths        

def all_pairs_dijkstra_path(G):
    """ Compute shortest paths between all nodes in a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    distance : dictionary
       Dictionary, keyed by source and target, of shortest paths.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> path=nx.all_pairs_dijkstra_path(G)
    >>> print path[0][4]
    [0, 1, 2, 3, 4]

    See Also
    --------
    floyd_warshall()

    """
    paths={}
    for n in G:
        paths[n]=single_source_dijkstra_path(G,n)
    return paths        

