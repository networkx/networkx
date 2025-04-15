import random
import time

import pytest

import networkx as nx
from networkx.algorithms.shortest_paths.dstarlite import (
    d_star_modify_edge,
    d_star_recalculate_path,
    new_dstar_lite_instance,
)


def create_predefined_graph():
    """
    Creates a predefined DiGraph with an expected cost of 6 from 'A' to 'E'.

    Returns
    -------
    G : nx.DiGraph
        The predefined graph.
    source : hashable
        'A'
    target : hashable
        'E'
    """
    G = nx.DiGraph()
    edges = [
        ("A", "B", 1),
        ("B", "C", 2),
        ("A", "D", 4),
        ("D", "C", 1),
        ("C", "E", 3),
        ("B", "E", 5),
    ]
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    return G, "A", "E"


def generate_weighted_graph(G, min_w=1, max_w=10, directed=True):
    """
    Randomly assigns integer weights to edges between min_w and max_w.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        The base graph.
    min_w, max_w : int
        Range for random weights.
    directed : bool
        If True, ensures the graph is directed.

    Returns
    -------
    H : Graph
        The weighted graph.
    """
    H = G.to_directed() if directed else G
    if isinstance(H, nx.MultiGraph | nx.MultiDiGraph):
        for u, v, k in H.edges(keys=True):
            H[u][v][k]["weight"] = random.randint(min_w, max_w)
    else:
        for u, v in H.edges():
            H[u][v]["weight"] = random.randint(min_w, max_w)
    return H


class TestDStarLiteBasic:
    def test_source_equals_target(self):
        """If source equals target, path should be [source]."""
        G, source, _ = create_predefined_graph()
        target = source
        dstar = new_dstar_lite_instance(G, source, target)
        assert dstar.get_path() == [source], (
            f"Expected [source] but got {dstar.get_path()}"
        )

    def test_disconnected_graph(self):
        """For a disconnected graph, D* Lite should return None."""
        G = nx.DiGraph()
        G.add_edge("A", "B", weight=1)
        G.add_edge("B", "C", weight=2)
        G.add_edge("X", "Y", weight=3)
        dstar = new_dstar_lite_instance(G, "A", "Y")
        assert dstar.get_path() is None, "Expected None for disconnected graph."


class TestDStarLiteDynamic:
    def test_repeated_updates(self):
        """Repeatedly update edges and ensure path cost is computed."""
        G, source, target = create_predefined_graph()
        dstar = new_dstar_lite_instance(G, source, target)
        modifications = [
            ("B", "C", 10),
            ("C", "E", 50),
            ("A", "D", 2),
            ("D", "C", 3),
        ]
        for u, v, new_w in modifications:
            d_star_modify_edge(dstar, u, v, new_w)
            d_star_recalculate_path(dstar)
            path = dstar.get_path()
            if path:
                cost = dstar.get_path_cost()
                assert isinstance(cost, (int | float)), "Cost should be a number."

    def test_edge_update_reconnect(self):
        """
        Remove all critical connections (to disconnect the graph) and then
        reconnect them. Expect None when disconnected and a valid path when reconnected.
        """
        G, source, target = create_predefined_graph()
        for edge in [("B", "C"), ("B", "E"), ("A", "D"), ("D", "C"), ("C", "E")]:
            if G.has_edge(*edge):
                G.remove_edge(*edge)
        dstar = new_dstar_lite_instance(G, source, target)
        d_star_recalculate_path(dstar)
        assert dstar.get_path() is None, "Expected None when disconnected."
        G.add_edge("B", "C", weight=1)
        G.add_edge("C", "E", weight=1)
        d_star_modify_edge(dstar, "B", "C", 1)
        d_star_modify_edge(dstar, "C", "E", 1)
        d_star_recalculate_path(dstar)
        assert dstar.get_path() is not None, "Expected a valid path after reconnecting."


