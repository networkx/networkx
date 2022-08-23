import time

import networkx as nx

# Graph initialization
G1 = nx.gnp_random_graph(500, 0.6, seed=42)
G2 = nx.gnp_random_graph(500, 0.6, seed=42)

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

# VF2++ initialization
# c = 0
# for node in G1.nodes():
#     # if c == 400:
#     #     break
#     # if c % 3 == 0:
#     #     G1.nodes[node]["label"] = -1
#     #     G2.nodes[node]["label"] = -1
#     G1.nodes[node]["color"] = "blue"
#     G2.nodes[node]["color"] = "blue"
#     c += 1

# VF2++
t0 = time.time()
m = nx.vf2pp_is_isomorphic(G1, G2, node_labels=None)
print(f"VF2++ elapsed time: {time.time() - t0}")

print(nx.get_node_attributes(G1, "label"))
print(m)

# G1 = nx.MultiGraph([(0, 0), (0, 1), (0, 2)])
# uncovered_neighbors_G1 = {nbr for nbr in G1[0]}
#
# T1 = {0}
#
# T1.update(uncovered_neighbors_G1)
# T1.discard(0)
# print(T1)
