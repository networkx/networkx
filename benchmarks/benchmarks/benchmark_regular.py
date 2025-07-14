"""Benchmarks networkx/algorithms/regular.py"""

import networkx as nx


class RegularBenchmarks:
    timeout = 120
    _graph_names = [
        "nx.complete_graph(6)",
        "nx.grid_graph([10, 10], periodic=True)",
        "nx.erdos_renyi_graph(100, 0.1)",
    ]
    _graphs = (
        nx.complete_graph(6),
        nx.grid_graph([10, 10], periodic=True),
        nx.erdos_renyi_graph(100, 0.1, seed=2),  # Minimum degree is 4.
    )
    _ks = [1, 2, 3, 4]

    def setup(self, graph, k):
        self.graphs = dict(zip(self._graph_names, self._graphs))

    def time_k_factor(self, graph, k):
        _ = nx.k_factor(self.graphs[graph], k)

    time_k_factor.params = (_graph_names, _ks)
    time_k_factor.param_names = ("graph", "k")
