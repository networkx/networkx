"""Benchmarks networkx/algorithms/regular.py"""

import networkx as nx


class KFactorBenchmarks:
    timeout = 120
    _graph_names = [
        "nx.complete_graph(6)",
        "nx.complete_graph(20)",
        "nx.grid_graph([10, 10], periodic=True)",
        "nx.erdos_renyi_graph(100, 0.1)",
        "nx.erdos_renyi_graph(10, 0.7)",
    ]
    _graphs = (
        nx.complete_graph(6),
        nx.complete_graph(20),
        nx.grid_graph([10, 10], periodic=True),
        nx.erdos_renyi_graph(100, 0.1, seed=2),  # Minimum degree is 4.
        nx.erdos_renyi_graph(10, 0.8, seed=2),  # Minimum degree is 6.
    )
    _ks = [1, 2, 3, 4]

    def setup(self, graph, k):
        self.graphs = dict(zip(self._graph_names, self._graphs))

    def time_k_factor(self, graph, k):
        _ = nx.k_factor(self.graphs[graph], k)

    time_k_factor.params = (_graph_names, _ks)
    time_k_factor.param_names = ("graph", "k")


class IsRegularCompleteGraph:
    param_names = ["n", "directed", "is_regular"]
    params = ([10, 20, 100], [True, False], [True, False])

    def setup(self, n, directed, is_regular):
        G = nx.complete_graph(n)
        if directed:
            G = G.to_directed()
        if not is_regular:
            G.remove_edge(n - 2, n - 1)
        self.G = G

    def time_is_regular(self, n, directed, is_regular):
        _ = nx.is_regular(self.G)
