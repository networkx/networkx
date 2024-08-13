"""Benchmarks for a certain set of algorithms"""

import networkx as nx


class HarmonicCentralityBenchmarks:
    timeout = 120
    nodes = [10, 100, 1000]
    _graphs = [nx.wheel_graph(n) for n in nodes]
    params = [f"wheel_graph({i})" for i in nodes]

    param_names = ["graph"]

    def setup(self, graph):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_harmonic_centrality(self, graph):
        _ = nx.harmonic_centrality(self.graphs_dict[graph])

    def time_harmonic_centrality_single_node(self, graph):
        _ = nx.harmonic_centrality(self.graphs_dict[graph], nbunch=[0])

    def time_harmonic_centrality_node_subset(self, graph):
        _ = nx.harmonic_centrality(self.graphs_dict[graph], nbunch=[0, 1, 2, 3])
