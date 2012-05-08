# -*- coding: utf-8 -*-
"""
**********************
Minimum Dominating Set
**********************


A dominating set for a graph G = (V, E) is a subset D of V such that every
vertex not in D is joined to at least one member of D by some edge. The
domination number gamma(G) is the number of vertices in a smallest dominating
set for G. Given a graph G = (V, E) find a minimum weight dominating set V'.

http://en.wikipedia.org/wiki/Dominating_set

This is reducible to the minimum set dom_set problem.
"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   All rights reserved.
#   BSD license.
import networkx as nx
__all__ = ["min_weighted_dominating_set",
           "min_edge_dominating_set"]
__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""

def min_weighted_dominating_set(graph, weight=None):
    """Return minimum weight dominating set.

    Parameters
    ----------
    graph : NetworkX graph
      Undirected graph

    weight : None or string, optional (default = None)
        If None, every edge has weight/distance/weight 1. If a string, use this
        edge attribute as the edge weight. Any edge attribute not present
        defaults to 1.

    Returns
    -------
    min_weight_dominating_set : set
      Returns a set of vertices whose weight sum is no more than 1 + log w(V)

    References
    ----------
    .. [1] Vazirani, Vijay Approximation Algorithms (2001)
    """
    if not graph:
        raise ValueError("Expected non-empty NetworkX graph!")

    # min cover = min dominating set
    dom_set = set([])
    cost_func = dict((node, nd.get(weight, 1)) \
                     for node, nd in graph.nodes_iter(data=True))

    vertices = set(graph)
    sets = dict((node, set([node]) | set(graph[node])) for node in graph)

    def _cost(subset):
        """ Our cost effectiveness function for sets given its weight
        """
        cost = sum(cost_func[node] for node in subset)
        return cost / float(len(subset - dom_set))

    while vertices:
        # find the most cost effective set, and the vertex that for that set
        dom_node, min_set = min(sets.items(),
                                key=lambda x: (x[0], _cost(x[1])))
        alpha = _cost(min_set)

        # reduce the cost for the rest
        for node in min_set - dom_set:
            cost_func[node] = alpha

        # add the node to the dominating set and reduce what we must cover
        dom_set.add(dom_node)
        del sets[dom_node]
        vertices = vertices - min_set

    return dom_set


def min_edge_dominating_set(graph):
    """Return minimum weight dominating edge set.

    Parameters
    ----------
    graph : NetworkX graph
      Undirected graph

    Returns
    -------
    min_edge_dominating_set : set
      Returns a set of dominating edges whose size is no more than 2 * OPT.
    """
    if not graph:
        raise ValueError("Expected non-empty NetworkX graph!")
    return nx.maximal_matching(graph)
