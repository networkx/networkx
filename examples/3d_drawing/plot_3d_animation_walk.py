"""
====================
Animation: Node Walk
====================

NetworkX supports several 3D layout functions for visualization.
These layouts can be combined with :external+matplotlib:doc:`api/animation_api`
for 3D graph visualization.

This animation illustrates a walk along the nodes as the view rotates.

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
# Pick a graph for visualization in 3D, such as one of the Platonic solids

G = nx.dodecahedral_graph()
pos = nx.spectral_layout(G, dim=3)
nodes = np.array([pos[v] for v in G])
edges = np.array([(pos[u], pos[v]) for u, v in G.edges()])

###############################################################################
# Random walk on rotating 3D graph animation.
# -------------------------------------------
#
# Modify the plot itself along with the view, showing a wandering node that
# travels to a new neighbor every 5 frames


def init():
    ax.clear()
    ax.scatter(*nodes.T, alpha=0.2, s=100, color="blue")
    for vizedge in edges:
        ax.plot(*vizedge.T, color="gray")
    # Initialize the "walking" node
    ax.plot(*nodes[0], alpha=1, marker="s", color="red")
    ax.grid(False)
    ax.set_axis_off()


def _frame_update(index):
    global node
    # Update "current" node every 5 frames
    neighbors = list(G.neighbors(node))
    if index % 5 == 0:
        # Update node
        node = random.choice(neighbors)
        # Update the last line object, which corresponds to the walking node
        _ = ax.lines[-1].set_data_3d(nodes[node][:, np.newaxis])
    # Update view
    ax.view_init(index * 0.2, index * 0.5)


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
fig.tight_layout()
node = 0  # Initialize the walking node
ani = animation.FuncAnimation(
    fig,
    _frame_update,
    init_func=init,
    interval=50,
    cache_frame_data=False,
    frames=100,
)

plt.show()
