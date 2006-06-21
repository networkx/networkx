"""
Shortest paths, diameter, radius, eccentricity, and related methods.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
__date__ = ""
__credits__ = """"""
__revision__ = ""
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

def eccentricity(G, v=None, sp=None, with_labels=False):
    """Return the eccentricity of node v in G (or all nodes if v is None).

    The eccentricity is the maximum of shortest paths to all other nodes. 

    The optional keyword sp must be a dict of dicts of
    shortest_path_length keyed by source and target.
    That is, sp[v][t] is the length from v to t.
       
    If with_labels=True 
    return dict of eccentricities keyed by vertex.
    """
    nodes=[]
    if v is None:                # none, use entire graph 
        nodes=G.nodes() 
    elif isinstance(v, list):  # check for a list
        nodes=v
    else:                      # assume it is a single value
        nodes=[v]

    e={}
    for v in nodes:
        if sp is None:
            length=single_source_shortest_path_length(G,v)
        else:
            length=sp[v]
        try:
            assert len(length)==G.number_of_nodes()
        except:
            raise networkx.NetworkXError,\
                  "Graph not connected: infinite path length"
            
        e[v]=max(length.values())

    if with_labels:
        return e
    else:
        if len(e)==1: return e.values()[0] # return single value
        return e.values()

def diameter(G, e=None):
    """Return the diameter of the graph G.

    The diameter is the maximum of all pairs shortest path.
    """
    if e is None:
        e=eccentricity(G,with_labels=True)
    return max(e.values())

def periphery(G, e=None):
    """Return the periphery of the graph G. 

    The periphery is the set of nodes with eccentricity equal to the diameter. 
    """
    if e is None:
        e=eccentricity(G,with_labels=True)
    diameter=max(e.values())
    p=[v for v in e if e[v]==diameter]
    return p


def radius(G, e=None):
    """Return the radius of the  graph G.

    The radius is the minimum of all pairs shortest path.
       """
    if e is None:
        e=eccentricity(G,with_labels=True)
    return min(e.values())

def center(G, e=None):
    """Return the center of graph G.

    The center is the set of nodes with eccentricity equal to radius. 
    """
    if e is None:
        e=eccentricity(G,with_labels=True)
    # order the nodes by path length
    radius=min(e.values())
    p=[v for v in e if e[v]==radius]
    return p


def shortest_path_length(G,source,target):
    """Return the shortest path length in the graph G between
    the source and target.

    G is treated as an unweighted graph.  For weighted graphs
    see dijkstra_path_length.

    """
    return len(bidirectional_shortest_path(G,source,target))-1


def single_source_shortest_path_length(G,source):
    """
    Shortest path length from source to all targets.

    Returns a dictionary of shortest path lengths keyed by source.

    >>> G=path_graph(5)
    >>> paths=single_source_shortest_path_length(G,1)
    >>> paths[4]
    [1, 2, 3, 4]
    >>> print paths
    {0: [1, 0], 1: [1], 2: [1, 2], 3: [1, 2, 3], 4: [1, 2, 3, 4]}

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
        level=level+1
    return seen  # return all path lengths as hash


def all_pairs_shortest_path_length(G):
    """ Return dictionary of shortest path lengths between all nodes in G.

    The dictionary only has keys for reachable node pairs.
    >>> G=path_graph(5)
    >>> paths=all_pairs_shortest_path_length(G)
    >>> print paths[1][4]
    3
    >>> paths[1]
    {0: 1, 1: 0, 2: 1, 3: 2, 4: 3}

    """
    paths={}
    for n in G:
        paths[n]=single_source_shortest_path_length(G,n)
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

       Also known as shortest_path.

    """
    try:
        # call helper to do the real work
        pred,succ,w=_bidirectional_pred_succ(G,source,target)
    except:
        return False  # no path from source to target

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
    if target == source:  return []

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

    Cutoff is a limit on the number of hops traversed.

    See also shortest_path and bidirectional_shortest_path.
    """
    level=0                  # the current level
    nextlevel={source:1}       # list of nodes to check at next level
    paths={source:[source]}  # paths hash  (paths to key from source)
    while nextlevel:
        thislevel=nextlevel
        nextlevel={}
        for v in thislevel:
            for w in G.neighbors(v):
                if not paths.has_key(w): 
                    paths[w]=paths[v]+[w]
                    nextlevel[w]=1
        level=level+1
        if (cutoff is not None and cutoff <= level):
            break
    return paths   


def all_pairs_shortest_path(G):
    """ Return dictionary of shortest paths between all nodes in G.

    The dictionary only has keys for reachable node pairs.

    See also floyd_warshall.

    """
    paths={}
    for n in G:
        paths[n]=single_source_shortest_path(G,n)
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



