"""Benchmarks for a certain set of algorithms"""

import networkx as nx

seed = 0xDEADC0DE


class HitsAlgorithm:
    timeout = 120
    _graphs = [
        nx.barabasi_albert_graph(1000, m=3, seed=seed),
        nx.barabasi_albert_graph(10_000, m=3, seed=seed),
        nx.gnp_random_graph(5000, 0.001, seed=seed),
        nx.scale_free_graph(10_000, seed=seed),
        nx.grid_2d_graph(30, 30),
    ]
    params = [
        "BA(1000, m=3)",
        "BA(10000, m=3)",
        "gnp(5000, 0.001)",
        "scale_free(10000)",
        "grid(30, 30)",
    ]

    param_names = ["graph"]

    def setup(self, graph):
        self.graphs_dict = dict(zip(self.params, self._graphs))

    def time_hits(self, graph):
        _, _ = nx.hits(self.graphs_dict[graph])
