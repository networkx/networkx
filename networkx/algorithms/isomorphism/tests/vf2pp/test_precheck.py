import itertools

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import vf2pp_is_isomorphic


class TestPreCheck:
    def test_first_graph_empty(self):
        G1 = nx.Graph()
        G2 = nx.Graph([(0, 1), (1, 2)])
        assert not vf2pp_is_isomorphic(G1, G2)

    def test_second_graph_empty(self):
        G1 = nx.Graph([(0, 1), (1, 2)])
        G2 = nx.Graph()
        assert not vf2pp_is_isomorphic(G1, G2)

    def test_different_order1(self):
        G1 = nx.path_graph(5)
        G2 = nx.path_graph(6)
        assert not vf2pp_is_isomorphic(G1, G2)

    def test_different_order2(self):
        G1 = nx.barbell_graph(100, 20)
        G2 = nx.barbell_graph(101, 20)
        assert not vf2pp_is_isomorphic(G1, G2)

    def test_different_order3(self):
        G1 = nx.complete_graph(7)
        G2 = nx.complete_graph(8)
        assert not vf2pp_is_isomorphic(G1, G2)

    def test_different_degree_sequences1(self):
        G1 = nx.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (0, 4)])
        G2 = nx.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (0, 4), (2, 5)])
        assert not vf2pp_is_isomorphic(G1, G2)

        G2.remove_node(3)
        nx.set_node_attributes(G1, dict(zip(G1, itertools.cycle(["a"]))), "label")
        nx.set_node_attributes(G2, dict(zip(G2, itertools.cycle("a"))), "label")

        assert vf2pp_is_isomorphic(G1, G2)

    def test_different_degree_sequences2(self):
        G1 = nx.Graph(
            [
                (0, 1),
                (1, 2),
                (0, 2),
                (2, 3),
                (3, 4),
                (4, 5),
                (5, 6),
                (6, 3),
                (4, 7),
                (7, 8),
                (8, 3),
            ]
        )
        G2 = G1.copy()
        G2.add_edge(8, 0)
        assert not vf2pp_is_isomorphic(G1, G2)

        G1.add_edge(6, 1)
        nx.set_node_attributes(G1, dict(zip(G1, itertools.cycle(["a"]))), "label")
        nx.set_node_attributes(G2, dict(zip(G2, itertools.cycle("a"))), "label")

        assert vf2pp_is_isomorphic(G1, G2)

    def test_different_degree_sequences3(self):
        G1 = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)])
        G2 = nx.Graph(
            [(0, 1), (0, 6), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)]
        )
        assert not vf2pp_is_isomorphic(G1, G2)

        G1.add_edge(3, 5)
        nx.set_node_attributes(G1, dict(zip(G1, itertools.cycle(["a"]))), "label")
        nx.set_node_attributes(G2, dict(zip(G2, itertools.cycle("a"))), "label")

        assert vf2pp_is_isomorphic(G1, G2)

    def test_label_distribution(self):
        G1 = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)])
        G2 = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)])

        colors1 = ["blue", "blue", "blue", "yellow", "black", "purple", "purple"]
        colors2 = ["blue", "blue", "yellow", "yellow", "black", "purple", "purple"]

        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(colors1[::-1]))), "label"
        )
        nx.set_node_attributes(
            G2, dict(zip(G2, itertools.cycle(colors2[::-1]))), "label"
        )

        assert not vf2pp_is_isomorphic(G1, G2, node_label="label")
        G2.nodes[3]["label"] = "blue"
        assert vf2pp_is_isomorphic(G1, G2, node_label="label")
