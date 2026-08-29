import pytest

import networkx as nx
from networkx.algorithms.approximation.steinertree import (
    _remove_nonterminal_leaves,
    metric_closure,
    steiner_tree,
)
from networkx.utils import edges_equal


@pytest.fixture(params=["kou", "mehlhorn"])
def method(request):
    return request.param


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

        G4 = nx.Graph()
        G4.add_edge(0, 2, my_weight=2)
        G4.add_edge(0, 1, my_weight=0.1)
        G4.add_edge(1, 2, my_weight=0.1)
        G4.add_edge(2, 3, my_weight=1)
        G4.add_edge(2, 4)

        cls.G1 = G1
        cls.G2 = G2
        cls.G3 = G3
        cls.G4 = G4

        cls.G1_term_nodes = [1, 2, 3, 4, 5]
        cls.G2_term_nodes = [0, 2, 3]
        cls.G3_term_nodes = [1, 3, 5, 6, 8, 10, 11, 12, 13]
        cls.G4_term_nodes = [0, 3, 4]

    def test_connected_metric_closure(self):
        G = self.G1.copy()
        G.add_node(100)
        with pytest.raises(nx.NetworkXError):
            with pytest.deprecated_call():
                metric_closure(G)

    def test_metric_closure(self):
        with pytest.deprecated_call():
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

    def test_steiner_tree(self, method):
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

    def test_multigraph_steiner_tree(self, method):
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
        S = steiner_tree(G, terminal_nodes, method=method)
        assert edges_equal(S.edges(data=True, keys=True), expected_edges)

    def test_remove_nonterminal_leaves(self):
        G = nx.path_graph(10)
        _remove_nonterminal_leaves(G, [4, 5, 6])

        assert list(G) == [4, 5, 6]  # only the terminal nodes are left

    @pytest.mark.parametrize(
        ("weight", "expected_edges"),
        [
            (
                None,
                [
                    (0, 2, {"my_weight": 2}),
                    (2, 3, {"my_weight": 1}),
                    (2, 4, {}),
                ],
            ),
            (
                "my_weight",
                [
                    (0, 1, {"my_weight": 0.1}),
                    (1, 2, {"my_weight": 0.1}),
                    (2, 3, {"my_weight": 1}),
                    (2, 4, {}),
                ],
            ),
        ],
    )
    def test_weighted(self, method, weight, expected_edges):
        G = self.G4
        terminal_nodes = self.G4_term_nodes

        S = steiner_tree(G, terminal_nodes, method=method, weight=weight)
        assert edges_equal(list(S.edges(data=True)), expected_edges)


def test_steiner_tree_weight_attribute(method):
    G = nx.star_graph(4)
    # Add an edge attribute that is named something other than "weight"
    nx.set_edge_attributes(G, {e: 10 for e in G.edges}, name="distance")
    H = nx.approximation.steiner_tree(G, [1, 3], method=method, weight="distance")
    assert nx.utils.edges_equal(H.edges, [(0, 1), (0, 3)])


def test_steiner_tree_multigraph_weight_attribute(method):
    G = nx.cycle_graph(3, create_using=nx.MultiGraph)
    nx.set_edge_attributes(G, {e: 10 for e in G.edges}, name="distance")
    G.add_edge(2, 0, distance=5)
    H = nx.approximation.steiner_tree(G, list(G), method=method, weight="distance")
    assert len(H.edges) == 2 and H.has_edge(2, 0, key=1)
    assert sum(dist for *_, dist in H.edges(data="distance")) == 15


@pytest.mark.parametrize("method", (None, "mehlhorn", "kou"))
def test_steiner_tree_methods(method):
    G = nx.star_graph(4)
    expected = nx.Graph([(0, 1), (0, 3)])
    st = nx.approximation.steiner_tree(G, [1, 3], method=method)
    assert nx.utils.edges_equal(st.edges, expected.edges)


