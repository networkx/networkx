import collections
import random
import time

import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import VF2pp

# Graph initialization
G1 = nx.gnp_random_graph(350, 0.7, 42)
G2 = nx.gnp_random_graph(350, 0.7, 42)

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
for node in G1.nodes():
    color = colors[random.randrange(0, len(colors))]
    G1.nodes[node]["label"] = color
    G2.nodes[node]["label"] = color

G1_labels = nx.get_node_attributes(G1, "label")
G2_labels = nx.get_node_attributes(G2, "label")

# VF2++
t0 = time.time()
m = VF2pp(G1, G2, G1_labels, G2_labels)
print(f"VF2++ elapsed time: {time.time() - t0}")

assert m

t0 = time.time()
nx.is_isomorphic(G1, G2)
print(f"VF2 elapsed time: {time.time() - t0}")
