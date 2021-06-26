"""Function for detecting communities base on Louvain Community Detection
Algorithm"""

from copy import deepcopy
import random

import networkx as nx
from networkx.algorithms.community import modularity

__all__ = ["louvain_communities"]


def louvain_communities(G, weight="weight", threshold=0):
    """Find communities in G using the Louvain Community Detection
    Algorithm.

    Parameters
    ----------
    G : NetworkX graph
    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1.
    threshold : float, optional (default=0)
        Modularity gain threshold for each level. If the gain of modularity
        between 2 levels of the algorithm is less than the given threshold
        then the algorithm stops and returns the resulting communities.

    Returns
    -------
    list
        A list of lists of sets. Each sublist of sets represents one
        level of the tree and each set represents the communities with
        all the nodes that constitute them.

    References
    ----------
    .. [1] Blondel, V.D. et al. Fast unfolding of communities in
       large networks. J. Stat. Mech 10008, 1-12(2008)
    """

    partitions = []
    partition = [{u} for u in G.nodes()]
    mod = modularity(G, partition)
    current_graph = G.copy()
    m = current_graph.size(weight=weight)

    while True:
        partition, improvement = _one_level(
            current_graph, m, deepcopy(partition), weight
        )
        if not improvement:
            break
        new_mod = modularity(G, partition)
        if new_mod - mod <= threshold:
            break
        partitions.append(partition)
        current_graph = _gen_graph(G, partition)
    return partitions


def _one_level(G, m, partition, weight="weight"):
    """Calculate one level of the tree"""
    node2com = {u: i for i, u in enumerate(G.nodes())}
    degrees = dict(G.degree(weight=weight))
    total_weights = {i: deg for i, deg in enumerate(degrees.values())}
    rand_nodes = list(G.nodes)
    random.shuffle(rand_nodes)
    nb_moves = 1
    improvement = False
    while nb_moves > 0:
        nb_moves = 0
        for u in rand_nodes:
            nbrs = G.adj[u]
            best_mod = 0
            best_com = node2com[u]
            partition[best_com].difference_update(G.nodes[u].get("graph", {u}))
            weights2com = _neighbor_weights(u, nbrs, node2com, weight)
            degree = degrees[u]
            total_weights[best_com] -= degree
            for nbr_com, weight in weights2com.items():
                # Modularity gain
                gain = weight - (total_weights[nbr_com] * degree) / m
                if gain > best_mod:
                    best_mod = gain
                    best_com = nbr_com
            partition[best_com].update(G.nodes[u].get("graph", {u}))
            total_weights[best_com] += degree
            if best_com != node2com[u]:
                improvement = True
                nb_moves += 1
                node2com[u] = best_com
    partition = list(filter(len, partition))
    return partition, improvement


def _neighbor_weights(node, nbrs, node2com, weight):
    """Calculate node's neighbor communities and weights"""
    weights = {}
    for nbr, data in nbrs.items():
        if nbr != node:
            weights[node2com[nbr]] = weights.get(node2com[nbr], 0) + 2 * data.get(
                weight, 1
            )
    return weights


def _gen_graph(G, partition):
    """Generate induced graph from given partition"""
    H = nx.quotient_graph(G, partition, relabel=True)
    for u in H.nodes:
        if H.nodes[u]["nedges"] != 0:
            H.add_edge(u, u, weight=H.nodes[u]["nedges"])
    return H
