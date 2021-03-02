"""
==========
Scikit-Learn Spectral Clustering based Graph
==========

Example of writing creating a graph from a dataset with 2 features using SpectralClustering from scikit-learn

"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from sklearn.datasets import make_blobs
from sklearn.cluster import SpectralClustering

import networkx as nx

np.random.seed(0)


def spectral_clustering_to_graph(X, sc: SpectralClustering):
    # get affinity matrix from spectral clustering
    clusters = sc.fit(X)
    cluster_affinity_matrix = clusters.affinity_matrix_

    pred_labels = clusters.labels_.astype(int)
    G = nx.from_scipy_sparse_matrix(cluster_affinity_matrix)
    # remove self edges
    G.remove_edges_from(nx.selfloop_edges(G))

    cluser_member = []
    for u in G.nodes:
        cluser_member.append(pred_labels[u])

    # plot two subplots, one for predicted sample labels, one for predicted sample graph
    # Create 2x2 sub plots
    gs = gridspec.GridSpec(2, 2)
    fig = plt.figure(figsize=(15, 15))
    fig.suptitle("Feature Space to Spectral Clustering based Graph", fontsize=20)

    ax = plt.subplot(gs[0, 0], projection="3d")
    ax.set_title("Step 1. Scatterplot for available data")
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], s=26, alpha=0.3, cmap="cool")
    ax.set_xlabel("feature 0")
    ax.set_ylabel("feature 1")
    ax.set_zlabel("feature 2")

    ax = plt.subplot(gs[0, 1], projection="3d")
    ax.set_title("Step 2. Scatterplot for the Clustering Output")
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], s=26, c=pred_labels, alpha=0.3, cmap="cool")
    ax.set_xlabel("feature 0")
    ax.set_ylabel("feature 1")
    ax.set_zlabel("feature 2")

    # draw resulting network according to Force directed layout to keep relative node separations
    # in the visualizations close to the feature space
    ax = plt.subplot(gs[1, :])
    ax.set_title("Step 3. Resulting Graph from Affinity Matrix")
    pos = nx.spring_layout(G, seed=19, iterations=100)
    nx.draw_networkx(
        G,
        node_color=cluser_member,
        cmap=plt.cm.cool,
        pos=pos,
        alpha=0.5,
        node_size=100,
        with_labels=False,
        ax=ax,
    )
    plt.tight_layout()
    plt.show()
    return G


if __name__ == "__main__":
    n_samples = 500
    X, Y = make_blobs(n_samples=n_samples, centers=3, n_features=3, random_state=4242)

    num_clusters = 3
    spectralClustering = SpectralClustering(
        n_clusters=num_clusters,
        affinity="nearest_neighbors",
        random_state=4242,
        n_neighbors=10,
        assign_labels="discretize",
        n_jobs=-1,
    )

    G_output = spectral_clustering_to_graph(X, spectralClustering)

    print(G_output.edges.data())
