"""
=====================================================
Image Segmentation via Spectral Graph Partitionioning
=====================================================
Example of partitioning a undirected graph obtained by `k-neighbors`
from an RGB image into a two subgraphs using spectral clusering
illustrated by 3D plots of the original labeled data points in RGB 3D space
vs the bi-partition marking performed by graph partitioning via spectral clustering.
Includes 3D plots of the graph in the spring and spectral layouts.
"""
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import gridspec
from sklearn.cluster import SpectralClustering
from matplotlib.lines import Line2D

###############################################################################
# Create an example 3D dataset "The Rings".
# -----------------------------------------
# The dataset is made of two entangled noisy rings in 3D.
np.random.seed(0)
n_samples = 128
X = np.random.random((n_samples, 3)) * 5e-1
m = int(np.round(n_samples / 2))
theta = np.linspace(0, 2 * np.pi, m)
X[0:m, 0] += 2 * np.cos(theta)
X[0:m, 1] += 3 * np.sin(theta) + 1
X[0:m, 2] += np.sin(theta) + 0.5
X[m:, 0] += 2 * np.sin(theta)
X[m:, 1] += 2 * np.cos(theta) - 1
X[m:, 2] += 3 * np.sin(theta)
Y = np.zeros(n_samples, dtype=np.int8)
Y[m:] = np.ones(m, dtype=np.int8)

# map X to int8 for 8-bit RGB interpretation for drawing
for i in np.arange(X.shape[1]):
    x = X[:, i]
    min_x = np.min(x)
    max_x = np.max(x)
    X[:, i] = np.round(255 * (x - min_x) / (max_x - min_x))

###############################################################################
# Generate the graph and determine the two clusters.
# --------------------------------------------------
# The graph is constructed using the "nearest_neighbors" and the two clusters
# are determined by spectral clustering/graph partitioning.
num_clusters = 2
sc = SpectralClustering(
    n_clusters=num_clusters,
    affinity="nearest_neighbors",
    random_state=4242,
    n_neighbors=10,
    assign_labels="cluster_qr",
    n_jobs=-1,
)
clusters = sc.fit(X)
cluster_affinity_matrix = clusters.affinity_matrix_.H

pred_labels = clusters.labels_.astype(int)
G = nx.from_scipy_sparse_array(cluster_affinity_matrix)
# remove self edges
G.remove_edges_from(nx.selfloop_edges(G))

cluser_member = []
for u in G.nodes:
    cluser_member.append(pred_labels[u])

###############################################################################
# Generate the plots of the data.
# -------------------------------
# The data points are marked according to the original labels and via clustering.
# get affinity matrix from spectral clustering

# select the second half of the list of markers
list_of_markers = Line2D.filled_markers[len(Line2D.filled_markers) // 2 :]

# plot two subplots, one for predicted sample labels, one for predicted sample graph
# Create 1x2 sub plots
gs = gridspec.GridSpec(1, 2)
fig = plt.figure(figsize=(10, 5))
fig.suptitle("Spectral Clustering as Graph Partitioning Illustrated", fontsize=20)

ax = plt.subplot(gs[0, 0], projection="3d")
ax.set_title("Original labeled RGB data")
array_of_markers = np.array(list_of_markers)[Y.astype(int)]
# `marker` parameter does not support list or array format, needs a loop
for i in range(len(array_of_markers)):
    ax.scatter(
        X[i, 0],
        X[i, 1],
        X[i, 2],
        s=26,
        marker=array_of_markers[i],
        alpha=0.8,
        color=X[i] / 255,
    )
ax.set_xlabel("Red")
ax.set_ylabel("Green")
ax.set_zlabel("Blue")
ax.grid(False)
ax.view_init(elev=6.0, azim=-22.0)

ax = plt.subplot(gs[0, 1], projection="3d")
ax.set_title("Data marked by clustering")
array_of_markers = np.array(list_of_markers)[pred_labels.astype(int)]
for i, marker in enumerate(array_of_markers):
    ax.scatter(
        X[i, 0],
        X[i, 1],
        X[i, 2],
        s=26,
        marker=marker,
        alpha=0.8,
        color=X[i] / 255,
    )
ax.set_xlabel("Red")
ax.set_ylabel("Green")
ax.set_zlabel("Blue")
ax.grid(False)
ax.view_init(elev=6.0, azim=-22.0)
plt.show()

###############################################################################
# Generate the plots of the graph.
# ---------------------------------
# The nodes of the graph are marked according to clustering.

# get affinity matrix from spectral clustering
weights = [d["weight"] for u, v, d in G.edges(data=True)]

gs = gridspec.GridSpec(1, 2)
fig = plt.figure(figsize=(10, 5))
# fig.suptitle("Spectral Clustering as Graph Partitioning Illustrated", fontsize=10)
# # draw resulting network according to Force directed layout to keep relative node separations
# # in the visualizations close to the feature space
ax = plt.subplot(gs[0, 0])
ax.set_title("Graph of Affinity Matrix by k-nieghbors in spectral layout")
# pos = nx.spring_layout(G, seed=2020, iterations=100)
pos = nx.spectral_layout(G)
nx.draw_networkx(
    G,
    # node_color=cluser_member,
    pos=pos,
    alpha=0.5,
    node_size=50,
    with_labels=False,
    ax=ax,
    node_color=X / 255,
    edge_color=weights,
    edge_cmap=plt.cm.Greys,
)
plt.box(False)
ax.grid(False)
ax.set_axis_off()

ax = fig.add_subplot(gs[0, 1], projection="3d")
ax.set_title("Partitioned graph by spectral clustering")
pos = nx.spring_layout(
    G,
    iterations=30,  # Convergence expected
    dim=3,
    seed=1721,
)
# pos = nx.spectral_layout(G) # is flat not good fot 3D
nodes = np.array([pos[v] for v in G])
edges = np.array([(pos[u], pos[v]) for u, v in G.edges()])
point_size = int(800 / np.sqrt(len(nodes)))
for i, marker in enumerate(array_of_markers):
    ax.scatter(
        *nodes[i].T,
        s=point_size,
        color=X[i] / 255,
        marker=marker,
        alpha=0.5,
    )
for vizedge, weight in zip(edges, weights):
    ax.plot(*vizedge.T, color="tab:gray", linewidth=weight, alpha=weight)
ax.view_init(elev=130.0, azim=-6.0)
plt.box(False)
ax.grid(False)
ax.set_axis_off()
plt.tight_layout()
plt.show()
