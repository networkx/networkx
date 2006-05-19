"""
Shortest paths, diameter, radius, eccentricity, and related methods.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-16 14:29:18 -0600 (Thu, 16 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1046 $"
#    Copyright (C) 2004,2005 by 
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
    """Eccentricity of node v (or all nodes if v is None).
       Maximum of shortest paths to all other nodes. 

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
            length=shortest_path_length(G,v)
        else:
            length=sp[v]
        try:
            assert len(length)==G.number_of_nodes()
        except:
            raise networkx.NetworkXError, "Graph not connected: infinite path length"
            
        e[v]=max(length.values())

    if with_labels:
        return e
    else:
        if len(e)==1: return e.values()[0] # return single value
        return e.values()

def diameter(G, e=None):
    """Diameter of graph.
       Maximum of all pairs shortest path.
    """
    if e is None:
        e=eccentricity(G,with_labels=True)
    return max(e.values())

def periphery(G, e=None):
    """Periphery of graph.
       Nodes with eccentricity equal to diameter. 
    """
    if e is None:
        e=eccentricity(G,with_labels=True)
    diameter=max(e.values())
    p=[v for v in e if e[v]==diameter]
    return p


def radius(G, e=None):
    """Radius of graph
       Minimum of all pairs shortest path.
       """
    if e is None:
        e=eccentricity(G,with_labels=True)
    return min(e.values())

def center(G, e=None):
    """Center of graph.
       Nodes with eccentricity equal to radius. 
    """
    if e is None:
        e=eccentricity(G,with_labels=True)
    # order the nodes by path length
    radius=min(e.values())
    p=[v for v in e if e[v]==radius]
    return p


def shortest_path_length(G,source,target=None):
    """
    Shortest path length from source to target.
    If target is None, a dict of shortest path lengths
    from source to keyed node is returned.
    """
    seen={}                  # level (number of hops) when seen in BFS
    level=0                  # the current level
    nextlevel={source:1}  # dict of nodes to check at next level
    while nextlevel:
        thislevel=nextlevel  # advance to next level
        nextlevel={}         # and start a new list (fringe)
        for v in thislevel:
            if not seen.has_key(v): 
                if v==target: # shortcut if target
                    return level
                seen[v]=level # set the level of vertex v
                nbrs=dict.fromkeys(G.neighbors_iter(v),1)
                nextlevel.update(nbrs) # add neighbors of v
        level=level+1

    if target is not None:
        return -1            # return -1 if not reachable
    else:
        return seen  # return all path lengths as hash

def shortest_path(G,source,target=None,cutoff=None):
    """
       Return list of nodes in a shortest path between source
       and target (there might be more than one).

       If no target is specified, returns dict of lists of 
       paths from source to all nodes.
       Cutoff is a limit on the number of hops traversed.
       See also 'bidirectional_shortest_path'
    """
    if target==source: return []  # trivial path
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
                    if w==target:      # Shortcut if target is not None
                        return paths[w] 
                    nextlevel[w]=1
        level=level+1
        if (cutoff is not None and cutoff <= level):
            break

    if target is None:
        return paths    # return them all
    else:
        return False     # return False if not reachable

def bidirectional_shortest_path(G, source, target):
    """
       Return list of nodes in a shortest path between source and target.

       This bidirectional version of shortest_path is much faster.
       Note that it requires target node to be specified.
    """
    if source == None or target == None:
        raise NetworkXException(\
            "Bidirectional shortest path called without source or target")
    if source == target:
        return [source]
    paths = [{source:None},{target:None}]
    Q =     [[],[]] 
    if G.is_directed():
        graph_nbrs=[G.successors, G.predecessors]
    else:
        graph_nbrs=[G.neighbors_iter]*2
    Q[0].append(source)
    Q[1].append(target)
    dir = 1
    count = 0
    while Q[0] and Q[1]:
        count += 1
        #chose direction
        dir = 1-dir
        #make local variables for this direction (for speed)
        thisQ = Q[dir]
        nextQ = []
        pathforw = paths[dir]
        pathback = paths[1-dir]
        neighs = graph_nbrs[dir]
        #visit all nodes on this level
        for u in thisQ:
            #go through their neighbors
            for v in neighs(u):
                if not v in pathforw:
                    #update path if found
                    paths[dir][v] = u 
                    if v in pathback:
                        #We have found a shortest path. 
                        #build path using traceback
                        path = []
                        temp = v
                        while temp != None:
                            path.insert(0, temp)
                            temp = paths[0][temp]
                        temp = paths[1][v]
                        while temp != None:
                            path.append(temp)
                            temp = paths[1][temp]
                        return path
                    nextQ.append(v)
        #update que for next level
        Q[dir] = nextQ
    return False
    
def bidirectional_shortest_path2(G,source,target):
    """
       Return list of nodes in a shortest path between source and target.

       This bidirectional version of shortest_path is much faster than
       shortest_path in most cases.
       Note that it requires target node to be specified.
    """
    try:
        # call helper to do the real work
        pred,succ,w=bidirectional_pred_succ(G,source,target)
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

