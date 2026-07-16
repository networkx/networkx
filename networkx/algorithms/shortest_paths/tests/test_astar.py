import random

import pytest

import networkx as nx
from networkx.utils import pairwise


class TestAStar:
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
        """Tests that A* algorithm finds any of multiple optimal paths"""
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
        assert nx.astar_path(graph, "a", "d", h) in (path1, path2)

    def test_astar_directed(self):
        assert nx.astar_path(self.XG, "s", "v") == ["s", "x", "u", "v"]
        assert nx.astar_path_length(self.XG, "s", "v") == 9

    def test_astar_directed_weight_function(self):
        def w1(u, v, d):
            return d["weight"]

        assert nx.astar_path(self.XG, "x", "u", weight=w1) == ["x", "u"]
        assert nx.astar_path_length(self.XG, "x", "u", weight=w1) == 3
        assert nx.astar_path(self.XG, "s", "v", weight=w1) == ["s", "x", "u", "v"]
        assert nx.astar_path_length(self.XG, "s", "v", weight=w1) == 9

        def w2(u, v, d):
            return None if (u, v) == ("x", "u") else d["weight"]

        assert nx.astar_path(self.XG, "x", "u", weight=w2) == ["x", "y", "s", "u"]
        assert nx.astar_path_length(self.XG, "x", "u", weight=w2) == 19
        assert nx.astar_path(self.XG, "s", "v", weight=w2) == ["s", "x", "v"]
        assert nx.astar_path_length(self.XG, "s", "v", weight=w2) == 10

        def w3(u, v, d):
            return d["weight"] + 10

        assert nx.astar_path(self.XG, "x", "u", weight=w3) == ["x", "u"]
        assert nx.astar_path_length(self.XG, "x", "u", weight=w3) == 13
        assert nx.astar_path(self.XG, "s", "v", weight=w3) == ["s", "x", "v"]
        assert nx.astar_path_length(self.XG, "s", "v", weight=w3) == 30

    def test_astar_multigraph(self):
        G = nx.MultiDiGraph(self.XG)
        G.add_weighted_edges_from((u, v, 1000) for (u, v) in list(G.edges()))
        assert nx.astar_path(G, "s", "v") == ["s", "x", "u", "v"]
        assert nx.astar_path_length(G, "s", "v") == 9

    def test_astar_undirected(self):
        GG = self.XG.to_undirected()
        # make sure we get lower weight
        # to_undirected might choose either edge with weight 2 or weight 3
        GG["u"]["x"]["weight"] = 2
        GG["y"]["v"]["weight"] = 2
        assert nx.astar_path(GG, "s", "v") == ["s", "x", "u", "v"]
        assert nx.astar_path_length(GG, "s", "v") == 8

    def test_astar_directed2(self):
        XG2 = nx.DiGraph()
        edges = [
            (1, 4, 1),
            (4, 5, 1),
            (5, 6, 1),
            (6, 3, 1),
            (1, 3, 50),
            (1, 2, 100),
            (2, 3, 100),
        ]
        XG2.add_weighted_edges_from(edges)
        assert nx.astar_path(XG2, 1, 3) == [1, 4, 5, 6, 3]

    def test_astar_undirected2(self):
        XG3 = nx.Graph()
        edges = [(0, 1, 2), (1, 2, 12), (2, 3, 1), (3, 4, 5), (4, 5, 1), (5, 0, 10)]
        XG3.add_weighted_edges_from(edges)
        assert nx.astar_path(XG3, 0, 3) == [0, 1, 2, 3]
        assert nx.astar_path_length(XG3, 0, 3) == 15

    def test_astar_undirected3(self):
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
        assert nx.astar_path(XG4, 0, 2) == [0, 1, 2]
        assert nx.astar_path_length(XG4, 0, 2) == 4

    """ Tests that A* finds correct path when multiple paths exist
        and the best one is not expanded first (GH issue #3464)
    """

    def test_astar_directed3(self):
        heuristic_values = {"n5": 36, "n2": 4, "n1": 0, "n0": 0}

        def h(u, v):
            return heuristic_values[u]

        edges = [("n5", "n1", 11), ("n5", "n2", 9), ("n2", "n1", 1), ("n1", "n0", 32)]
        graph = nx.DiGraph()
        graph.add_weighted_edges_from(edges)
        answer = ["n5", "n2", "n1", "n0"]
        assert nx.astar_path(graph, "n5", "n0", h) == answer

    """ Tests that parent is not wrongly overridden when a node
        is re-explored multiple times.
    """

    def test_astar_directed4(self):
        edges = [
            ("a", "b", 1),
            ("a", "c", 1),
            ("b", "d", 2),
            ("c", "d", 1),
            ("d", "e", 1),
        ]
        graph = nx.DiGraph()
        graph.add_weighted_edges_from(edges)
        assert nx.astar_path(graph, "a", "e") == ["a", "c", "d", "e"]

    # >>> MXG4=NX.MultiGraph(XG4)
    # >>> MXG4.add_edge(0,1,3)
    # >>> NX.dijkstra_path(MXG4,0,2)
    # [0, 1, 2]

    def test_astar_w1(self):
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
        assert nx.astar_path(G, "s", "v") == ["s", "u", "v"]
        assert nx.astar_path_length(G, "s", "v") == 2

    def test_astar_nopath(self):
        with pytest.raises(nx.NodeNotFound):
            nx.astar_path(self.XG, "s", "moon")

    def test_astar_cutoff(self):
        with pytest.raises(nx.NetworkXNoPath):
            # optimal path_length in XG is 9
            nx.astar_path(self.XG, "s", "v", cutoff=8.0)
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path_length(self.XG, "s", "v", cutoff=8.0)

    def test_astar_admissible_heuristic_with_cutoff(self):
        heuristic_values = {"s": 36, "y": 4, "x": 0, "u": 0, "v": 0}

        def h(u, v):
            return heuristic_values[u]

        assert nx.astar_path_length(self.XG, "s", "v") == 9
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h) == 9
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=12) == 9
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=9) == 9
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=8)

    def test_astar_inadmissible_heuristic_with_cutoff(self):
        heuristic_values = {"s": 36, "y": 14, "x": 10, "u": 10, "v": 0}

        def h(u, v):
            return heuristic_values[u]

        # optimal path_length in XG is 9. This heuristic gives over-estimate.
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h) == 10
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=15) == 10
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=9)
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=12)

    def test_astar_cutoff2(self):
        assert nx.astar_path(self.XG, "s", "v", cutoff=10.0) == ["s", "x", "u", "v"]
        assert nx.astar_path_length(self.XG, "s", "v") == 9

    def test_cycle(self):
        C = nx.cycle_graph(7)
        assert nx.astar_path(C, 0, 3) == [0, 1, 2, 3]
        assert nx.dijkstra_path(C, 0, 4) == [0, 6, 5, 4]

    def test_unorderable_nodes(self):
        """Tests that A* accommodates nodes that are not orderable.

        For more information, see issue #554.

        """
        # Create the cycle graph on four nodes, with nodes represented
        # as (unorderable) Python objects.
        nodes = [object() for n in range(4)]
        G = nx.Graph()
        G.add_edges_from(pairwise(nodes, cyclic=True))
        path = nx.astar_path(G, nodes[0], nodes[2])
        assert len(path) == 3

    def test_astar_NetworkXNoPath(self):
        """Tests that exception is raised when there exists no
        path between source and target"""
        G = nx.gnp_random_graph(10, 0.2, seed=10)
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path(G, 4, 9)

    def test_astar_NodeNotFound(self):
        """Tests that exception is raised when either
        source or target is not in graph"""
        G = nx.gnp_random_graph(10, 0.2, seed=10)
        with pytest.raises(nx.NodeNotFound):
            nx.astar_path_length(G, 11, 9)

    def test_alt_heuristic(self):
        """Tests that alt_heuristic returns a heuristic function
        that is admissible and consistent"""
        G = nx.grid_graph(dim=[5, 5])  # nodes are two-tuples (x,y)
        h = nx.alt_heuristic(G, k=4, weight="weight", method="farthest", seed=10)
        for u in G.nodes():
            for v in G.nodes():
                assert h(u, v) <= nx.shortest_path_length(G, u, v)

    def test_alt_heuristic_k_greater_than_nodes(self):
        """Tests that alt_heuristic caps k at the number of nodes in the graph"""
        G = nx.grid_graph(dim=[3, 3])
        h = nx.alt_heuristic(G, k=10, weight="weight", method="farthest", seed=10)
        for u in G.nodes():
            for v in G.nodes():
                assert h(u, v) <= nx.shortest_path_length(G, u, v)

    def test_alt_heuristic_negative_k(self):
        """Tests that alt_heuristic raises NetworkXError for negative k"""
        G = nx.grid_graph(dim=[3, 3])
        with pytest.raises(nx.NetworkXError):
            nx.alt_heuristic(G, k=-1, weight="weight", method="farthest", seed=10)

    def test_alt_heuristic_zero_k(self):
        """Tests that alt_heuristic raises NetworkXError for k=0"""
        G = nx.grid_graph(dim=[3, 3])
        with pytest.raises(nx.NetworkXError):
            nx.alt_heuristic(G, k=0, weight="weight", method="farthest", seed=10)

    def test_alt_heuristic_invalid_method(self):
        """Tests that alt_heuristic raises ValueError for invalid
        method (not 'farthest' or 'random')"""
        G = nx.grid_graph(dim=[3, 3])
        with pytest.raises(ValueError):
            nx.alt_heuristic(G, k=4, weight="weight", method="invalid", seed=10)

    def test_alt_heuristic_empty_graph(self):
        with pytest.raises(nx.NetworkXPointlessConcept):
            nx.alt_heuristic(nx.Graph())

    def test_alt_heuristic_default_weight_directed(self):
        # Regression guard: with default arguments on a directed weighted graph,
        # the heuristic must stay admissible
        G = self._weighted_random_graph(25, 120, seed=10, directed=True)
        h = nx.alt_heuristic(G, k=4, seed=10)
        assert self._admissible(G, h)

    def test_alt_heuristic_directed_consistent(self):
        G = self._weighted_random_graph(25, 120, seed=2, directed=True)
        h = nx.alt_heuristic(G, k=6, weight="weight", seed=3)
        assert self._admissible(G, h)
        assert self._consistent(G, h)

    def test_alt_heuristic_random_method(self):
        G = nx.grid_2d_graph(5, 5)
        nx.set_edge_attributes(G, 1, "weight")
        h = nx.alt_heuristic(G, k=4, weight="weight", method="random", seed=7)
        assert self._admissible(G, h)

    def test_alt_heuristic_disconnected(self):
        G = nx.disjoint_union(nx.path_graph(5), nx.cycle_graph(5))
        nx.set_edge_attributes(G, 1, "weight")
        h = nx.alt_heuristic(G, k=3, weight="weight", seed=0)
        assert all(0 <= h(u, 7) < float("inf") for u in G)

    def test_alt_heuristic_matches_dijkstra(self):
        G = self._weighted_random_graph(40, 150, seed=3, directed=True)
        h = nx.alt_heuristic(G, k=8, weight="weight", seed=0)
        rng = random.Random(0)
        pairs = 0
        while pairs < 15:
            s, t = rng.sample(list(G), 2)
            if not nx.has_path(G, s, t):
                continue
            pairs += 1
            assert nx.astar_path_length(
                G, s, t, heuristic=h, weight="weight"
            ) == pytest.approx(nx.dijkstra_path_length(G, s, t, weight="weight"))

    def _admissible(self, G, h, weight="weight"):
        true = dict(nx.all_pairs_dijkstra_path_length(G, weight=weight))
        return all(h(u, t) <= true[u].get(t, float("inf")) + 1e-9 for t in G for u in G)

    def _consistent(self, G, h, weight="weight"):
        for t in G:
            for u, v, d in G.edges(data=True):
                w = d.get(weight, 1)
                if h(u, t) > w + h(v, t) + 1e-9:
                    return False
                if not G.is_directed() and h(v, t) > w + h(u, t) + 1e-9:
                    return False
        return True

    def _weighted_random_graph(self, n, m, seed, directed=False):
        G = nx.gnm_random_graph(n, m, seed=seed, directed=directed)
        for u, v in G.edges():
            G[u][v]["weight"] = random.Random(u * 31 + v).uniform(0.1, 5)
        return G
