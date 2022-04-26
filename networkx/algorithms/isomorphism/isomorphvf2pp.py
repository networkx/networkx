"""
***************
VF2++ Algorithm
***************

Implementation of the VF2++ algorithm for the Graph Isomorphism problem.
"""
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


def main():
    # T = binary_tree()
    T = nx.gnp_random_graph(20, 0.24, seed=23)

    # pos = graphviz_layout(T, prog='dot')
    # nx.draw(T, pos, with_labels=True, arrows=False)
    # plt.show()

    M = matching_order(G1=T, G2=None)
    print('M:', M)


def connectivity(G, u, H):
    return len([v for v in G[u] if v in H])


def F(G2, M, L, l):
    # todo: if L is indexed via nodes and not node indices, replace L[i] with L[u].
    # If no label function is considered, F should not be used in determining the matching order.
    card1 = len([u for i, u in enumerate(G2.nodes) if L[i] == l])
    card2 = len([v for i, v in enumerate(M) if L[i] == l])
    return card1 - card2


def arg_max_degree(G1, S):
    # todo: for every node, take degree in G1 or in S ?
    max_degree = max(G1.degree[node] for node in S)
    return [u for u in S if G1.degree[u] == max_degree]


def arg_max_connectivity(G, Vd, M):
    max_conn = max(connectivity(G, v, M) for v in Vd)
    return [v for v in Vd if connectivity(G, v, M) == max_conn]


def process_level(G, Vd, M):
    # todo: add FM(L) filter as well (argminFM(L)).
    while len(Vd) > 0:
        m = arg_max_degree(G, arg_max_connectivity(G, Vd, M))
        for node in m:
            Vd.remove(node)
            M.append(node)
    return M


def matching_order(G1, G2):
    V1 = G1.nodes
    M = []
    while len(set(V1) - set(M)) > 0:
        S = set(V1) - set(M)
        r = arg_max_degree(G1, S)
        for node in r:
            T = d_level_bfs_tree(G1, source=node)
            for Vd in T:
                M = process_level(G1, Vd, M)
    return M


def d_level_bfs_tree(G, source):
    # todo: when the d-th level is computed, immediately call 'process_level', to avoid redundant iterations/operations.
    d = 0
    T = []
    d_level_successors = nx.descendants_at_distance(G, source=source, distance=d)
    while len(d_level_successors) > 0:
        T.append(d_level_successors)
        d += 1
        d_level_successors = nx.descendants_at_distance(G, source=source, distance=d)
    return T


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
