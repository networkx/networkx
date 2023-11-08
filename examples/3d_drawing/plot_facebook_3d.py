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
import random

# The graph to plot
facebook = pd.read_csv(
    "./facebook_combined_shortened.txt.gz",
    compression="gzip",
    sep=" ",
    names=["start_node", "end_node"],
)

# random sampling from graph
n = 2000 # n_max=5000
random.seed(n)
random_indices = [random.randint(0, 5000) for _ in range(n)]
# Generate graph from CSV data
print(facebook)
facebook_random = facebook.loc[random_indices]

G = nx.from_pandas_edgelist(facebook_random, "start_node", "end_node")

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

#camera drive parameters
frames = 60

azimuthal_min = 0
azimuthal_max = 100

elevation_min = 0
elevation_max = 40

# Calculate the step size of camera angles for the first half
step_size_azimuthal = (azimuthal_max - azimuthal_min) / (frames // 2 - 1)
step_size_elevation = (elevation_max - elevation_min) / (frames // 2 - 1)

# Create the angles for the first half
azimuthal_angles_first_half = [azimuthal_min + i * step_size_azimuthal for i in range(frames // 2)]
elevation_angles_first_half = [elevation_min + i * step_size_elevation for i in range(frames // 2)]

# Reverse the first half angles to create the second half
azimuthal_angles_second_half = azimuthal_angles_first_half[::-1]
elevation_angles_second_half = elevation_angles_first_half[::-1]

# Combine the two halves to create the complete angles
azimuthal_angles = azimuthal_angles_first_half + azimuthal_angles_second_half
elevation_angles = elevation_angles_first_half + elevation_angles_second_half


def init():
    ax.scatter(*nodes.T, alpha=0.2, s=point_size, ec="w")
    for vizedge in edges:
        ax.plot(*vizedge.T, color="tab:gray")
    ax.grid(False)
    ax.set_axis_off()

    plt.tight_layout()
    return


def _frame_update(index):
    ax.view_init(elevation_angles[index], azimuthal_angles[index])
    print('index')
    print(index)
    print(elevation_angles[index])
    print(azimuthal_angles[index])
    return


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

ani = animation.FuncAnimation(
    fig,
    _frame_update,
    init_func=init,
    interval=50,
    cache_frame_data=False,
    frames=frames,
)
plt.show()
