"""
Betweenness centrality measures.

"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

__all__ = ['betweenness_centrality',
           'edge_betweenness_centrality',
           'edge_betweenness'
           ]

import heapq
import networkx as nx

def betweenness_centrality(G,normalized=True,
                           weighted_edges=False,
                           endpoints=False):
    """Compute betweenness centrality for nodes.

    Betweenness centrality of a node is the fraction of all shortest 
    paths that pass through that node.

    Parameters
    ----------
    G : graph
      A networkx graph 

    normalized : bool, optional
      If True the betweenness values are normalized by
      b=b/(n-1)(n-2) where n is the number of nodes in G.
       
    weighted_edges : bool, optional
      Consider the edge weights in determining the shortest paths.
      The edge weights must be greater than zero.
      If False, all edge weights are considered equal.



    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with betweenness centrality as the value.

    See Also
    --------
    edge_betweenness_centrality
    load_centrality

    Notes
    -----
    The algorithm is from Ulrik Brandes [1]_.

    For weighted graphs the edge weights must be greater than zero.
    Zero edge weights can produce an infinite number of equal length 
    paths between pairs of nodes.

    References
    ----------
    .. [1]  A Faster Algorithm for Betweenness Centrality.
       Ulrik Brandes, 
       Journal of Mathematical Sociology 25(2):163-177, 2001.
       http://www.inf.uni-konstanz.de/algo/publications/b-fabc-01.pdf
    """
    betweenness=dict.fromkeys(G,0.0) # b[v]=0 for v in G
    for s in G:
        # single source shortest paths
        if weighted_edges:  # use Dijkstra's algorithm
            S,P,sigma=_single_source_dijkstra_path_basic(G,s)
        else:  # use BFS
            S,P,sigma=_single_source_shortest_path_basic(G,s)
        # accumulation
        if endpoints: 
            betweenness=_accumulate_endpoints(betweenness,S,P,sigma,s)        
        else:
            betweenness=_accumulate_basic(betweenness,S,P,sigma,s)
    # rescaling
    betweenness=_rescale(betweenness,
                         normalized=normalized,
                         directed=G.is_directed())
    return betweenness            


def edge_betweenness_centrality(G,normalized=True,
                                weighted_edges=False):
    """Compute betweenness centrality for edges.

    Betweenness centrality of an edge is the fraction of all shortest 
    paths that pass through that edge.

    Parameters
    ----------
    G : graph
      A networkx graph 

    normalized : bool, optional
      If True the betweenness values are normalized by 
      b=b/(n-1)(n-2) where n is the number of nodes in G.
       
    weighted_edges : bool, optional
      Consider the edge weights in determining the shortest paths.
      The edge weights must be greater than zero.
      If False, all edge weights are considered equal.


    Returns
    -------
    edges : dictionary
       Dictionary of edges with betweenness centrality as the value.
        
    See Also
    --------
    betweenness_centrality
    edge_load

    Notes
    -----
    The algorithm is from Ulrik Brandes [1]_.

    For weighted graphs the edge weights must be greater than zero.
    Zero edge weights can produce an infinite number of equal length 
    paths between pairs of nodes.


    References
    ----------
    .. [1]  A Faster Algorithm for Betweenness Centrality.
       Ulrik Brandes, 
       Journal of Mathematical Sociology 25(2):163-177, 2001.
       http://www.inf.uni-konstanz.de/algo/publications/b-fabc-01.pdf
    """
    betweenness=dict.fromkeys(G,0.0) # b[v]=0 for v in G
    # b[e]=0 for e in G.edges()
    betweenness.update(dict.fromkeys(G.edges(),0.0)) 
    for s in G:
        # single source shortest paths
        if weighted_edges:  # use Dijkstra's algorithm
            S,P,sigma=_single_source_dijkstra_path_basic(G,s)
        else:  # use BFS
            S,P,sigma=_single_source_shortest_path_basic(G,s)
        # accumulation
        betweenness=_accumulate_edges(betweenness,S,P,sigma,s)
    # rescaling
    for n in G: # remove nodes to only return edges 
        del betweenness[n]
    betweenness=_rescale(betweenness,
                         normalized=normalized,
                         directed=G.is_directed())
    return betweenness            

# obsolete name
def edge_betweenness(G,normalized=True,weighted_edges=False):
    import warnings
    warnings.warn("""edge_betweenness() is deprecated, 
