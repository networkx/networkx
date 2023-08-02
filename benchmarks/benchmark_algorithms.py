"""Benchmarks for a certain set of algorithms"""

import networkx as nx
from benchmarks.utils import fetch_drug_interaction_network
from networkx.algorithms import community


class AlgorithmBenchmarks:
    timeout = 120
    nodes = 100
    params = [
        nx.erdos_renyi_graph(nodes, 0.1),
        nx.erdos_renyi_graph(nodes, 0.5),
        nx.erdos_renyi_graph(nodes, 0.9),
        fetch_drug_interaction_network(),
    ]
    param_names = ["graph_type"]

    def time_betweenness_centrality(self, graph_type):
        # timing this should also give us information about underlying shortest path
        # methods
        _ = nx.betweenness_centrality(graph_type)

    def time_greedy_modularity_communities(self, graph_type):
        _ = community.greedy_modularity_communities(graph_type)

    def time_louvain_communities(self, graph_type):
        _ = community.louvain_communities(graph_type)

    def time_pagerank(self, graph_type):
        _ = nx.pagerank(graph_type)

    def time_connected_components(self, graph_type):
        _ = list(nx.connected_components(graph_type))

    def time_k_core(self, graph_type):
        _ = nx.k_core(graph_type)

    def time_average_clustering(self, graph_type):
        _ = nx.average_clustering(graph_type)
