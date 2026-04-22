"""
===============
Greedy Coloring
===============

We attempt to color a graph using as few colors as possible, where no neighbors
of a node can have same color as the node itself.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mpl
from matplotlib import animation

G = nx.dodecahedral_graph()

# Apply greedy coloring
graph_coloring = nx.greedy_color(G)
unique_colors = set(graph_coloring.values())

# Assign colors to nodes based on the greedy coloring
graph_color_to_mpl_color = dict(zip(unique_colors, mpl.TABLEAU_COLORS))
node_colors = [graph_color_to_mpl_color[graph_coloring[n]] for n in G.nodes()]

pos = nx.spring_layout(G, seed=14)
nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=500,
    node_color=node_colors,
    edge_color="grey",
    font_size=12,
    font_color="#333333",
    width=2,
)
plt.show()
