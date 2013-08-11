"""Stocastic graph."""
#    Copyright (C) 2010-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = "Aric Hagberg <aric.hagberg@gmail.com>"
__all__ = ['stochastic_graph']

def stochastic_graph(G, copy=True, weight='weight'):
    """Return a right-stochastic representation of G.

    A right-stochastic graph is a weighted digraph in which all of
    the node (out) neighbors edge weights sum to 1.

    Parameters
    -----------
    G : graph
      A NetworkX graph

    copy : boolean, optional
      If True make a copy of the graph, otherwise modify the original graph

    weight : edge attribute key (optional, default='weight')
      Edge data key used for weight.  If no attribute is found for an edge
      the edge weight is set to 1.
    """
    if type(G) == nx.MultiGraph or type(G) == nx.MultiDiGraph:
        raise nx.NetworkXError('stochastic_graph not implemented '
                               'for multigraphs')

    if not G.is_directed():
        raise nx.NetworkXError('stochastic_graph not implemented '
                               'for undirected graphs')

    if copy:
        W = nx.DiGraph(G)
    else:
        W = G # reference original graph, no copy

    degree = W.out_degree(weight=weight)
    for (u,v,d) in W.edges(data=True):
        d[weight] = float(d.get(weight,1.0))/degree[u]
    return W
