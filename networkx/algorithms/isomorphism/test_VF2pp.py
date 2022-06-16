import random
import time
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


def main():
    G = nx.gnp_random_graph(20, 0.25, seed=23)
    colors = ["blue", "red", "green", "orange", "grey"]

    for i in range(len(G.nodes)):
        G.nodes[i]["label"] = colors[random.randrange(len(colors))]

    # pos = graphviz_layout(G, prog='dot')
    # nx.draw(G, pos, with_labels=True, arrows=False)
    # plt.show()

    L = node_labels(G)

    t0 = time.time()
    M = matching_order(G, G, L)
    print('Elapsed time: ', time.time() - t0)
    print('Order:', M)


def connectivity(G, u, H):
    return len([v for v in G[u] if v in H])


def node_labels(G):
    return {n: G.nodes[n]["label"] for n in G.nodes()}


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


def process_level(G1, G2, Vd, M, L):
    while len(Vd) > 0:
        m = argmin_F(G2, M, L, argmax_degree(G1, argmax_connectivity(G1, Vd, M)))
        for node in m:
            Vd.remove(node)
            M.append(node)
    return M


def dlevel_bfs_tree(G, source):
    # todo: optimize descendants_at_distance. Compute all levels once. distance(2) re-computes distance(1).
    d = 0
    T = []
    d_level_successors = nx.descendants_at_distance(G, source=source, distance=d)
    while len(d_level_successors) > 0:
        T.append(d_level_successors)
        d += 1
        d_level_successors = nx.descendants_at_distance(G, source=source, distance=d)
    return T


def matching_order(G1, G2, L):
    V1 = G1.nodes
    M = []
    while len(set(V1) - set(M)) > 0:
        S = set(V1) - set(M)
        r = argmax_degree(G1, argmin_F(G2, M, L, S))
        for node in r:
            T = dlevel_bfs_tree(G1, source=node)
            for Vd in T:
                M = process_level(G1, G2, Vd, M, L)
    return M


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
