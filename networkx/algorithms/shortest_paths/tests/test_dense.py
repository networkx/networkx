from random import Random

import pytest

import networkx as nx

floyd_fns = [
    nx.floyd_warshall_predecessor_and_distance,
    nx.floyd_warshall_tree,
]


@pytest.mark.parametrize("floyd_fn", floyd_fns)
class TestFloyd:
    @classmethod
    def setup_class(cls):
        pass

    def test_floyd_warshall_predecessor_and_distance(self, floyd_fn):
        XG = nx.DiGraph()
        XG.add_weighted_edges_from(
            [
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
        )
        path, dist = floyd_fn(XG)
        assert dist["s"]["v"] == 9
        assert path["s"]["v"] == "u"
        assert dist == {
            "y": {"y": 0, "x": 12, "s": 7, "u": 15, "v": 6},
            "x": {"y": 2, "x": 0, "s": 9, "u": 3, "v": 4},
            "s": {"y": 7, "x": 5, "s": 0, "u": 8, "v": 9},
            "u": {"y": 2, "x": 2, "s": 9, "u": 0, "v": 1},
            "v": {"y": 1, "x": 13, "s": 8, "u": 16, "v": 0},
        }

        GG = XG.to_undirected()
        # make sure we get lower weight
        # to_undirected might choose either edge with weight 2 or weight 3
        GG["u"]["x"]["weight"] = 2
        path, dist = floyd_fn(GG)
        assert dist["s"]["v"] == 8
        # skip this test, could be alternate path s-u-v
        #        assert_equal(path['s']['v'],'y')

        G = nx.DiGraph()  # no weights
        G.add_edges_from(
            [
                ("s", "u"),
                ("s", "x"),
                ("u", "v"),
                ("u", "x"),
                ("v", "y"),
                ("x", "u"),
                ("x", "v"),
                ("x", "y"),
                ("y", "s"),
                ("y", "v"),
            ]
        )
        path, dist = floyd_fn(G)
        assert dist["s"]["v"] == 2
        # skip this test, could be alternate path s-u-v
        # assert_equal(path['s']['v'],'x')

        # floyd_warshall_predecessor_and_distance returns
        # dicts-of-defautdicts
        # make sure we don't get empty dictionary
        XG = nx.DiGraph()
        XG.add_weighted_edges_from(
            [("v", "x", 5.0), ("y", "x", 5.0), ("v", "y", 6.0), ("x", "u", 2.0)]
        )
        path, dist = floyd_fn(XG)
        inf = float("inf")
        assert dist == {
            "v": {"v": 0, "x": 5.0, "y": 6.0, "u": 7.0},
            "x": {"x": 0, "u": 2.0, "v": inf, "y": inf},
            "y": {"y": 0, "x": 5.0, "v": inf, "u": 7.0},
            "u": {"u": 0, "v": inf, "x": inf, "y": inf},
        }
        assert path == {
            "v": {"x": "v", "y": "v", "u": "x"},
            "x": {"u": "x"},
            "y": {"x": "y", "u": "x"},
        }

    def test_reconstruct_path(self, floyd_fn):
        with pytest.raises(KeyError):
            XG = nx.DiGraph()
            XG.add_weighted_edges_from(
                [
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
            )
            predecessors, _ = floyd_fn(XG)

            path = nx.reconstruct_path("s", "v", predecessors)
            assert path == ["s", "x", "u", "v"]

            path = nx.reconstruct_path("s", "s", predecessors)
            assert path == []

            # this part raises the keyError
            nx.reconstruct_path("1", "2", predecessors)

    def test_cycle(self, floyd_fn):
        path, dist = floyd_fn(nx.cycle_graph(7))
        assert dist[0][3] == 3
        assert path[0][3] == 2
        assert dist[0][4] == 3

    def test_weighted(self, floyd_fn):
        XG3 = nx.Graph()
        XG3.add_weighted_edges_from(
            [[0, 1, 2], [1, 2, 12], [2, 3, 1], [3, 4, 5], [4, 5, 1], [5, 0, 10]]
        )
        path, dist = floyd_fn(XG3)
        assert dist[0][3] == 15
        assert path[0][3] == 2

    def test_weighted2(self, floyd_fn):
        XG4 = nx.Graph()
        XG4.add_weighted_edges_from(
            [
                [0, 1, 2],
                [1, 2, 2],
                [2, 3, 1],
                [3, 4, 1],
                [4, 5, 1],
                [5, 6, 1],
                [6, 7, 1],
                [7, 0, 1],
            ]
        )
        path, dist = floyd_fn(XG4)
        assert dist[0][2] == 4
        assert path[0][2] == 1

    def test_weight_parameter(self, floyd_fn):
        XG4 = nx.Graph()
        XG4.add_edges_from(
            [
                (0, 1, {"heavy": 2}),
                (1, 2, {"heavy": 2}),
                (2, 3, {"heavy": 1}),
                (3, 4, {"heavy": 1}),
                (4, 5, {"heavy": 1}),
                (5, 6, {"heavy": 1}),
                (6, 7, {"heavy": 1}),
                (7, 0, {"heavy": 1}),
            ]
        )
        path, dist = floyd_fn(XG4, weight="heavy")
        assert dist[0][2] == 4
        assert path[0][2] == 1

    def test_zero_distance(self, floyd_fn):
        XG = nx.DiGraph()
        XG.add_weighted_edges_from(
            [
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
                ("x", "x", 3),  # added a positive self loop
            ]
        )
        path, dist = floyd_fn(XG)

        for u in XG:
            assert dist[u][u] == 0

        GG = XG.to_undirected()
        # make sure we get lower weight
        # to_undirected might choose either edge with weight 2 or weight 3
        GG["u"]["x"]["weight"] = 2
        path, dist = floyd_fn(GG)

        for u in GG:
            assert dist[u][u] == 0

    def test_zero_weight(self, floyd_fn):
        G = nx.DiGraph()
        edges = [(1, 2, -2), (2, 3, -4), (1, 5, 1), (5, 4, 0), (4, 3, -5), (2, 5, -7)]
        G.add_weighted_edges_from(edges)

        pred, dist = floyd_fn(G)
        assert dist[1][3] == -14

        G = nx.MultiDiGraph()
        edges.append((2, 5, -7))
        G.add_weighted_edges_from(edges)

        pred, dist = floyd_fn(G)
        assert dist[1][3] == -14

    def test_weight_function(self, floyd_fn):
        """Floyd Warshall algorithm using user defined weight function"""
        G = nx.complete_graph(3)
        G.adj[0][2]["weight"] = 10  # assymetric
        G.adj[0][1]["weight"] = 1
        G.adj[1][2]["weight"] = 1

        # weight function is inverse of "weight"
        def weight(u, v, d):
            return 1 / d["weight"]

        pred, dist = floyd_fn(G, weight)
        # shortest: direct edge (smallest inverse "weight") dist=1/10
        assert dist[0][2] == 1 / 10

        def weight_02_hidden(u, v, d):
            if u == 0 and v == 2:
                return None  # hides direct edge 0--2
            return 1 / d["weight"]

        pred, dist = floyd_fn(G, weight_02_hidden)
        # Direct edge hidden ==> Only 1 path exist ==> dist=2
        assert dist[0][2] == 2

    def test_negative_cycle(self, floyd_fn):
        G = nx.cycle_graph(5, create_using=nx.DiGraph())
        G.add_edge(1, 2, weight=-7)
        pytest.raises(nx.NetworkXUnbounded, floyd_fn, G)

        G = nx.cycle_graph(5)  # undirected Graph
        G.add_edge(1, 2, weight=-3)
        pytest.raises(nx.NetworkXUnbounded, floyd_fn, G)

        G.add_edge(1, 2, weight=-7)
        pytest.raises(nx.NetworkXUnbounded, floyd_fn, G)

        G = nx.DiGraph([(1, 1, {"weight": -1})])
        pytest.raises(nx.NetworkXUnbounded, floyd_fn, G)

        G = nx.MultiDiGraph([(1, 1, {"weight": -1})])
        pytest.raises(nx.NetworkXUnbounded, floyd_fn, G)

        G = nx.Graph()
        G.add_edge(0, 1, weight=-1)
        pytest.raises(nx.NetworkXUnbounded, floyd_fn, G)

        G = nx.cycle_graph(5, create_using=nx.DiGraph())
        nx.add_cycle(G, [3, 5, 6, 7, 8, 9])
        G.add_edge(1, 2, weight=-30)
        pytest.raises(nx.NetworkXUnbounded, floyd_fn, G)

    def test_zero_cycle(self, floyd_fn):
        G = nx.cycle_graph(5, create_using=nx.DiGraph())
        G.add_edge(2, 3, weight=-4)
        floyd_fn(G)  # check that zero cycle doesn't raise

        G.add_edge(2, 3, weight=-4.0001)
        # check that negative cycle does raise
        pytest.raises(nx.NetworkXUnbounded, floyd_fn, G)


@pytest.mark.parametrize("seed", list(range(10)))
@pytest.mark.parametrize("n", list(range(10, 20)))
@pytest.mark.parametrize("prob", [x / 10 for x in range(0, 10, 2)])
def test_floyd_warshall_consistency(seed, n, prob):
    """Validate consistency of all Floyd-Warshall algorithm variants.

    Distances returned by nx.floyd_warshall_predecessor_and_distance
    and nx.floyd_warshall_tree must match on the same graph for both
    unweighted and weighted cases. The graph may be connected or
    disconnected; behavior must remain consistent.

    Note: Predecessor data can differ when multiple shortest paths exist.
    """
    rng = Random(seed)

    # random graph, possibly disconnected
    graph = nx.erdos_renyi_graph(n, prob, seed=rng)

    # unweighted case
    base_pred, base_dist = floyd_fns[0](graph)
    for floyd_fn in floyd_fns[1:]:
        pred, dist = floyd_fn(graph)
        for u in graph:
            for v in graph:
                assert dist[u][v] == base_dist[u][v]

    # weighted case
    max_weight_list = [5, 10, 1000]
    for max_weight in max_weight_list:
        for u, v in graph.edges():
            graph[u][v]["w"] = rng.randint(1, max_weight)

        base_pred_w, base_dist_w = floyd_fns[0](graph, weight="w")
        for floyd_fn in floyd_fns[1:]:
            pred_w, dist_w = floyd_fn(graph, weight="w")
            for u in graph:
                for v in graph:
                    assert dist_w[u][v] == base_dist_w[u][v]
