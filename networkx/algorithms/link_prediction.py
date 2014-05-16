"""
Link prediction algorithms.
"""

from __future__ import division

import math

import networkx as nx
from networkx.exception import *
from networkx.utils.decorators import *

__all__ = ['resource_allocation_index',
           'jaccard_coefficient',
           'adamic_adar_index',
           'preferential_attachment',
           'cn_soundarajan_hopcroft',
           'ra_index_soundarajan_hopcroft',
           'within_inter_cluster']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def resource_allocation_index(G, u, v):
    r"""Compute the resource allocation index of two nodes.

    Resource allocation index of `u` and `v` is defined as

    .. math::

        \sum_{w \in \Gamma(u) \cap \Gamma(v)} \frac{1}{|\Gamma(w)|}

    where :math:`\Gamma(u)` denotes the set of neighbors of `u`.

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : float
        The resource allocation index of `u` and `v`.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> '%.8f' % nx.resource_allocation_index(G, 0, 1)
    '0.75000000'

    References
    ----------
    .. [1] T. Zhou, L. Lu, Y.-C. Zhang.
       Predicting missing links via local information.
       Eur. Phys. J. B 71 (2009) 623.
       http://arxiv.org/pdf/0901.0553.pdf
    """
    return sum(1 / G.degree(w) for w in nx.common_neighbors(G, u, v))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def jaccard_coefficient(G, u, v):
    r"""Compute the Jaccard coefficient of two nodes.

    Jaccard coefficient of nodes `u` and `v` is defined as

    .. math::

        \frac{|\Gamma(u) \cap \Gamma(v)|}{|\Gamma(u) \cup \Gamma(v)|}

    where :math:`\Gamma(u)` denotes the set of neighbors of `u`.

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : float
        The Jaccard coefficient of `u` and `v`.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> '%.8f' % nx.jaccard_coefficient(G, 0, 1)
    '0.60000000'

    References
    ----------
    .. [1] D. Liben-Nowell, J. Kleinberg.
           The Link Prediction Problem for Social Networks (2004).
           http://www.cs.cornell.edu/home/kleinber/link-pred.pdf
    """
    cnbors = list(nx.common_neighbors(G, u, v))
    union_size = len(set(G[u]) | set(G[v]))
    if union_size == 0:
        return 0
    else:
        return len(cnbors) / union_size


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def adamic_adar_index(G, u, v):
    r"""Compute the Adamic-Adar index of two nodes.

    Adamic-Adar index of `u` and `v` is defined as

    .. math::

        \sum_{w \in \Gamma(u) \cap \Gamma(v)} \frac{1}{\log |\Gamma(w)|}

    where :math:`\Gamma(u)` denotes the set of neighbors of `u`.

    Parameters
    ----------
    G : graph
        NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : float
        The Adamic-Adar index of `u` and `v`.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> '%.8f' % nx.adamic_adar_index(G, 0, 1)
    '2.16404256'

    References
    ----------
    .. [1] D. Liben-Nowell, J. Kleinberg.
           The Link Prediction Problem for Social Networks (2004).
           http://www.cs.cornell.edu/home/kleinber/link-pred.pdf
    """
    return sum(1 / math.log(G.degree(w)) for w in nx.common_neighbors(G, u, v))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def preferential_attachment(G, u, v):
    r"""Compute the preferential attachment score of two nodes.

    Preferential attachment score of `u` and `v` is defined as

    .. math::

        |\Gamma(u)| |\Gamma(v)|

    where :math:`\Gamma(u)` denotes the set of neighbors of `u`.

    Parameters
    ----------
    G : graph
        NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : int
        The preferential attachment score of `u` and `v`.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> nx.preferential_attachment(G, 0, 1)
    16

    References
    ----------
    .. [1] D. Liben-Nowell, J. Kleinberg.
           The Link Prediction Problem for Social Networks (2004).
           http://www.cs.cornell.edu/home/kleinber/link-pred.pdf
    """
    if u not in G:
        raise nx.NetworkXError('u is not in the graph.')
    if v not in G:
        raise nx.NetworkXError('v is not in the graph.')

    return G.degree(u) * G.degree(v)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def cn_soundarajan_hopcroft(G, u, v):
    r"""Count the number of common neighbors of two nodes using community information.

    One is added to the count for each common neighbor that belongs
    to the same community as `u` and `v`. Mathematically,

    .. math::

        |\Gamma(u) \cap \Gamma(v)| + \sum_{w \in \Gamma(u) \cap \Gamma(v)} f(w)

    where `f(w)` equals 1 if `w` belongs to the same community as `u`
    and `v` or 0 otherwise and :math:`\Gamma(u)` denotes the set of
    neighbors of `u`.

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : int
        The number of common neighbors between `u` and `v` plus bonus
        for each common neighbor belonging to the same community as
        `u` and `v`.

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
    cnbors = list(nx.common_neighbors(G, u, v))
    if Cu == Cv:
        return len(cnbors) + sum(_community(G, w) == Cu for w in cnbors)
    else:
        return len(cnbors)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def ra_index_soundarajan_hopcroft(G, u, v):
    r"""Compute the resource allocation index of two nodes using community information.


    This function computes the resource allocation index of `u` and `v`
    considering only common neighbors belonging to the same community
    as `u` and `v`. Mathematically,

    .. math::

        \sum_{w \in \Gamma(u) \cap \Gamma(v)} \frac{f(w)}{|\Gamma(w)|}

    where `f(w)` equals 1 if `w` belongs to the same community as `u`
    and `v` or 0 otherwise and :math:`\Gamma(u)` denotes the set of
    neighbors of `u`.

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    value : float
        The resource allocation index of `u` and `v` considering only
        common neighbors that belong to the same community as
        `u` and `v`.

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
    >>> '%.8f' % nx.ra_index_soundarajan_hopcroft(G, 0, 3)
    '0.50000000'

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
    if Cu == Cv:
        cnbors = nx.common_neighbors(G, u, v)
        return sum(1 / G.degree(w) for w in cnbors if _community(G, w) == Cu)
    else:
        return 0


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def within_inter_cluster(G, u, v, delta=0.001):
    """Compute the ratio of within- and inter-cluster common neighbors of two nodes.

    If a common neighbor `w` belongs to the same community as `u`
    and `v`, `w` is considered as within-cluster common neighbor of `u`
    and `v`. Otherwise, it is considered as inter-cluster common neighbor
    of `u` and `v`. The ratio between the size of the set of within- and
    inter-cluster common neighbors is defined as the WIC measure. [1]_

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    delta : float, optional
        Value to prevent division by zero in case there is no inter-cluster
        common neighbor of `u` and `v`. See [1]_ for details.

    Returns
    -------
    value : float
        The WIC measure of `u` and `v`.

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
    >>> '%.8f' % nx.within_inter_cluster(G, 0, 4)
    '1.99800200'
    >>> '%.8f' % nx.within_inter_cluster(G, 0, 4, delta=0.5)
    '1.33333333'

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
    if Cu == Cv:
        cnbors = set(nx.common_neighbors(G, u, v))
        within = set(w for w in cnbors if _community(G, w) == Cu)
        inter = cnbors - within
        return len(within) / (len(inter) + delta)
    else:
        return 0


def _community(G, u):
    """Get the community of the given node."""
    try:
        return G.node[u]['community']
    except KeyError:
        raise NetworkXAlgorithmError('No community information')
