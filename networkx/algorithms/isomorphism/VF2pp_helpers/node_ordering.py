import networkx as nx


def matching_order(G1, G2, G1_labels, G2_labels):
    nodes_of_G1Labels, nodes_of_G2Labels, V1_unordered, current_labels = initialise_preprocess(G1, G2, G1_labels,
                                                                                               G2_labels)
    used_degrees = {node: 0 for node in G1}
    node_order = []

    while V1_unordered:
        rare_nodes = min(nx.utils.groups(current_labels).values(), key=len)
        max_node = max(rare_nodes, key=G1.degree)
        label_rarity = {label: len(nodes) for label, nodes in nodes_of_G2Labels.items()}

        node_order, label_rarity, dlevel_nodes, used_degrees, V1_unordered = \
            BFS_levels(max_node, G1, G1_labels, V1_unordered, label_rarity, used_degrees, node_order)

        node_order.append(max_node)
        V1_unordered.discard(max_node)
        del current_labels[max_node]

    return node_order


def initialise_preprocess(G1, G2, G1_labels, G2_labels):
    nodes_of_G1Labels = nx.utils.groups(G1_labels)
    nodes_of_G2Labels = nx.utils.groups(G2_labels)

    V1_unordered = set(G1)
    current_labels = {node: G1_labels[node] for node in V1_unordered}
    return nodes_of_G1Labels, nodes_of_G2Labels, V1_unordered, current_labels


def BFS_levels(source_node, G1, G1_labels, V1_unordered, label_rarity, used_degrees, node_order):
    dlevel_nodes = set()
    for node, nbr in nx.bfs_edges(G1, source_node):
        if node not in dlevel_nodes:  # This checks for when we finish one depth of the BFS
            dlevel_nodes.add(nbr)
            continue

        node_order, label_rarity, _, used_degrees, V1_unordered = \
            process_level(V1_unordered, G1, G1_labels, node_order, dlevel_nodes, label_rarity, used_degrees)

        # initialize next level to indicate that we finished the next depth of the BFS
        V1_unordered -= dlevel_nodes
        dlevel_nodes = {nbr}
    # Process the last level
    return process_level(V1_unordered, G1, G1_labels, node_order, dlevel_nodes, label_rarity, used_degrees)


def process_level(V1, G1, G1_labels, order, dlevel_nodes, label_rarity, used_degree):
    max_nodes = []
    while dlevel_nodes:
        # Get the nodes with the max used_degree
        max_used_deg = -1
        for node in dlevel_nodes:
            deg = used_degree[node]
            if deg >= max_used_deg:  # most common case: deg < max_deg
                if deg > max_used_deg:
                    max_used_deg = deg
                    max_nodes = [node]
                else:  # deg == max_deg
                    max_nodes.append(node)

        # max_conn = max(len([v for v in G1[u]]) for u in dlevel_nodes)
        # max_conn_nodes = [v for v in dlevel_nodes if len([k for k in G1[v]]) == max_conn]
        #
        # max_deg = max(G1.degree[u] for u in max_conn_nodes)
        # max_nodes = [n for n in max_conn_nodes if G1.degree[n] == max_deg]

        # Get the max_used_degree node with the rarest label
        next_node = min(max_nodes, key=lambda x: label_rarity[G1_labels[x]])
        order.append(next_node)

        for node in G1.neighbors(next_node):
            used_degree[node] += 1

        dlevel_nodes.remove(next_node)
        label_rarity[G1_labels[next_node]] -= 1
        V1.remove(next_node)
    return order, label_rarity, dlevel_nodes, used_degree, V1
