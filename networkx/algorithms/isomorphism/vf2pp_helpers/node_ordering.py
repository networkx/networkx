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

        _bfs_levels(
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


def _bfs_levels(
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
    """
    dlevel_nodes = set()
    for node, nbr in nx.bfs_edges(G1, source_node):
        if (
            node not in dlevel_nodes
        ):  # This checks for when we finish one depth of the BFS
            dlevel_nodes.add(nbr)
            continue

        _process_level(
            V1_unordered,
            G1,
            G1_labels,
            node_order,
            dlevel_nodes,
            label_rarity,
            used_degree,
        )

        # initialize next level to indicate that we finished the next depth of the BFS
        V1_unordered.difference_update(dlevel_nodes)
        dlevel_nodes = {nbr}
    # Process the last level
    _process_level(
        V1_unordered, G1, G1_labels, node_order, dlevel_nodes, label_rarity, used_degree
    )


def _process_level(
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
    """
    max_nodes = []
    max_deg_nodes = []
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
                    max_deg_nodes = [node]
                else:  # deg == max_deg
                    max_nodes.append(node)
                    deg = G1.degree[node]
                    if deg > max_degree:
                        max_degree = deg
                        max_deg_nodes = [node]
                    elif deg == max_degree:
                        max_deg_nodes.append(node)

        # Get the max_used_degree node with the rarest label
        next_node = min(max_deg_nodes, key=lambda x: label_rarity[G1_labels[x]])
        order.append(next_node)

        for node in G1.neighbors(next_node):
            used_degree[node] += 1

        dlevel_nodes.remove(next_node)
        label_rarity[G1_labels[next_node]] -= 1
        V1_unordered.discard(next_node)


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
