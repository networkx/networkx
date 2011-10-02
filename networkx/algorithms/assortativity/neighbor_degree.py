#-*- coding: utf-8 -*-
#    Copyright (C) 2011 by 
#    Jordi Torrents <jtorrents@milnou.net>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = """\n""".join(['Jordi Torrents <jtorrents@milnou.net>',
                            'Aric Hagberg (hagberg@lanl.gov)'])
__all__ = ["average_neighbor_degree",
           "average_neighbor_in_degree",
           "average_neighbor_out_degree"]


def _average_nbr_deg(G, degree_method, nodes=None, weight=None):
    avg_nbr_deg = {}
    for n in G.nbunch_iter(nodes):
        nbrdeg = degree_method(G[n])
        if weight is None:
            nbrv = nbrdeg.values()
        else:
            nbrv = [G[n][nbr].get(weight,1)*d for nbr,d in nbrdeg.items()]
        norm = degree_method(n,weight=weight)
        avg_nbr_deg[n] = float(sum(nbrv))
        if norm > 0:
            avg_nbr_deg[n] /= norm
    return avg_nbr_deg

def average_neighbor_degree(G, nodes=None, weight=None):
    r"""Returns the average degree of the neighborhood of each node.

    The average degree of a node `i` is

    .. math::

        k_{nn,i} = \frac{1}{|N(i)|} \sum_{j \in N(i)} k_j

    where `N(i)` are the neighbors of node `i` and `k_j` is
    the degree of node `j` which belongs to `N(i)`. For weighted 
    graphs, an analogous measure can be defined [1]_,

    .. math::

        k_{nn,i}^{w} = \frac{1}{s_i} \sum_{j \in N(i)} w_{ij} k_j

    where `s_i` is the weighted degree of node `i`, `w_{ij}`
    is the weight of the edge that links `i` and `j` and
    `N(i)` are the neighbors of node `i`.


    Parameters
    ----------
    G : NetworkX graph

    nodes : list or iterable, optional (default is all nodes)
        Compute neighbor connectivity for these nodes. 

    weight : string or None, optional (default=None)
       The edge attribute that holds the numerical value used as a weight.
       If None, then each edge has weight 1.

    Returns
    -------
    d: dict
       A dictionary keyed by node with average neighbors degree value.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> G.edge[0][1]['weight'] = 5
    >>> G.edge[2][3]['weight'] = 3
    >>> nx.average_neighbor_degree(G)
    {0: 2.0, 1: 1.5, 2: 1.5, 3: 2.0}
    >>> nx.average_neighbor_degree(G, weight='weight')
    {0: 2.0, 1: 1.1666666666666667, 2: 1.25, 3: 2.0}

    >>> G=nx.DiGraph()
    >>> G.add_path([0,1,2,3])
    >>> nx.average_neighbor_in_degree(G)
    {0: 1.0, 1: 1.0, 2: 1.0, 3: 0.0}
    >>> nx.average_neighbor_out_degree(G)
    {0: 1.0, 1: 1.0, 2: 0.0, 3: 0.0}
 
    Notes
    -----
    For directed graphs you can also specify in-degree or out-degree 
    by calling the relevant functions.  

    See Also
    --------
    average_neighbor_out_degree, average_neighbor_in_degree, 
    average_degree_connectivity 
    
    References
    ----------    
    .. [1] A. Barrat, M. Barthélemy, R. Pastor-Satorras, and A. Vespignani, 
       "The architecture of complex weighted networks". 
       PNAS 101 (11): 3747–3752 (2004).
    """
    degree_method = G.degree
    return _average_nbr_deg(G, degree_method, nodes, weight)

def average_neighbor_in_degree(G, nodes=None, weight=None):
    if not G.is_directed():
        raise nx.NetworkXError("Not defined for undirected graphs.")
    degree_method = G.in_degree
    return _average_nbr_deg(G, degree_method, nodes, weight)
average_neighbor_in_degree.__doc__=average_neighbor_degree.__doc__

def average_neighbor_out_degree(G, nodes=None, weight=None):
    if not G.is_directed():
        raise nx.NetworkXError("Not defined for undirected graphs.")
    degree_method = G.out_degree
    return _average_nbr_deg(G, degree_method, nodes, weight)
average_neighbor_out_degree.__doc__=average_neighbor_degree.__doc__