use edge_betweenness_centrality()""", 
                      DeprecationWarning)

    return edge_betweenness_centrality(G,
                                       normalized=normalized,
                                       weighted_edges=weighted_edges)


# helpers for betweenness centrality

def _single_source_shortest_path_basic(G,s):
    S=[]
    P={}
    for v in G:
        P[v]=[]
    sigma=dict.fromkeys(G,0.0)    # sigma[v]=0 for v in G
    D={}
    sigma[s]=1.0
    D[s]=0
    Q=[s]
    while Q:   # use BFS to find shortest paths
        v=Q.pop(0)
        S.append(v)
        Dv=D[v]
        sigmav=sigma[v]
        for w in G[v]:
            if w not in D:
                Q.append(w)
                D[w]=Dv+1
            if D[w]==Dv+1:   # this is a shortest path, count paths
                sigma[w] += sigmav
                P[w].append(v) # predecessors 
    return S,P,sigma



def _single_source_dijkstra_path_basic(G,s):
    # modified from Eppstein
    S=[]
    P={}
    for v in G:
        P[v]=[]
    sigma=dict.fromkeys(G,0.0)    # sigma[v]=0 for v in G
    D={}
    sigma[s]=1.0
    push=heapq.heappush
    pop=heapq.heappop
    seen = {s:0} 
    Q=[]   # use Q as heap with (distance,node id) tuples
    push(Q,(0,s,s))
    while Q:   
        (dist,pred,v)=pop(Q)
        if v in D:
            continue # already searched this node.
        sigma[v] += sigma[pred] # count paths
        S.append(v)
        D[v] = dist
        for w,edgedata in G[v].iteritems():
            vw_dist = dist + edgedata.get('weight',1)
            if w not in D and (w not in seen or vw_dist < seen[w]):
                seen[w] = vw_dist
                push(Q,(vw_dist,v,w))
                sigma[w]=0.0
                P[w]=[v]
            elif vw_dist==seen[w]:  # handle equal paths
                sigma[w] += sigma[v]
                P[w].append(v)
    return S,P,sigma

def _accumulate_basic(betweenness,S,P,sigma,s):
    delta=dict.fromkeys(S,0) 
    while S:
        w=S.pop()
        coeff=(1.0+delta[w])/sigma[w]
        for v in P[w]:
            delta[v] += sigma[v]*coeff
        if w != s:
            betweenness[w]+=delta[w]
    return betweenness

def _accumulate_endpoints(betweenness,S,P,sigma,s):
    betweenness[s]+=len(S)-1
    delta=dict.fromkeys(S,0) 
    while S:
        w=S.pop()
        coeff=(1.0+delta[w])/sigma[w]
        for v in P[w]:
            delta[v] += sigma[v]*coeff
        if w != s:
            betweenness[w] += delta[w]+1
    return betweenness

def _accumulate_edges(betweenness,S,P,sigma,s):
    delta=dict.fromkeys(S,0) 
    while S:
        w=S.pop()
        coeff=(1.0+delta[w])/sigma[w]
        for v in P[w]:
            c=sigma[v]*coeff
            if (v,w) not in betweenness:
                betweenness[(w,v)]+=c
            else:
                betweenness[(v,w)]+=c
            delta[v]+=c
        if w != s:
            betweenness[w]+=delta[w]
    return betweenness

def _rescale(betweenness,normalized,directed=False):
    if normalized is True:
        order=len(betweenness)
        if order <=2:
            scale=None  # no normalization b=0 for all nodes
        else:
            scale=1.0/((order-1)*(order-2))
    else: # rescale by 2 for undirected graphs
        if not directed:
            scale=1.0/2.0
        else:
            scale=None
    if scale is not None:
        for v in betweenness:
            betweenness[v] *= scale
    return betweenness

