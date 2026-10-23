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

left_nodes = [f"A{n}" for n in range(1, 5)]
right_nodes = [f"B{n}" for n in range(1, 4)]
G = nx.complete_bipartite_graph(left_nodes, right_nodes)
pos = nx.multipartite_layout(G, subset_key={0: left_nodes, 1: right_nodes})

ha = {n: "right" if n.startswith("A") else "left" for n in G}

nx.draw(G, pos, with_labels=True, horizontalalignment=ha, node_size=0)
