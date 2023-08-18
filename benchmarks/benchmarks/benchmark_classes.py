from itertools import permutations

import networkx as nx


class GraphBenchmark:
    params = ["Graph", "DiGraph", "MultiGraph", "MultiDiGraph"]

    def setup(self, n):
        self.nodes = list(range(1, 1000))
        self.edges = []
        self.subgraph_nodes = list(range(1, 100))
        self.subgraph_nodes_large = list(range(1, 900))
        self.G = getattr(nx, n)()

    def time_graph_create(self, n):
        _ = getattr(nx, n)()

    def time_add_nodes_from(self, n):
        self.G.add_nodes_from(self.nodes)

    def time_add_edges_from(self, n):
        self.G.add_edges_from(self.edges)

    def time_remove_nodes_from(self, n):
        self.G.remove_nodes_from(self.nodes)

    def time_remove_edges_from(self, n):
        self.G.remove_edges_from(self.edges)

    def time_copy(self, n):
        _ = self.G.copy()

    def time_to_directed(self, n):
        _ = self.G.to_directed()

    def time_to_undirected(self, n):
        _ = self.G.to_undirected()

    def time_subgraph(self, n):
        _ = self.G.subgraph(self.subgraph_nodes).copy()

    def time_subgraph_large(self, n):
        _ = self.G.subgraph(self.subgraph_nodes_large).copy()