class TestDStarLiteLargeGraphs:
    def test_large_directed_random_graph(self):
        """Generate a large random directed graph and compare costs and times between D* Lite and A*."""
        G = nx.gnp_random_graph(5000, 0.02, directed=True)
        for u, v in G.edges():
            G[u][v]["weight"] = random.randint(1, 10)
        nodes = list(G.nodes())
        source, target = random.sample(nodes, 2)
        if not nx.has_path(G, source, target):
            pytest.skip("No path available")
        start_dstar = time.perf_counter()
        dstar = new_dstar_lite_instance(G, source, target)
        path_d = dstar.get_path()
        time_dstar = time.perf_counter() - start_dstar
        cost_d = dstar.get_path_cost()
        start_astar = time.perf_counter()
        cost_a = nx.astar_path_length(G, source, target, weight="weight")
        time_astar = time.perf_counter() - start_astar
        assert cost_d == cost_a, f"Cost mismatch: D* Lite {cost_d} vs A* {cost_a}"
        print(f"[Large Random Graph] From {source} to {target}: cost {cost_d}")
        print(f"D* Lite time: {time_dstar:.6f} s, A* time: {time_astar:.6f} s")

    def test_dynamic_directed_grid_environment(self):
        """Simulate a dynamic environment on a directed 10x10 grid."""
        width, height = 10, 10
        G = nx.DiGraph()
        """Create a directed grid (only rightwards and downwards)"""
        for x in range(width):
            for y in range(height):
                if x + 1 < width:
                    G.add_edge((x, y), (x + 1, y), weight=1)
                if y + 1 < height:
                    G.add_edge((x, y), (x, y + 1), weight=1)
        source, target = (0, 0), (9, 9)
        dstar = new_dstar_lite_instance(G, source, target)
        path = dstar.get_path()
        assert path is not None, "Expected an initial path"
        print(f"[Dynamic Grid] Initial path: {path}")
        """Simulate dynamic obstacles by blocking a few edges repeatedly"""
        for i in range(5):
            if len(path) < 3:
                break
            to_block = random.sample(list(zip(path, path[1:])), k=min(3, len(path) - 1))
            for u, v in to_block:
                if G.has_edge(u, v):
                    G[u][v]["weight"] = float("inf")
                    d_star_modify_edge(dstar, u, v, float("inf"))
            d_star_recalculate_path(dstar)
            path = dstar.get_path()
            if path is None:
                print(
                    f"[Dynamic Grid] No path possible after obstacles at iteration {i + 1}"
                )
                break
            cost = dstar.get_path_cost()
            print(f"[Dynamic Grid] New path: {path}, cost={cost}")


def run_manual_tests():
    print("===== MANUAL DEMO OF D* LITE =====")
    G, source, target = create_predefined_graph()
    print(
        f"\nPredefined graph: Nodes: {list(G.nodes())}, Edges: {list(G.edges(data=True))}"
    )

    dstar = new_dstar_lite_instance(G, source, target)
    path = dstar.get_path()
    if path:
        cost = dstar.get_path_cost()
        print(f"Initial path: {path}, cost: {cost}")
    else:
        print("Initial path: None")

    print(
        "\nModifying critical edge ('B','C') to infinite weight and removing ('B','E')..."
    )
    if G.has_edge("B", "C"):
        G.remove_edge("B", "C")
    if G.has_edge("B", "E"):
        G.remove_edge("B", "E")

    d_star_modify_edge(dstar, "B", "C", float("inf"))
    d_star_recalculate_path(dstar)

    path = dstar.get_path()
    if path:
        cost = dstar.get_path_cost()
        print(f"After modification: Path: {path}, cost: {cost}")
    else:
        print("After modification: No path found (correct behavior).")


if __name__ == "__main__":
    print("==> Running tests with pytest:")
    pytest.main([__file__, "-v"])
    print("\n==> Running manual demo:")
    run_manual_tests()
