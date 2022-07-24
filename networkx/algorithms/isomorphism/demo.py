import collections
import random
import time

import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import isomorphic_VF2pp
from networkx.algorithms.isomorphism.VF2pp_helpers.node_ordering import matching_order

# # Graph initialization
# G1 = nx.gnp_random_graph(350, 0.7, 42)
# G2 = nx.gnp_random_graph(350, 0.7, 42)
# # G1, G2 = nx.Graph(), nx.Graph()
# #
# # G1_edges = [(1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5), (1, 6), (6, 7), (6, 8), (8, 9), (7, 9), (7, 10)]
# # G2_edges = [(1, 2), (2, 3), (3, 4), (1, 4), (4, 9), (9, 8), (8, 7), (7, 6), (8, 6), (9, 6), (5, 6), (5, 9), (1, 10), (1, 5)]
# #
# # G1.add_edges_from(G1_edges)
# # G2.add_edges_from(G2_edges)
# # # G1.add_node(0)
# # # G2.add_node(0)
# #
# # mapped = {1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 8: 3, 9: 2, 7: 1, 10: 10}
# #
# colors = [
#     "white",
#     "black",
#     "green",
#     "purple",
#     "orange",
#     "red",
#     "blue",
#     "pink",
#     "yellow",
#     "none",
# ]
#
# # VF2++ initialization
# for node in G1.nodes():
#     color = colors[random.randrange(0, len(colors))]
#     G1.nodes[node]["label"] = color
#     G2.nodes[node]["label"] = color
#
# G1_labels = nx.get_node_attributes(G1, "label")
# G2_labels = nx.get_node_attributes(G2, "label")
#
# # G1 = nx.Graph()
# #
# # mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
# # edges1 = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 6), (3, 4), (5, 1), (5, 2)]
# #
# # G1.add_edges_from(edges1)
# # G2 = nx.relabel_nodes(G1, mapped)
#
#
def VF2pp(G1, G2, G1_labels, G2_labels):
    try:
        m = next(isomorphic_VF2pp(G1, G2, G1_labels, G2_labels))
        return m
    except StopIteration:
        return None


#
#
# # print(G1.edges)
# # print(sorted(d for n, d in G1.degree()))
# # print(sorted(d for n, d in G2.degree()))
#
# # print(sorted(d for n, d in G1.degree()))
# # print(G1.edges)
#
#
# # VF2++
# # t0 = time.time()
# # m = VF2pp(G1, G2, G1_labels, G2_labels)
# # print(f"VF2++ elapsed time: {time.time() - t0}")
# #
# # assert m
# #
# # t0 = time.time()
# # nx.is_isomorphic(G1, G2)
# # print(f"VF2 elapsed time: {time.time() - t0}")


G1 = nx.Graph(
    [
        (1, 2),
        (1, 4),
        (1, 6),
        (1, 7),
        (1, 5),
        (2, 3),
        (2, 5),
        (2, 4),
        (3, 4),
        (3, 6),
        (4, 5),
        (5, 6),
        (5, 7),
        (6, 7),
    ]
)
G2 = nx.Graph(
    [
        (1, 2),
        (1, 5),
        (1, 6),
        (2, 3),
        (2, 4),
        (2, 7),
        (3, 6),
        (3, 7),
        (3, 4),
        (3, 5),
        (4, 6),
        (4, 5),
        (4, 7),
        (5, 6),
    ]
)

for n1, n2 in zip(G1.nodes(), G2.nodes()):
    G1.nodes[n1]["label"] = "red"
    G2.nodes[n2]["label"] = "red"

l1, l2 = nx.get_node_attributes(G1, "label"), nx.get_node_attributes(G2, "label")

# m = VF2pp(G1, G2, l1, l2)
# print(m)
print(nx.is_isomorphic(G1, G2))
