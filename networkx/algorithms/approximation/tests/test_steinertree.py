import pytest

import networkx as nx
from networkx.algorithms.approximation.steinertree import metric_closure, steiner_tree
from networkx.utils import edges_equal


class TestSteinerTree:
    @classmethod
    def setup_class(cls):
        G1 = nx.Graph()
        G1.add_edge(1, 2, weight=10)
        G1.add_edge(2, 3, weight=10)
        G1.add_edge(3, 4, weight=10)
        G1.add_edge(4, 5, weight=10)
        G1.add_edge(5, 6, weight=10)
        G1.add_edge(2, 7, weight=1)
        G1.add_edge(7, 5, weight=1)

        G2 = nx.Graph()
        G2.add_edge(0, 5, weight=6)
        G2.add_edge(1, 2, weight=2)
        G2.add_edge(1, 5, weight=3)
        G2.add_edge(2, 4, weight=4)
        G2.add_edge(3, 5, weight=5)
        G2.add_edge(4, 5, weight=1)

        G3 = nx.Graph()
        G3.add_edge(1, 2, weight=8)
        G3.add_edge(1, 9, weight=3)
        G3.add_edge(1, 8, weight=6)
        G3.add_edge(1, 10, weight=2)
        G3.add_edge(1, 14, weight=3)
        G3.add_edge(2, 3, weight=6)
        G3.add_edge(3, 4, weight=3)
        G3.add_edge(3, 10, weight=2)
        G3.add_edge(3, 11, weight=1)
        G3.add_edge(4, 5, weight=1)
        G3.add_edge(4, 11, weight=1)
        G3.add_edge(5, 6, weight=4)
        G3.add_edge(5, 11, weight=2)
        G3.add_edge(5, 12, weight=1)
        G3.add_edge(5, 13, weight=3)
        G3.add_edge(6, 7, weight=2)
        G3.add_edge(6, 12, weight=3)
        G3.add_edge(6, 13, weight=1)
        G3.add_edge(7, 8, weight=3)
        G3.add_edge(7, 9, weight=3)
        G3.add_edge(7, 11, weight=5)
        G3.add_edge(7, 13, weight=2)
        G3.add_edge(7, 14, weight=4)
        G3.add_edge(8, 9, weight=2)
        G3.add_edge(9, 14, weight=1)
        G3.add_edge(10, 11, weight=2)
        G3.add_edge(10, 14, weight=1)
        G3.add_edge(11, 12, weight=1)
        G3.add_edge(11, 14, weight=7)
        G3.add_edge(12, 14, weight=3)
        G3.add_edge(12, 15, weight=1)
        G3.add_edge(13, 14, weight=4)
        G3.add_edge(13, 15, weight=1)
        G3.add_edge(14, 15, weight=2)

        cls.G1 = G1
        cls.G2 = G2
        cls.G3 = G3
        cls.G1_term_nodes = [1, 2, 3, 4, 5]
        cls.G2_term_nodes = [0, 2, 3]
        cls.G3_term_nodes = [1, 3, 5, 6, 8, 10, 11, 12, 13]

        cls.methods = ["kou", "mehlhorn"]

    def test_connected_metric_closure(self):
        G = self.G1.copy()
        G.add_node(100)
        pytest.raises(nx.NetworkXError, metric_closure, G)

    def test_metric_closure(self):
        M = metric_closure(self.G1)
        mc = [
            (1, 2, {"distance": 10, "path": [1, 2]}),
            (1, 3, {"distance": 20, "path": [1, 2, 3]}),
            (1, 4, {"distance": 22, "path": [1, 2, 7, 5, 4]}),
            (1, 5, {"distance": 12, "path": [1, 2, 7, 5]}),
            (1, 6, {"distance": 22, "path": [1, 2, 7, 5, 6]}),
            (1, 7, {"distance": 11, "path": [1, 2, 7]}),
            (2, 3, {"distance": 10, "path": [2, 3]}),
            (2, 4, {"distance": 12, "path": [2, 7, 5, 4]}),
            (2, 5, {"distance": 2, "path": [2, 7, 5]}),
            (2, 6, {"distance": 12, "path": [2, 7, 5, 6]}),
            (2, 7, {"distance": 1, "path": [2, 7]}),
            (3, 4, {"distance": 10, "path": [3, 4]}),
            (3, 5, {"distance": 12, "path": [3, 2, 7, 5]}),
            (3, 6, {"distance": 22, "path": [3, 2, 7, 5, 6]}),
            (3, 7, {"distance": 11, "path": [3, 2, 7]}),
            (4, 5, {"distance": 10, "path": [4, 5]}),
            (4, 6, {"distance": 20, "path": [4, 5, 6]}),
            (4, 7, {"distance": 11, "path": [4, 5, 7]}),
            (5, 6, {"distance": 10, "path": [5, 6]}),
            (5, 7, {"distance": 1, "path": [5, 7]}),
            (6, 7, {"distance": 11, "path": [6, 5, 7]}),
        ]
        assert edges_equal(list(M.edges(data=True)), mc)

    def test_steiner_tree(self):
        valid_steiner_trees = [
            [
                [
                    (1, 2, {"weight": 10}),
                    (2, 3, {"weight": 10}),
                    (2, 7, {"weight": 1}),
                    (3, 4, {"weight": 10}),
                    (5, 7, {"weight": 1}),
                ],
                [
                    (1, 2, {"weight": 10}),
                    (2, 7, {"weight": 1}),
                    (3, 4, {"weight": 10}),
                    (4, 5, {"weight": 10}),
                    (5, 7, {"weight": 1}),
                ],
                [
                    (1, 2, {"weight": 10}),
                    (2, 3, {"weight": 10}),
                    (2, 7, {"weight": 1}),
                    (4, 5, {"weight": 10}),
                    (5, 7, {"weight": 1}),
                ],
            ],
            [
                [
                    (0, 5, {"weight": 6}),
                    (1, 2, {"weight": 2}),
                    (1, 5, {"weight": 3}),
                    (3, 5, {"weight": 5}),
                ],
                [
                    (0, 5, {"weight": 6}),
                    (4, 2, {"weight": 4}),
                    (4, 5, {"weight": 1}),
                    (3, 5, {"weight": 5}),
                ],
            ],
            [
                [
                    (1, 10, {"weight": 2}),
                    (3, 10, {"weight": 2}),
                    (3, 11, {"weight": 1}),
                    (5, 12, {"weight": 1}),
                    (6, 13, {"weight": 1}),
                    (8, 9, {"weight": 2}),
                    (9, 14, {"weight": 1}),
                    (10, 14, {"weight": 1}),
                    (11, 12, {"weight": 1}),
                    (12, 15, {"weight": 1}),
                    (13, 15, {"weight": 1}),
                ]
            ],
        ]
        for method in self.methods:
            for G, term_nodes, valid_trees in zip(
                [self.G1, self.G2, self.G3],
                [self.G1_term_nodes, self.G2_term_nodes, self.G3_term_nodes],
                valid_steiner_trees,
            ):
                S = steiner_tree(G, term_nodes, method=method)
                assert any(
                    edges_equal(list(S.edges(data=True)), valid_tree)
                    for valid_tree in valid_trees
                )

    def test_multigraph_steiner_tree(self):
        G = nx.MultiGraph()
        G.add_edges_from(
            [
                (1, 2, 0, {"weight": 1}),
                (2, 3, 0, {"weight": 999}),
                (2, 3, 1, {"weight": 1}),
                (3, 4, 0, {"weight": 1}),
                (3, 5, 0, {"weight": 1}),
            ]
        )
        terminal_nodes = [2, 4, 5]
        expected_edges = [
            (2, 3, 1, {"weight": 1}),  # edge with key 1 has lower weight
            (3, 4, 0, {"weight": 1}),
            (3, 5, 0, {"weight": 1}),
        ]
        for method in self.methods:
            S = steiner_tree(G, terminal_nodes, method=method)
            assert edges_equal(S.edges(data=True, keys=True), expected_edges)
