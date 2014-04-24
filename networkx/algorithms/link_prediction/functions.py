from __future__ import division

from networkx.exception import *
from networkx.utils.decorators import *


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def common_neighbors(G, u, v):
    """Count the number of common neighbors of two nodes"""
    return len(_get_common_neighbors(G, u, v))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def resource_allocation_index(G, u, v):
    """Compute the resource allocation index (RA) of two nodes

    RA index is defined as the sum of reciprocal of the degree of nodes
    over all common neighbors of the two nodes.

    """
    cnbors = _get_common_neighbors(G, u, v)
    return sum(map(lambda x: 1 / x, G.degree(cnbors).values()))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def cn_soundarajan_hopcroft(G, u, v):
    """Count the number of common neighbors of two nodes

    One is added to the count for each common neighbor that belongs
    to the same community as the two nodes. Based on Soundarajan, et al
    2012.

    """
    c1 = _get_community(G, u)
    c2 = _get_community(G, v)
    cnbors = _get_common_neighbors(G, u, v)
    if c1 == c2:
        def is_same_cmty(w):
            return _get_community(G, w) == c1
        return len(cnbors) + sum(map(is_same_cmty, cnbors))
    else:
        return len(cnbors)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def ra_index_soundarajan_hopcroft(G, u, v):
    """Compute the RA index of two nodes using community information

    RA index is defined as the sum of reciprocal of the degree of nodes
    over all common neighbors of the two nodes. However, this function
    only considers common neighbors belonging to the same community
    as the given two nodes. Based on Soundarajan, et al (2012).

    """
    c1 = _get_community(G, u)
    c2 = _get_community(G, v)
    cnbors = _get_common_neighbors(G, u, v)
    if c1 == c2:
        def is_same_cmty(w):
            return _get_community(G, w) == c1
        filtered = filter(is_same_cmty, cnbors)
        return sum(map(lambda x: 1 / x, G.degree(filtered).values()))
    else:
        return 0


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def within_inter_cluster(G, u, v, delta=0.001):
    """Compute the ratio of within and inter cluster common neighbor

    If a common neighbor belongs to the same community with the two
    nodes, it is considered as within cluster common neighbor.
    Otherwise, it is considered as inter cluster common neighbor. The
    ratio between the two of them is the WIC measure. Based on
    Valverde-Rebaza, et al (2012).

    """
    if delta <= 0:
        raise NetworkXAlgorithmError('Delta must be greater than zero')

    c1 = _get_community(G, u)
    c2 = _get_community(G, v)
    cnbors = _get_common_neighbors(G, u, v)
    if c1 == c2:
        def is_same_cmty(w):
            return _get_community(G, w) == c1
        within = set(filter(is_same_cmty, cnbors))
        inter = cnbors - within
        return len(within) / (len(inter) + delta)
    else:
        return 0


def _get_common_neighbors(G, u, v):
    """Get the set of common neighbors between two nodes"""
    nset1 = set(G[u])
    nset2 = set(G[v])
    return nset1 & nset2


def _get_community(G, u):
    """Get the community of the given node"""
    try:
        return G.node[u]['community']
    except KeyError:
        raise NetworkXAlgorithmError('No community information')
