import math
import networkx as nx
import random

__all__ = ['spanner_bla', 'spanner_guarantee']


def _weight_triple(G, u, v, weight):
    if not weight:
        edge_weight = 1
    else:
        edge_weight = G[u][v][weight]
    return edge_weight, id(u), id(v)


def _lightest_edges_to_clusters(residual_graph, clustering, centers, node, weight):
    lightest_edge_weight = {v: (math.inf, math.inf, math.inf) for v in centers}
    lightest_edge_neighbor = {v: None for v in centers}

    for neighbor in residual_graph.adj[node]:
        weight_triple = _weight_triple(residual_graph, node, neighbor, weight)
        neighbor_center = clustering[neighbor]

        if weight_triple < lightest_edge_weight[neighbor_center]:
            lightest_edge_weight[neighbor_center] = weight_triple
            lightest_edge_neighbor[neighbor_center] = neighbor

    neighbors = set()
    for center in centers:
        if lightest_edge_neighbor[center]:
            neighbors.add(lightest_edge_neighbor[center])
    return neighbors


def _isolate_node(G, v):
    for neighbor in list(G.adj[v]):
        G.remove_edge(v, neighbor)


def spanner_bla(G, stretch_parameter, weight=None):
    if stretch_parameter < 1:
        raise ValueError('stretch_parameter must be at least 1')

    sample_prob = math.pow(G.number_of_nodes(), - 1 / stretch_parameter)
    spanner = nx.empty_graph()
    spanner.add_nodes_from(G.nodes)

    # phase 1: forming the clusters
    residual_graph = G.copy()  # graph (V', E') from paper
    clustering = {v: v for v in G.nodes}

    for _ in range(stretch_parameter - 1):
        # step 1: sample clusters / centers
        centers = set(clustering[u] for u in residual_graph.nodes)
        sampled_centers = set()
        for center in centers:
            if random.random() < sample_prob:
                sampled_centers.add(center)

        # step 2: find nearest neighboring sampled cluster
        nearest_sampled_cluster_neighbor = {}
        for v in residual_graph.nodes:
            if clustering[v] in sampled_centers:
                continue

            min_weight_triple = (math.inf, math.inf, math.inf)
            min_neighbor = None
            for neighbor in G.adj[v]:
                if neighbor not in clustering or clustering[neighbor] not in sampled_centers:
                    continue
                weight_triple = _weight_triple(G, v, neighbor, weight)
                if weight_triple < min_weight_triple:
                    min_weight_triple = weight_triple
                    min_neighbor = neighbor
            nearest_sampled_cluster_neighbor[v] = min_neighbor

        # step 3: add edges to spanner
        new_clustering = {}
        for v in residual_graph.nodes:
            if clustering[v] in sampled_centers:
                continue

            if not nearest_sampled_cluster_neighbor[v]:
                neighbors = _lightest_edges_to_clusters(residual_graph, clustering, centers, v, weight)
                for neighbor in neighbors:
                    spanner.add_edge(v, neighbor)
                    spanner[v][neighbor][weight] = G[v][neighbor][weight]
                _isolate_node(residual_graph, v)
            else:
                sampled_cluster_neighbor = nearest_sampled_cluster_neighbor[v]
                new_clustering[v] = clustering[sampled_cluster_neighbor]
                spanner.add_edge(v, sampled_cluster_neighbor)
                spanner[v][sampled_cluster_neighbor][weight] = G[v][sampled_cluster_neighbor][weight]
                spanner_edge_weight = _weight_triple(G, v, sampled_cluster_neighbor, weight)
                for neighbor in list(residual_graph.adj[v]):
                    if clustering[neighbor] is clustering[sampled_cluster_neighbor]:
                        residual_graph.remove_edge(v, neighbor)
                    else:
                        weight_triple = _weight_triple(residual_graph, v, neighbor, weight)
                        if weight_triple < spanner_edge_weight:
                            residual_graph.remove_edge(v, neighbor)

        # update clustering
        for node, center in clustering.items():
            if center in sampled_centers:
                new_clustering[node] = center
        clustering = new_clustering

        # step 4: remove intra-cluster edges
        for u in residual_graph.nodes:
            for v in list(residual_graph.adj[u]):
                if clustering[u] is clustering[v]:
                    residual_graph.remove_edge(u, v)

        # update residual graph node set
        for v in list(residual_graph.nodes):
            if v not in clustering and residual_graph.degree[v] == 0:
                residual_graph.remove_node(v)

    # phase 2: vertex-cluster joining
    centers = set(clustering[u] for u in residual_graph.nodes)
    for v in residual_graph.nodes:
        neighbors = _lightest_edges_to_clusters(residual_graph, clustering, centers, v, weight)
        for neighbor in neighbors:
            spanner.add_edge(v, neighbor)
            spanner[v][neighbor][weight] = G[v][neighbor][weight]
        _isolate_node(residual_graph, v)

    return spanner


def spanner_guarantee(G, stretch_parameter, weight=None):
    spanner = spanner_bla(G, stretch_parameter, weight)
    while spanner.number_of_edges() >= 2 * stretch_parameter * math.pow(G.number_of_nodes(), 1 + 1 / stretch_parameter):
        print("repeat", spanner.number_of_edges() / (stretch_parameter * math.pow(G.number_of_nodes(), 1 + 1 / stretch_parameter)))
        spanner = spanner_bla(G, stretch_parameter, weight)
    return spanner