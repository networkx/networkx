"""
===========
Mantas Zdanavičius
===========
Create an G{n,m} random graph with n nodes and m edges.
Similar to Erdos Renyi example.
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from sklearn.cluster import SpectralClustering

n = 100  # 10 nodes
m = 320  # 20 edges
cluster_nr = 2 # Number of clusters to identify
seed = 20160  # seed random number generators for reproducibility

# Generate random graph
G = nx.gnm_random_graph(n, m, seed=seed)

# Get adjacency  matrx
adj_matrix = nx.to_numpy_matrix(G)

# Cluster nodes based on adjacency  matrix and extract labels
clustering = SpectralClustering(n_clusters=cluster_nr, affinity="precomputed", assign_labels="discretize", random_state=0).fit(adj_matrix)
labels = clustering.labels_

# Generate color map based on the number of clusters
get_colors = lambda n: list(map(lambda i: "#" + "%06x" % np.random.randint(0, 0xFFFFFF), range(n)))
colors = get_colors(cluster_nr)
color_map = []
for i in range(len(G.nodes)):
    color_map.append(colors[labels[i]])

# Print out the graph with consistant positioning and colors
pos = nx.spring_layout(G, seed=seed)  # Seed for reproducible layout
nx.draw(G, with_labels=True, font_weight='bold', node_color=color_map, pos=pos)
plt.show()
