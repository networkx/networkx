"""Benchmarks for a certain set of algorithms"""

import networkx as nx
from benchmarks.utils import fetch_drug_interaction_network
from networkx.algorithms import community


class AlgorithmBenchmarks:
    timeout = 120
    nodes = 100
    _graphs = [
        nx.erdos_renyi_graph(nodes, 0.1),
        nx.erdos_renyi_graph(nodes, 0.5),
        nx.erdos_renyi_graph(nodes, 0.9),
        fetch_drug_interaction_network(),
    ]
    params = [
        "Erdos Renyi (100, 0.1)",
        "Erdos Renyi (100, 0.5)",
        "Erdos Renyi (100, 0.9)",
        "Drug Interaction network",
    ]

    def setup(self, n):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_betweenness_centrality(self, n):
        # timing this should also give us information about
        # underlying shortest path methods
        _ = nx.betweenness_centrality(self.graphs_dict[n])

    def time_greedy_modularity_communities(self, n):
        _ = community.greedy_modularity_communities(self.graphs_dict[n])

    def time_louvain_communities(self, n):
        _ = community.louvain_communities(self.graphs_dict[n])

    def time_pagerank(self, n):
        _ = nx.pagerank(self.graphs_dict[n])

    def time_connected_components(self, n):
        _ = list(nx.connected_components(self.graphs_dict[n]))

    def time_k_core(self, n):
        _ = nx.k_core(self.graphs_dict[n])

    def time_average_clustering(self, n):
        _ = nx.average_clustering(self.graphs_dict[n])
