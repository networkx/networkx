#-*- coding: utf-8 -*-
#    Copyright (C) 2011 by 
#    Jordi Torrents <jtorrents@milnou.net>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
from collections import defaultdict
import networkx as nx
__author__ = """\n""".join(['Jordi Torrents <jtorrents@milnou.net>',
                            'Aric Hagberg (hagberg@lanl.gov)'])
__all__ = ['average_degree_connectivity',
           'average_in_degree_connectivity',
           'average_out_degree_connectivity',
           'k_nearest_neighbors']

def _avg_deg_conn(G, degree_method, nodes=None, weight=None):
    # "k nearest neighbors, or neighbor_connectivity
    dsum = defaultdict(float)
    dnorm = defaultdict(float)

    for n,k in degree_method(nodes).items():
        nbrdeg = degree_method(G[n])
        if weight is None:
            s = float(sum(nbrdeg.values()))
        else: # weight nbr degree by weight of (n,nbr) edge
            s = float(sum((G[n][nbr].get(weight,1)*d 
                           for nbr,d in nbrdeg.items())))
        dnorm[k] += degree_method(n, weight=weight)
        dsum[k] += s

    # normalize
    dc = {}
    for k,avg in dsum.items():
        dc[k]=avg
        if avg > 0:
            dc[k]/=dnorm[k]
    return dc


def average_degree_connectivity(G, nodes=None, weight=None):
    r"""Compute the average degree connectivity of graph.

    The average degree connectivity is the average nearest neighbor degree of
    nodes with degree k. For weighted graphs, an analogous measure can 
    be computed using the weighted average neighbors degree defined in 
    [1]_, for a node `i`, as:

    .. math::

        k_{nn,i}^{w} = \frac{1}{s_i} \sum_{j \in N(i)} w_{ij} k_j

    where `s_i` is the weighted degree of node `i`, 
    `w_{ij}`is the weight of the edge that links `i` and `j`,
    and `N(i)` are the neighbors of node `i`.

    Parameters
    ----------
    G : NetworkX graph

    nodes: list or iterable (optional)
        Compute neighbor connectivity for these nodes. The default is all nodes.

    weight : string or None, optional (default=None)
       The edge attribute that holds the numerical value used as a weight.
       If None, then each edge has weight 1.

    Returns
    -------
    d: dict
       A dictionary keyed by degree k with the value of average neighbor degree.
    
    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> G.edge[1][2]['weight'] = 3
    >>> nx.k_nearest_neighbors(G)
    {1: 2.0, 2: 1.5}
    >>> nx.k_nearest_neighbors(G, weight='weight')
    {1: 2.0, 2: 1.75}

    See also
    --------
    neighbors_average_degree

    Notes
    -----
    This algorithm is sometimes called "k nearest neighbors'.

    References
    ----------    
    .. [1] A. Barrat, M. Barthélemy, R. Pastor-Satorras, and A. Vespignani, 
       "The architecture of complex weighted networks". 
       PNAS 101 (11): 3747–3752 (2004).
    """
    return _avg_deg_conn(G, G.degree, nodes, weight)

def average_in_degree_connectivity(G, nodes=None, weight=None):
    if not G.is_directed():
        raise nx.NetworkXError("Not defined for undirected graphs.")
    return _avg_deg_conn(G, G.in_degree, nodes, weight)
average_in_degree_connectivity.__doc__=average_degree_connectivity.__doc__

def average_out_degree_connectivity(G, nodes=None, weight=None):
    if not G.is_directed():
        raise nx.NetworkXError("Not defined for undirected graphs.")
    return _avg_deg_conn(G, G.out_degree, nodes, weight)
average_out_degree_connectivity.__doc__=average_degree_connectivity.__doc__


k_nearest_neighbors=average_degree_connectivity
neighbor_connectivity=average_degree_connectivity
