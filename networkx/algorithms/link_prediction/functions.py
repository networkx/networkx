import networkx as nx


def common_neighbors(G, node1, node2):
    """Count the number of common neighbors of two nodes"""
    return len(_common_neighbors_list(G, node1, node2))


def resource_allocation_index(G, node1, node2):
    """Compute the resource allocation index (RA) of two nodes

    RA index is defined as the sum of reciprocal of the degree of nodes
    over all common neighbors of the two nodes.

    """
    cn_list = _common_neighbors_list(G, node1, node2)
    return sum(map(lambda x: 1 / x, list(G.degree(cn_list).values())))


def _common_neighbors_list(G, node1, node2):
    """Get the list of common neighbors between two nodes"""
    nset1 = set(G.neighbors(node1))
    nset2 = set(G.neighbors(node2))
    return list(nset1 & nset2)