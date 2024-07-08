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

###############################################################################
# 3D graph.
# ---------
#
# The same graph plotted in 3D.

pos = nx.spectral_layout(G, dim=3)
labels = list(G)
nodes = np.array([pos[v] for v in G])
edges = np.array([(pos[u], pos[v]) for u, v in G.edges()])


def init():
    ax.clear()
    ax.scatter(*nodes.T, alpha=0.9, s=500, color=node_colors)
    for vizedge in edges:
        ax.plot(*vizedge.T, color="gray")
    ax.grid(False)
    ax.set_axis_off()
    for p in pos:
        ax.text(
            *pos[p],
            labels[p],
            size=14,
            horizontalalignment="center",
            verticalalignment="center",
        )


fig = plt.figure(layout="tight")
ax = fig.add_subplot(111, projection="3d")
init()
plt.show()

###############################################################################
# Rotating 3D graph animation.
# ----------------------------
#
# Rotation of the 3D graph.


def _frame_update(index):
    ax.view_init(index * 0.2, index * 0.5)


fig = plt.figure(layout="tight")
ax = fig.add_subplot(111, projection="3d")
ax.grid(False)
ax.set_axis_off()
ani = animation.FuncAnimation(
    fig,
    _frame_update,
    init_func=init,
    interval=50,
    cache_frame_data=False,
    frames=100,
)

plt.show()
