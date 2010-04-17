"""
Betweenness centrality measures for subsets of nodes.

"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

__all__ = ['betweenness_centrality_subset',
           'edge_betweenness_centrality_subset',
           'betweenness_centrality_source']

import networkx as nx

from networkx.algorithms.centrality.betweenness import\
    _single_source_dijkstra_path_basic as dijkstra
from networkx.algorithms.centrality.betweenness import\
    _single_source_shortest_path_basic as shortest_path


def betweenness_centrality_subset(G,sources,targets,
                                  normalized=False,
                                  weighted_edges=False):
    """Compute betweenness centrality for nodes.

    Betweenness centrality of a node is the fraction of all shortest 
    paths that pass through that node.

    Parameters
    ----------
    G : graph
      A networkx graph 

    sources: list of nodes
      Nodes to use as sources for shortest paths in betweenness

    targets: list of nodes
      Nodes to use as targets for shortest paths in betweenness

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
    The basic algorithm is from Ulrik Brandes [1]_.

    For weighted graphs the edge weights must be greater than zero.
    Zero edge weights can produce an infinite number of equal length 
    paths between pairs of nodes.

    The normalization might seem a little strange but it is the same
    as in betweenness_centrality() and is designed to make
    betweenness_centrality(G) be the same as
    betweenness_centrality_subset(G,sources=G.nodes(),targets=G.nodes()).

    
    References
    ----------
    .. [1]  A Faster Algorithm for Betweenness Centrality.
       Ulrik Brandes, 
       Journal of Mathematical Sociology 25(2):163-177, 2001.
       http://www.inf.uni-konstanz.de/algo/publications/b-fabc-01.pdf
    """
    b=dict.fromkeys(G,0.0) # b[v]=0 for v in G
    for s in sources:
        # single source shortest paths
        if weighted_edges:  # use Dijkstra's algorithm
            S,P,sigma=dijkstra(G,s)
        else:  # use BFS
            S,P,sigma=shortest_path(G,s)
        b=_accumulate_subset(b,S,P,sigma,s,targets)
    b=_rescale(b,normalized=normalized,directed=G.is_directed())
    return b


def edge_betweenness_centrality_subset(G,sources,targets,
                                       normalized=False,
                                       weighted_edges=False):
    """Compute betweenness centrality for edges.

    Betweenness centrality of an edge is the fraction of all shortest 
    paths that pass through that edge.

    Parameters
    ----------
    G : graph
      A networkx graph 

    sources: list of nodes
      Nodes to use as sources for shortest paths in betweenness

    targets: list of nodes
      Nodes to use as targets for shortest paths in betweenness

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
       Dictionary of edges with Betweenness centrality as the value.
        
    See Also
    --------
    betweenness_centrality
    edge_load

    Notes
    -----
    The basic algorithm is from Ulrik Brandes [1]_.

    For weighted graphs the edge weights must be greater than zero.
    Zero edge weights can produce an infinite number of equal length 
    paths between pairs of nodes.

    The normalization might seem a little strange but it is the same
    as in edge_betweenness_centrality() and is designed to make
    edge_betweenness_centrality(G) be the same as
    edge_betweenness_centrality_subset(G,sources=G.nodes(),targets=G.nodes()).

    References
    ----------
    .. [1]  A Faster Algorithm for Betweenness Centrality.
       Ulrik Brandes, 
       Journal of Mathematical Sociology 25(2):163-177, 2001.
       http://www.inf.uni-konstanz.de/algo/publications/b-fabc-01.pdf
    """

    b=dict.fromkeys(G,0.0) # b[v]=0 for v in G
    b.update(dict.fromkeys(G.edges(),0.0)) # b[e] for e in G.edges()
    for s in sources:
        # single source shortest paths
        if weighted_edges:  # use Dijkstra's algorithm
            S,P,sigma=dijkstra(G,s)
        else:  # use BFS
            S,P,sigma=shortest_path(G,s)
        b=_accumulate_edges_subset(b,S,P,sigma,s,targets)
    for n in G: # remove nodes to only return edges 
        del b[n]
    b=_rescale(b,normalized=normalized,directed=G.is_directed())
    return b

# obsolete name
def betweenness_centrality_source(G,normalized=True,
                                  weighted_edges=False,
                                  sources=None):
    import warnings
    warnings.warn("""betweenness_centrality_source() is deprecated, 
use betweenness_centrality_subset()""", 
                  DeprecationWarning)

    if sources is None:
        sources=G.nodes()
    targets=G.nodes()
    return betweenness_centrality_subset(G,sources,targets,
                                       normalized=normalized,
                                       weighted_edges=weighted_edges)


def _accumulate_subset(betweenness,S,P,sigma,s,targets):
    delta=dict.fromkeys(S,0) 
    target_set=set(targets)
    while S:
        w=S.pop()
        for v in P[w]:
            if w in target_set:
                delta[v]+=(sigma[v]/sigma[w])*(1.0+delta[w])
            else:
                delta[v]+=delta[w]/len(P[w])
        if w != s:
            betweenness[w]+=delta[w]
    return betweenness

def _accumulate_edges_subset(betweenness,S,P,sigma,s,targets):
    delta=dict.fromkeys(S,0) 
    target_set=set(targets)
    while S:
        w=S.pop()
        for v in P[w]:
            if w in target_set:
                c=(sigma[v]/sigma[w])*(1.0+delta[w])
            else:
                c=delta[w]/len(P[w])
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
