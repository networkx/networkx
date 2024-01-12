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

parameters = {
    "frames_number": 10,  # number of frames in animation
    "azimuthal_min": 0,  # initial azimuthal angle of camera drive
    "azimuthal_max": 100,  # maxmimal azimuthal angle of camera drive
    "elevation_min": 0,  # initial elevation angle of camera drive
    "elevation_max": 10,  # maximal elevation angle of camera drive
}

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

# Parameters defining the animation, feel free to play around

# Ensure that the number of frames is even
frames = parameters["frames_number"]
frames = frames + (frames % 2)

# Define the minimum and maximum azimuthal angles for camera movement.
azimuthal_min = parameters["azimuthal_min"]
azimuthal_max = parameters["azimuthal_max"]

# Define the minimum and maximum elevation angles for camera movement.
elevation_min = parameters["elevation_min"]
elevation_max = parameters["elevation_max"]

# Calculate the step size and create the angles for the first half
step_size_azimuthal = (azimuthal_max - azimuthal_min) / (frames // 2 - 1)
step_size_elevation = (elevation_max - elevation_min) / (frames // 2 - 1)
azimuthal_angles_first_half = [
    azimuthal_min + i * step_size_azimuthal for i in range(frames // 2)
]
elevation_angles_first_half = [
    elevation_min + i * step_size_elevation for i in range(frames // 2)
]

# Combine the first half with its reverse to create the complete angles
azimuthal_angles = azimuthal_angles_first_half + azimuthal_angles_first_half[::-1]
elevation_angles = elevation_angles_first_half + elevation_angles_first_half[::-1]
# generating the plot

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.scatter(*nodes.T, alpha=0.2, s=point_size, ec="w")
for vizedge in edges:
    ax.plot(*vizedge.T, color="tab:gray")
ax.grid(False)
ax.set_axis_off()
plt.tight_layout()

plt.show()  # uncomment, if you want to see the animation


def init():
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
    ax.view_init(elevation_angles[index], azimuthal_angles[index])
    return


# Create a 3D plot, set up animation, and display the plot.


ani = animation.FuncAnimation(
    fig,
    _frame_update,
    init_func=init,
    interval=50,
    cache_frame_data=False,
    frames=frames,
)
plt.show()
