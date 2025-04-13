import time
import tracemalloc

import pytest

import networkx as nx
from networkx.algorithms.shortest_paths.smastar import *
from networkx.utils import pairwise


class TestSMAStar:
    @classmethod
    def setup_class(cls):
        edges = [
            ("s", "u", 10),
            ("s", "x", 5),
            ("u", "v", 1),
            ("u", "x", 2),
            ("v", "y", 1),
            ("x", "u", 3),
            ("x", "v", 5),
            ("x", "y", 2),
            ("y", "s", 7),
            ("y", "v", 6),
        ]
        cls.XG = nx.DiGraph()
        cls.XG.add_weighted_edges_from(edges)

    def test_multiple_optimal_paths(self):
        heuristic_values = {"a": 1.35, "b": 1.18, "c": 0.67, "d": 0}

        def h(u, v):
            return heuristic_values[u]

        graph = nx.Graph()
        points = ["a", "b", "c", "d"]
        edges = [("a", "b", 0.18), ("a", "c", 0.68), ("b", "c", 0.50), ("c", "d", 0.67)]

        graph.add_nodes_from(points)
        graph.add_weighted_edges_from(edges)

        path1 = ["a", "c", "d"]
        path2 = ["a", "b", "c", "d"]
        assert sma_star_path(graph, "a", "d", h) in (path1, path2)

    def test_idastar_directed(self):
        assert sma_star_path(self.XG, "s", "v") == ["s", "x", "u", "v"]

    def test_astar_directed_weight_function(self):
        def w1(u, v, d):
            return d["weight"]

        assert sma_star_path(self.XG, "x", "u", weight=w1) == ["x", "u"]
        assert sma_star_path_length(self.XG, "x", "u", weight=w1) == 3
        assert sma_star_path(self.XG, "s", "v", weight=w1) == ["s", "x", "u", "v"]
        assert sma_star_path_length(self.XG, "s", "v", weight=w1) == 9

    def test_astar_multigraph(self):
        G = nx.MultiDiGraph(self.XG)
        G.add_weighted_edges_from((u, v, 1000) for (u, v) in list(G.edges()))
        assert sma_star_path(G, "s", "v") == ["s", "x", "u", "v"]
        assert sma_star_path_length(G, "s", "v") == 9

    def test_astar_undirected(self):
        GG = self.XG.to_undirected()
        GG["u"]["x"]["weight"] = 2
        GG["y"]["v"]["weight"] = 2
        assert sma_star_path(GG, "s", "v") == ["s", "x", "u", "v"]
        assert sma_star_path_length(GG, "s", "v") == 8

    def test_astar_nopath(self):
        with pytest.raises(nx.NodeNotFound):
            sma_star_path(self.XG, "s", "moon")

    def test_astar_admissible_heuristic_with_cutoff(self):
        heuristic_values = {"s": 36, "y": 4, "x": 0, "u": 0, "v": 0}

        def h(u, v):
            return heuristic_values[u]

        assert sma_star_path_length(self.XG, "s", "v", heuristic=h) == 9

    def test_astar_inadmissible_heuristic_with_cutoff(self):
        heuristic_values = {"s": 36, "y": 14, "x": 10, "u": 10, "v": 0}

        def h(u, v):
            return heuristic_values[u]

        assert sma_star_path_length(self.XG, "s", "v", heuristic=h) == 10

    def test_cycle(self):
        C = nx.cycle_graph(7)
        assert sma_star_path(C, 0, 3) == [0, 1, 2, 3]
        assert nx.dijkstra_path(C, 0, 4) == [0, 6, 5, 4]

    def test_unorderable_nodes(self):
        nodes = [object() for n in range(4)]
        G = nx.Graph()
        G.add_edges_from(pairwise(nodes, cyclic=True))
        path = sma_star_path(G, nodes[0], nodes[2])
        assert len(path) == 3

    def test_astar_NetworkXNoPath(self):
        G = nx.gnp_random_graph(10, 0.2, seed=10)
        with pytest.raises(nx.NetworkXNoPath):
            sma_star_path(G, 4, 9)

    def test_astar_NodeNotFound(self):
        G = nx.gnp_random_graph(10, 0.2, seed=10)
        with pytest.raises(nx.NodeNotFound):
            sma_star_path_length(G, 11, 9)


# ---------------- Performance Benchmark ---------------- #


def create_grid_graph(n, m, with_coords=True):
    G = nx.grid_2d_graph(n, m)
    if with_coords:
        for x, y in G.nodes():
            G.nodes[(x, y)]["x"] = x
            G.nodes[(x, y)]["y"] = y
    return G


def run_with_memory_tracking(func, *args, **kwargs):
    tracemalloc.start()
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed_time = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "result": result,
        "time": elapsed_time,
        "peak_memory_kb": peak / 1024,
    }


@pytest.mark.parametrize("size", [1000])  # Test with one grid size for now
def test_benchmark_astar_vs_smastar(size):
    print("\n>> Running A* vs SMA* Benchmark with Grid Size:", size)
    G = create_grid_graph(size, size)

    source = (0, 0)
    target = (size - 1, size - 1)

    print(">> Running A*")
    astar_stats = run_with_memory_tracking(
        nx.astar_path,
        G,
        source,
        target,
        heuristic=lambda u, v: ((v[0] - u[0]) ** 2 + (v[1] - u[1]) ** 2) ** 0.5,
    )

    print(">> Running SMA*")
    sma_star_stats = run_with_memory_tracking(sma_star_path, G, source, target)

    print("\nResult Comparison:")
    print(
        f"A*       => Time: {astar_stats['time']:.2f}s | Peak Memory: {astar_stats['peak_memory_kb']:.2f} KB"
    )
    print(
        f"SMA*     => Time: {sma_star_stats['time']:.2f}s | Peak Memory: {sma_star_stats['peak_memory_kb']:.2f} KB"
    )
    print(f"Same path: {astar_stats['result'] == sma_star_stats['result']}")
