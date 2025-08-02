"""
====================
3D Facebook Network
====================

Visualizing a subsampled 2500-edge subgraph of the  Facebook graph investigated in
<https://networkx.org/nx-guides/content/exploratory_notebooks/facebook_notebook.html>
in 3D plotting with matplotlib.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import animation
import pandas as pd
import random

# The graph to plot
facebook = pd.read_csv(
    # Dataset from the SNAP database
    "https://snap.stanford.edu/data/facebook_combined.txt.gz",
    compression="gzip",
    sep=" ",
    names=["start_node", "end_node"],
)

# Randomly select 50% of the edges
rng = np.random.default_rng()
G = nx.from_edgelist(rng.choice(facebook, size=2500, replace=False))

# Generate layout of the graph using spring_layout in 3D
pos = nx.spring_layout(
    G,
    iterations=30,  # Convergence expected
    dim=3,
    seed=1721,
)

# Getting nodes and edges into the right format for matplotlib
nodes = np.array([pos[v] for v in G])
edges = np.array([(pos[u], pos[v]) for u, v in G.edges()])
point_size = 1000 // np.sqrt(len(G))


def init():
    ax.clear()
    ax.scatter(*nodes.T, alpha=0.2, s=point_size, ec="w")
    for vizedge in edges:
        ax.plot(*vizedge.T, color="tab:gray")


def _frame_update(idx):
    ax.view_init(idx * 0.2, idx * 0.5)


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.view_init(20, 11)
ax.clear()
ax.grid(False)
ax.set_axis_off()
fig.tight_layout()

anim = animation.FuncAnimation(
    fig,
    func=_frame_update,
    init_func=init,
    interval=50,
    cache_frame_data=False,
    frames=100,
)

plt.show()
