"""Benchmarks for Reverse Cuthill-McKee node ordering."""

import networkx as nx


def _smallest_degree(G):
    return min(G, key=G.degree)


def _many_small_components():
    return nx.disjoint_union_all(
        nx.barabasi_albert_graph(10, 2, seed=42 + i) for i in range(200)
    )


class ReverseCuthillMcKeeBenchmarks:
    timeout = 120
    params = (
        [
            "grid_2d_50x50",
            "grid_3d_15x15x15",
            "triangular_40x80",
            "barabasi_albert_3000",
            "many_small_components",
        ],
        ["default", "smallest_degree"],
    )
    param_names = ["graph", "heuristic"]

    def setup(self, graph, heuristic):
        graph_builders = {
            "grid_2d_50x50": lambda: nx.grid_2d_graph(50, 50),
            "grid_3d_15x15x15": lambda: nx.grid_graph([15, 15, 15]),
            "triangular_40x80": lambda: nx.triangular_lattice_graph(40, 80),
            "barabasi_albert_3000": lambda: nx.barabasi_albert_graph(3000, 3, seed=42),
            "many_small_components": _many_small_components,
        }
        self.G = graph_builders[graph]()
        self.heuristic = None if heuristic == "default" else _smallest_degree

    def time_reverse_cuthill_mckee(self, graph, heuristic):
        list(nx.utils.reverse_cuthill_mckee_ordering(self.G, heuristic=self.heuristic))