def test_steiner_tree_method_invalid():
    G = nx.star_graph(4)
    with pytest.raises(
        ValueError, match="invalid_method is not a valid choice for an algorithm."
    ):
        nx.approximation.steiner_tree(G, terminal_nodes=[1, 3], method="invalid_method")


def test_steiner_tree_remove_non_terminal_leaves_self_loop_edges():
    # To verify that the last step of the steiner tree approximation
    # behaves in the case where a non-terminal leaf has a self loop edge
    G = nx.path_graph(10)

    # Add self loops to the terminal nodes
    G.add_edges_from([(2, 2), (3, 3), (4, 4), (7, 7), (8, 8)])

    # Remove non-terminal leaves
    _remove_nonterminal_leaves(G, [4, 5, 6, 7])

    # The terminal nodes should be left
    assert list(G) == [4, 5, 6, 7]  # only the terminal nodes are left


def test_steiner_tree_non_terminal_leaves_multigraph_self_loop_edges():
    # To verify that the last step of the steiner tree approximation
    # behaves in the case where a non-terminal leaf has a self loop edge
    G = nx.MultiGraph()
    G.add_edges_from([(i, i + 1) for i in range(10)])
    G.add_edges_from([(2, 2), (3, 3), (4, 4), (4, 4), (7, 7)])

    # Remove non-terminal leaves
    _remove_nonterminal_leaves(G, [4, 5, 6, 7])

    # Only the terminal nodes should be left
    assert list(G) == [4, 5, 6, 7]


