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
        rarest_nodes = _all_argmax(
            V1_unordered, key_function=lambda x: -label_rarity[G1_labels[x]]
        )
        max_node = max(rarest_nodes, key=G1.degree)

        for dlevel_nodes in nx.bfs_layers(G1, max_node):
            nodes_to_add = dlevel_nodes.copy()
            while nodes_to_add:
                max_used_deg_nodes = _all_argmax(
                    nodes_to_add, key_function=lambda x: used_degrees[x]
                )
                max_deg_nodes = _all_argmax(
                    max_used_deg_nodes, key_function=lambda x: G1.degree[x]
                )
                next_node = min(max_deg_nodes, key=lambda x: label_rarity[G1_labels[x]])

                node_order.append(next_node)
                for node in G1.neighbors(next_node):
                    used_degrees[node] += 1

                nodes_to_add.remove(next_node)
                label_rarity[G1_labels[next_node]] -= 1
                V1_unordered.discard(next_node)

    return node_order


def _all_argmax(nodes, key_function):
    best_nodes = []
    best = -float("inf")
    for n in nodes:
        if key_function(n) > best:
            best = key_function(n)
            best_nodes = [n]
            continue
        if key_function(n) == best:
            best_nodes.append(n)

    return best_nodes
