"""Benchmarks for current-flow betweenness centrality."""

import networkx as nx


class CurrentFlowBetweennessCentralityBenchmarks:
    timeout = 120
    params = ["full", "lu", "cg"]
    param_names = ["solver"]

    def setup(self, solver):
        self.graph = nx.complete_graph(40)
        self.sources = [0]
        self.targets = [39]

    def time_current_flow_betweenness_centrality_subset(self, solver):
        _ = nx.current_flow_betweenness_centrality_subset(
            self.graph, self.sources, self.targets, solver=solver
        )


class AdjacentCurrentFlowBetweennessCentralityBenchmarks:
    timeout = 120
    params = ["lu", "cg"]
    param_names = ["solver"]

    def setup(self, solver):
        self.graph = nx.path_graph(1024)
        self.sources = [0]
        self.targets = [1023]

    def time_current_flow_betweenness_centrality_subset(self, solver):
        _ = nx.current_flow_betweenness_centrality_subset(
            self.graph, self.sources, self.targets, solver=solver
        )
