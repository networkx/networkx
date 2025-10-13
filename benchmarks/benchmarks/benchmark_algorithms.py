"""Benchmarks for a certain set of algorithms"""

import random

import networkx as nx
from benchmarks.utils import fetch_drug_interaction_network
from networkx.algorithms import community


class UndirectedAlgorithmBenchmarks:
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

    param_names = ["graph"]

    def setup(self, graph):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_betweenness_centrality(self, graph):
        # timing this should also give us information about
        # underlying shortest path methods
        _ = nx.betweenness_centrality(self.graphs_dict[graph])

    def time_greedy_modularity_communities(self, graph):
        _ = community.greedy_modularity_communities(self.graphs_dict[graph])

    def time_louvain_communities(self, graph):
        _ = community.louvain_communities(self.graphs_dict[graph])

    def time_pagerank(self, graph):
        _ = nx.pagerank(self.graphs_dict[graph])

    def time_connected_components(self, graph):
        _ = list(nx.connected_components(self.graphs_dict[graph]))

    def time_k_core(self, graph):
        _ = nx.k_core(self.graphs_dict[graph])

    def time_average_clustering(self, graph):
        _ = nx.average_clustering(self.graphs_dict[graph])


class DirectedAlgorithmBenchmarks:
    timeout = 120
    _graphs = [
        nx.erdos_renyi_graph(100, 0.1, directed=True),
        nx.erdos_renyi_graph(100, 0.5, directed=True),
        nx.erdos_renyi_graph(100, 0.9, directed=True),
        nx.erdos_renyi_graph(1000, 0.01, directed=True),
        nx.erdos_renyi_graph(1000, 0.05, directed=True),
        nx.erdos_renyi_graph(1000, 0.09, directed=True),
    ]
    params = [
        "Erdos Renyi (100, 0.1)",
        "Erdos Renyi (100, 0.5)",
        "Erdos Renyi (100, 0.9)",
        "Erdos Renyi (1000, 0.01)",
        "Erdos Renyi (1000, 0.05)",
        "Erdos Renyi (1000, 0.09)",
    ]

    param_names = ["graph"]

    def setup(self, graph):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_tarjan_scc(self, graph):
        _ = list(nx.strongly_connected_components(self.graphs_dict[graph]))

    def time_kosaraju_scc(self, graph):
        _ = list(nx.kosaraju_strongly_connected_components(self.graphs_dict[graph]))


class AlgorithmBenchmarksConnectedGraphsOnly:
    timeout = 120
    nodes = 100
    _graphs = [
        nx.erdos_renyi_graph(nodes, 0.1),
        nx.erdos_renyi_graph(nodes, 0.5),
        nx.erdos_renyi_graph(nodes, 0.9),
    ]
    params = [
        "Erdos Renyi (100, 0.1)",
        "Erdos Renyi (100, 0.5)",
        "Erdos Renyi (100, 0.9)",
    ]

    param_names = ["graph"]

    def setup(self, graph):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_eigenvector_centrality_numpy(self, graph):
        # Added to ensure the connectivity check doesn't affect
        # performance too much (see gh-6888, gh-7549).
        _ = nx.eigenvector_centrality_numpy(self.graphs_dict[graph])

    def time_square_clustering(self, graph):
        _ = nx.square_clustering(self.graphs_dict[graph])


def _make_tournament_benchmark_graphs(seed):
    number_of_nodes = [10, 100, 1000]
    graphs = {}
    for nodes in number_of_nodes:
        G = nx.tournament.random_tournament(nodes, seed=seed)
        graphs[f"Tournament ({nodes}, seed={seed})"] = G
    return graphs


class ReachabilityBenchmark:
    timeout = 120
    _seed = 42
    param_names = ["graph"]

    _graphs = _make_tournament_benchmark_graphs(_seed)
    params = list(_graphs)

    def setup(self, graph):
        self.G = self._graphs[graph]
        self.nodes = sorted(self.G)
        rng = random.Random(self._seed)
        self.source, self.target = rng.sample(self.nodes, 2)

    def time_is_reachable(self, graph):
        _ = nx.tournament.is_reachable(self.G, self.source, self.target)
