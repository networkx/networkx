"""
=======================
Maximum Independent Set
=======================

An independent set is a set of vertices in a graph where no two vertices in the
set are adjacent. The maximum independent set is the independent set of largest
possible size for a given graph.
"""

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

G = nx.Graph()

G.add_nodes_from(
    [
        ("1"),
        ("2"),
        ("3"),
        ("4"),
        ("5"),
        ("6"),
        ("7"),
        ("9"),
        ("10"),
    ]
)

G.add_edges_from(
    [
        ("1", "2"),
        ("7", "2"),
        ("3", "9"),
        ("3", "2"),
        ("7", "6"),
        ("5", "2"),
        ("1", "5"),
        ("2", "8"),
        ("10", "2"),
        ("1", "7"),
        ("6", "1"),
        ("6", "9"),
        ("8", "4"),
        ("9", "4"),
    ]
)

from networkx.algorithms import approximation as apxa

I = apxa.maximum_independent_set(G)

color_map_1 = []
for node in G:
    if node in I:
        color_map_1.append("red")
    else:
        color_map_1.append("grey")
nx.draw(
    G,
    with_labels=True,
    node_size=50,
    font_size=25,
    edge_color="grey",
    node_color=color_map_1,
)

plt.show()
