# -*- coding: utf-8 -*-
"""
Measures of how hierarchical a graph is, including 'Flow Hierarchy'
and the 'Global reaching centrality'.
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
import itertools
__authors__ = "\n".join(['Ben Edwards (bedwards@cs.unm.edu)',
                         'Conrad Lee (conradlee@gmail.com)'])
__all__ = ['flow_hierarchy', 'global_reaching_centrality']

def flow_hierarchy(G, weight=None):
    """Returns the flow hierarchy of a directed network.

    Flow hierarchy is defined as the fraction of edges not participating
    in cycles in a directed graph [1]_.

    Parameters
    ----------
    G : DiGraph or MultiDiGraph

    weight : key,optional (default=None)
        Attribute to use for node weights. If None the weight defaults to 1.

    Returns
    -------
    h : float
        Flow heirarchy value 

    Notes
    -----
    The algorithm described in [1]_ computes the flow hierarchy through
    exponentiation of the adjacency matrix.  This function implements an
    alternative approach that finds strongly connected components.    
    An edge is in a cycle if and only if it is in a strongly connected 
    component, which can be found in `O(m)`time using Tarjan's algorithm.
    
    References
    ----------
    .. [1] Luo, J.; Magee, C.L. (2011),
       Detecting evolving patterns of self-organizing networks by flow
       hierarchy measurement, Complexity, Volume 16 Issue 6 53-61.
       DOI: 10.1002/cplx.20368
       http://web.mit.edu/~cmagee/www/documents/28-DetectingEvolvingPatterns_FlowHierarchy.pdf
    """
    if not G.is_directed():
        raise nx.NetworkXError("G must be a digraph in flow_heirarchy")
    scc = nx.strongly_connected_components(G)
    return 1.-sum(G.subgraph(c).size(weight) for c in scc)/float(G.size(weight))

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def weights_to_lengths(G, weight_key, length_key):
    total_weight = float(G.size(weight=weight_key))
    for i, j, attr_dict in G.edges_iter(data=True):
        if attr_dict[weight_key] <= 0.:
            raise nx.NetworkXError("All edges must have a positive weight to be converted into a length")
        length = total_weight / attr_dict[weight_key]
        G.edge[i][j][length_key] = length


def global_reaching_centrality(G, weight=None):
    """Returns the global reaching centrality of a directed network.

    The global reaching centrality is based on the local reaching centrality,
    which, for some node i, indicates the proportion of the graph that is
    accessible from the outgoing edges of node i. For weighted directed graphs,
    the weight is taken into account. See references for details.

    Parameters
    ----------
    G : DiGraph

    weight : key,optional (default=None)
        Attribute to use for node weights. If None the weight defaults to 1.
        A higher weight here implies a stronger connection between nodes and
        a shorter path length.

    Returns
    -------
    h : float
        global reaching centrality

    Notes
    -----
    The algorithm described in [1] computes the global reaching centrality
    by using dijkstra's shortest path finding algorithm.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_edge(1, 2)
    >>> G.add_edge(1, 3)
    >>> nx.hierarchy.global_reaching_centrality(G)
    1.0
    >>> G.add_edge(3, 2)
    >>> nx.hierarchy.global_reaching_centrality(G)
    0.75

    References
    ----------
    .. [1] @article{mones2012hierarchy,
             title={Hierarchy measure for complex networks},
             author={Mones, E. and Vicsek, L. and Vicsek, T.},
             journal={Arxiv preprint arXiv:1202.0191},
             year={2012}
             }
    """
    lengths_key = "grc_lengths"
    if not G.is_directed():
        raise nx.NetworkXError("G must be a digraph in global_reaching_centrality")

    # Transform weights to lengths in order to use nx.all_pairs_dijkstra_path
    if not(weight is None):
        weights_to_lengths(G, weight, lengths_key)

    denom = float(G.order() - 1)
    local_reaching_centralities = []
    for node, path_dict in nx.all_pairs_dijkstra_path(G, weight=lengths_key).iteritems():
        sum_avg_weight = len(path_dict) - 1
        if not(weight is None):
            avg_weights = []
            for neighbor, path in path_dict.iteritems():
                path_weights = [G.edge[i][j][weight] for i, j in pairwise(path)]
                avg_path_weight = sum(path_weights) / float(len(path_weights))
                avg_weights.append(avg_path_weight)
            sum_avg_weight = sum(avg_weights)
        local_reaching_centralities.append(sum_avg_weight / denom)
    max_lrc = max(local_reaching_centralities)

    # Clean up
    return sum(max_lrc - lrc for lrc in local_reaching_centralities) / denom
    
