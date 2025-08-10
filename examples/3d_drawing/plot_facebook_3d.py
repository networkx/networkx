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
df = pd.read_csv(
    # Dataset from the SNAP database
    "https://snap.stanford.edu/data/facebook_combined.txt.gz",
    compression="gzip",
    sep=" ",
    names=["source", "target"],
)

G = nx.from_pandas_edgelist(df)

# Extract the ego_graph for node `n`, i.e. the induced subgraph of neighbors of
# `n` within a given radius
node = 3981
radius = 2
ego = nx.ego_graph(G, node, radius)

# Generate layout of the graph using spring_layout in 3D
pos = nx.spring_layout(ego, dim=3, seed=25519, method="energy")

# Getting nodes and edges into the right format for matplotlib
nodes = np.array([pos[v] for v in ego])
edges = np.array([(pos[u], pos[v]) for u, v in ego.edges()])
point_size = 1000 // np.sqrt(len(ego))


def init():
    ax.clear()
    ax.scatter(*nodes.T, alpha=0.2, s=point_size, ec="w")
    for vizedge in edges:
        ax.plot(*vizedge.T, color="tab:gray")
    ax.grid(False)
    ax.set_axis_off()


def _frame_update(idx):
    ax.view_init(idx * 0.9, idx * 1.8)


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.clear()
fig.tight_layout()

anim = animation.FuncAnimation(
    fig,
    func=_frame_update,
    init_func=init,
    interval=50,
    cache_frame_data=False,
    frames=40,
)

plt.show()
