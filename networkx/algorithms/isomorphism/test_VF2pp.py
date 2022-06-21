import random
import time

import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


def main():
    G = nx.gnp_random_graph(100, 0.15, seed=19)
    colors = ["blue", "red", "green", "orange", "grey", "yellow", "purple", "black", "white"]

    for i in range(len(G.nodes)):
        G.nodes[i]["label"] = colors[random.randrange(len(colors))]

    # pos = graphviz_layout(G, prog='dot')
    # nx.draw(G, pos, with_labels=True, arrows=False)
    # plt.show()

    L = node_labels(G)

    t0 = time.time()
    M = matching_order(G, G, L)
    print('Elapsed time: ', time.time() - t0)

    t0 = time.time()
    M2 = matching_order2(G, G, L)
    print('Elapsed time: ', time.time() - t0)

    print("len= ", len(M))
    print(M)
    print("len= ", len(M2))
    print(M2)

    if len(M) != len(M2):
        print("ERROR")
        exit(0)

    for m1, m2 in zip(M, M2):
        if m1 != m2:
            print("ERROR")
            exit(0)

    print("CORRECT")


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
        print("nds ", nodes_with_most_ordered_neighbors)

        # print(nodes_with_most_ordered_neighbors)
        max_degree_nodes = [max(nodes_with_most_ordered_neighbors, key=G1.degree)]
        print("max= ", max_degree_nodes)
        labels = {node: G1.nodes[node]["label"] for node in max_degree_nodes}
        print("rarity ", label_nodes(labels).values())
        rarest_node = min(label_nodes(labels).values(), key=len)
        # m = argmin_F(G2, M, L, argmax_degree(G1, argmax_connectivity(G1, Vd, M)))
        print("rare= ", rarest_node)
        for node in rarest_node:
            Vd.remove(node)
            M.append(node)
    return M


def matching_order(G1, G2, L):
    V1_unordered = set(G1)
    current_labels = {node: node_labels(G1)[node] for node in V1_unordered}
    M = []
    while V1_unordered:
        rare_nodes = min(label_nodes(current_labels).values(), key=len)
        best_nodes = max(rare_nodes, key=G1.degree)
        T, M, V1_unordered = dlevel_bfs_tree(G1, G2, M, L, V1_unordered, best_nodes)
        del current_labels[best_nodes]
    return M


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
