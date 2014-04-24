from __future__ import division

from networkx.exception import *
from networkx.utils.decorators import *


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def common_neighbors(G, node1, node2):
    """Count the number of common neighbors of two nodes"""
    return len(_get_common_neighbors(G, node1, node2))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def resource_allocation_index(G, node1, node2):
    """Compute the resource allocation index (RA) of two nodes

    RA index is defined as the sum of reciprocal of the degree of nodes
    over all common neighbors of the two nodes.

    """
    cnbors = _get_common_neighbors(G, node1, node2)
    return sum(map(lambda x: 1 / x, G.degree(cnbors).values()))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def cn_soundarajan_hopcroft(G, node1, node2):
    """Count the number of common neighbors of two nodes

    One is added to the count for each common neighbor that belongs
    to the same community as the two nodes. Based on Soundarajan, et al
    2012.

    """
    cmty1 = _get_community(G, node1)
    cmty2 = _get_community(G, node2)
    cnbors = _get_common_neighbors(G, node1, node2)
    if cmty1 == cmty2:
        def is_same_cmty(w):
            return _get_community(G, w) == cmty1
        return len(cnbors) + sum(map(is_same_cmty, cnbors))
    else:
        return len(cnbors)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def ra_index_soundarajan_hopcroft(G, node1, node2):
    """Compute the RA index of two nodes using community information

    RA index is defined as the sum of reciprocal of the degree of nodes
    over all common neighbors of the two nodes. However, this function
    only considers common neighbors belonging to the same community
    as the given two nodes. Based on Soundarajan, et al (2012).

    """
    cmty1 = _get_community(G, node1)
    cmty2 = _get_community(G, node2)
    cnbors = _get_common_neighbors(G, node1, node2)
    if cmty1 == cmty2:
        def is_same_cmty(w):
            return _get_community(G, w) == cmty1
        filtered = filter(is_same_cmty, cnbors)
        return sum(map(lambda x: 1 / x, G.degree(filtered).values()))
    else:
        return 0


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def within_inter_cluster(G, node1, node2, delta=0.001):
    """Compute the ratio of within and inter cluster common neighbor

    If a common neighbor belongs to the same community with the two
    nodes, it is considered as within cluster common neighbor.
    Otherwise, it is considered as inter cluster common neighbor. The
    ratio between the two of them is the WIC measure. Based on
    Valverde-Rebaza, et al (2012).

    """
    if delta <= 0:
        raise NetworkXAlgorithmError('Delta must be greater than zero')

    cmty1 = _get_community(G, node1)
    cmty2 = _get_community(G, node2)
    cnbors = _get_common_neighbors(G, node1, node2)
    if cmty1 == cmty2:
        def is_same_cmty(w):
            return _get_community(G, w) == cmty1
        within = set(filter(is_same_cmty, cnbors))
        inter = cnbors - within
        return len(within) / (len(inter) + delta)
    else:
        return 0


def _get_common_neighbors(G, node1, node2):
    """Get the set of common neighbors between two nodes"""
    nset1 = set(G[node1])
    nset2 = set(G[node2])
    return nset1 & nset2


def _get_community(G, node):
    """Get the community of the given node"""
    try:
        cmty = G.node[node]['community']
    except KeyError:
        raise NetworkXAlgorithmError('No community information')
    return cmty
