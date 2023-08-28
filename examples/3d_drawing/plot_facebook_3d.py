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
print("graph read")
# generate layout of the graph using spinrg_layout in 3-D
pos = nx.spring_layout(
    graph,
    iterations=30,  # convergence expected
    dim=3,
    seed=1721,
)
print("positins calculated")
# getting nodes and edges into right format for matplotlib
nodes = np.array([pos[v] for v in graph])
edges = np.array([(pos[u], pos[v]) for u, v in graph.edges()])

# initialize 3D plot
fig = plt.figure()
axis = fig.add_subplot(111, projection="3d")
axis.view_init(elev=50.0, azim=50)
# the size of the nodes should be depending on the number of nodes
point_size = int(1000 / np.sqrt(len(nodes)))

# plot the nodes as scatter plot
axis.scatter(*nodes.T, s=point_size, ec="w")
print("nodes plot")
# plot the edges
for vizedge in edges:
    axis.plot(*vizedge.T, color="tab:gray", linewidth=0.15)
print("edges plot")
# Turn gridlines off
axis.grid(False)
axis.axis("off")

fig.tight_layout()
plt.show()
