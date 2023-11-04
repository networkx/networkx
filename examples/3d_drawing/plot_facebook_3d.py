"""
====================
3D Facebook Network
====================
3D spring plot for the (reduced to 5000 nodes) Facebook graph investigated at https://networkx.org/nx-guides/content/exploratory_notebooks/facebook_notebook.html.
The plots is shown rotating. One can see a slightly better clustering than the coreesponding spring layout in 2D.
"""
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import animation
import pandas as pd

# The graph to plot
facebook = pd.read_csv(
    "./facebook_combined_shortened.txt.gz",
    compression="gzip",
    sep=" ",
    names=["start_node", "end_node"],
)
# Generate graph from CSV data
G = nx.from_pandas_edgelist(facebook, "start_node", "end_node")

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

###############################################################################
# Rotating 3D graph animation.
# ----------------------------
#
# In this example, a frame update is only a rotation of a given 3D graph.


def init():
    ax.scatter(*nodes.T, alpha=0.2, s=point_size, ec="w")
    for vizedge in edges:
        ax.plot(*vizedge.T, color="tab:gray")
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
plt.show()
