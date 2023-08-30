"""
================
3D Facebook Network Plot 
================

3D spring plot for the Facebook graph investigated at https://networkx.org/nx-guides/content/exploratory_notebooks/facebook_notebook.html.
The plots are shown for two different azimuthal angles. One can see a slightly better clustering than the coreesponding spring layout in 2D.

"""
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# The graph to plot
facebook = pd.read_csv(
    "./facebook_combined.txt.gz",
    compression="gzip",
    sep=" ",
    names=["start_node", "end_node"],
)
# Generate graph from CSV data
graph = nx.from_pandas_edgelist(facebook, "start_node", "end_node")

# Generate layout of the graph using spring_layout in 3D
pos = nx.spring_layout(
    graph,
    iterations=30,  # Convergence expected
    dim=3,
    seed=1721,
)

# Getting nodes and edges into the right format for matplotlib
nodes = np.array([pos[v] for v in graph])
edges = np.array([(pos[u], pos[v]) for u, v in graph.edges()])

point_size = int(1000 / np.sqrt(len(nodes)))

# Create the 3D subplot
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1, projection="3d")

# Plot the nodes as a scatter plot
scatter = ax.scatter(*nodes.T, s=point_size, ec="w")

# Plot the edges
for vizedge in edges:
    ax.plot(*vizedge.T, color="tab:gray", linewidth=0.15)

# Turn gridlines off
ax.grid(False)
ax.set_axis_off()

# Set azimuthal angle
azimuthal_angle = 30
ax.view_init(elev=50.0, azim=azimuthal_angle)

# Define the rectangular region to zoom into
x_min, x_max = -0.5, 0.5
y_min, y_max = -0.5, 0.5
z_min, z_max = -0.5, 0.5

# Set limits for the zoomed region
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_zlim(z_min, z_max)


# Adjust layout
fig.tight_layout()
plt.show()  # to play around interactively a strong CPU is needed
