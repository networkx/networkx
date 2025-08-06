import networkx as nx


class AdjlistCompleteGraph:
    params = [("Graph", "DiGraph", "MultiGraph", "MultiDiGraph"), (100, 200)]
    param_names = ["graph_type", "n"]

    def setup(self, graph_type, n):
        self.create_using = getattr(nx, graph_type)
        self.G = nx.complete_graph(n, create_using=self.create_using)
        if self.G.is_multigraph():
            self.G.add_edges_from(self.G.edges)

    def time_generate_adjlist(self, graph_type, n):
        _ = list(nx.generate_adjlist(self.G))


class EdgelistCompleteGraph:
    params = [
        ("Graph", "DiGraph", "MultiGraph", "MultiDiGraph"),
        (100, 200),
        (True, False, ("weight",)),
    ]
    param_names = ["graph_type", "n", "data"]

    def setup(self, graph_type, n, data):
        self.create_using = getattr(nx, graph_type)
        self.G = nx.complete_graph(n, create_using=self.create_using)
        if self.G.is_multigraph():
            self.G.add_edges_from(self.G.edges)
            for u, v, k in self.G.edges(keys=True):
                self.G[u][v][k].update({"weight": 1})
        else:
            for u, v in self.G.edges():
                self.G[u][v].update({"weight": 1})

    def time_write_edgelist(self, graph_type, n, data):
        # data = ("weight",) corresponds to `write_weighted_edgelist`.
        _ = nx.write_edgelist(self.G, path="benchmark_edgelist.txt", data=data)
