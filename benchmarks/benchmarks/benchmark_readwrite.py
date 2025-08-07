from asv_runner.benchmarks.mark import SkipNotImplemented

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

    def time_write_multiline_adjlist(self, graph_type, n):
        _ = nx.write_multiline_adjlist(
            self.G, path="benchmark_write_multiline_adjlist.txt"
        )


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
        graphs = [self.G]
        if not self.G.is_directed():
            self.B = nx.bipartite.complete_bipartite_graph(
                n // 2, n // 2, create_using=self.create_using
            )
            graphs.append(self.B)
        for graph in graphs:
            if graph.is_multigraph():
                graph.add_edges_from(graph.edges)
                for u, v, k in graph.edges(keys=True):
                    graph[u][v][k].update({"weight": 1})
            else:
                for u, v in graph.edges():
                    graph[u][v].update({"weight": 1})

    def time_write_edgelist(self, graph_type, n, data):
        # data = ("weight",) corresponds to `write_weighted_edgelist`.
        _ = nx.write_edgelist(self.G, path="benchmark_write_edgelist.txt", data=data)

    def time_bipartite_write_edgelist(self, graph_type, n, data):
        if graph_type in {"DiGraph", "MultiDiGraph"}:
            raise SkipNotImplemented(f"bipartite graph not defined for {graph_type}")
        _ = nx.bipartite.write_edgelist(
            self.B, path="benchmark_write_bipartite_edgelist.txt", data=data
        )
