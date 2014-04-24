from __future__ import division

from networkx.exception import *
from networkx.utils.decorators import *


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def common_neighbors(G, u, v):
    """Count the number of common neighbors of two nodes."""
    return len(_get_common_neighbors(G, u, v))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def resource_allocation_index(G, u, v):
    """Compute the resource allocation index (RA) of two nodes.

    RA index of two nodes is defined as the sum of reciprocals of the
    degree of all their common neighbors.

    References
    ----------
    Lü, Linyuan and Zhou, Tao. Link prediction in complex networks:
    A survey. In Physica A, (390) 6: 11501170, Year 2011.
    http://arxiv.org/pdf/1010.0725v1.pdf
    """
    cnbors = _get_common_neighbors(G, u, v)
    return sum(map(lambda x: 1 / x, G.degree(cnbors).values()))


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def cn_soundarajan_hopcroft(G, u, v):
    """Count the number of common neighbors using community information.

    One is added to the count for each common neighbor that belongs
    to the same community as the given nodes.

    References
    ----------
    Sucheta Soundarajan and John Hopcroft. 2012. Using community
    information to improve the precision of link prediction methods.
    In Proceedings of the 21st international conference companion on
    World Wide Web (WWW '12 Companion). ACM, New York, NY, USA, 607-608.
    DOI=10.1145/2187980.2188150
    http://doi.acm.org/10.1145/2187980.2188150
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
    """Compute the RA index of two nodes using community information.

    RA index is defined as the sum of reciprocals of the degree of all
    all common neighbors of the two nodes. However, this function only
    considers common neighbors belonging to the same community as the
    given nodes.

    References
    ----------
    Sucheta Soundarajan and John Hopcroft. 2012. Using community
    information to improve the precision of link prediction methods.
    In Proceedings of the 21st international conference companion on
    World Wide Web (WWW '12 Companion). ACM, New York, NY, USA, 607-608.
    DOI=10.1145/2187980.2188150
    http://doi.acm.org/10.1145/2187980.2188150
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

    References
    ----------
    Jorge Carlos Valverde-Rebaza and Alneu de Andrade Lopes. 2012.
    Link prediction in complex networks based on cluster information.
    In Proceedings of the 21st Brazilian conference on Advances in
    Artificial Intelligence (SBIA'12), Leliane N. Barros, Marcelo
    Finger, Aurora T. Pozo, Gustavo A. Gimenénez-Lugo, and Marcos
    Castilho (Eds.). Springer-Verlag, Berlin, Heidelberg, 92-101.
    DOI=10.1007/978-3-642-34459-6_10
    http://dx.doi.org/10.1007/978-3-642-34459-6_10
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
    """Get the set of common neighbors between two nodes."""
    nset1 = set(G[u])
    nset2 = set(G[v])
    return nset1 & nset2


def _get_community(G, u):
    """Get the community of the given node."""
    try:
        return G.node[u]['community']
    except KeyError:
        raise NetworkXAlgorithmError('No community information')
