"""Quotient construction for sparse and dense graphs."""

import networkx as nx


class QuotientGraph:
    params = ("path", "star", "sparse", "dense")
    param_names = ("graph",)

    def setup(self, graph):
        if graph == "path":
            self.G = nx.path_graph(1000)
        elif graph == "star":
            self.G = nx.star_graph(999)
        elif graph == "sparse":
            self.G = nx.fast_gnp_random_graph(1000, 0.004, seed=42)
        else:
            self.G = nx.gnp_random_graph(200, 0.5, seed=42)
        self.partition = [set(range(i, i + 2)) for i in range(0, len(self.G), 2)]

    def time_quotient_graph(self, graph):
        nx.quotient_graph(self.G, self.partition, relabel=True)

    def peakmem_quotient_graph(self, graph):
        nx.quotient_graph(self.G, self.partition, relabel=True)
