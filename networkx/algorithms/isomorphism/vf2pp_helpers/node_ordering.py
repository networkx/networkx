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

    V1_unordered = set(G1.nodes())
    label_rarity = {label: len(nodes) for label, nodes in nodes_of_G2Labels.items()}
    used_degrees = {node: 0 for node in G1}
    node_order = []

    while V1_unordered:
        max_node = max(
            _rarest_nodes(V1_unordered, G1_labels, label_rarity), key=G1.degree
        )

        for dlevel_nodes in nx.bfs_layers(G1, max_node):
            max_deg_nodes = []
            max_degree = 0
            while dlevel_nodes:
                # Get the nodes with the max used_degree
                max_used_deg = -1
                for node in dlevel_nodes:
                    deg = used_degrees[node]
                    if deg >= max_used_deg:  # most common case: deg < max_deg
                        if deg > max_used_deg:
                            max_used_deg = deg
                            max_degree = G1.degree[node]
                            max_deg_nodes = [node]
                        else:  # deg == max_deg
                            deg = G1.degree[node]
                            if deg > max_degree:
                                max_degree = deg
                                max_deg_nodes = [node]
                            elif deg == max_degree:
                                max_deg_nodes.append(node)

                # Get the max_used_degree node with the rarest label
                next_node = min(max_deg_nodes, key=lambda x: label_rarity[G1_labels[x]])
                node_order.append(next_node)

                for node in G1.neighbors(next_node):
                    used_degrees[node] += 1

                dlevel_nodes.remove(next_node)
                label_rarity[G1_labels[next_node]] -= 1
                V1_unordered.discard(next_node)

    return node_order


def _rarest_nodes(V1_unordered, G1_labels, label_rarity):
    rare = []
    rarest = float("inf")
    for n in V1_unordered:
        if label_rarity[G1_labels[n]] < rarest:
            rarest = label_rarity[G1_labels[n]]
            rare = [n]
            continue
        if label_rarity[G1_labels[n]] == rarest:
            rare.append(n)

    return rare
