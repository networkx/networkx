import numpy as np
from scipy.optimize import linprog

import networkx as nx


def maximum_weight_fractional_matching(G: nx.Graph):
    if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
        return dict()
    num_nodes = len(G.nodes)
    num_edges = len(G.edges)
    c = [G.edges[edge].get("weight", 1) for edge in G.edges]
    b = [1] * num_nodes
    bounds = (-1, 0)
    index_node = {node: i for i, node in enumerate(G.nodes)}
    index_edge = {edge: i for i, edge in enumerate(G.edges)}
    A = np.zeros([num_nodes, num_edges], dtype=int)
    for edge in G.edges:
        weight = G.edges[edge].get("weight", 1)
        i_edge = index_edge[edge]
        i_node1, i_node2 = index_node[edge[0]], index_node[edge[1]]
        A[i_node1, i_edge] = -1 * weight
        A[i_node2, i_edge] = -1 * weight
    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds)
    return dict(zip(G.edges, np.abs(np.round(res.x, 3))))


if __name__ == "__main__":
    G = nx.complete_graph(4)
    res = maximum_weight_fractional_matching(G)
    print(res)
    # G = nx.Graph()
    # G.add_node(1)  # 0
    # G.add_node(2)  # 1
    # G.add_node("liel")  # 2
    # G.add_node("oriya")  # 3

    # G.add_edge(1, 2, weight=3)
    # G.add_weighted_edges_from([(1, 2, -1)])

    # G.add_edge(1, "liel")
    # G.add_edge(2, "liel")

    # G.add_weighted_edges_from([(1, 2, -1), (1, "liel", -2), (2, "liel", 3)])
    # G.add_weighted_edges_from([(1, 2, -1), (1, "liel", 5)])

    # G.add_edge(1, "oriya")
    # G.add_edge(2, "liel")
    # G.add_edge(2, "oriya")
    # G.add_edge("oriya", "liel")
    # res = maximum_weight_fractional_matching(G)
    # print(np.allclose(res, [0.5, 0.5, 0.5]))
    # print(np.round(res, 3))
    # print(res)
