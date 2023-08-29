"""
================
3D Facebook Network Plot with Subplots
================

The 3D version of spring plot of the graph investigated at https://networkx.org/nx-guides/content/exploratory_notebooks/facebook_notebook.html

"""
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# the graph to plot
facebook = pd.read_csv(
    "./facebook_combined.txt.gz",
    compression="gzip",
    sep=" ",
    names=["start_node", "end_node"],
)
# generate graph from csv data
graph = nx.from_pandas_edgelist(facebook, "start_node", "end_node")

# generate layout of the graph using spring_layout in 3-D
pos = nx.spring_layout(
    graph,
    iterations=30,  # convergence expected
    dim=3,
    seed=1721,
)

# getting nodes and edges into right format for matplotlib
nodes = np.array([pos[v] for v in graph])
edges = np.array([(pos[u], pos[v]) for u, v in graph.edges()])


point_size = int(1000 / np.sqrt(len(nodes)))

# Create the 3D subplots
fig = plt.figure(figsize=(12, 6))
azimuthal_angles = [30, 120]  # Azimuthal angles for the three subplots

for i, angle in enumerate(azimuthal_angles):
    # Create a 3D subplot
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")

    # Plot the nodes as scatter plot
    scatter = ax.scatter(*nodes.T, s=point_size, ec="w")

    # Plot the edges
    for vizedge in edges:
        ax.plot(*vizedge.T, color="tab:gray", linewidth=0.15)

    # Turn gridlines off
    ax.grid(False)
    ax.set_axis_off()

    # Set azimuthal angle for this subplot
    ax.view_init(elev=50.0, azim=angle)

# Adjust layout
fig.tight_layout()
plt.show()
