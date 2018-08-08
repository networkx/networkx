import math
import networkx as nx
import random

__all__ = ['spanner']


def spanner(G, stretch, weight=None, limit_size=True):
    if stretch < 1:
        raise ValueError('stretch must be at least 1')

    k = _stretch_to_k(stretch)
    H = _baswana_sen_spanner(G, k, weight)

    if limit_size:
        size_limit = 2 * _spanner_expected_number_of_edges(G.number_of_nodes(), stretch)
        while H.number_of_edges() > size_limit:
            # TODO: add reference to paper
            # this loop runs for O(1) iterations with high probability
            H = _baswana_sen_spanner(G, k, weight)

    return H


def _stretch_to_k(stretch):
    return int(math.floor((stretch + 1) / 2))


def _spanner_expected_number_of_edges(number_of_nodes, stretch):
    k = _stretch_to_k(stretch)
    return k * math.pow(number_of_nodes, 1 + 1 / k)


def _baswana_sen_spanner(G, k, weight=None):
    # initialize spanner H with empty edge set
    H = nx.empty_graph()
    H.add_nodes_from(G.nodes)

    # phase 1: forming the clusters
    residual_graph = _setup_residual_graph(G, weight)
    clustering = {v: v for v in G.nodes}
    sample_prob = math.pow(G.number_of_nodes(), - 1 / k)

    for _ in range(k - 1):
        # step 1: sample centers
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
            lightest_edge_neighbor, lightest_edge_weight = _lightest_edge_dicts(residual_graph, clustering, v)
            neighboring_sampled_centers = set(lightest_edge_weight.keys()) & sampled_centers

            # step 3: add edges to spanner
            if not neighboring_sampled_centers:
                # connect to each neighboring center via lightest edge
                for neighbor in lightest_edge_neighbor.values():
                    _add_edge_to_spanner(H, residual_graph, v, neighbor, weight)
                # remove all incident edges
                for neighbor in residual_graph.adj[v]:
                    edges_to_delete.add((v, neighbor))

            else:  # there is a neighboring sampled center
                closest_center = _closest_sampled_center(lightest_edge_weight, neighboring_sampled_centers)
                closest_center_weight = lightest_edge_weight[closest_center]
                closest_center_neighbor = lightest_edge_neighbor[closest_center]

                _add_edge_to_spanner(H, residual_graph, v, closest_center_neighbor, weight)
                new_clustering[v] = closest_center

                # connect to centers with edge weight less than closest_center_weight
                for center, edge_weight in lightest_edge_weight.items():
                    if edge_weight < closest_center_weight:
                        neighbor = lightest_edge_neighbor[center]
                        _add_edge_to_spanner(H, residual_graph, v, neighbor, weight)

                # remove edges to centers with edge weight less than closest_center_weight
                for neighbor in residual_graph.adj[v]:
                    neighbor_cluster = clustering[neighbor]
                    neighbor_weight = lightest_edge_weight[neighbor_cluster]
                    if neighbor_cluster is closest_center or neighbor_weight < closest_center_weight:
                        edges_to_delete.add((v, neighbor))

        # actually delete edges from residual graph
        residual_graph.remove_edges_from(edges_to_delete)

        # copy old clustering data to new_clustering
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
        lightest_edge_neighbor, _ = _lightest_edge_dicts(residual_graph, clustering, v)
        for neighbor in lightest_edge_neighbor.values():
            _add_edge_to_spanner(H, residual_graph, v, neighbor, weight)

    return H


def _setup_residual_graph(G, weight):
    residual_graph = G.copy()

    # establish unique edge weights, even for unweighted graphs
    for u, v in G.edges():
        if not weight:
            residual_graph[u][v]['weight'] = (id(u), id(v), 0)
        else:
            residual_graph[u][v]['weight'] = (G[u][v][weight], id(u), id(v))

    return residual_graph


def _lightest_edge_dicts(residual_graph, clustering, node):
    lightest_edge_neighbor = {}
    lightest_edge_weight = {}
    center = clustering[node]
    for neighbor in residual_graph.adj[node]:
        neighbor_center = clustering[neighbor]
        if neighbor_center is center:
            continue
        weight = residual_graph[node][neighbor]['weight']
        if neighbor_center not in lightest_edge_weight or weight < lightest_edge_weight[neighbor_center]:
            lightest_edge_neighbor[neighbor_center] = neighbor
            lightest_edge_weight[neighbor_center] = weight
    return lightest_edge_neighbor, lightest_edge_weight


def _closest_sampled_center(lightest_edge_weight, neighboring_sampled_centers):
    closest_center = None
    closest_weight = math.inf, math.inf, math.inf
    for center in neighboring_sampled_centers:
        if lightest_edge_weight[center] < closest_weight:
            closest_center = center
            closest_weight = lightest_edge_weight[center]
    return closest_center


def _add_edge_to_spanner(H, residual_graph, u, v, weight):
    H.add_edge(u, v)
    if weight:
        H[u][v][weight] = residual_graph[u][v]['weight'][0]