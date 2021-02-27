"""
This file provides two functions for adding
spectral-clustering in scikit-learn to networkx gallery example,
which is supposed to be useful in two ways:

-- given a spectral clustering, use the output affinity matrix to draw networkx graph.
-- given a networkx graph, use the graph affinity matrix to do spectral clustering;
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
    get_colors = lambda n: list(
        map(lambda i: "#" + "%06x" % np.random.randint(0, 0xFFFFFF), range(n))
    )
    colors = get_colors(n_clusters)
    color_map = []
    for i in range(len(G.nodes)):
        color_map.append(colors[pred_labels[i]])

    # plot two subplots, one for predicted sample labels, one for predicted sample graph
    # Create 2x2 sub plots
    gs = gridspec.GridSpec(2, 2)
    fig = plt.figure(figsize=(15, 10))
    fig.suptitle("Features Space to Spectral Clustering based Graph", fontsize=20)
    ax = plt.subplot(gs[0, 0])
    ax.set_title("True Data")
    ax.scatter(X[:, 0], X[:, 1], s=26, c=true_labels, cmap="coolwarm")

    ax = plt.subplot(gs[0, 1])
    ax.set_title("Clustering Output")
    ax.scatter(X[:, 0], X[:, 1], s=26, c=pred_labels, cmap="coolwarm")

    # draw resulting network according to Force directed layout to keep relative node separations
    # in the visualizations close to the feature space
    ax = plt.subplot(gs[1, :])
    ax.set_title("Resulting Network")
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


# given a networkx graph, do spectral clustering
# def graph_to_spectral_clustering(G, sc: SpectralClustering, cluster_nr):
#     # Extract a graph affinity matrix with each element represents weight between nodes
#     aff_matrix = nx.to_scipy_sparse_matrix(G)
#     # clusters = sc.fit_predict(aff_matrix)
#     # Spectral clustering
#     pred_labels = sc.fit_predict(aff_matrix).astype(int)
#
#     # randomly set n distinct colors for n clusters
#     get_colors = lambda n: list(map(lambda i: "#" + "%06x" % np.random.randint(0, 0xFFFFFF), range(n)))
#     colors = get_colors(cluster_nr)
#     color_map = []
#     for i in range(len(G.nodes)):
#         color_map.append(colors[pred_labels[i]])
#
#     # Draw predicted cluster labels from graphs, graphviz_layout is for better graph visualization
#     nx.draw(G, with_labels=True, font_weight='bold', node_color=color_map, pos=graphviz_layout(G))
#     plt.show()


if __name__ == "__main__":
    # toy example for spectral_clustering_to_graph
    n_samples = 100
    X, y = datasets.make_moons(n_samples=n_samples)
    # add noise to data
    X = X + np.random.normal(1, 0.1, X.shape)

    num_clusters = 2
    sc = SpectralClustering(
        n_clusters=num_clusters,
        affinity="nearest_neighbors",
        random_state=4242,
        assign_labels="discretize",
    )

    G_output = spectral_clustering_to_graph(num_clusters, sc, y)

    ############################################################################

    # toy example for graph_to_spectral_clustering

    # either through random graph generation
    # n = 10  # 10 nodes
    # m = 20  # 20 edges
    # seed = 20160
    # G = nx.gnm_random_graph(n, m, seed=seed)
    # sc = SpectralClustering(n_clusters=num_clusters,
    #                         affinity='precomputed',
    #                         assign_labels="discretize",
    #                         random_state=0)
    # graph_to_spectral_clustering(G_output, sc, num_clusters)

    # either through G returned from spectral_clustering_to_graph
    # graph_to_spectral_clustering(G_output, derived_clusters, cluster_nr)
