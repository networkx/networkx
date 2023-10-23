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
# Create a sample animation.
# --------------------------
#
# Test animation plot for testing doc generation for animation.
# Animation is copy/pasted from
# https://matplotlib.org/gallery/animation/basic_example.html
# https://sphinx-gallery.github.io/stable/auto_examples/plot_8_animations.html


def _update_line(num):
    line.set_data(data[..., :num])
    return (line,)


fig, ax = plt.subplots()
data = np.random.RandomState(0).rand(2, 25)
(line,) = ax.plot([], [], "r-")
ax.set(xlim=(0, 1), ylim=(0, 1))
ani = animation.FuncAnimation(fig, _update_line, 25, interval=100, blit=True)
# plt.show()

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
ani = animation.FuncAnimation(fig, _frame_update, interval=20, frames=60,
                              cache_frame_data=False)
# plt.show()

###############################################################################
# Random jumping on rotating 3D graph animation.
# ----------------------------------------------
#
# The frame update can also draw a new plot in every frame giving the ultimate
# flexibility at the cost of performance loss.


def _frame_update(index):
    ax.clear()
    ax.scatter(*nodes.T, alpha=0.5, s=100)
    for vizedge in edges:
        ax.plot(*vizedge.T, color="tab:gray")
    node = random.choice(nodes)
    ax.scatter(*node, alpha=1, marker="s", color="red", s=100)
    ax.view_init(index * 0.2, index * 0.5)
    ax.grid(False)
    ax.set_axis_off()
    return


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.grid(False)
ax.set_axis_off()
plt.tight_layout()
ani = animation.FuncAnimation(fig, _frame_update, interval=20, frames=60,
                              cache_frame_data=False)
# plt.show()
