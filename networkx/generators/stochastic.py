"""Functions for generating stochastic graphs from a given weighted directed
graph.

"""
#    Copyright (C) 2010-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from __future__ import division
import warnings

import networkx as nx
from networkx.utils import not_implemented_for

__author__ = "Aric Hagberg <aric.hagberg@gmail.com>"
__all__ = ['stochastic_graph']


@not_implemented_for('multigraph')
@not_implemented_for('undirected')
def stochastic_graph(G, copy=True, weight='weight'):
    """Returns a right-stochastic representation of the directed graph ``G``.

    A right-stochastic graph is a weighted digraph in which for each node, the
    sum of the weights of all the out-edges of that node is 1. If the graph is
    already weighted (for example, via a ``'weight'`` edge attribute), the
    reweighting takes that into account.

    Parameters
    ----------
    G : directed graph
        A :class:`~networkx.DiGraph` or :class:`~networkx.MultiDiGraph`.

    copy : boolean, optional
      If this is ``True``, then this function returns a new instance of
      :class:`networkx.Digraph`. Otherwise, the original graph is modified
      in-place (and also returned, for convenience).

    weight : edge attribute key (optional, default='weight')
      Edge attribute key used for reading the existing weight and setting the
      new weight.  If no attribute with this key is found for an edge, then the
      edge weight is assumed to be 1. If an edge has a weight, it must be a
      a positive number.

    """
    if copy:
        W = nx.DiGraph(G)
    else:
        # Reference the original graph, don't make a copy.
        W = G
    degree = W.out_degree(weight=weight)
    for (u, v, d) in W.edges(data=True):
        if degree[u] == 0:
            warnings.warn('zero out-degree for node %s' % u)
            d[weight] = 0
        else:
            d[weight] = d.get(weight, 1) / degree[u]
    return W
