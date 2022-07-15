import os
import networkx as nx


def matching_order(G1, G2, G1_labels, G2_labels):
    if not G1 and not G2:
        return {}

    (
        nodes_of_G1Labels,
        nodes_of_G2Labels,
        V1_unordered,
        current_labels,
    ) = initialise_preprocess(G1, G2, G1_labels, G2_labels)
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
            current_labels,
        ) = BFS_levels(
            max_node,
            G1,
            G1_labels,
            V1_unordered,
            label_rarity,
            used_degrees,
            node_order,
            current_labels,
        )

        node_order.append(max_node)
        V1_unordered.discard(max_node)
        current_labels.pop(max_node)
        label_rarity[G1_labels[max_node]] -= 1  # todo: do we need that?

    return node_order


def BFS_levels(
    source_node,
    G1,
    G1_labels,
    V1_unordered,
    label_rarity,
    used_degrees,
    node_order,
    current_labels,
):
    dlevel_nodes = set()
    for node, nbr in nx.bfs_edges(G1, source_node):
        if (
            node not in dlevel_nodes
        ):  # This checks for when we finish one depth of the BFS
            dlevel_nodes.add(nbr)
            continue

        (
            node_order,
            label_rarity,
            _,
            used_degrees,
            V1_unordered,
            current_labels,
        ) = process_level(
            V1_unordered,
            G1,
            G1_labels,
            node_order,
            dlevel_nodes,
            label_rarity,
            used_degrees,
            current_labels,
        )

        # initialize next level to indicate that we finished the next depth of the BFS
        V1_unordered -= dlevel_nodes
        dlevel_nodes = {nbr}
    # Process the last level
    return process_level(
        V1_unordered,
        G1,
        G1_labels,
        node_order,
        dlevel_nodes,
        label_rarity,
        used_degrees,
        current_labels,
    )


def process_level(
    V1, G1, G1_labels, order, dlevel_nodes, label_rarity, used_degree, current_labels
):
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
        current_labels.pop(next_node)

        for node in G1.neighbors(next_node):
            used_degree[node] += 1

        dlevel_nodes.remove(next_node)
        label_rarity[G1_labels[next_node]] -= 1
        V1.discard(next_node)
    return order, label_rarity, dlevel_nodes, used_degree, V1, current_labels


def initialise_preprocess(G1, G2, G1_labels, G2_labels):
    nodes_of_G1Labels = nx.utils.groups(G1_labels)
    nodes_of_G2Labels = nx.utils.groups(G2_labels)

    V1_unordered = set(G1)
    current_labels = {node: G1_labels[node] for node in V1_unordered}
    return nodes_of_G1Labels, nodes_of_G2Labels, V1_unordered, current_labels
