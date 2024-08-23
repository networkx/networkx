"""
=========================================
Animations of 3D rotation and random walk
=========================================
Examples of 3D plots of a graph in the 3D spectral layout with animation.
Following
https://sphinx-gallery.github.io/stable/auto_examples/plot_8_animations.html
using frame rotation of an initial plot of a graph as in
https://matplotlib.org/stable/api/animation_api.html
or complete frame redraw to plot a random walk on the graph.

The commented out line with 'plt.show()' needs to be commented back in
in both examples when running locally.
"""

import numpy as np
import networkx as nx
import random
import matplotlib.pyplot as plt
from matplotlib import animation

###############################################################################
# Define a graph to plot.
# -----------------------
#
# Pick up a graph to look good in 3D.

G = nx.dodecahedral_graph()
pos = nx.spectral_layout(G, dim=3)
nodes = np.array([pos[v] for v in G])
edges = np.array([(pos[u], pos[v]) for u, v in G.edges()])

###############################################################################
# Rotating 3D graph animation.
# ----------------------------
#
# In this example, a frame update is only a rotation of a given 3D graph.


def init():
    ax.scatter(*nodes.T, alpha=0.2, s=100, color="blue")
    for vizedge in edges:
        ax.plot(*vizedge.T, color="gray")
    ax.grid(False)
    ax.set_axis_off()
    plt.tight_layout()
    return


def _frame_update(index):
    ax.view_init(index * 0.2, index * 0.5)
    return


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

ani = animation.FuncAnimation(
    fig,
    _frame_update,
    init_func=init,
    interval=50,
    cache_frame_data=False,
    frames=100,
)
# plt.show()

###############################################################################
# Random walk on rotating 3D graph animation.
# -------------------------------------------
#
# The frame update can also draw a new plot in every frame giving the ultimate
# flexibility at the cost of performance loss.


def _frame_update(index):
    ax.clear()
    ax.scatter(*nodes.T, alpha=0.2, s=100, color="blue")
    for vizedge in edges:
        ax.plot(*vizedge.T, color="gray")
    neighbors = list(G.neighbors(node[0]))
    if index % 5 == 0:
        node[0] = random.choice(neighbors)
    node0 = nodes[node[0]]
    ax.scatter(*node0, alpha=1, marker="s", color="red", s=100)
    ax.view_init(index * 0.2, index * 0.5)
    ax.grid(False)
    ax.set_axis_off()
    plt.tight_layout()
    return


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.grid(False)
ax.set_axis_off()
plt.tight_layout()
node = [0]
ani = animation.FuncAnimation(
    fig,
    _frame_update,
    interval=50,
    cache_frame_data=False,
    frames=100,
)
# plt.show()
