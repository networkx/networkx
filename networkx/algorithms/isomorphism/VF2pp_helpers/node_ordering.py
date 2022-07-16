import networkx as nx


def matching_order(G1, G2, G1_labels, G2_labels):
    """The node ordering as introduced in VF2++.

    Notes
    -----
    Taking into account the structure of the Graph and the node labeling, the nodes are placed in an order such that,
    most of the unfruitful/infeasible branches of the search space can be pruned on high levels, significantly
    decreasing the number of visited states. The premise is that, the algorithm will be able to recognize
    inconsistencies early, proceeding to go deep into the search tree only if it's needed.

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.

    Returns
    -------
    node_order: list
        The ordering of the nodes.
    """
    if not G1 and not G2:
        return {}

    (nodes_of_G1Labels, nodes_of_G2Labels, V1_unordered) = initialise_preprocess(
        G1, G1_labels, G2_labels
    )
    label_rarity = {label: len(nodes) for label, nodes in nodes_of_G2Labels.items()}
    used_degrees = {node: 0 for node in G1}
    node_order = []

    while V1_unordered:
        # nodes_of_current_labels = nx.utils.groups(current_labels)
        rarest_node = min(V1_unordered, key=lambda x: label_rarity[G1_labels[x]])
        rare_nodes = [
            n
            for n in V1_unordered
            if label_rarity[G1_labels[n]] == label_rarity[G1_labels[rarest_node]]
        ]
        # max_rarity = min(len(v) for v in nodes_of_current_labels.values())
        # rare_nodes = {u for l, nodes in nodes_of_current_labels.items() for u in nodes if len(nodes) == max_rarity}
        max_node = max(rare_nodes, key=G1.degree)

        (
            node_order,
            label_rarity,
            dlevel_nodes,
            used_degrees,
            V1_unordered,
        ) = BFS_levels(
            max_node,
            G1,
            G1_labels,
            V1_unordered,
            label_rarity,
            used_degrees,
            node_order,
        )

        node_order.append(max_node)
        V1_unordered.discard(max_node)
        label_rarity[G1_labels[max_node]] -= 1  # todo: do we need that?

    return node_order


def BFS_levels(
    source_node, G1, G1_labels, V1_unordered, label_rarity, used_degree, node_order
):
    """Performs a BFS search, storing and processing each level of the BFS, separately.

    Parameters
    ----------
    source_node: int
        The node from which the BFS starts.

    G1: NetworkX Graph or MultiGraph instances.
        The graph on which the BFS is performed.

    G1_labels: dict
        The label of every node in G1.

    V1_unordered: set
        The nodes from G1 that are not ordered yet.

    label_rarity: dict
        Contains the number of nodes that have a specific label. Labels are used as keys.

    used_degree: dict
        Nodes are used as keys. Indicates how many neighbors of each node have been ordered.

    node_order: list
        Contains all the nodes that have been ordered until now.

    Returns
    -------
    @see process_level
    """
    dlevel_nodes = set()
    for node, nbr in nx.bfs_edges(G1, source_node):
        if (
            node not in dlevel_nodes
        ):  # This checks for when we finish one depth of the BFS
            dlevel_nodes.add(nbr)
            continue

        (node_order, label_rarity, _, used_degree, V1_unordered) = process_level(
            V1_unordered,
            G1,
            G1_labels,
            node_order,
            dlevel_nodes,
            label_rarity,
            used_degree,
        )

        # initialize next level to indicate that we finished the next depth of the BFS
        V1_unordered -= dlevel_nodes
        dlevel_nodes = {nbr}
    # Process the last level
    return process_level(
        V1_unordered, G1, G1_labels, node_order, dlevel_nodes, label_rarity, used_degree
    )


def process_level(
    V1_unordered, G1, G1_labels, order, dlevel_nodes, label_rarity, used_degree
):
    """Processes the nodes of a BFS level.

    Parameters
    ----------
    V1_unordered: set
        The nodes from G1 that are not ordered yet.

    G1: NetworkX Graph or MultiGraph instances.
        The graph on which the BFS is performed.

    G1_labels: dict
        The label of every node in G1.

    order: list
        Contains all the nodes that have been ordered until now.

    dlevel_nodes: set
        Contains the nodes of a BFS level.

    label_rarity: dict
        Contains the number of nodes that have a specific label. Labels are used as keys.

    used_degree: dict
        Nodes are used as keys. Indicates how many neighbors of each node have been ordered.

    Returns
    -------
    The updated order, label_rarity, dlevel_nodes, used_degree, V1_unordered
    """
    max_nodes = []
    max_degree = 0
    while dlevel_nodes:
        # Get the nodes with the max used_degree
        max_used_deg = -1
        for node in dlevel_nodes:
            deg = used_degree[node]
            if deg >= max_used_deg:  # most common case: deg < max_deg
                if deg > max_used_deg:
                    max_used_deg = deg
                    max_nodes = [node]
                    max_degree = G1.degree[node]
                else:  # deg == max_deg
                    max_nodes.append(node)
                    if G1.degree[node] > max_degree:
                        max_degree = G1.degree[node]

        # Get the max_used_degree node with the rarest label
        max_deg_nodes = [
            node for node in max_nodes if G1.degree[node] == max_degree
        ]  # todo: this can be computed on the go
        next_node = min(max_deg_nodes, key=lambda x: label_rarity[G1_labels[x]])
        order.append(next_node)

        for node in G1.neighbors(next_node):
            used_degree[node] += 1

        dlevel_nodes.remove(next_node)
        label_rarity[G1_labels[next_node]] -= 1
        V1_unordered.discard(next_node)
    return order, label_rarity, dlevel_nodes, used_degree, V1_unordered


def initialise_preprocess(G1, G1_labels, G2_labels):
    """Initializes basic information, needed for the ordering

    Parameters
    ----------
    G1: NetworkX Graph or MultiGraph instances.
        The graph on which the BFS is performed.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.
    """
    nodes_of_G1Labels = nx.utils.groups(G1_labels)
    nodes_of_G2Labels = nx.utils.groups(G2_labels)

    V1_unordered = set(G1)
    return nodes_of_G1Labels, nodes_of_G2Labels, V1_unordered
