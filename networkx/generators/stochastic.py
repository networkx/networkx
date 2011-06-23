"""Stocastic graph."""
import networkx as nx
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = "Aric Hagberg <hagberg@lanl.gov>"
__all__ = ['stochastic_graph']

def stochastic_graph(G, copy=True, weight='weight'):
    """Return a right-stochastic representation of G.

    A right-stochastic graph is a weighted graph in which all of
    the node (out) neighbors edge weights sum to 1.
    
    Parameters
    -----------
    G : graph
      A NetworkX graph, must have valid edge weights

    copy : boolean, optional
      If True make a copy of the graph, otherwise modify original graph

    weight : key (optional)
      Edge data key used for weight.  If None all weights are set to 1.
    """        
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise Exception("stochastic_graph not implemented for multigraphs")

    if not G.is_directed():
        raise Exception("stochastic_graph not defined for undirected graphs")

    if copy:
        W=nx.DiGraph(G)
    else:
        W=G # reference original graph, no copy

    try:
        degree=W.out_degree(weight=weight)
    except:
        degree=W.out_degree()
#    for n in W:
#        for p in W[n]:
#            weight=G[n][p].get('weight',1.0)
#            W[n][p]['weight']=weight/degree[n]        

    for (u,v,d) in W.edges(data=True):
        d[weight]=d.get(weight,1.0)/degree[u]
    return W
