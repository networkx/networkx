"""
===============
Basic Animation
===============

NetworkX supports several 3D layout functions for visualization.
These layouts can be combined with :external+matplotlib:doc:`api/animation_api`
for 3D graph visualization.

This example shows a basic animation incrementing the camera view.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import animation

###############################################################################
# Define a graph to plot.
# -----------------------
#
# Pick a graph for visualization in 3D, such as one of the Platonic solids

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
    ax.clear()
    ax.scatter(*nodes.T, alpha=0.2, s=100, color="blue")
    for vizedge in edges:
        ax.plot(*vizedge.T, color="gray")
    ax.grid(False)
    ax.set_axis_off()


def _frame_update(index):
    ax.view_init(index * 0.2, index * 0.5)


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
fig.tight_layout()

ani = animation.FuncAnimation(
    fig,
    _frame_update,
    init_func=init,
    interval=50,
    cache_frame_data=False,
    frames=100,
)

plt.show()
