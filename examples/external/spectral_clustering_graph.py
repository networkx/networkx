"""
==========
Scikit-Learn Spectral Clustering based Graph
==========

Example of writing creating a graph from a dataset with 2 features using SpectralClustering from scikit-learn

"""
import numpy as np
from matplotlib import gridspec
import matplotlib.pyplot as plt
from sklearn.cluster import SpectralClustering
from sklearn.datasets import make_blobs

import networkx as nx
import seaborn as sns

np.random.seed(0)


def spectral_clustering_to_graph(X, n_clusters: int, sc: SpectralClustering):
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

    # compute clustering quality
    clustering_quality = get_cluster_quality(G, n_clusters, cluser_member)

    # plot two subplots, one for predicted sample labels, one for predicted sample graph
    # Create 2x2 sub plots
    gs = gridspec.GridSpec(2, 2)
    fig = plt.figure(figsize=(10, 10))
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
    ax = plt.subplot(gs[1, 0])
    ax.set_title("Step 3. Resulting Graph from Affinity Matrix")
    pos = nx.spring_layout(G, seed=2020, iterations=100)
    nx.draw_networkx(
        G,
        node_color=cluser_member,
        cmap=plt.cm.cool,
        pos=pos,
        alpha=0.5,
        node_size=50,
        with_labels=False,
        ax=ax,
    )

    # draw the confusion matrix for the cut sizes
    ax = plt.subplot(gs[1, 1])
    ax.set_title(
        "Step 4. Clustering quality: cut-sizes for cluster pairs.\n(lower is better)"
    )
    sns.heatmap(clustering_quality, cmap="Blues", vmin=0, annot=True, ax=ax)

    plt.tight_layout()
    plt.show()
    return G


def get_cluster_quality(G, n_clusters: int, labels):
    out = np.zeros((n_clusters, n_clusters), int)
    labels = np.array(labels)
    for i in range(n_clusters):
        S = np.where(labels == i)[0]
        for j in range(n_clusters):
            if i == j:
                continue
            T = np.where(labels == j)[0]
            out[i, j] = nx.cut_size(G, S, T, weight="weight")
    print(out)
    return out


if __name__ == "__main__":
    n_samples = 500
    X, Y = make_blobs(
        n_samples=n_samples,
        centers=3,
        n_features=3,
        center_box=(-1, 1),
        cluster_std=0.2,
        random_state=4242,
    )

    num_clusters = 3
    spectralClustering = SpectralClustering(
        n_clusters=num_clusters,
        affinity="nearest_neighbors",
        random_state=4242,
        n_neighbors=10,
        assign_labels="discretize",
        n_jobs=-1,
    )

    G_output = spectral_clustering_to_graph(X, num_clusters, spectralClustering)
