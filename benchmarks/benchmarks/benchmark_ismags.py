"""Benchmarks for ISMAGS monomorphism enumeration."""

import networkx as nx


class ISMAGSMonomorphism:
    params = [[1000, 10000], [False, True]]
    param_names = ["n", "directed"]

    def setup(self, n, directed):
        graph_class = nx.DiGraph if directed else nx.Graph
        self.graph = nx.path_graph(n, create_using=graph_class)
        self.subgraph = nx.path_graph(2, create_using=graph_class)

    def time_edge_in_path(self, n, directed):
        matcher = nx.isomorphism.ISMAGS(self.graph, self.subgraph)
        sum(1 for _ in matcher.monomorphisms_iter(symmetry=False))
