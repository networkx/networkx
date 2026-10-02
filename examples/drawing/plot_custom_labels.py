"""
=============
Custom Labels
=============
"""

import matplotlib.pyplot as plt
import networkx as nx

plt.figure(figsize=(4, 4))

G = nx.cycle_graph(24)
pos = nx.circular_layout(G)

rotation = {n: n * 15 for n in G.nodes()}

nx.draw(G, pos, with_labels=True, rotation=rotation)

pos = {
    "A1": (0, 3),
    "A2": (0, 2),
    "A3": (0, 1),
    "A4": (0, 0),
    "B1": (1, 2.5),
    "B2": (1, 1.5),
    "B3": (1, 0.5),
}

G = nx.DiGraph()
for a in ["A1", "A2", "A3", "A4"]:
    for b in ["B1", "B2", "B3"]:
        G.add_edge(a, b)

horizontalalignment = {n: "right" if "A" in n else "left" for n in G.nodes()}


nx.draw(
    G,
    pos,
    with_labels=True,
    horizontalalignment=horizontalalignment,
    node_size=0,
    arrowstyle="-",
)
