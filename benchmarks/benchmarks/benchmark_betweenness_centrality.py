"""Exact betweenness on forests and graphs that cannot use the forest shortcut."""

import networkx as nx


class BetweennessCentralityForests:
    params = [
        [10, 100, 1000],
        ["path", "star", "forest", "isolates", "cycle", "cycle_with_isolates"],
        [False, True],
    ]
    param_names = ["n", "graph", "endpoints"]

    def setup(self, n, graph, endpoints):
        if graph == "path":
            self.G = nx.path_graph(n)
        elif graph == "star":
            self.G = nx.star_graph(n - 1)
        elif graph == "forest":
            self.G = nx.disjoint_union_all([nx.path_graph(n // 10) for _ in range(10)])
        elif graph == "isolates":
            self.G = nx.empty_graph(n)
        elif graph == "cycle":
            self.G = nx.cycle_graph(n)
        else:
            self.G = nx.cycle_graph(n // 2)
            self.G.add_nodes_from(range(n))

    def time_betweenness_centrality(self, n, graph, endpoints):
        nx.betweenness_centrality(self.G, endpoints=endpoints)

    def peakmem_betweenness_centrality(self, n, graph, endpoints):
        nx.betweenness_centrality(self.G, endpoints=endpoints)
