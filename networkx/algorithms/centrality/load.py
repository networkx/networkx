"""
Load centrality. 

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

__all__ = ['load_centrality',
           'edge_load']

import networkx as nx

def newman_betweenness_centrality(G,v=None,cutoff=None,
                           normalized=True,
                           weight=None):
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
       
    weight : None or string, optional  
      If None, edge weights are ignored.
      Otherwise holds the name of the edge attribute used as weight.

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
            ubetween = _node_betweenness(G, source, cutoff, False, weight)
            betweenness += ubetween[v] if v in ubetween else 0
        if normalized:
            order = G.order()
            if order <= 2:
                return betweenness # no normalization b=0 for all nodes
            betweenness *= 1.0 / ((order-1) * (order-2))
        return betweenness
    else:
        betweenness = {}.fromkeys(G,0.0)
        for source in betweenness:
            ubetween = _node_betweenness(G, source, cutoff, False, weight)
            for vk in ubetween:
                betweenness[vk] += ubetween[vk]
        if normalized:
            order = G.order()
            if order <= 2:
                return betweenness # no normalization b=0 for all nodes
            scale = 1.0 / ((order-1) * (order-2))
            for v in betweenness:
                betweenness[v] *= scale
        return betweenness  # all nodes

def _node_betweenness(G,source,cutoff=False,normalized=True,weight=None):
    """Node betweenness helper:
    see betweenness_centrality for what you probably want.

    This actually computes "load" and not betweenness.
    See https://networkx.lanl.gov/ticket/103

    This calculates the load of each node for paths from a single source.
    (The fraction of number of shortests paths from source that go
    through each node.)

    To get the load for a node you need to do all-pairs shortest paths.

    If weight is not None then use Dijkstra for finding shortest paths.
    In this case a cutoff is not implemented and so is ignored.

    """

    # get the predecessor and path length data
    if weight is None:
        (pred,length)=nx.predecessor(G,source,cutoff=cutoff,return_seen=True)
    else:
        (pred,length)=nx.dijkstra_predecessor_and_distance(G,source,weight=weight)

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
    (pred,length)=nx.predecessor(G,source,cutoff=cutoff,return_seen=True)
    # order the nodes by path length
    onodes = [ nn for dd,nn in sorted( (dist,n) for n,dist in length.items() )]
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


