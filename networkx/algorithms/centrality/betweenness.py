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
           'edge_betweenness']

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



