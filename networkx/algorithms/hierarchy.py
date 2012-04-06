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


    if G.size() < 1:
        raise nx.NetworkXError("Size of G must be positive for global_reaching_centrality")

    # Transform weights to lengths in order to use nx.all_pairs_dijkstra_path
    # Will stomp all over edge attribute "grc_lengths" if in use
    if not(weight is None):
        lengths_key = "grc_lengths"
        total_weight = float(G.size(weight=weight))
        for i, j, attr_dict in G.edges_iter(data=True):
            if attr_dict[weight] <= 0.:
                raise nx.NetworkXError("All edges must have a positive weight to be converted into a length")
            length = total_weight / attr_dict[weight]
            G.edge[i][j][lengths_key] = length
    else:
        lengths_key = None

    denom = float(G.order() - 1)
    local_reaching_centralities = []
    for node, path_dict in nx.all_pairs_dijkstra_path(G, weight=lengths_key).iteritems():
        if (weight is None) and G.is_directed():
            sum_avg_weight = len(path_dict) - 1
        else:
            avg_weights = []
            for neighbor, p in path_dict.iteritems():
                path = list(pairwise(p))
                if len(path) > 0:
                    if (weight is None):
                        path_weight = 1.
                    else:
                        path_weight = float(sum([G.edge[i][j][weight] for i, j in path]))
                    avg_weights.append(path_weight / len(path))
            sum_avg_weight = sum(avg_weights)
        local_reaching_centralities.append(sum_avg_weight / denom)
    max_lrc = max(local_reaching_centralities)
    grc = sum(max_lrc - lrc for lrc in local_reaching_centralities) / denom

    # Clean up by removing "grc_lengths" edge attribute, if necessary
    if (not weight is None):
        for i, j in G.edges_iter():
            del G.edge[i][j][lengths_key]

    return grc
    
# Helper functions for global_reaching_centrality

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)