def bidirectional_dijkstra(graph, source, target):
    """
    Dijkstra's algorithm for shortest paths using bidirectional search. 

    Returns a tuple where the first item stores distance from the 
    source and the second stores the path from the source to the  
    target node.

    Distances are calculated as sums of weighted edges traversed.
    Edges must hold numerical values for XGraph and XDiGraphs.
    The weights are 1 for Graphs and DiGraphs.
    
    This algorithm will perform a lot faster than ordinary dijkstra.
    Ordinary Dijkstra expands nodes in a sphere-like manner from the
    source. The radius of this sphere will eventually be the length 
    of the shortest path. Bidirectional Dijkstra will expand nodes 
    from both the source and the target, making two spheres of half 
    this radius. Volume of the first sphere is pi*r*r while the  
    others are 2*pi*r/2*r/2, making up half the volume. In practice 
    bidirectional Dijkstra is much more than twice as fast as 
    ordinary Dijkstra.
    
    Note: Bidirectional Dijkstra requires both source and target to 
    be specified.

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff erros can cause problems). 

    """
    if source is None or target is None:
        raise NetworkXException(
            "Bidirectional Dijkstra called with no source or target")
    if source == target:
        return (0, [source])
    #Init:   Forward             Backward
    dists =  [{},                {}]# dictionary of final distances
    paths =  [{source:[source]}, {target:[target]}] # dictionary of paths 
    fringe = [[],                []] #heap of (distance, node) tuples for extracting next node to expand
    seen =   [{source:0},        {target:0} ]#dictionary of distances to nodes seen 
    #initialize fringe heap
    heapq.heappush(fringe[0], (0, source)) 
    heapq.heappush(fringe[1], (0, target))
    #neighs for extracting correct neighbor information
    if graph.is_directed():
        neighs = [graph.successors_iter, graph.predecessors_iter]
    else:
        neighs = [graph.neighbors_iter, graph.neighbors_iter]
    #variables to hold shortest discovered path
    #finaldist = 1e30000
    finalpath = []
    # if unweighted graph, set the weights to 1 on edges by
    # introducing a get_edge method
    if not hasattr(graph,"get_edge"): graph.get_edge=lambda x,y:1
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
                vwLength = dists[dir][v] + graph.get_edge(v,w)
            else: #back, must remember to change v,w->w,v
                vwLength = dists[dir][v] + graph.get_edge(w,v)
            
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
    (overflows and roundoff erros can cause problems). 
    
    See also 'bidirectional_dijkstra_path'
    """
    if source==target: return (0, [source])
    dist = {}  # dictionary of final distances
    paths = {source:[source]}  # dictionary of paths
    seen = {source:0} 
    fringe=networkx.queues.Priority(lambda x: seen[x])
    fringe.append(source)
    
    if not G.is_directed():  G.successors=G.neighbors
    # if unweighted graph, set the weights to 1 on edges by
    # introducing a get_edge method
    # NB: for the weighted graphs (XGraph,XDiGraph), the data
    # on the edge (returned by get_edge) must be numerical
    if not hasattr(G,"get_edge"): G.get_edge=lambda x,y:1

    while fringe:
        v=fringe.smallest()
        if v in dist: continue # already searched this node.
        dist[v] = seen[v]
        if v == target: break
            
        for w in G.successors(v):
            vwLength = dist[v] + G.get_edge(v,w)
            if w in dist:
                if vwLength < dist[w]:
                    raise ValueError,\
                          "Contradictory paths found: negative weights?"
            elif w not in seen or vwLength < seen[w]:
                seen[w] = vwLength
                fringe.append(w) # breadth first search
                paths[w] = paths[v]+[w]
    return (dist,paths)


def floyd_warshall(graph):
    """
    The Floyd-Warshall algorithm for all pairs shortest paths.
    
    Returns a tuple (distance,path) containing two matrixes of
    shortest distance and paths as dicts-in-dicts. 
        
    Not intended for large graphs. Time and space grows as O(N^3).
    This algorithm handles negative weights.
    """
    
    dist = {}
    path = {}
    for i in graph:
        dist[i] = {}
        path[i] = {}
        for j in graph:
            if i == j :continue
            if not graph.has_edge(i,j): continue
            if hasattr(graph,"get_edge"): 
                val = graph.get_edge(i,j)
            else:
                val= 1
            path[i][j] = [i, j]
            dist[i][j] = val
    for k in graph:
        for i in graph:
            if i==k : continue
            for j in graph:
                if j == i or j == k: continue
                if j in dist[k] and k in dist[i]: 
                    if j in dist[i]:
                        if dist[i][j] > dist[i][k] + dist[k][j]:
                            dist[i][j] = dist[i][k] + dist[k][j]
                            path[i][j] = path[i][k] + path[k][j][1:]
                    else:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        path[i][j] = path[i][k] + path[k][j][1:]
    return dist, path


def is_directed_acyclic_graph(G):
    """Return True if the graph G is a directed acyclic graph (DAG).

    Otherwise return False.
    
    """
    if topological_sort(G) is None:
        return False
    else:
        return True

def topological_sort(G):
    """
    Return a list of nodes of the digraph G in topological sort order.

    A topological sort is a nonunique permutation of the nodes
    such that an edge from u to v implies that u appears before v in the
    topological sort order.

    If G is not a directed acyclic graph no topological sort exists
    and the Python keyword None is returned.

    This algorithm is based on a description and proof at
    http://www2.toki.or.id/book/AlgDesignManual/book/book2/node70.htm

    See also is_directed_acyclic_graph()
    
    """
    # nonrecursive version

    seen={}
    order_explored=[] # provide order and 
    explored={}       # fast search without more general priorityDictionary
                     
    if not G.is_directed():  G.successors_iter=G.neighbors_iter

    for v in G.nodes_iter():     # process all vertices in G
        if v in explored: continue

        fringe=[v]   # nodes yet to look at
        while fringe:
            w=fringe[-1]  # depth first search
            if w in explored: # already looked down this branch
                fringe.pop()
                continue
            seen[w]=1     # mark as seen
            # Check successors for cycles and for new nodes
            new_nodes=[]
            for n in G.successors_iter(w):  
                if n not in explored:
                    if n in seen: return #CYCLE !!
                    new_nodes.append(n)
            if new_nodes:   # Add new_nodes to fringe
                fringe.extend(new_nodes)
            else:           # No new nodes so w is fully explored
                explored[w]=1
                order_explored.insert(0,w) # reverse order explored
                fringe.pop()    # done considering this node
    return order_explored

def topological_sort_recursive(G):
    """
    Return a list of nodes of the digraph G in topological sort order.

    This is a recursive version of topological sort.
    
    """
    # function for recursive dfs
    def _dfs(G,seen,explored,v):
        seen[v]=1
        for w in G.successors(v):
            if w not in seen: 
                if not _dfs(G,seen,explored,w):
                    return
            elif w in seen and w not in explored:
                # cycle Found--- no topological sort
                return False
        explored.insert(0,v) # inverse order of when explored 
        return v

    seen={}
    explored=[]

    if not G.is_directed():  G.successors=G.neighbors
    
    for v in G.nodes_iter():  # process all nodes
        if v not in explored:
            if not _dfs(G,seen,explored,v): 
                return 
    return explored

def predecessor(G,source,target=False,cutoff=False):
    """ Returns dictionary of predecessors for the path from source to all
    nodes in G.  

    Optional target returns only predecessors between source and target.
    Cutoff is a limit on the number of hops traversed.

    Example for the path graph 0-1-2-3
    
    >>> from networkx import *
    >>> G=path_graph(4)
    >>> print G.nodes()
    [0, 1, 2, 3]
    >>> predecessor(G,0)
    {0: [], 1: [0], 2: [1], 3: [2]}

    """
    level=0                  # the current level
    nextlevel=[source]       # list of nodes to check at next level
    seen={source:level}      # level (number of hops) when seen in BFS
    pred={source:[]}         # predecessor hash
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

    if target:
        if not pred.has_key(target): return ([],-1)  # No predecessor
        return pred[target]
    else:
        return pred

def connected_components(G):
    """
    Return a list of lists of nodes in each connected component of G.

    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 
    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""
    seen={}
    components=[]
    for v in G:      
        if v not in seen:
            c=single_source_shortest_path_length(G,v)
            components.append(c.keys())
            seen.update(c)
    components.sort(lambda x, y: cmp(len(y),len(x)))
    return components            


def number_connected_components(G):
    """Return the number of connected components in G.
    For undirected graphs only. 
    """
    return len(connected_components(G))


def is_connected(G):
    """Return True if G is connected.
    For undirected graphs only. 
    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""
    return len(single_source_shortest_path(G, G.nodes_iter().next()))==len(G)


def connected_component_subgraphs(G):
    """
    Return a list of graphs of each connected component of G.
    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 

    For example, to get the largest connected component:
    >>> H=connected_component_subgraphs(G)[0]

    """
    cc=connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c,inplace=False))
    return graph_list


def node_connected_component(G,n):
    """
    Return a list of nodes of the connected component containing node n.

    For undirected graphs only. 

    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""
    return single_source_shortest_path_length(G,n).keys()

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/paths.txt',package='networkx')
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
    