def bidirectional_pred_succ(G, source, target):
    """
       Bidirectional shortest path helper.  Returns (pred,succ,w) where
       pred is a dictionary of predecessors from w to the source, and
       succ is a dictionary of successors from w to the target.
    """
    # does BFS from both source and target and meets in the middle
    if source == None or target == None:
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

    

def dijkstra_path(G,source,target=None):
    """
    Returns the shortest path for a weighted graph using
    Dijkstra's algorithm.

    The path is computed from the source to an optional target.
    If a target is specified the path is returned as a list of nodes.
    If the target is not specified a dictionary of path lists keyed
    by target node is returned.
    
    Edge data must be numerical values for XGraph and XDiGraphs.
    The weights are assigned to be 1 for Graphs and DiGraphs.

    See also 'dijkstra' for more information about the algorithm.

    """
    (length,path)=dijkstra(G,source,target=target)

    if target is not None:
        try:
            return path[target]
        except KeyError:
            raise networkx.NetworkXError, \
                  "node %s not reachable from %s"%(source,target)
    return path

def dijkstra_path_length(G,source,target=None):
    """
    Returns the shortest path length for a weighted graph using
    Dijkstra's algorithm .

    The path length is computed from the source to an optional target.
    If a target is specified the length is returned as an integer.
    If the target is not specified a dictionary of path lengths keyed
    by target node is returned.
    
    Edge data must be numerical values for XGraph and XDiGraphs.
    The weights are assigned to be 1 for Graphs and DiGraphs.

    See also "dijkstra" for more information about the algorithm.

    """
    (length,path)=dijkstra(G,source,target=target)


    if target is not None:
        try:
            return length[target]
        except KeyError:
            raise networkx.NetworkXError, \
                  "node %s not reachable from %s"%(source,target)

    return length


def dijkstra(G,source,target=None):
    """
    Dijkstra's algorithm for shortest paths in a weighted graph.

    See

    dijkstra_path() - shortest path list of nodes 
    dijkstra_path_length() - shortest path length


    Returns a tuple of two dictionaries keyed by node.
    The first stores distance from the source.
    The second stores the path from the source to that node.

    Distances are calculated as sums of weighted edges traversed.
    Edges must hold numerical values for XGraph and XDiGraphs.
    The weights are 1 for Graphs and DiGraphs.

    Optional target argument stops the search when target is found.

    Based on python cookbook recipe (119466) at 
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/119466

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers (
    overflows and roundoff erros can cause problems). 
    
    See also 'dijkstra_bi'
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

def dijkstra_bi(graph, source, target):
    """
    Dijkstra's algorithm for shortest paths using bidirectional 
    search. 

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
    are negative or are floating point numbers (
    overflows and roundoff erros can cause problems). 

    """
    if source == None or target == None:
        raise NetworkXException("Bidirectional Dijkstra called with no source or target")
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
    finaldist = 1e30000
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
                    if finaldist > totaldist:
                        finaldist = totaldist
                        revpath = paths[1][w][:]
                        revpath.reverse()
                        finalpath = paths[0][w] + revpath[1:]
    return False

def floyd_warshall(graph):
    """
    The Floyd-Warshall algorithm for all pair shortest paths.
    
    Returns a tuple distance, path containing two matrixes of shortest distance
    and paths as dicts-in-dicts. 
        
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
                dij = 1e3000
                dik = 1e3000
                dkj = 1e3000
                if j in dist[i]: dij = dist[i][j]
                if k in dist[i]: dik = dist[i][k]
                if j in dist[k]: dkj = dist[k][j]
                if dij > dik + dkj:
                    dist[i][j] = dik + dkj
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
    Return a list of nodes of the graph G in topological sort order.

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
    Return a list of nodes of the graph G in topological sort order.

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
    """
    seen={}
    components=[]
    for v in G:      
        if v not in seen:
            c=shortest_path_length(G,v)
            components.append(c.keys())
            seen.update(c)
    components.sort(lambda x, y: cmp(len(y),len(x)))
    return components            

def number_connected_components(G):
    """Return the number of connected components in G."""
    return len(connected_components(G))

def is_connected(G):
    """Return True if G is connected."""
    return len(shortest_path(G, G.nodes_iter().next()))==len(G)

def connected_component_subgraphs(G):
    """
    Return a list of graphs of each connected component of G.
    The list is ordered from largest connected component to smallest.

    For example, to only get the largest connected component:

    >>> from networkx import *
    >>> G=erdos_renyi_graph(100,0.02)    
    >>> H=connected_component_subgraphs(G)[0]

    """
    cc=connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c,inplace=False))
    return graph_list


def node_connected_component(G,n):
    """
    Return the connected component to which node n belongs as a list of nodes.
    """
    return shortest_path_length(G,n).keys()

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
    
