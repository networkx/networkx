import random
import time

import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


def Dan(G1, G2, L):
    G1_labels = nx.get_node_attributes(G1, "label")  # a dict keyed by node to label
    G2_labels = nx.get_node_attributes(G2, "label")
    nodes_by_G1labels = nx.utils.groups(G1_labels)  # a dict keyed by label to list of nodes with that label
    nodes_by_G2labels = nx.utils.groups(G2_labels)

    V1_not_in_order = set(G1)
    # Get the labels of every node not in the order yet
    current_labels = {node: G1_labels[node] for node in V1_not_in_order}
    order = []
    used_degree = {node: 0 for node in G1}
    while V1_not_in_order:
        # Get the nodes with the rarest label
        # groups() returns a dict keyed by label to the set of nodes with that label
        rare_nodes = min(nx.utils.groups(current_labels).values(), key=len)

        # Get the node from this list with the highest degree
        max_node = max(rare_nodes, key=G1.degree)

        label_rarity = {a_label: len(nodes) for a_label, nodes in nodes_by_G2labels.items()}

        # consider nodes at each depth from max_node
        current_nodes = set()
        for node, nbr in nx.bfs_edges(G1, max_node):
            if node not in current_nodes:  # This checks for when we finish one depth of the BFS
                current_nodes.add(nbr)
                continue
            # process current level's nodes
            order, label_rarity, _, used_degree, V1_not_in_order = _process_level(V1_not_in_order, G1, G1_labels, order, current_nodes, label_rarity, used_degree)

            # initialize next level to indicate that we finished the next depth of the BFS
            V1_not_in_order -= current_nodes
            current_nodes = {nbr}

        # Process the last level
        order, label_rarity, current_nodes, used_degree, V1_not_in_order = _process_level(V1_not_in_order, G1, G1_labels, order, current_nodes, label_rarity, used_degree)
        # V1_not_in_order -= current_nodes
        # Add the root node of this component
        order.append(max_node)
        V1_not_in_order.discard(max_node)
        del current_labels[max_node]

    return order


def _process_level(V1, G1, G1_labels, order, current_nodes, label_rarity, used_degree):
    """Update order, label_rarity and used_degree"""
    max_nodes = []
    while current_nodes:
        # Get the nodes with the max used_degree
        max_used_deg = -1
        for node in current_nodes:
            deg = used_degree[node]
            if deg >= max_used_deg:  # most common case: deg < max_deg
                if deg > max_used_deg:
                    max_used_deg = deg
                    max_nodes = [node]
                else:  # deg == max_deg
                    max_nodes.append(node)

        # Get the max_used_degree node with the rarest label
        next_node = min(max_nodes, key=lambda x: label_rarity[G1_labels[x]])
        order.append(next_node)

        for node in G1.neighbors(next_node):
            used_degree[node] += 1

        current_nodes.remove(next_node)
        label_rarity[G1_labels[next_node]] -= 1
        V1.remove(next_node)
    return order, label_rarity, current_nodes, used_degree, V1



def main():
    G = nx.gnp_random_graph(50, 0.25, seed=19)
    colors = ["blue", "red", "green", "orange", "grey", "yellow", "purple", "black", "white"]

    for i in range(len(G.nodes)):
        G.nodes[i]["label"] = colors[random.randrange(len(colors))]

    L = node_labels(G)

    M = Dan(G, G, L)
    print(len(M))
    print(M)

    # t0 = time.time()
    M = matching_order(G, G, L)
    # print('Elapsed time: ', time.time() - t0)

    print("len= ", len(M))
    print(M)

    # print("len= ", len(M2))
    # print(M2)

    # if len(M) != len(M2):
    #     print("ERROR")
    #     exit(0)
    #
    # for m1, m2 in zip(M, M2):
    #     if m1 != m2:
    #         print("ERROR")
    #         exit(0)
    #
    # print("CORRECT")


def connectivity(G, u, H):
    return len([v for v in G[u] if v in H])


def node_labels(G):
    return nx.get_node_attributes(G, "label")


def label_nodes(labels):
    return nx.utils.groups(labels)


def F(G2, M, L, label):
    # If no label function is considered, F should not be used in determining the matching order.
    card1 = len([u for u in G2.nodes if L[u] == label])
    card2 = len([v for v in M if L[v] == label])
    return card1 - card2


def argmin_F(G2, M, L, S):
    min_unmatched_nodes = min(F(G2, M, L, L[u]) for u in S)
    return [v for v in S if F(G2, M, L, L[v]) == min_unmatched_nodes]


def argmax_degree(G1, S):
    max_degree = max(G1.degree[node] for node in S)
    return [u for u in S if G1.degree[u] == max_degree]


def argmax_connectivity(G, Vd, M):
    max_conn = max(connectivity(G, v, M) for v in Vd)
    return [v for v in Vd if connectivity(G, v, M) == max_conn]


def process_level2(G1, G2, Vd, M, L):
    while len(Vd) > 0:
        # nodes_with_most_ordered_neighbors = [max(G1.nodes, key=lambda n: connectivity(G1, n, Vd))]
        nodes_with_most_ordered_neighbors = argmax_connectivity(G1, Vd, M)
        # print("Vd= ", Vd)/
        # print("nds ", nodes_with_most_ordered_neighbors)

        # print(nodes_with_most_ordered_neighbors)
        max_degree_nodes = [max(nodes_with_most_ordered_neighbors, key=G1.degree)]
        # print("max= ", max_degree_nodes)
        labels = {node: G1.nodes[node]["label"] for node in max_degree_nodes}
        # print("rarity ", label_nodes(labels).values())
        rarest_node = min(label_nodes(labels).values(), key=len)
        # m = argmin_F(G2, M, L, argmax_degree(G1, argmax_connectivity(G1, Vd, M)))
        # print("rare= ", rarest_node)
        for node in rarest_node:
            Vd.remove(node)
            M.append(node)
    return M


