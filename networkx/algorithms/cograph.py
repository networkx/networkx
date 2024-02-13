from itertools import combinations

import networkx as nx


def cograph_from_cotree(cotree):
    if not nx.is_tree(cotree):
        raise nx.NotATree

    leaves = [v for v in cotree.nodes if cotree.degree(v) == 1]
    internal = [v for v in cotree.nodes if cotree.degree(v) > 1]

    cograph = nx.Graph()
    cograph.add_nodes_from(leaves)

    for pair in combinations(leaves, 2):
        u, v = pair
        lca = nx.lowest_common_ancestor(cotree, u, v)
        if "cotree_label" in cotree.nodes[lca]:
            if cotree.nodes[lca]["cotree_label"] == 1:
                cograph.add_edge(u, v)
            elif cotree.nodes[lca]["cotree_label"] != 0:
                raise Exception("Error: 'cotree_label' takes values in {0, 1}")
        else:
            raise Exception(
                "Error: Internal vertices must contain 'cotree_label' attribute"
            )

    return cograph


def is_cograph(graph):
    pass
