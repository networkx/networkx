import random
import time
import networkx as nx
from networkx.algorithms.isomorphism.VF2pp_helpers.node_ordering import matching_order
from networkx.algorithms.isomorphism.VF2pp import isomorphic_VF2pp

# Graph initialization

G1 = nx.gnp_random_graph(50, 0.65, 42)
G2 = nx.gnp_random_graph(50, 0.65, 42)

# nx.draw(G1, with_labels=True)
# plt.show()

# G1_edges = [(1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5), (1, 6), (6, 7), (6, 8), (8, 9), (7, 9)]
# G2_edges = [(1, 2), (2, 3), (3, 4), (1, 4), (4, 9), (9, 8), (8, 7), (7, 6), (8, 6), (9, 6), (5, 6), (5, 9)]

# G1.add_edges_from(G1_edges)
# G2.add_edges_from(G2_edges)
# G1.add_node(0)  # todo: problem when a node is not connected to the graph. Figure out the problem.
# G2.add_node(0)

# mapped_nodes = {0: 0, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 1, 8: 3, 9: 2}

colors = ["white", "black", "green", "purple", "orange", "red", "blue", "pink", "yellow", "none"]
# for node, color in zip(G1.nodes, colors):
#     G1.nodes[node]["label"] = color
#     G2.nodes[mapped_nodes[node]]["label"] = color

# VF2++ initialization
for node in G1.nodes():
    color = colors[random.randrange(0, len(colors))]
    G1.nodes[node]["label"] = color
    G2.nodes[node]["label"] = color

# for n in G1.nodes():
#     G1.nodes[n]["label"] = "blue"
#     G2.nodes[n]["label"] = "blue"

G1_labels = nx.get_node_attributes(G1, "label")
G2_labels = nx.get_node_attributes(G2, "label")

# Node ordering
node_order = [n for n in G1.nodes()]  # todo: dummy ordering until the issue with "match_ordering" is fixed

# VF2++
t0 = time.time()
mapping = isomorphic_VF2pp(G1, G2, G1_labels, G2_labels, node_order)
print(f"VF2++ elapsed time: {time.time() - t0}")

# node_order = [n for n in G1.nodes()]

# t0 = time.time()
# nx.is_isomorphic(G1, G2)
# print(f"VF2 elapsed time: {time.time() - t0}")

# print(mapping)
