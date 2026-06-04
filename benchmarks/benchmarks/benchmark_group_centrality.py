"""Benchmarks for group centrality algorithms."""

import networkx as nx


class GroupBetweennessCentralityBenchmarks:
    timeout = 120
    nodes = [10, 100, 1000]
    params = (
        [f"wheel_graph({i})" for i in nodes]
        + [f"directed_wheel({i})" for i in nodes]
        + [f"weighted_path_graph({i})" for i in nodes]
    )
    param_names = ["graph"]

    def setup(self, graph):
        def directed_wheel(n):
            # bidirectional edges on the rim with directed edges to the central node
            G = nx.DiGraph(nx.cycle_graph(range(1, n)))
            G.add_node(0)
            G.add_edges_from((0, i) for i in range(1, n))
            return G

        def weighted_path_graph(n):
            G = nx.path_graph(n)
            nx.set_edge_attributes(G, 1, "weight")
            return G

        self.graphs_dict = {}
        self.single_node_groups = {}
        self.node_subset_groups = {}
        self.weights = {}
        for n in self.nodes:
            self.graphs_dict[f"wheel_graph({n})"] = nx.wheel_graph(n)
            self.single_node_groups[f"wheel_graph({n})"] = [0]
            self.node_subset_groups[f"wheel_graph({n})"] = [1, 2, 3]
            self.weights[f"wheel_graph({n})"] = None

            self.graphs_dict[f"directed_wheel({n})"] = directed_wheel(n)
            self.single_node_groups[f"directed_wheel({n})"] = [0]
            self.node_subset_groups[f"directed_wheel({n})"] = [1, 2, 3]
            self.weights[f"directed_wheel({n})"] = None

            self.graphs_dict[f"weighted_path_graph({n})"] = weighted_path_graph(n)
            self.single_node_groups[f"weighted_path_graph({n})"] = [n // 2]
            self.node_subset_groups[f"weighted_path_graph({n})"] = [
                n // 4,
                n // 2,
                3 * n // 4,
            ]
            self.weights[f"weighted_path_graph({n})"] = "weight"

    def time_group_betweenness_centrality_single_node(self, graph):
        _ = nx.group_betweenness_centrality(
            self.graphs_dict[graph],
            self.single_node_groups[graph],
            normalized=False,
            weight=self.weights[graph],
        )

    def time_group_betweenness_centrality_node_subset(self, graph):
        _ = nx.group_betweenness_centrality(
            self.graphs_dict[graph],
            self.node_subset_groups[graph],
            normalized=False,
            weight=self.weights[graph],
        )

    def time_group_betweenness_centrality_node_subset_endpoints(self, graph):
        _ = nx.group_betweenness_centrality(
            self.graphs_dict[graph],
            self.node_subset_groups[graph],
            normalized=False,
            weight=self.weights[graph],
            endpoints=True,
        )
