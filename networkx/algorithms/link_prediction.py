from __future__ import division

from networkx.exception import *
from networkx.utils.decorators import *

__all__ = ['common_neighbors',
           'resource_allocation_index',
           'cn_soundarajan_hopcroft',
           'ra_index_soundarajan_hopcroft',
           'within_inter_cluster']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def common_neighbors(G, u, v):
    """Count the number of common neighbors of u and v.

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : int
        The number of common neighbors of u and v.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> nx.common_neighbors(G, 0, 1)
    3
    """
    return len(_common_neighbors(G, u, v))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def resource_allocation_index(G, u, v):
    """Compute the resource allocation index of u and v.

    Resource allocation index of nodes u and v is defined as the sum of
    reciprocals of the degree of all the common neighbors w of u and v.

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : float
        The resource allocation index of u and v.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> nx.resource_allocation_index(G, 0, 1)
    0.75

    References
    ----------
    .. [1] T. Zhou, L. Lu, Y.-C. Zhang.
       Predicting missing links via local information.
       Eur. Phys. J. B 71 (2009) 623.
       http://arxiv.org/pdf/0901.0553.pdf
    """
    return sum(1 / G.degree(w) for w in _common_neighbors(G, u, v))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def cn_soundarajan_hopcroft(G, u, v):
    """Count the number of common neighbors using community information.

    One is added to the count for each common neighbor that belongs
    to the same community as u and v.

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : int
        The number of common neighbors between u and v plus bonus for
        each common neighbor belonging to the same community as u and v.

    Notes
    -----
    The community information is defined as the information of which
    community each node belongs to. This information should be stored
    as the nodes attribute with 'community' as the name.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(3)
    >>> G.node[0]['community'] = 0
    >>> G.node[1]['community'] = 0
    >>> G.node[2]['community'] = 0
    >>> nx.cn_soundarajan_hopcroft(G, 0, 2)
    2

    References
    ----------
    .. [1] Sucheta Soundarajan and John Hopcroft.
       Using community information to improve the precision of link prediction methods.
       In Proceedings of the 21st international conference companion on
       World Wide Web (WWW '12 Companion). ACM, New York, NY, USA, 607-608.
       http://doi.acm.org/10.1145/2187980.2188150
    """
    Cu = _community(G, u)
    Cv = _community(G, v)
    cnbors = _common_neighbors(G, u, v)
    if Cu == Cv:
        return len(cnbors) + sum(_community(G, w) == Cu for w in cnbors)
    else:
        return len(cnbors)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def ra_index_soundarajan_hopcroft(G, u, v):
    """Compute the resource allocation index of u and v using community information.

    Resource allocation index of two nodes is defined as the sum of
    reciprocals of the degree of all their common neighbors. However,
    this function only considers common neighbors belonging to the same
    community as u and v.

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : float
        The resource allocation index of u and v considering only
        common neighbors that belong to the same community as u and v.

    Notes
    -----
    The community information is defined as the information of which
    community each node belongs to. This information should be stored
    as the nodes attribute with 'community' as the name.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
    >>> G.node[0]['community'] = 0
    >>> G.node[1]['community'] = 0
    >>> G.node[2]['community'] = 1
    >>> G.node[3]['community'] = 0
    >>> nx.ra_index_soundarajan_hopcroft(G, 0, 3)
    0.5

    References
    ----------
    .. [1] Sucheta Soundarajan and John Hopcroft.
       Using community information to improve the precision of link prediction methods.
       In Proceedings of the 21st international conference companion on
       World Wide Web (WWW '12 Companion). ACM, New York, NY, USA, 607-608.
       http://doi.acm.org/10.1145/2187980.2188150
    """
    Cu = _community(G, u)
    Cv = _community(G, v)
    cnbors = _common_neighbors(G, u, v)
    if Cu == Cv:
        return sum(1 / G.degree(w) for w in cnbors if _community(G, w) == Cu)
    else:
        return 0


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def within_inter_cluster(G, u, v, delta=0.001):
    """Compute the ratio of within- and inter-cluster common neighbor.

    If a common neighbor w belongs to the same community with u and v,
    w is considered as within-cluster common neighbor of u and v.
    Otherwise, it is considered as inter-cluster common neighbor of u
    and v. The ratio between the size of the set of within- and
    inter-cluster common neighbors is defined as the WIC measure. [1]_

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    delta : float, optional
        Value to prevent division by zero in case there is no inter-cluster
        common neighbor of u and v. See [1]_ for details.

    Returns
    -------
    value : float
        The WIC measure of u and v.

    Notes
    -----
    The community information is defined as the information of which
    community each node belongs to. This information should be stored
    as the nodes attribute with 'community' as the name.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 4)])
    >>> G.node[0]['community'] = 0
    >>> G.node[1]['community'] = 1
    >>> G.node[2]['community'] = 0
    >>> G.node[3]['community'] = 0
    >>> G.node[4]['community'] = 0
    >>> nx.within_inter_cluster(G, 0, 4)
    1.9980019980019983
    >>> nx.within_inter_cluster(G, 0, 4, delta=0.5)
    1.3333333333333333

    References
    ----------
    .. [1] Jorge Carlos Valverde-Rebaza and Alneu de Andrade Lopes.
       Link prediction in complex networks based on cluster information.
       In Proceedings of the 21st Brazilian conference on Advances in
       Artificial Intelligence (SBIA'12)
       http://dx.doi.org/10.1007/978-3-642-34459-6_10
    """
    if delta <= 0:
        raise NetworkXAlgorithmError('Delta must be greater than zero')

    Cu = _community(G, u)
    Cv = _community(G, v)
    cnbors = _common_neighbors(G, u, v)
    if Cu == Cv:
        within = set(w for w in cnbors if _community(G, w) == Cu)
        inter = cnbors - within
        return len(within) / (len(inter) + delta)
    else:
        return 0


def _common_neighbors(G, u, v):
    """Get the set of common neighbors between two nodes."""
    return set(G[u]) & set(G[v])


def _community(G, u):
    """Get the community of the given node."""
    try:
        return G.node[u]['community']
    except KeyError:
        raise NetworkXAlgorithmError('No community information')
