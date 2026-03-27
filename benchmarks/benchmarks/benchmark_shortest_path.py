"""Benchmarks for a certain set of algorithms"""

import random

import networkx as nx


class UndirectedGraphAtlasSevenNodesConnected:
    timeout = 120
    seed = 0xDEADC0DE
    params = ["unweighted", "uniform", "increasing", "random"]
    param_names = ["edge_weights"]

    def setup(self, edge_weights):
        connected_sevens = [
            G for G in nx.graph_atlas_g() if (len(G) == 7) and nx.is_connected(G)
        ]

        match edge_weights:
            case "uniform":
                for G in connected_sevens:
                    nx.set_edge_attributes(G, values=5, name="weight")
            case "random":
                random.seed(self.seed)
                for G in connected_sevens:
                    nx.set_edge_attributes(
                        G,
                        values={e: random.randint(1, len(G)) for e in G.edges},
                        name="weight",
                    )
            case "increasing":
                for G in connected_sevens:
                    nx.set_edge_attributes(
                        G, {e: max(e) for e in G.edges}, name="weight"
                    )
            case _:
                pass  # Default case ("unweighted")

        self.graphs = connected_sevens

    def time_multi_source_dijkstra_over_atlas(self, edge_weights):
        """How long it takes to compute dijkstra multisource paths over many
        small graphs."""
        for G in self.graphs:
            _ = nx.multi_source_dijkstra(G, sources=[0, 1])

    def time_multi_source_dijkstra_over_atlas_with_target(self, edge_weights):
        for G in self.graphs:
            _ = nx.multi_source_dijkstra(G, sources=[0, 1], target=6)


class AllShortestPathsGrid:
    """
    This tests the performance of _build_paths_from_predecessors
    on graphs with a large number of paths (high recursion depth).
    """

    params = [8, 10, 12]
    param_names = ["N"]
    timeout = 300

    def setup(self, N):
        self.G = nx.grid_2d_graph(N, N)
        self.source = (0, 0)
        self.target = (N - 1, N - 1)

    def time_all_shortest_paths(self, N):
        for _ in nx.all_shortest_paths(self.G, self.source, self.target):
            pass
