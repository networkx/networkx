import pytest

import networkx as nx
from networkx.algorithms.shortest_paths.ada_star import ada_star
from networkx.utils import pairwise


class TestADAStar:
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

        search = ada_star(
            graph, "a", "d", heuristic=h, weight="weight", initial_epsilon=1
        )
        path = search.extract_path()

        assert path in (path1, path2)

    def test_ada_star_undirected(self):
        GG = self.XG.to_undirected()
        # make sure we get lower weight
        # to_undirected might choose either edge with weight 2 or weight 3
        GG["u"]["x"]["weight"] = 2
        GG["y"]["v"]["weight"] = 2

        search = ada_star(
            GG, "s", "v", heuristic=None, weight="weight", initial_epsilon=1
        )
        path = search.extract_path()
        assert path == ["s", "x", "u", "v"]
        assert nx.path_weight(GG, path, "weight") == 8

    def test_ada_star_undirected2(self):
        XG3 = nx.Graph()
        edges = [(0, 1, 2), (1, 2, 12), (2, 3, 1), (3, 4, 5), (4, 5, 1), (5, 0, 10)]
        XG3.add_weighted_edges_from(edges)
        search = ada_star(XG3, 0, 3, heuristic=None, weight="weight", initial_epsilon=1)
        path = search.extract_path()
        assert path == [0, 1, 2, 3]
        assert nx.path_weight(XG3, path, "weight") == 15

    def test_ada_star_undirected3(self):
        XG4 = nx.Graph()
        edges = [
            (0, 1, 2),
            (1, 2, 2),
            (2, 3, 1),
            (3, 4, 1),
            (4, 5, 1),
            (5, 6, 1),
            (6, 7, 1),
            (7, 0, 1),
        ]
        XG4.add_weighted_edges_from(edges)
        search = ada_star(XG4, 0, 2, heuristic=None, weight="weight", initial_epsilon=1)
        path = search.extract_path()
        assert path == [0, 1, 2]
        assert nx.path_weight(XG4, path, "weight") == 4

    def test_ada_star_w1(self):
        G = nx.DiGraph()
        G.add_edges_from(
            [
                ("s", "u"),
                ("s", "x"),
                ("u", "v"),
                ("u", "x"),
                ("v", "y"),
                ("x", "u"),
                ("x", "w"),
                ("w", "v"),
                ("x", "y"),
                ("y", "s"),
                ("y", "v"),
            ]
        )

        search = ada_star(
            G, "s", "v", heuristic=None, weight="weight", initial_epsilon=1
        )
        path = search.extract_path()
        assert path == ["s", "u", "v"]
        assert nx.shortest_path_length(G, "s", "v") == 2

    def test_cycle(self):
        C = nx.cycle_graph(7)
        search = ada_star(C, 0, 3, heuristic=None, weight="weight", initial_epsilon=1)
        path = search.extract_path()
        assert path == [0, 1, 2, 3]
        assert nx.shortest_path_length(C, 0, 4) == 3
        assert nx.dijkstra_path(C, 0, 4) == [0, 6, 5, 4]

    def test_unorderable_nodes(self):
        # Create the cycle graph on four nodes, with nodes represented
        # as (unorderable) Python objects.
        nodes = [object() for n in range(4)]
        G = nx.Graph()
        G.add_edges_from(pairwise(nodes, cyclic=True))
        search = ada_star(G, nodes[0], nodes[2], heuristic=None, initial_epsilon=1)
        path = search.extract_path()
        assert len(path) == 3

    def test_ada_star_anytime_dynamic(self):
        import math

        G = nx.random_geometric_graph(100, 0.20, seed=896803)
        for u, v, w in G.edges(data=True):  # Euclidean distance between nodes
            w["weight"] = math.sqrt(
                (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
                + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
            )
        source, target = 42, 25

        def heuristic(u, v):  # Euclidean distance between nodes
            return math.sqrt(
                (G.nodes[v]["pos"][0] - G.nodes[u]["pos"][0]) ** 2
                + (G.nodes[v]["pos"][1] - G.nodes[u]["pos"][1]) ** 2
            )

        # A* search for comparison
        path = nx.astar_path(G, source, target, heuristic)
        # create search object
        search = ada_star(G, source, target, heuristic=heuristic)

        # compute first suboptimal path epsilon = 2
        search.compute_or_improve_path(epsilon=2)
        path = search.extract_path()
        assert path == [42, 32, 24, 40, 59, 4, 66, 27, 35, 25]

        # compute second (better) suboptimal path
        search.compute_or_improve_path(epsilon=1.2)
        path = search.extract_path()
        assert path == [42, 32, 24, 12, 59, 4, 1, 27, 35, 25]

        # compute third (best) suboptimal path
        search.compute_or_improve_path(epsilon=1)
        path = search.extract_path()
        assert path == nx.astar_path(G, source, target, heuristic)
        assert nx.path_weight(G, path, "weight") == nx.astar_path_length(
            G, source, target, heuristic
        )

        # change graph edge weight
        search.update_graph([[49, 97, 0]])  # add edge between 77 and 15 with weight 0
        search.compute_or_improve_path(epsilon=1)
        path = search.extract_path()
        assert path == [42, 32, 19, 72, 49, 29, 31, 94, 35, 25]
        assert path == nx.astar_path(G, source, target, heuristic)
        assert nx.path_weight(G, path, "weight") == nx.astar_path_length(
            G, source, target, heuristic
        )

    def test_ada_star_NetworkXNoPath(self):
        G = nx.gnp_random_graph(10, 0.2, seed=10)
        with pytest.raises(nx.NetworkXNoPath):
            search = ada_star(
                G, 4, 9, heuristic=None, weight="weight", initial_epsilon=1
            )
            path = search.extract_path()

    def test_ada_star_NetworkXNoPath2(self):
        # graph with no edges
        G = nx.gnp_random_graph(10, 0.2, seed=10)
        for u, v in G.edges():
            G.remove_edge(u, v)

        with pytest.raises(nx.NetworkXNoPath):
            search = ada_star(
                G, 4, 9, heuristic=None, weight="weight", initial_epsilon=1
            )
            path = search.extract_path()

    def test_ada_star_NodeNotFound(self):
        G = nx.gnp_random_graph(10, 0.2, seed=10)
        with pytest.raises(nx.NodeNotFound):
            search = ada_star(G, 11, 9, heuristic=None, initial_epsilon=1)
