# -*- coding: utf-8 -*-
"""
Shortest path algorithms.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['average_shortest_path_length',
           'shortest_path', 'shortest_path_length',
           'bidirectional_shortest_path',
           'single_source_shortest_path', 
           'single_source_shortest_path_length',
           'all_pairs_shortest_path', 'all_pairs_shortest_path_length',
           'dijkstra_path', 'dijkstra_path_length', 'bidirectional_dijkstra',
           'single_source_dijkstra_path', 'single_source_dijkstra_path_length',
           'single_source_dijkstra',
           'dijkstra_predecessor_and_distance', 'predecessor', 'floyd_warshall']


import networkx
#use deque only if networkx requires python 2.4
#from collections import deque 
import heapq


def shortest_path_length(G,source,target):
    """Return the shortest path length between the source and target.  

    Raise an exception if no path exists.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    target : node label
       Ending node for path 

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print nx.shortest_path_length(G,0,4)
    4
    
    Notes
    -----
    G is treated as an unweighted graph.  For weighted graphs
    see dijkstra_path_length.
    """
    path=bidirectional_shortest_path(G,source,target)
    if path is False:
        raise networkx.NetworkXError,\
              "no path from %s to %s"%(source,target)
    return len(path)-1

def single_source_shortest_path_length(G,source,cutoff=None):
    """Return the shortest path length from source to all reachable nodes.

    Returns a dictionary of shortest path lengths keyed by target.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    cutoff : integer, optional
        Depth to stop the search - only
        paths of length <= cutoff are returned.


    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> length=nx.single_source_shortest_path_length(G,0)
    >>> length[4]
    4
    >>> print length
    {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

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
    """ Return dictionary of shortest path lengths between all nodes in G.

    The dictionary only has keys for reachable node pairs.

    Parameters
    ----------
    G : NetworkX graph

    cutoff : integer, optional
        depth to stop the search - only
        paths of length <= cutoff are returned.

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
        

def average_shortest_path_length(G,weighted=False):
    """ Return the average shortest path length.

    Parameters
    ----------
    G : NetworkX graph

    weighted : bool, optional, default=False 
       If true use edge weights on path.  If False,
       use 1 as the edge distance.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> print nx.average_shortest_path_length(G)
    1.25

    """
    if weighted:
        path_length=single_source_dijkstra_path_length
    else:
        path_length=single_source_shortest_path_length
    avg=0.0
    for n in G:
        l=path_length(G,n).values()
        avg+=float(sum(l))/len(l)
    return avg/len(G)
        

def shortest_path(G,source,target):
    """Return a list of nodes in a shortest path between source and target.

    There may be more than one shortest path.  This returns only one.
    
    Parameters
    ----------
    G : NetworkX graph

    source : node label
       starting node for path

    target : node label
       ending node for path 

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print nx.shortest_path(G,0,4)
    [0, 1, 2, 3, 4]

    """
    return bidirectional_shortest_path(G,source,target)


def bidirectional_shortest_path(G,source,target):
    """Return a list of nodes in a shortest path between source and target.

    Also known as shortest_path()

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       starting node for path

    target : node label
       ending node for path 
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
        this_level=forward_fringe
        forward_fringe=[]
        for v in this_level:
            for w in Gsucc(v):
                if w not in pred:
                    forward_fringe.append(w)
                    pred[w]=v
                if w in succ:  return pred,succ,w # found path
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
    """Return list of nodes in a shortest path between source
    and all other nodes reachable from source.

    There may be more than one shortest path between the
    source and target nodes - this routine returns only one.

    Returns a dictionary of shortest path lengths keyed by target.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       starting node for path

    cutoff : integer, optional
        depth to stop the search - only
        paths of length <= cutoff are returned.

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> path=nx.single_source_shortest_path(G,0)
    >>> path[4]
    [0, 1, 2, 3, 4]

    See Also
    --------
    shortest_path()
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
    """ Return shortest paths between all nodes.

    Returns a dictionary with keys for all reachable node pairs.

    Parameters
    ----------
    G : NetworkX graph

    cutoff : integer, optional
        depth to stop the search - only
        paths of length <= cutoff are returned.

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


def dijkstra_path(G,source,target):
    """Returns the shortest path from source to target in a weighted
    graph G.  

    Uses a bidirectional version of Dijkstra's algorithm.
    
    Parameters
    ----------
    G : NetworkX graph

    source : node label
       starting node for path

    target : node label
       ending node for path 

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> print nx.dijkstra_path(G,0,4)
    [0, 1, 2, 3, 4]


    Notes
    ------
    Edge data must be numerical values for Graph and DiGraphs.

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
        raise networkx.NetworkXError, \
              "node %s not reachable from %s"%(source,target)


def dijkstra_path_length(G,source,target):
    """
    Returns the shortest path length from source to target in a weighted
    graph G.  

    Raise an exception if no path exists.

    Parameters
    ----------
    G : NetworkX graph, weighted

    source : node label
       starting node for path

    target : node label
       ending node for path 

    Examples
    --------
    >>> G=nx.path_graph(5) # a weighted graph by default
    >>> print nx.dijkstra_path_length(G,0,4)
    4
    
    Notes
    -----
    Edge data must be numerical values for Graph and DiGraphs.

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
        raise networkx.NetworkXError, \
              "node %s not reachable from %s"%(source,target)



def bidirectional_dijkstra(G, source, target):
    """Dijkstra's algorithm for shortest paths using bidirectional search. 

    Returns a tuple of two dictionaries keyed by node.
    The first dicdtionary stores distance from the source.
    The second stores the path from the source to that node.

    Raise an exception if no path exists.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    target : node label
       Ending node for path 

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
    Distances are calculated as sums of weighted edges traversed.

    Edges must hold numerical values for Graph and DiGraphs.

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
    """Return list of nodes in a shortest path between source
    and all other nodes reachable from source for a weighted graph.

    Returns a dictionary of shortest path lengths keyed by target.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       starting node for path

    Examples
    --------
    >>> G=nx.path_graph(5)
    >>> path=nx.single_source_dijkstra_path(G,0)
    >>> path[4]
    [0, 1, 2, 3, 4]


    Notes
    -----
    Edge data must be numerical values for Graph and DiGraphs.

    See Also
    --------
    single_source_dijkstra()

    """
    (length,path)=single_source_dijkstra(G,source)
    return path


def single_source_dijkstra_path_length(G,source):
    """
    Returns the shortest path lengths from source to all other
    reachable nodes in a weighted graph G.  

    Returns a dictionary of shortest path lengths keyed by target.
    Uses Dijkstra's algorithm.


    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

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
    """Returns shortest paths and lengths in a weighted graph G.

    Uses Dijkstra's algorithm for shortest paths. 
    Returns a tuple of two dictionaries keyed by node.
    The first dicdtionary stores distance from the source.
    The second stores the path from the source to that node.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    target : node label, optional
       Ending node for path 

    cutoff : integer or float, optional
        Depth to stop the search - only
        paths of length <= cutoff are returned.


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
    """Returns two dictionaries representing a list of predecessors 
    of a node and the distance to each node respectively.  

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    Notes
    -----
    The list of predecessors
    contains more than one element only when there are more than one
    shortest paths to the key node.

    This routine is intended for use with the betweenness centrality
    algorithms in centrality.py.
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

######################################################################
### Jeff A mods.  Kept very local for now.

def floyd_warshall_array(G):
    """The Floyd-Warshall algorithm for all pairs shortest paths.
 
    Returns a tuple (distance,path) containing two arrays of shortest
    distance and paths as a predecessor matrix.

    Parameters
    ----------
    G : NetworkX graph

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

def floyd_warshall(G,huge=1e30000):
    """The Floyd-Warshall algorithm for all pairs shortest paths.
    
    Returns a tuple (distance,path) containing two dictionaries of shortest
    distance and predecessor paths.

    Parameters
    ----------
    G : NetworkX graph

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
        Depth to stop the search - only
        paths of length <= cutoff are returned.


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

