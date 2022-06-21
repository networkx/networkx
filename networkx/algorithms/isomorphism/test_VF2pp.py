import collections
import random
import runpy
import time

import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


def main():
    G = nx.gnp_random_graph(20, 0.25, seed=42)
    colors = ["blue", "red", "green", "orange", "grey", "yellow", "purple", "black", "white"]

    for i in range(len(G.nodes)):
        G.nodes[i]["label"] = colors[random.randrange(len(colors))]

    # pos = graphviz_layout(G, prog='dot')
    # nx.draw(G, pos, with_labels=True, arrows=False)
    # plt.show()

    m = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
    for i in range(20):
        print(prune_ISO(G, G, 5, i, m))
        print(prune_IND(G, G, 5, i, m))

    # for l in colors:
    #     print(l)
    #     ul = [v for v in ul if G.nodes[v]["label"] == l]
    #     print(ul)

    # t0 = time.time()
    # M = matching_order(G, G, L)
    # print('Elapsed time: ', time.time() - t0)
    # print(M)


def connectivity(G, u, H):
    return len([v for v in G[u] if v in H])


def node_labels(G):
    return nx.get_node_attributes(G, "label")


def label_nodes(labels):
    return nx.utils.groups(labels)


def F(G2, M, L, label):
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


def prune_ISO(G1, G2, u, v, m):
    T1 = set()
    for covered_node in m:
        for neighbor in G1[covered_node]:
            if neighbor not in m:
                T1.add(neighbor)

    T2 = set()
    for covered_node in m.values():  # todo: store T1 and T2 in the state.
        for neighbor in G2[covered_node]:  # todo: should we keep the reverse mapping, instead of using values?
            if neighbor not in m.values():
                T2.add(neighbor)

    T1_out = {n1 for n1 in G1.nodes() if n1 not in m and n1 not in T1}
    T2_out = {n2 for n2 in G2.nodes() if n2 not in m.values() and n2 not in T2}

    u_neighbors_labels = {n1: G1.nodes[n1]["label"] for n1 in G1[u]}
    u_labels_neighbors = collections.OrderedDict(sorted(nx.utils.groups(u_neighbors_labels).items()))

    v_neighbors_labels = {n2: G2.nodes[n2]["label"] for n2 in G2[v]}
    v_labels_neighbors = collections.OrderedDict(sorted(nx.utils.groups(v_neighbors_labels).items()))
    # print(u_neighbors_labels)
    # print(u_labels_neighbors)
    # print(v_labels_neighbors)

    # if the neighbors of u, do not have the same labels as those of v, feasibility cannot be established.
    if set(u_labels_neighbors.keys()) != set(v_labels_neighbors.keys()):
        return False

    for nh1, nh2 in zip(u_labels_neighbors.values(), v_labels_neighbors.values()):
        if len(T1.intersection(nh1)) != len(T2.intersection(nh2)) or \
                len(T1_out.intersection(nh1)) != len(T2_out.intersection(nh2)):
            return False

    return True


def prune_IND(G1, G2, u, v, m):
    T1 = set()
    for covered_node in m:
        for neighbor in G1[covered_node]:
            if neighbor not in m:
                T1.add(neighbor)

    T2 = set()
    for covered_node in m.values():  # todo: store T1 and T2 in the state.
        for neighbor in G2[covered_node]:  # todo: should we keep the reverse mapping, instead of using values?
            if neighbor not in m.values():
                T2.add(neighbor)

    T1_out = {n1 for n1 in G1.nodes() if n1 not in m and n1 not in T1}
    T2_out = {n2 for n2 in G2.nodes() if n2 not in m.values() and n2 not in T2}

    u_neighbors_labels = {n1: G1.nodes[n1]["label"] for n1 in G1[u]}
    u_labels_neighbors = collections.OrderedDict(sorted(nx.utils.groups(u_neighbors_labels).items()))

    v_neighbors_labels = {n2: G2.nodes[n2]["label"] for n2 in G2[v]}
    v_labels_neighbors = collections.OrderedDict(sorted(nx.utils.groups(v_neighbors_labels).items()))
    # print(u_neighbors_labels)
    # print(u_labels_neighbors)
    # print(v_labels_neighbors)

    # if the neighbors of u, do not have the same labels as those of v, feasibility cannot be established.
    if set(u_labels_neighbors.keys()) != set(v_labels_neighbors.keys()):
        return False

    for nh1, nh2 in zip(u_labels_neighbors.values(), v_labels_neighbors.values()):
        if len(T1.intersection(nh1)) < len(T2.intersection(nh2)) or \
                len(T1_out.intersection(nh1)) < len(T2_out.intersection(nh2)):
            return False

    return True


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
