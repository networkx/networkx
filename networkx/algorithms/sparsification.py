import math
import networkx as nx
import random

__all__ = ['spanner']


def spanner(G, stretch, weight=None):
    if stretch < 1:
        raise ValueError('stretch must be at least 1')
    k = int(math.floor((stretch + 1) / 2))
    return baswana_sen_spanner(G, k, weight)


def baswana_sen_spanner(G, k, weight=None):
    # initialize empty spanner H
    H = nx.empty_graph()
    H.add_nodes_from(G.nodes)

    # phase 1: forming the clusters
    residual_graph = G.copy()
    _make_edge_weights_distinct(residual_graph, weight)

    clustering = {v: v for v in G.nodes}

    for _ in range(k - 1):
        # step 1: sample centers
        sample_prob = math.pow(G.number_of_nodes(), - 1 / k)
        sampled_centers = set()
        for center in clustering.values():
            if random.random() < sample_prob:
                sampled_centers.add(center)

        # combined loop for steps 2 and 3
        edges_to_delete = set()
        new_clustering = {}
        for v in residual_graph.nodes:
            if clustering[v] in sampled_centers:
                continue

            # step 2: find neighboring (sampled) clusters and lightest edges to them
            lightest_edge_to_cluster_weight, lightest_edge_to_cluster_neighbor = _lightest_edge_to_clusters_dicts(residual_graph, clustering, v)
            neighboring_sampled_centers = set(lightest_edge_to_cluster_weight.keys()) & sampled_centers

            # step 3: add edges to spanner
            if not neighboring_sampled_centers:
                for neighbor in lightest_edge_to_cluster_neighbor.values():
                    H.add_edge(v, neighbor)
                    if weight:
                        H[v][neighbor][weight] = residual_graph[v][neighbor]['weight'][0]
                for neighbor in residual_graph.adj[v]:
                    edges_to_delete.add((v, neighbor))

            else:
                lightest_edge_to_sampled_cluster_weight = _infinite_edge_weight()
                lightest_edge_to_sampled_cluster_center = None
                for center in neighboring_sampled_centers:
                    if lightest_edge_to_cluster_weight[center] < lightest_edge_to_sampled_cluster_weight:
                        lightest_edge_to_sampled_cluster_weight = lightest_edge_to_cluster_weight[center]
                        lightest_edge_to_sampled_cluster_center = center
                neighbor = lightest_edge_to_cluster_neighbor[lightest_edge_to_sampled_cluster_center]
                H.add_edge(v, neighbor)
                if weight:
                    H[v][neighbor][weight] = residual_graph[v][neighbor]['weight'][0]
                new_clustering[v] = lightest_edge_to_sampled_cluster_center

                for center, edge_weight in lightest_edge_to_cluster_weight.items():
                    if edge_weight < lightest_edge_to_sampled_cluster_weight:
                        neighbor = lightest_edge_to_cluster_neighbor[center]
                        H.add_edge(v, neighbor)
                        if weight:
                            H[v][neighbor][weight] = residual_graph[v][neighbor]['weight'][0]

                # simplify this
                for neighbor in residual_graph.adj[v]:
                    if clustering[neighbor] is clustering[lightest_edge_to_sampled_cluster_center] or lightest_edge_to_cluster_weight[clustering[neighbor]] < lightest_edge_to_sampled_cluster_weight:
                        edges_to_delete.add((v, neighbor))

        # actually delete edges from residual graph
        residual_graph.remove_edges_from(edges_to_delete)

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
    for v in residual_graph.nodes:
        lightest_edge_to_cluster_weight, lightest_edge_to_cluster_neighbor =\
            _lightest_edge_to_clusters_dicts(residual_graph, clustering, v)
        for neighbor in lightest_edge_to_cluster_neighbor.values():
            H.add_edge(v, neighbor)
            if weight:
                H[v][neighbor][weight] = residual_graph[v][neighbor]['weight'][0]

    return H


def _infinite_edge_weight():
    return math.inf, math.inf, math.inf


def _make_edge_weights_distinct(G, weight):
    for u, v in G.edges():
        if not weight:
            G[u][v]['weight'] = (id(u), id(v), 0)
        else:
            G[u][v]['weight'] = (G[u][v][weight], id(u), id(v))


def _lightest_edge_to_clusters_dicts(residual_graph, clustering, node):
    lightest_edge_weight = {}
    lightest_edge_neighbor = {}
    for neighbor in residual_graph.adj[node]:
        if clustering[neighbor] is clustering[node]:
            continue
        weight = residual_graph[node][neighbor]['weight']
        neighbor_center = clustering[neighbor]
        if neighbor_center not in lightest_edge_weight or weight < lightest_edge_weight[neighbor_center]:
            lightest_edge_weight[neighbor_center] = weight
            lightest_edge_neighbor[neighbor_center] = neighbor
    return lightest_edge_weight, lightest_edge_neighbor