def test_steiner_tree_result_is_a_tree(method):
    # Regression test for gh-3820: when several shortest paths tie for
    # optimal, the union of the paths selected for the edges of the
    # metric-closure MST could contain a cycle, so `steiner_tree` returned
    # a graph with cycles instead of a tree.  The extra spanning-tree step
    # in `_kou_steiner_tree` (gh-7767) removes such cycles; this test pins
    # that behavior down with the graph reported in gh-3820, which
    # includes zero-weight edges and many shortest-path ties.
    #
    # fmt: off
    # (keep the reported edge list compact)
    edges = [
        (0, 16, {'weight': 0}), (0, 24, {'weight': 0}), (0, 32, {'weight': 0}),
        (0, 40, {'weight': 0}), (0, 48, {'weight': 0}), (0, 56, {'weight': 0}),
        (0, 64, {'weight': 0}), (0, 72, {'weight': 0}), (1, 16, {}),
        (1, 24, {}), (1, 32, {}), (1, 40, {}),
        (1, 48, {}), (1, 56, {}), (1, 64, {}),
        (1, 72, {}), (2, 16, {}), (2, 24, {}),
        (2, 32, {}), (2, 40, {}), (2, 48, {}),
        (2, 56, {}), (2, 64, {}), (2, 72, {}),
        (3, 16, {}), (3, 24, {}), (3, 32, {}),
        (3, 40, {}), (3, 48, {}), (3, 56, {}),
        (3, 64, {}), (3, 72, {}), (4, 17, {}),
        (4, 25, {}), (4, 33, {}), (4, 41, {}),
        (4, 49, {}), (4, 57, {}), (4, 65, {}),
        (4, 73, {}), (5, 17, {}), (5, 25, {}),
        (5, 33, {}), (5, 41, {}), (5, 49, {}),
        (5, 57, {}), (5, 65, {}), (5, 73, {}),
        (6, 17, {}), (6, 25, {}), (6, 33, {}),
        (6, 41, {}), (6, 49, {}), (6, 57, {}),
        (6, 65, {}), (6, 73, {}), (7, 17, {'weight': 0}),
        (7, 25, {'weight': 0}), (7, 33, {'weight': 0}), (7, 41, {'weight': 0}),
        (7, 49, {'weight': 0}), (7, 57, {'weight': 0}), (7, 65, {'weight': 0}),
        (7, 73, {'weight': 0}), (8, 18, {}), (8, 26, {}),
        (8, 34, {}), (8, 42, {}), (8, 50, {}),
        (8, 58, {}), (8, 66, {}), (8, 74, {}),
        (9, 18, {}), (9, 26, {}), (9, 34, {}),
        (9, 42, {}), (9, 50, {}), (9, 58, {}),
        (9, 66, {}), (9, 74, {}), (10, 18, {}),
        (10, 26, {}), (10, 34, {}), (10, 42, {}),
        (10, 50, {}), (10, 58, {}), (10, 66, {}),
        (10, 74, {}), (11, 18, {}), (11, 26, {}),
        (11, 34, {}), (11, 42, {}), (11, 50, {}),
        (11, 58, {}), (11, 66, {}), (11, 74, {}),
        (12, 19, {}), (12, 27, {}), (12, 35, {}),
        (12, 43, {}), (12, 51, {}), (12, 59, {}),
        (12, 67, {}), (12, 75, {}), (13, 19, {}),
        (13, 27, {}), (13, 35, {}), (13, 43, {}),
        (13, 51, {}), (13, 59, {}), (13, 67, {}),
        (13, 75, {}), (14, 19, {}), (14, 27, {}),
        (14, 35, {}), (14, 43, {}), (14, 51, {}),
        (14, 59, {}), (14, 67, {}), (14, 75, {}),
        (15, 19, {}), (15, 27, {}), (15, 35, {}),
        (15, 43, {}), (15, 51, {}), (15, 59, {}),
        (15, 67, {}), (15, 75, {}), (16, 20, {'weight': 0}),
        (16, 21, {}), (16, 22, {'weight': 0}), (16, 23, {}),
        (17, 20, {'weight': 0}), (17, 21, {}), (17, 22, {'weight': 0}),
        (17, 23, {}), (18, 20, {}), (18, 21, {}),
        (18, 22, {}), (18, 23, {}), (19, 20, {}),
        (19, 21, {}), (19, 22, {}), (19, 23, {}),
        (20, 1000, {'weight': 0}), (20, 1001, {}), (21, 1002, {}),
        (21, 1003, {}), (22, 1004, {}), (22, 1005, {'weight': 0}),
        (23, 1006, {}), (23, 1007, {}), (24, 28, {'weight': 0}),
        (24, 29, {}), (24, 30, {'weight': 0}), (24, 31, {'weight': 0}),
        (25, 28, {'weight': 0}), (25, 29, {}), (25, 30, {'weight': 0}),
        (25, 31, {}), (26, 28, {}), (26, 29, {}),
        (26, 30, {}), (26, 31, {}), (27, 28, {}),
        (27, 29, {}), (27, 30, {}), (27, 31, {}),
        (28, 1008, {'weight': 0}), (28, 1009, {'weight': 0}), (29, 1010, {}),
        (29, 1011, {}), (30, 1012, {'weight': 0}), (30, 1013, {'weight': 0}),
        (31, 1014, {'weight': 0}), (31, 1015, {}), (32, 36, {}),
        (32, 37, {}), (32, 38, {'weight': 0}), (32, 39, {}),
        (33, 36, {}), (33, 37, {'weight': 0}), (33, 38, {}),
        (33, 39, {'weight': 0}), (34, 36, {}), (34, 37, {}),
        (34, 38, {}), (34, 39, {}), (35, 36, {}),
        (35, 37, {}), (35, 38, {}), (35, 39, {}),
        (36, 1016, {}), (36, 1017, {}), (37, 1018, {}),
        (37, 1019, {'weight': 0}), (38, 1020, {}), (38, 1021, {'weight': 0}),
        (39, 1022, {'weight': 0}), (39, 1023, {}), (40, 44, {}),
        (40, 45, {'weight': 0}), (40, 46, {}), (40, 47, {}),
        (41, 44, {'weight': 0}), (41, 45, {'weight': 0}), (41, 46, {}),
        (41, 47, {}), (42, 44, {}), (42, 45, {}),
        (42, 46, {}), (42, 47, {}), (43, 44, {}),
        (43, 45, {}), (43, 46, {}), (43, 47, {}),
        (44, 1024, {'weight': 0}), (44, 1025, {}), (45, 1026, {'weight': 0}),
        (45, 1027, {'weight': 0}), (46, 1028, {}), (46, 1029, {}),
        (47, 1030, {}), (47, 1031, {}), (48, 52, {}),
        (48, 53, {}), (48, 54, {'weight': 0}), (48, 55, {}),
        (49, 52, {}), (49, 53, {}), (49, 54, {'weight': 0}),
        (49, 55, {'weight': 0}), (50, 52, {}), (50, 53, {}),
        (50, 54, {}), (50, 55, {}), (51, 52, {}),
        (51, 53, {}), (51, 54, {}), (51, 55, {}),
        (52, 1032, {}), (52, 1033, {}), (53, 1034, {}),
        (53, 1035, {}), (54, 1036, {'weight': 0}), (54, 1037, {'weight': 0}),
        (55, 1038, {'weight': 0}), (55, 1039, {'weight': 0}), (56, 60, {'weight': 0}),
        (56, 61, {}), (56, 62, {'weight': 0}), (56, 63, {'weight': 0}),
        (57, 60, {'weight': 0}), (57, 61, {'weight': 0}), (57, 62, {'weight': 0}),
        (57, 63, {'weight': 0}), (58, 60, {}), (58, 61, {}),
        (58, 62, {}), (58, 63, {}), (59, 60, {}),
        (59, 61, {}), (59, 62, {}), (59, 63, {}),
        (60, 1040, {'weight': 0}), (60, 1041, {'weight': 0}), (61, 1042, {'weight': 0}),
        (61, 1043, {}), (62, 1044, {'weight': 0}), (62, 1045, {'weight': 0}),
        (63, 1046, {'weight': 0}), (63, 1047, {'weight': 0}), (64, 68, {}),
        (64, 69, {'weight': 0}), (64, 70, {'weight': 0}), (64, 71, {'weight': 0}),
        (65, 68, {'weight': 0}), (65, 69, {}), (65, 70, {}),
        (65, 71, {'weight': 0}), (66, 68, {}), (66, 69, {}),
        (66, 70, {}), (66, 71, {}), (67, 68, {}),
        (67, 69, {}), (67, 70, {}), (67, 71, {}),
        (68, 1048, {'weight': 0}), (68, 1049, {}), (69, 1050, {}),
        (69, 1051, {'weight': 0}), (70, 1052, {'weight': 0}), (70, 1053, {'weight': 0}),
        (71, 1054, {'weight': 0}), (71, 1055, {'weight': 0}), (72, 76, {'weight': 0}),
        (72, 77, {'weight': 0}), (72, 78, {}), (72, 79, {'weight': 0}),
        (73, 76, {}), (73, 77, {'weight': 0}), (73, 78, {}),
        (73, 79, {}), (74, 76, {}), (74, 77, {}),
        (74, 78, {}), (74, 79, {}), (75, 76, {}),
        (75, 77, {}), (75, 78, {}), (75, 79, {}),
        (76, 1056, {}), (76, 1057, {'weight': 0}), (77, 1058, {'weight': 0}),
        (77, 1059, {'weight': 0}), (78, 1060, {}), (78, 1061, {}),
        (79, 1062, {}), (79, 1063, {'weight': 0}),
    ]
    # fmt: on
    terminal_nodes = [
        1048,
        1025,
        1027,
        1030,
        1000,
        1033,
        1035,
        1003,
        1006,
        1039,
        1042,
        1013,
        1022,
    ]

    G = nx.Graph()
    G.add_edges_from(edges)

    T = steiner_tree(G, terminal_nodes, method=method)
    assert nx.is_tree(T)
    assert set(terminal_nodes) == set(T) & set(terminal_nodes)
    assert T.number_of_edges() == T.number_of_nodes() - 1
