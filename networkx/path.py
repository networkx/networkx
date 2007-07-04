# -*- coding: utf-8 -*-
"""
Shortest path algorithms.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
___revision__ = ""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import networkx
#use deque only if networkx requires python 2.4
#from collections import deque 
import heapq


def shortest_path_length(G,source,target):
    """Return the shortest path length in the graph G between
    the source and target.  Raise an exception if no path exists.

    G is treated as an unweighted graph.  For weighted graphs
    see dijkstra_path_length.
    """
    path=bidirectional_shortest_path(G,source,target)
    if path is False:
        raise networkx.NetworkXError,\
              "no path from %s to %s"%(source,target)
    return len(path)-1

def single_source_shortest_path_length(G,source,cutoff=None):
    """
    Shortest path length from source to all reachable nodes.

    Returns a dictionary of shortest path lengths keyed by target.

    >>> G=path_graph(5)
    >>> length=single_source_shortest_path_length(G,1)
    >>> length[4]
    3
    >>> print length
    {0: 1, 1: 0, 2: 1, 3: 2, 4: 3}

    cutoff is optional integer depth to stop the search - only
    paths of length <= cutoff are returned.

    """
    seen={}                  # level (number of hops) when seen in BFS
    level=0                  # the current level
    nextlevel={source:1}  # dict of nodes to check at next level
    while nextlevel:
        thislevel=nextlevel  # advance to next level
        nextlevel={}         # and start a new list (fringe)
        for v in thislevel:
            if not seen.has_key(v): 
                seen[v]=level # set the level of vertex v
                nbrs=dict.fromkeys(G.neighbors_iter(v),1)
                nextlevel.update(nbrs) # add neighbors of v
        if (cutoff is not None and cutoff <= level):  break
        level=level+1
    return seen  # return all path lengths as dictionary


def all_pairs_shortest_path_length(G,cutoff=None):
    """ Return dictionary of shortest path lengths between all nodes in G.

    The dictionary only has keys for reachable node pairs.
    >>> G=path_graph(5)
    >>> length=all_pairs_shortest_path_length(G)
    >>> print length[1][4]
    3
    >>> length[1]
    {0: 1, 1: 0, 2: 1, 3: 2, 4: 3}


    cutoff is optional integer depth to stop the search - only
    paths of length <= cutoff are returned.

    """
    paths={}
    for n in G:
        paths[n]=single_source_shortest_path_length(G,n,cutoff=cutoff)
    return paths        
        
def shortest_path(G,source,target):
    """Return a list of nodes in G for a shortest path between source
    and target.

    There may be more than one shortest path.  This returns only one.
    
    """
    return bidirectional_shortest_path(G,source,target)


def bidirectional_shortest_path(G,source,target):
    """
       Return list of nodes in a shortest path between source and target.
       Return False if no path exists.

       Also known as shortest_path.

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
    """
       Bidirectional shortest path helper.

       Returns (pred,succ,w) where
       pred is a dictionary of predecessors from w to the source, and
       succ is a dictionary of successors from w to the target.
    """
    # does BFS from both source and target and meets in the middle
    if source is None or target is None:
        raise NetworkXException(\
            "Bidirectional shortest path called without source or target")
    if target == source:  return ({1:None},{1:None},1)

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
    """
    Return list of nodes in a shortest path between source
    and all other nodes in G reachable from source.

    There may be more than one shortest path between the
    source and target nodes - this routine returns only one.

    cutoff is optional integer depth to stop the search - only
    paths of length <= cutoff are returned.

    See also shortest_path and bidirectional_shortest_path.
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
            for w in G.neighbors(v):
                if not paths.has_key(w): 
                    paths[w]=paths[v]+[w]
                    nextlevel[w]=1
        level=level+1
        if (cutoff is not None and cutoff <= level):  break
    return paths   


def all_pairs_shortest_path(G,cutoff=None):
    """ Return dictionary of shortest paths between all nodes in G.

    The dictionary only has keys for reachable node pairs.

    cutoff is optional integer depth to stop the search - only
    paths of length <= cutoff are returned.

    See also floyd_warshall.

    """
    paths={}
    for n in G:
        paths[n]=single_source_shortest_path(G,n,cutoff=cutoff)
    return paths        


def dijkstra_path(G,source,target):
    """
    Returns the shortest path from source to target in a weighted
    graph G.  Uses a bidirectional version of Dijkstra's algorithm.

    Edge data must be numerical values for XGraph and XDiGraphs.
    The weights are assigned to be 1 for Graphs and DiGraphs.

    See also bidirectional_dijkstra for more information about the algorithm.
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
    graph G.  Uses a bidirectional version of Dijkstra's algorithm.

    Edge data must be numerical values for XGraph and XDiGraphs.
    The weights are assigned to be 1 for Graphs and DiGraphs.

    See also bidirectional_dijkstra for more information about the algorithm.

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
    """
    Dijkstra's algorithm for shortest paths using bidirectional search. 

    Returns a two-tuple (d,p) where d is the distance and p
    is the path from the source to the target.

    Distances are calculated as sums of weighted edges traversed.

    Edges must hold numerical values for XGraph and XDiGraphs.
    The weights are set to 1 for Graphs and DiGraphs.
    
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
    # if unweighted graph, set the weights to 1 on edges by
    # introducing a get_edge method
    if not hasattr(G,"get_edge"): G.get_edge=lambda x,y:1
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
                vwLength = dists[dir][v] + G.get_edge(v,w)
            else: #back, must remember to change v,w->w,v
                vwLength = dists[dir][v] + G.get_edge(w,v)
            
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
    """
    Returns the shortest paths from source to all other reachable
    nodes in a weighted graph G.  Uses Dijkstra's algorithm.

    Returns a dictionary of shortest path lengths keyed by source.
    
    Edge data must be numerical values for XGraph and XDiGraphs.
    The weights are assigned to be 1 for Graphs and DiGraphs.

    See also single_source_dijkstra for more information about the algorithm.

    """
    (length,path)=single_source_dijkstra(G,source)
    return path


def single_source_dijkstra_path_length(G,source):
    """
    Returns the shortest path lengths from source to all other
    reachable nodes in a weighted graph G.  Uses Dijkstra's algorithm.

    Returns a dictionary of shortest path lengths keyed by source.
    
    Edge data must be numerical values for XGraph and XDiGraphs.
    The weights are assigned to be 1 for Graphs and DiGraphs.

    See also single_source_dijkstra for more information about the algorithm.

    """
    (length,path)=single_source_dijkstra(G,source)
    return length


def single_source_dijkstra(G,source,target=None):
    """
    Dijkstra's algorithm for shortest paths in a weighted graph G.

    Use:

    single_source_dijkstra_path() - shortest path list of nodes 

    single_source_dijkstra_path_length() - shortest path length

    Returns a tuple of two dictionaries keyed by node.
    The first stores distance from the source.
    The second stores the path from the source to that node.

    Distances are calculated as sums of weighted edges traversed.
    Edges must hold numerical values for XGraph and XDiGraphs.
    The weights are 1 for Graphs and DiGraphs.

    Optional target argument stops the search when target is found.

    Based on the Python cookbook recipe (119466) at 
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/119466

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems). 
    
    See also 'bidirectional_dijkstra_path'
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
        dist[v] = seen[v]
        if v == target: break
        for w in G.neighbors(v):
            vw_dist = dist[v] + G.get_edge(v,w)
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
    """
    Same algorithm as for single_source_dijsktra, but returns two
    dicts representing a list of predecessors of a node and the
    distance to each node respectively.  The list of predecessors
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
        dist[v] = seen[v]
        for w in G.neighbors(v):
            vw_dist = dist[v] + G.get_edge(v,w)
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

def floyd_warshall_array(graph):
    """
    The Floyd-Warshall algorithm for all pairs shortest paths.
    
    Returns a tuple (distance,path) containing two arrays of shortest
    distance and paths as a predecessor matrix.

    This differs from
    floyd_warshall only in the types of the return values.  Thus,
    path[i,j] gives the predecessor at j on a path from i to j.  A
    value of None indicates that no path exists.  A predecessor of i
    indicates the beginning of the path.  The advantage of this
    implementation is that, while running time is O(n^3), running
    space is O(n^2).

    This algorithm handles negative weights.
    """

    # A weight that's more than any path weight
    HUGE_VAL = 1
    for e in graph.edges():
        HUGE_VAL += abs(graph.get_edge(e[0],e[1]))

    dist = {}
    dist_prev = {}
    pred = {}
    pred_prev = {}
    for i in graph:
        dist[i] = {}
        dist_prev[i] = {}
        pred[i] = {}
        pred_prev[i] = {}
        for j in graph:
            dist[i][j] = 0              # arbitrary, just create slot
            pred[i][j] = 0              # arbitrary, just create slot
            if i == j:
                dist_prev[i][j] = 0
                pred_prev[i][j] = -1
            elif graph.has_edge(i,j):
                val = graph.get_edge(i,j)
                dist_prev[i][j] = val
                pred_prev[i][j] = i
            else:
                # no edge, distinct vertices
                dist_prev[i][j] = HUGE_VAL
                pred_prev[i][j] = -1    # None, but has to be numerically comparable
    for k in graph:
        for i in graph:
            for j in graph:
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
    """
    The Floyd-Warshall algorithm for all pairs shortest paths.
    
    Returns a tuple (distance,path) containing two dictionaries of shortest
    distance and predecessor paths.

    This algorithm is most appropriate for dense graphs.
    The running time is O(n^3), and running space is O(n^2)
    where n is the number of nodes in G.  

    For sparse graphs, see

    all_pairs_shortest_path
    all_pairs_shortest_path_length

    which are based on Dijkstra's algorithm.

    """
    # dictionary-of-dictionaries representation for dist and pred
    dist={} 
    # initialize path distance dictionary to be the adjacency matrix
    # but with sentinal value "huge" where there is no edge
    # also set the distance to self to 0 (zero diagonal)
    pred={}
    # initialize predecessor dictionary 
    for u in G.nodes():
        dist[u]={}
        pred[u]={}
        for v in G.nodes():
            if G.has_edge(u,v):
                dist[u][v]=G.get_edge(u,v)
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

    Optional target returns only predecessors between source and target.
    Cutoff is a limit on the number of hops traversed.

    Example for the path graph 0-1-2-3
    
    >>> G=path_graph(4)
    >>> print G.nodes()
    [0, 1, 2, 3]
    >>> predecessor(G,0)
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
            for w in G.neighbors(v):
                if (not seen.has_key(w)): 
                    pred[w]=[v]
                    seen[w]=level
                    nextlevel.append(w)
                elif (seen[w]==level):# add v to predecessor list if it 
                    pred[w].append(v) # is at the correct level
        if (cutoff and cutoff <= level):
            break

    if target is not None:
        if return_seen:
            if not pred.has_key(target): return ([],-1)  # No predecessor
            return (pred[target],seen[target])
        else:
            if not pred.has_key(target): return []  # No predecessor
            return pred[target]
    else:
        if return_seen:
            return (pred,seen)
        else:
            return pred



def bfs(G,source):
    """
    Traverse the graph G with breadth-first-search from source.
    Return list of nodes connected to source in BFS order.
    
    Primarily intended as an example.
    See also shortest_path and bidirectional_shortest_path.
    """

    nlist=[source] # list of nodes in a BFS order
    seen={} # nodes seen
    queue=[source] # FIFO queue
    seen[source]=True 
    while queue:
        v=queue.pop()
        for w in G.neighbors(v):
            if w not in seen:
                seen[w]=True
                queue.append(w)
                nlist.append(w)
    return nlist


def dfs(G,source):
    """
    Traverse the graph G with depth-first-search from source.
    Return list of nodes connected to source in DFS order.
    
    Primarily intended as an example.

    """
    nlist=[] # list of nodes in a DFS order
    seen={} # nodes seen
    queue=[source]  # use as LIFO queue
    seen[source]=True 
    while queue:
        v=queue.pop(0)  # this is expensive, should use a faster FIFO queue
        nlist.append(v)
        for w in G.neighbors(v):
            if w not in seen:
                seen[w]=True
                queue.append(w)
    return nlist



def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/shortest_path.txt',package='networkx')
    return suite


if __name__ == "__main__":
    import os
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    
