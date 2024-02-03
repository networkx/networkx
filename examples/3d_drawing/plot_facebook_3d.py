"""
====================
3D Facebook Network
====================

Visualizing a 5000-node subgraph of the  Facebook graph investigated in
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
    "./facebook_combined_shortened.txt.gz",
    compression="gzip",
    sep=" ",
    names=["start_node", "end_node"],
)

# Randomly select 10% of the edges
rng = np.random.default_rng()
G = nx.from_edgelist(rng.choice(facebook, size=500, replace=False))

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
point_size = int(1000 / np.sqrt(len(nodes)))

# generating the plot
num_frames = 15
azi_step = np.linspace(0, min(360,num_frames*5), num_frames, endpoint=False).astype(int)
elev_step = np.linspace(0, min(360,num_frames*5), num_frames, endpoint=False).astype(int)


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")


def init():
    ax.clear()
    # Initialize the 3D scatter plot with nodes, edges, and formatting.
    ax.scatter(*nodes.T, alpha=0.2, s=point_size, ec="w")
    for vizedge in edges:
        ax.plot(*vizedge.T, color="tab:gray")
    ax.grid(False)
    ax.set_axis_off()

    plt.tight_layout()
    return


def _frame_update(index):
    # Update the view of the 3D plot with specified azimuthal and elevation angles.
    ax.view_init(elev_step[index], azi_step[index])
    return


# Create the 3D animation
ani = animation.FuncAnimation(
    fig,
    _frame_update,
    init_func=init,
    interval=100,
    cache_frame_data=True,
    frames=num_frames
)
plt.show()
