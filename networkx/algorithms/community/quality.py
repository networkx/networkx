import random
import networkx as nx
#    Copyright(C) 2011 by
#    Ben Edwards <bedwards@cs.unm.edu>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__="""\n""".join(['Ben Edwards (bedwards@cs.unm.edu)',
                          'Aric Hagberg (hagberg@lanl.gov)'])

def modularity(G, communities, weight='weight'):
    r"""Determines the Modularity of a partition C
    on a graph G.

    Modularity is defined as

    .. math::

        Q = \frac{1}{2m} \sum_{ij} \left( A_{ij} - \frac{k_ik_j}{2m}\right) 
            \delta(c_i,c_j)

    where `m` is the number of edges, `A` is the adjacency matrix of G, 
    `k_i` is the degree of `i` and `\delta(c_i,c_j)` is 1 if `i` and `j` 
    are in the same community and 0 otherwise.

    Parameters
    ----------
    G : NetworkX Graph

    communinities : list of sets
      Non-overlaping sets of nodes 

    Returns
    -------
    Q : Float
      The Modularity of the paritition

    Raises
    ------
    NetworkXError
      If C is not a partition of the Nodes of G

    Examples
    --------
    >>> G = nx.Graph()
    >>> nx.modularity(G,nx.kernighan_lin(G))
    0.3571428571428571

    Notes
    -----
    Defined on all Graph types, tested on Graph.
    Add more tests.
    
    References
    ----------
    .. [1] M. E. J Newman 'Networks: An Introduction', page 224
       Oxford University Press 2011.
    """
    if not nx.unique_community(G, communities):
        raise NetworkXError("communities is not a unique partition of G")

    multigraph = G.is_multigraph()
    m = float(G.size(weight=weight))
    directed = G.is_directed()
    if G.is_directed():
        out_degree = G.out_degree(weight=weight)
        in_degree = G.in_degree(weight=weight)
        norm = 1.0/m
    else:
        out_degree = G.degree(weight=weight)
        in_degree = out_degree
        norm = 1.0/(2.0*m)
    affiliation = nx.affiliation_dict(communities)
    Q = 0.0
    for u in G:
        nbrs = (v for v in G if affiliation[u] == affiliation[v])
        for v in nbrs:
            try:
                if multigraph:
                    w = sum(d.get(weight,1) for k,d in G[u][v].items())
                else:
                    w = G[u][v].get(weight,1)
            except KeyError:
                w = 0
            #  double count self loop if undirected
            if u == v and not directed:
                w *= 2.0
            Q += w - in_degree[u] * out_degree[v] * norm
    return Q*norm

