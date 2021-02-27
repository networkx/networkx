"""
==========
Scikit-Learn Spectral Clustering based Graph
==========

Example of writing creating a graph from a dataset with 2 features using SpectralClustering from scikit-learn

"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from sklearn import datasets
from sklearn.cluster import SpectralClustering
import networkx as nx

np.random.seed(0)


def spectral_clustering_to_graph(n_clusters, sc: SpectralClustering, true_labels):
    clusters = sc.fit(X)
    # get affinity matrix from spectral clustering
    clusters = clusters
    cluster_affinity_matrix = clusters.affinity_matrix_

    pred_labels = clusters.labels_.astype(int)
    G = nx.from_scipy_sparse_matrix(cluster_affinity_matrix)
    # remove self edges
    G.remove_edges_from(nx.selfloop_edges(G))

    # randomly set n distinct colors for n clusters
    def get_colors(n):
        return list(
            map(lambda i: "#" + "%06x" % np.random.randint(0, 0xFFFFFF), range(n))
        )

    colors = get_colors(n_clusters)
    color_map = []
    for u in G.nodes:
        color_map.append(colors[pred_labels[u]])

    # plot two subplots, one for predicted sample labels, one for predicted sample graph
    # Create 2x2 sub plots
    gs = gridspec.GridSpec(2, 2)
    fig = plt.figure(figsize=(15, 10))
    fig.suptitle("Feature Space to Spectral Clustering based Graph", fontsize=20)

    ax = plt.subplot(gs[0, 0])
    ax.set_title("Step 1. True Data")
    ax.scatter(X[:, 0], X[:, 1], s=26, c=true_labels, cmap="Spectral")
    ax.set_xlabel("feature 0")
    ax.set_ylabel("feature 1")

    ax = plt.subplot(gs[0, 1])
    ax.set_title("Step 2. Clustering Output")
    ax.scatter(X[:, 0], X[:, 1], s=26, c=pred_labels, cmap="copper")
    ax.set_xlabel("feature 0")
    ax.set_ylabel("feature 1")

    # draw resulting network according to Force directed layout to keep relative node separations
    # in the visualizations close to the feature space
    ax = plt.subplot(gs[1, :])
    ax.set_title("Step 3. Resulting Network")
    nx.draw_networkx(
        G,
        node_color=color_map,
        pos=nx.kamada_kawai_layout(G),
        min_source_margin=10,
        min_target_margin=10,
        ax=ax,
    )
    plt.show()
    return G


if __name__ == "__main__":
    # toy example data
    n_samples = 100
    X, y = datasets.make_moons(n_samples=n_samples)

    # add noise to data
    X = X + np.random.normal(1, 0.1, X.shape)

    num_clusters = 2
    spectralClustering = SpectralClustering(
        n_clusters=num_clusters,
        affinity="nearest_neighbors",
        random_state=4242,
        assign_labels="discretize",
    )

    G_output = spectral_clustering_to_graph(num_clusters, spectralClustering, y)