def matching_order(G1, G2, L):
    V1_unordered = set(G1)
    current_labels = {node: node_labels(G1)[node] for node in V1_unordered}
    # print(V1_unordered)
    # print(current_labels)
    M = []
    while V1_unordered:
        rare_nodes = min(label_nodes(current_labels).values(), key=len)
        best_nodes = max(rare_nodes, key=G1.degree)
        # print("best ", best_nodes)
        T, M, V1_unordered = dlevel_bfs_tree(G1, G2, M, L, V1_unordered, best_nodes)
        del current_labels[best_nodes]
    return M


def matching_order3(G1, G2, L):
    V1_unordered = set(G1)
    current_labels = {node: node_labels(G1)[node] for node in V1_unordered}
    # print(V1_unordered)
    # print(current_labels)
    M = []
    used_degrees = {node: 0 for node in G1}
    while V1_unordered:
        rare_nodes = min(label_nodes(current_labels).values(), key=len)
        max_degree_node = max(rare_nodes, key=G1.degree)
        # print("best ", best_nodes)
        node_rarity = {label: len(nodes) for label, nodes in label_nodes(current_labels).items()}
        dlevel_nodes = set()
        for node, nbr in nx.bfs_edges(G1, max_degree_node):
            if node not in dlevel_nodes:
                dlevel_nodes.add(node)
                continue
            process_level3(G1, G2, dlevel_nodes, M, L, node_rarity, used_degrees)

        # print(node_rarity)
        # T, M, V1_unordered = dlevel_bfs_tree(G1, G2, M, L, V1_unordered, best_nodes)
        # del current_labels[best_nodes]
    return M


def process_level3(G1, G2, dlevel_nodes, M, L, node_rarity, used_degrees):
    # max_nodes = []
    while dlevel_nodes:

        max_degree_nodes = argmax_connectivity(G1, dlevel_nodes, M)
        print("max1 = ", max_degree_nodes)

        # max_used_deg = -1
        # for node in dlevel_nodes:
        #     deg = used_degrees[node]
        #     if deg >= max_used_deg:  # most common case: deg < max_deg
        #         if deg > max_used_deg:
        #             max_used_deg = deg
        #             max_nodes = [node]
        #         else:  # deg == max_deg
        #             max_nodes.append(node)
        # print("max2 = ", max_nodes)

        # next_node = min(max_nodes, key=lambda x: node_rarity[node_labels(G1)[x]])
        # print("nxt1 = ", next_node)
        next_node = min(max_degree_nodes, key=lambda x: node_rarity[node_labels(G1)[x]])
        print("nxt2 = ", next_node)
        M.append(next_node)

        dlevel_nodes.remove(next_node)
        node_rarity[node_labels(G1)[next_node]] -= 1



def dlevel_bfs_tree(G1, G2, M, L, V1_unordered, source):
    # todo: optimize descendants_at_distance. Compute all levels once. distance(2) re-computes distance(1).
    d = 0
    T = []
    d_level_successors = nx.descendants_at_distance(G1, source=source, distance=d)
    while len(d_level_successors) > 0:
        T.append(d_level_successors)
        M = process_level(G1, G2, d_level_successors, M, L)
        V1_unordered -= set(M)
        d += 1
        d_level_successors = nx.descendants_at_distance(G1, source=source, distance=d)
    return T, M, V1_unordered


def process_level(G1, G2, Vd, M, L):
    while len(Vd) > 0:
        m = argmin_F(G2, M, L, argmax_degree(G1, argmax_connectivity(G1, Vd, M)))
        # print("m ", m)
        for node in m:
            Vd.remove(node)
            M.append(node)
    return M


"""
Second version
"""
def matching_order2(G1, G2, L):
    V1_unordered = set(G1)
    current_labels = {node: node_labels(G1)[node] for node in V1_unordered}
    M = []
    while V1_unordered:
        rare_nodes = min(label_nodes(current_labels).values(), key=len)
        best_nodes = max(rare_nodes, key=G1.degree)
        T, M, V1_unordered = dlevel_bfs_tree2(G1, G2, M, L, V1_unordered, best_nodes)
        del current_labels[best_nodes]
    return M


def dlevel_bfs_tree2(G1, G2, M, L, V1_unordered, source):
    # todo: optimize descendants_at_distance. Compute all levels once. distance(2) re-computes distance(1).
    d = 0
    T = []
    d_level_successors = nx.descendants_at_distance(G1, source=source, distance=d)
    while len(d_level_successors) > 0:
        T.append(d_level_successors)
        M = process_level2(G1, G2, d_level_successors, M, L)
        V1_unordered -= set(M)
        d += 1
        d_level_successors = nx.descendants_at_distance(G1, source=source, distance=d)
    return T, M, V1_unordered


def binary_tree():
    T = nx.DiGraph()
    T.add_node(0)
    offset = 4
    for i in range(1, 5):
        T.add_node(i)
        T.add_edge(0, i)
        for j in range(2):
            T.add_node(i + j + offset)
            T.add_edge(i, i + j + offset)
        offset += 1
    return T


main()
