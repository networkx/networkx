"""
Betweenness centrality and similar centrality measures.

"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Sasha Gutfraind (ag362@cornell.edu)'])

__all__ = ['betweenness_centrality',
           'betweenness_centrality_source',
           'load_centrality',
           'newman_betweenness_centrality',
           'brandes_betweenness_centrality',
           'edge_betweenness',
           'edge_load']

import heapq
import networkx


def brandes_betweenness_centrality(G,normalized=True,weighted_edges=False):
    """Compute betweenness centrality for nodes.

    Betweenness centrality of a node is the fraction of all shortest 
    paths that pass through that node.

    Parameters
    ----------
    G : graph
      A networkx graph 

    normalized : bool, optional
      If True the betweenness values are normalized by b=b/(n-1)(n-2) where
      n is the number of nodes in G.
       
    weighted_edges : bool, optional
      Consider the edge weights in determining the shortest paths.
      If False, all edge weights are considered equal.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with betweeness centrality as the value.

        
    See Also
    --------
    load_centrality()

    Notes
    -----
    The algorithm is from Ulrik Brandes,
    A Faster Algorithm for Betweenness Centrality.
    Journal of Mathematical Sociology 25(2):163-177, 2001.
    http://www.inf.uni-konstanz.de/algo/publications/b-fabc-01.pdf

