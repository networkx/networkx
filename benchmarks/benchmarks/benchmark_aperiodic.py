"""Benchmarks for `is_aperiodic`."""

import networkx as nx


class AperiodicBenchmarks:
    timeout = 120
    seed = 42
    _graphs = [
        nx.erdos_renyi_graph(100, 0.05, seed=seed, directed=True),
        nx.erdos_renyi_graph(100, 0.1, seed=seed, directed=True),
        nx.erdos_renyi_graph(100, 0.5, seed=seed, directed=True),
        nx.erdos_renyi_graph(100, 0.9, seed=seed, directed=True),
        nx.erdos_renyi_graph(1000, 0.01, seed=seed, directed=True),
        nx.erdos_renyi_graph(1000, 0.05, seed=seed, directed=True),
        nx.erdos_renyi_graph(1000, 0.09, seed=seed, directed=True),
        nx.complete_graph(100, create_using=nx.DiGraph),
        nx.complete_graph(1000, create_using=nx.DiGraph),
        nx.star_graph(10000).to_directed(),
    ]
    params = [
        "Erdos Renyi (100, 0.05)",
        "Erdos Renyi (100, 0.1)",
        "Erdos Renyi (100, 0.5)",
        "Erdos Renyi (100, 0.9)",
        "Erdos Renyi (1000, 0.01)",
        "Erdos Renyi (1000, 0.05)",
        "Erdos Renyi (1000, 0.09)",
        "Complete (100)",
        "Complete (1000)",
        "Star (10000)",
    ]

    param_names = ["graph"]

    def setup(self, graph):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_is_aperiodic(self, graph):
        _ = nx.is_aperiodic(self.graphs_dict[graph])
