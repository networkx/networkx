import networkx as nx


def _matching_order(graph_params):
    """The node ordering as introduced in VF2++.

    Notes
    -----
    Taking into account the structure of the Graph and the node labeling, the nodes are placed in an order such that,
    most of the unfruitful/infeasible branches of the search space can be pruned on high levels, significantly
    decreasing the number of visited states. The premise is that, the algorithm will be able to recognize
    inconsistencies early, proceeding to go deep into the search tree only if it's needed.

    Parameters
    ----------
    graph_params: namedtuple
        Contains:

            G1,G2: NetworkX Graph or MultiGraph instances.
                The two graphs to check for isomorphism or monomorphism.

            G1_labels,G2_labels: dict
                The label of every node in G1 and G2 respectively.

    Returns
    -------
    node_order: list
        The ordering of the nodes.
    """
    G1, G2, G1_labels, _, _, nodes_of_G2Labels, _ = graph_params
    if not G1 and not G2:
        return {}

    if G1.is_directed():
        G1 = G1.to_undirected(as_view=True)

    V1_unordered = set(G1.nodes())
    label_rarity = {label: len(nodes) for label, nodes in nodes_of_G2Labels.items()}
    used_degrees = {node: 0 for node in G1}
    node_order = []

    while V1_unordered:
        max_rarity = min(label_rarity[G1_labels[x]] for x in V1_unordered)
        rarest_nodes = [
            n for n in V1_unordered if label_rarity[G1_labels[n]] == max_rarity
        ]
        max_node = max(rarest_nodes, key=G1.degree)

        for dlevel_nodes in nx.bfs_layers(G1, max_node):
            nodes_to_add = dlevel_nodes.copy()
            while nodes_to_add:
                max_used_degree = max(used_degrees[n] for n in nodes_to_add)
                max_used_degree_nodes = [
                    n for n in nodes_to_add if used_degrees[n] == max_used_degree
                ]
                max_degree = max(G1.degree[n] for n in max_used_degree_nodes)
                max_degree_nodes = [
                    n for n in max_used_degree_nodes if G1.degree[n] == max_degree
                ]
                next_node = min(
                    max_degree_nodes, key=lambda x: label_rarity[G1_labels[x]]
                )

                node_order.append(next_node)
                for node in G1.neighbors(next_node):
                    used_degrees[node] += 1

                nodes_to_add.remove(next_node)
                label_rarity[G1_labels[next_node]] -= 1
                V1_unordered.discard(next_node)

    return node_order