"""
    betweenness=dict.fromkeys(G,0.0) # b[v]=0 for v in G
    for s in G:
        S=[]
        P={}
        for v in G:
            P[v]=[]
        sigma=dict.fromkeys(G,0)    # sigma[v]=0 for v in G
        D={}
        sigma[s]=1
        if not weighted_edges:  # use BFS
            D[s]=0
            Q=[s]
            while Q:   # use BFS to find shortest paths
                v=Q.pop(0)
                S.append(v)
                for w in G[v]:
#                for w in G.adj[v]: # speed hack, exposes internals
                    if w not in D:
                        Q.append(w)
                        D[w]=D[v]+1
                    if D[w]==D[v]+1:   # this is a shortest path, count paths
                        sigma[w]=sigma[w]+sigma[v]
                        P[w].append(v) # predecessors 
        else:  # use Dijkstra's algorithm for shortest paths,
               # modified from Eppstein
            push=heapq.heappush
            pop=heapq.heappop
            seen = {s:0} 
            Q=[]   # use Q as heap with (distance,node id) tuples
            push(Q,(0,s,s))
            while Q:   
                (dist,pred,v)=pop(Q)
                if v in D:
                    continue # already searched this node.
                sigma[v]=sigma[v]+sigma[pred] # count paths
                S.append(v)
                D[v] = dist
                for w,edgedata in G[v].iteritems():
                    vw_dist = D[v] + edgedata.get('weight',1)
                    if w not in D and (w not in seen or vw_dist < seen[w]):
                        seen[w] = vw_dist
                        push(Q,(vw_dist,v,w))
                        sigma[w]=0
                        P[w]=[v]
                    elif vw_dist==seen[w]:  # handle equal paths
                        sigma[w]=sigma[w]+sigma[v]
                        P[w].append(v)


        delta=dict.fromkeys(G,0) 
        while S:
            w=S.pop()
            for v in P[w]:
                delta[v]=delta[v]+\
                          (float(sigma[v])/float(sigma[w]))*(1.0+delta[w])
            if w != s:
                betweenness[w]=betweenness[w]+delta[w]
                    
    # normalize
    if normalized:
        order=len(betweenness)
        if order <=2:
            return betweenness # no normalization b=0 for all nodes
        scale=1.0/((order-1)*(order-2))
        for v in betweenness:
            betweenness[v] *= scale

    return betweenness            

betweenness_centrality=brandes_betweenness_centrality


def newman_betweenness_centrality(G,v=None,cutoff=None,
                           normalized=True,
                           weighted_edges=False):
    """Compute load centrality for nodes.

    The load centrality of a node is the fraction of all shortest 
    paths that pass through that node.

    Parameters
    ----------
    G : graph
      A networkx graph 

    normalized : bool, optional
      If True the betweenness values are normalized by b=b/(n-1)(n-2) where
      n is the number of nodes in G.
       
    weighted_edges : bool, optional
      Consider the edge weights in determining the shortest paths.
      If False, all edge weights are considered equal.

    cutoff : bool, optional
      If specified, only consider paths of length <= cutoff.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with centrality as the value.

        
    See Also
    --------
    betweenness_centrality() 

    Notes
    -----
    Load centrality is slightly different than betweenness.
    For this load algorithm see the reference
    Scientific collaboration networks: II.
    Shortest paths, weighted networks, and centrality,
    M. E. J. Newman, Phys. Rev. E 64, 016132 (2001).

    """
    if v is not None:   # only one node
        betweenness=0.0
        for source in G: 
            ubetween=_node_betweenness(G,source,
                                       cutoff=cutoff,
                                       normalized=normalized,
                                       weighted_edges=weighted_edges)
            betweenness+=ubetween[v]
        return betweenness
    else:
        betweenness={}.fromkeys(G,0.0) 
        for source in betweenness: 
            ubetween=_node_betweenness(G,source,
                                       cutoff=cutoff,
                                       normalized=False,
                                       weighted_edges=weighted_edges)
            for vk in ubetween:
                betweenness[vk]+=ubetween[vk]
        if normalized:
            order=len(betweenness)
            if order <=2:
                return betweenness # no normalization b=0 for all nodes
            scale=1.0/((order-1)*(order-2))
            for v in betweenness:
                betweenness[v] *= scale
        return betweenness  # all nodes

def _node_betweenness(G,source,cutoff=False,normalized=True,weighted_edges=False):
    """Node betweenness helper:
    see betweenness_centrality for what you probably want.

    This actually computes "load" and not betweenness.
    See https://networkx.lanl.gov/ticket/103

    This calculates the load of each node for paths from a single source.
    (The fraction of number of shortests paths from source that go
    through each node.)

    To get the load for a node you need to do all-pairs shortest paths.

    If weighted_edges is True then use Dijkstra for finding shortest paths.
    In this case a cutoff is not implemented and so is ignored.

    """

    # get the predecessor and path length data
    if weighted_edges:
        (pred,length)=networkx.dijkstra_predecessor_and_distance(G,source) 
    else:
        (pred,length)=networkx.predecessor(G,source,cutoff=cutoff,return_seen=True) 

    # order the nodes by path length
    onodes = [ (l,vert) for (vert,l) in length.items() ]
    onodes.sort()
    onodes[:] = [vert for (l,vert) in onodes if l>0]
    
    # intialize betweenness
    between={}.fromkeys(length,1.0)

    while onodes:           
        v=onodes.pop()
        if v in pred:
            num_paths=len(pred[v])   # Discount betweenness if more than 
            for x in pred[v]:        # one shortest path.
                if x==source:   # stop if hit source because all remaining v  
                    break       #  also have pred[v]==[source]
                between[x]+=between[v]/float(num_paths)
    #  remove source
    for v in between:
        between[v]-=1
    # rescale to be between 0 and 1                
    if normalized:
        l=len(between)
        if l > 2:
            scale=1.0/float((l-1)*(l-2)) # 1/the number of possible paths
            for v in between:
                between[v] *= scale
    return between


load_centrality=newman_betweenness_centrality

def betweenness_centrality_source(G,normalized=True,
                                  weighted_edges=False,
                                  sources=None):
    """Compute betweenness centrality for a subgraph.

    Enchanced version of the method in centrality module that allows
    specifying a list of sources (subgraph).


    Parameters
    ----------
    G : graph
      A networkx graph 

    normalized : bool, optional
      If True the betweenness values are normalized by b=b/(n-1)(n-2) where
      n is the number of nodes in G.
       
    weighted_edges : bool, optional
      Consider the edge weights in determining the shortest paths.
      If False, all edge weights are considered equal.

    sources : node list 
      A list of nodes to consider as sources for shortest paths.
      

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with betweeness centrality as the value.


    Notes
    -----
    See Sec. 4 in 
    Ulrik Brandes,
    A Faster Algorithm for Betweenness Centrality.
    Journal of Mathematical Sociology 25(2):163-177, 2001.
    http://www.inf.uni-konstanz.de/algo/publications/b-fabc-01.pdf

    This algorithm does not count the endpoints, i.e.
    a path from s to t does not contribute to the betweenness of s and t.
    """
    if sources == None:
        sources = G   # only used to iterate over nodes.

    betweenness=dict.fromkeys(G,0.0)
    for s in sources:
        S,P,D,sigma = _brandes_betweenness_helper(G,s,weighted_edges)

        delta=dict.fromkeys(G,0) # unnormalized betweenness
        while S:
            w=S.pop()
            for v in P[w]:
                delta[v] += (1.0+delta[w])*sigma[v]/sigma[w] # 1.0 converts all to float
            if w == s:
                continue
            betweenness[w] = betweenness[w] + delta[w]
                   
    # normalize to size of entire graph
    if normalized and G.number_of_edges() > 1:
        order=len(betweenness)
        scale=1.0/((order-1)*(order-2))
        for v in betweenness:
            betweenness[v] *= scale

    return betweenness


def edge_betweenness(G,normalized=True,weighted_edges=False,sources=None):
    """Compute betweenness centrality for edges.

    Parameters
    ----------
    G : graph
      A networkx graph 

    normalized : bool, optional
      If True the betweenness values are normalized by b=b/(n-1)(n-2) where
      n is the number of nodes in G.
       
    weighted_edges : bool, optional
      Consider the edge weights in determining the shortest paths.
      If False, all edge weights are considered equal.

    sources : node list 
      A list of nodes to consider as sources for shortest paths.
      

    Returns
    -------
    nodes : dictionary
       Dictionary of edges with betweeness centrality as the value.
    """
    if sources is None:
        sources = G # only used to iterate over nodes

    betweenness=dict.fromkeys(G.edges(),0.0)
    if G.is_directed():
        for s in sources:
            S, P, D, sigma =_brandes_betweenness_helper(G,s,weighted_edges)
            delta=dict.fromkeys(G,0.0)
            while S:
                w=S.pop()
                for v in P[w]:
                    edgeFlow = (1.0+delta[w])*sigma[v]/sigma[w] # 1.0 converts all to float
                    edge = (v,w)
                    delta[v]          += edgeFlow
                    betweenness[edge] += edgeFlow
    else:
        for s in sources:
            S, P, D, sigma =_brandes_betweenness_helper(G,s,weighted_edges)
            delta=dict.fromkeys(G,0.0)
            while S:
                w=S.pop()
                for v in P[w]:
                    edgeFlow = (1.0+delta[w])*sigma[v]/sigma[w] # 1.0 converts all to float
                    edge = (v,w)
                    if edge not in betweenness:
                        edge = (w,v)
                    delta[v]          += edgeFlow
                    betweenness[edge] += edgeFlow

    size=len(betweenness)                
    if normalized and size > 1:
        # normalize to size of entire graph (beware of disconnected components)
        scale=1.0/((size-1)*(size-2))
        for edge in betweenness:
            betweenness[edge] *= scale

    return betweenness


def _brandes_betweenness_helper(G,root,weighted_edges):
    """
    Helper for betweenness centrality and edge betweenness centrality.

    Runs single-source shortest path from root node.

    weighted_edges:: consider edge weights 

    Finds::

    S=[] list of nodes reached during traversal
    P={} predecessors, keyed by child node
    D={} distances
    sigma={} indexed by node, is the number of paths to root
    going through the node
    """
    S=[]
    P={}
    for v in G:
        P[v]=[]
    sigma=dict.fromkeys(G,0.0)
    D={}
    sigma[root]=1

    if not weighted_edges:  # use BFS
        D[root]=0
        Q=[root]
        while Q:   # use BFS to find shortest paths
            v=Q.pop(0)
            S.append(v)
            for w in G[v]: #  for w in G.adj[v]: # speed hack, exposes internals
                if w not in D:
                    Q.append(w)
                    D[w]=D[v]+1
                if D[w]==D[v]+1:   # this is a shortest path, count paths
                    sigma[w]=sigma[w]+sigma[v]
                    P[w].append(v) # predecessors
    else:  # use Dijkstra's algorithm for shortest paths,
           # modified from Eppstein
        push=heapq.heappush
        pop=heapq.heappop
        seen = {root:0}
        Q=[]   # use Q as heap with (distance,node id) tuples
        push(Q,(0,root,root))
        while Q:   
            (dist,pred,v)=pop(Q)
            if v in D:
                continue # already searched this node.
            sigma[v]=sigma[v]+sigma[pred] # count paths
            S.append(v)
            D[v] = dist
            for w,edgedata in G[v].iteritems(): 
                vw_dist = D[v] + edgedata.get('weight',1)
                if w not in D and (w not in seen or vw_dist < seen[w]):
                    seen[w] = vw_dist
                    sigma[w] = 0
                    push(Q,(vw_dist,v,w))
                    P[w]=[v]
                elif vw_dist==seen[w]:  # handle equal paths
                    sigma[w]=sigma[w]+sigma[v]
                    P[w].append(v)
    return S, P, D, sigma


def edge_load(G,nodes=None,cutoff=False):
    """Compute edge load.

    WARNING:

    This module is for demonstration and testing purposes.

    """
    betweenness={} 
    if not nodes:         # find betweenness for every node  in graph
        nodes=G.nodes()   # that probably is what you want...
    for source in nodes:
        ubetween=_edge_betweenness(G,source,nodes,cutoff=cutoff)
        for v in ubetween.keys():
            b=betweenness.setdefault(v,0)  # get or set default
            betweenness[v]=ubetween[v]+b    # cumulative total
    return betweenness

def _edge_betweenness(G,source,nodes,cutoff=False):
    """
    Edge betweenness helper.
    """
    between={}
    # get the predecessor data
    #(pred,length)=_fast_predecessor(G,source,cutoff=cutoff) 
    (pred,length)=networkx.predecessor(G,source,cutoff=cutoff,return_seen=True) 
    # order the nodes by path length
    onodes = [ nn for dd,nn in sorted( (dist,n) for n,dist in length.iteritems() )]
    # intialize betweenness, doesn't account for any edge weights
    for u,v in G.edges(nodes):
        between[(u,v)]=1.0
        between[(v,u)]=1.0

    while onodes:           # work through all paths
        v=onodes.pop()
        if v in pred:
            num_paths=len(pred[v])   # Discount betweenness if more than 
            for w in pred[v]:        # one shortest path.
                if w in pred:
                    num_paths=len(pred[w])  # Discount betweenness, mult path  
                    for x in pred[w]: 
                        between[(w,x)]+=between[(v,w)]/num_paths
                        between[(x,w)]+=between[(w,v)]/num_paths
    return between


