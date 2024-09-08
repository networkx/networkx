"""Benchmarks for a certain set of algorithms"""

import networkx as nx


class HarmonicCentralityBenchmarks:
    timeout = 120
    nodes = [10, 100, 1000]
    params = [f"wheel_graph({i})" for i in nodes] + [
        f"directed_wheel({i})" for i in nodes
    ]
    param_names = ["graph"]

    def setup(self, graph):
        def directed_wheel(n):
            # bidirectional edges on the rim with directed edges to the central node
            G = nx.DiGraph(nx.cycle_graph(range(1, n)))
            G.add_node(0)
            G.add_edges_from((0, i) for i in range(1, n))
            return G

        self.graphs_dict = {}
        for n in self.nodes:
            self.graphs_dict[f"wheel_graph({n})"] = nx.wheel_graph(n)
            self.graphs_dict[f"directed_wheel({n})"] = directed_wheel(n)

    def time_harmonic_centrality(self, graph):
        _ = nx.harmonic_centrality(self.graphs_dict[graph])

    def time_harmonic_centrality_single_node(self, graph):
        _ = nx.harmonic_centrality(self.graphs_dict[graph], nbunch=[0])

    def time_harmonic_centrality_node_subset(self, graph):
        _ = nx.harmonic_centrality(self.graphs_dict[graph], nbunch=[0, 1, 2, 3])
