from networkx.exception import *


def common_neighbors(G, node1, node2):
    """Count the number of common neighbors of two nodes"""
    _ensure_undirected(G)
    return len(_common_neighbors_list(G, node1, node2))


def resource_allocation_index(G, node1, node2):
    """Compute the resource allocation index (RA) of two nodes

    RA index is defined as the sum of reciprocal of the degree of nodes
    over all common neighbors of the two nodes.

    """
    _ensure_undirected(G)
    cn_list = _common_neighbors_list(G, node1, node2)
    return sum(map(lambda x: 1 / x, list(G.degree(cn_list).values())))


def cn_soundarajan_hopcroft(G, node1, node2):
    """Count the number of common neighbors of two nodes

    One is added to the count for each common neighbor that belongs
    to the same community as the two nodes. Based on Soundarajan, et al
    2012.

    """
    _ensure_undirected(G)
    cmty1, cmty2 = _get_communities(G, node1, node2)
    cn_list = _common_neighbors_list(G, node1, node2)
    def score(u):
        cmty = G.node[u]['community']
        if cmty == cmty1 and cmty == cmty2:
            return 1
        else:
            return 0
    return len(cn_list) + sum(map(score, cn_list))


def ra_index_soundarajan_hopcroft(G, node1, node2):
    """Compute the RA index of two nodes using community information

    RA index is defined as the sum of reciprocal of the degree of nodes
    over all common neighbors of the two nodes. However, this function
    only considers common neighbors belonging to the same community
    as the given two nodes. Based on Soundarajan, et al (2012).

    """
    _ensure_undirected(G)
    cmty1, cmty2 = _get_communities(G, node1, node2)

    cn_list = _common_neighbors_list(G, node1, node2)
    def same_cmty(u):
        cmty = G.node[u]['community']
        return cmty == cmty1 and cmty == cmty2
    try:
        filtered_list = filter(same_cmty, cn_list)
    except KeyError:
        raise NetworkXAlgorithmError('No community information')
    return sum(map(lambda x: 1 / x, list(G.degree(filtered_list).values())))


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

    _ensure_undirected(G)

    cmty1, cmty2 = _get_communities(G, node1, node2)
    cn_list = _common_neighbors_list(G, node1, node2)
    def within(u):
        cmty = G.node[u]['community']
        return cmty == cmty1 and cmty == cmty2
    try:
        filtered_list = filter(within, cn_list)
    except KeyError:
        raise NetworkXAlgorithmError('No community information')
    num_within = len(list(filtered_list))
    num_inter = len(list(cn_list)) - num_within
    return num_within / (num_inter + delta)


def _common_neighbors_list(G, node1, node2):
    """Get the list of common neighbors between two nodes"""
    nset1 = set(G[node1])
    nset2 = set(G[node2])
    return list(nset1 & nset2)


def _get_communities(G, node1, node2):
    """Get communities of given nodes"""
    try:
        cmty1 = G.node[node1]['community']
        cmty2 = G.node[node2]['community']
    except KeyError:
        raise NetworkXAlgorithmError('No community information')
    return cmty1, cmty2


def _ensure_undirected(G):
    """Ensures that graph G is a simple undirected graph"""
    if G.is_directed() or G.is_multigraph():
        raise NetworkXNotImplemented()
