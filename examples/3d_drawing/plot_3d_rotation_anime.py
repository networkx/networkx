"""
===========================
3D Rotating Graph Animation
===========================

3D animations illustrated.
"""
import numpy as np
import networkx as nx
import random
import matplotlib.pyplot as plt
from matplotlib import animation

###############################################################################
# Rotating 3D graph animation.
# ----------------------------
#
# In this example, the frame update performs only a rotation of a 3D plot
# of a given graph.


def _frame_update(index):
    ax.view_init(index * 0.2, index * 0.5)
    return


G = nx.dodecahedral_graph()
pos = nx.spectral_layout(G, dim=3)
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
pos = nx.spectral_layout(G, dim=3)
nodes = np.array([pos[v] for v in G])
edges = np.array([(pos[u], pos[v]) for u, v in G.edges()])
ax.scatter(*nodes.T, alpha=0.5, s=100)
for vizedge in edges:
    ax.plot(*vizedge.T, color="tab:gray")
ax.grid(False)
ax.set_axis_off()
plt.tight_layout()
ani = animation.FuncAnimation(
    fig,
    _frame_update,
    interval=20,
    cache_frame_data=False,
    frames=60,
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
    ax.scatter(*nodes.T, alpha=0.5, s=100)
    for vizedge in edges:
        ax.plot(*vizedge.T, color="tab:gray")
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
    interval=20,
    cache_frame_data=False,
    frames=60,
)
# plt.show()
