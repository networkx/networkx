"""
This file provides two functions for adding
spectral-clustering in scikit-learn to networkx gallery example,
which is supposed to be useful in two ways:

-- given a spectral clustering, use the output affinity matrix to draw networkx graph.
-- given a networkx graph, use the graph affinity matrix to do spectral clustering;

"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import SpectralClustering
from sklearn import datasets
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout


def spectral_clustering_to_graph(clusters, n_clusters):
    # get affinity matrix from spectral clustering
    clusters = clusters
    cluster_affinity_matrix = clusters.fit(X).affinity_matrix_

    pred_labels = clusters.labels_.astype(int)
    G = nx.from_scipy_sparse_matrix(cluster_affinity_matrix)

    # randomly set n distinct colors for n clusters
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % np.random.randint(0, 0xFFFFFF), range(n)))
    colors = get_colors(n_clusters)
    color_map = []
    for i in range(len(G.nodes)):
        color_map.append(colors[pred_labels[i]])

    # plot two subplots, one for predicted sample labels, one for predicted sample graph
    plt.subplot(121)
    plt.scatter(X[:, 0], X[:, 1], s=10, c=pred_labels)
    plt.subplot(122)
    nx.draw(G, with_labels=True, font_weight='bold', node_color=color_map, pos=graphviz_layout(G))
    plt.show()

    return G


# given a networkx graph, do spectral clustering
def graph_to_spectral_clustering(G, clusters, n_clusters):
    # Extract a graph affinity matrix with each element represents weight between nodes
    aff_matrix = nx.to_scipy_sparse_matrix(G)

    # Spectral clustering
    clusters = clusters
    pred_labels = clusters.fit_predict(aff_matrix).astype(int)

    # randomly set n distinct colors for n clusters
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % np.random.randint(0, 0xFFFFFF), range(n)))
    colors = get_colors(n_clusters)
    color_map = []
    for i in range(len(G.nodes)):
        color_map.append(colors[pred_labels[i]])

    # Draw predicted cluster labels from graphs, graphviz_layout is for better graph visualization
    nx.draw(G, with_labels=True, font_weight='bold', node_color=color_map, pos=graphviz_layout(G))
    plt.show()


if __name__ == "__main__":

    # toy example for spectral_clustering_to_graph
    np.random.seed(0)
    n_samples = 100
    X, y = datasets.make_moons(n_samples=n_samples)
    n_clusters = 2
    known_clusters = SpectralClustering(n_clusters=n_clusters,
                                        affinity="nearest_neighbors",
                                        random_state=0,
                                        assign_labels="discretize")

    G_output = spectral_clustering_to_graph(known_clusters, n_clusters)

    ############################################################################

    # toy example for graph_to_spectral_clustering

    # either through random graph generation
    n = 10  # 10 nodes
    m = 20  # 20 edges
    G = nx.gnm_random_graph(n, m)
    derived_clusters = SpectralClustering(n_clusters=n_clusters,
                                          affinity='precomputed',
                                          assign_labels="discretize",
                                          random_state=0,
                                          )
    graph_to_spectral_clustering(G, derived_clusters, n_clusters)

    # either through G returned from spectral_clustering_to_graph
    graph_to_spectral_clustering(G_output, derived_clusters, n_clusters)
