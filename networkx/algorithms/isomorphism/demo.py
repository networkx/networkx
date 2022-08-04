import random
import time

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import VF2pp

# Graph initialization
G1 = nx.gnp_random_graph(500, 0.6, 42)
G2 = nx.gnp_random_graph(500, 0.6, 42)

colors = [
    "white",
    "black",
    "green",
    "purple",
    "orange",
    "red",
    "blue",
    "pink",
    "yellow",
    "none",
]

# VF2++ initialization
c = 0
for node in G1.nodes():
    # if c == 400:
    #     break
    # if c % 3 == 0:
    #     G1.nodes[node]["label"] = -1
    #     G2.nodes[node]["label"] = -1
    # G1.nodes[node]["color"] = "blue"
    # G2.nodes[node]["color"] = "blue"
    c += 1

# VF2++
t0 = time.time()
m = VF2pp(G1, G2, node_labels=None, default_label=-1)
print(f"VF2++ elapsed time: {time.time() - t0}")


assert m

# t0 = time.time()
# nx.is_isomorphic(G1, G2)
# print(f"VF2 elapsed time: {time.time() - t0}")

# G1 = nx.MultiGraph([(i, j) for i in range(250) for j in range(65)] * 10)
# G2 = nx.MultiGraph([(i, j) for i in range(250) for j in range(65)] * 10)
#
# for node in G1.nodes():
#     G1.nodes[node]["label"] = "blue"
#     G2.nodes[node]["label"] = "blue"
