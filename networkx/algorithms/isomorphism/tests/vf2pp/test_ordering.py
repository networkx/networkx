import itertools

import utils

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import _GraphParameters
from networkx.algorithms.isomorphism.vf2pp_helpers.node_ordering import _matching_order


class TestNodeOrdering:
    def test_empty_graph(self):
        G1 = nx.Graph()
        G2 = nx.Graph()
        gparams = _GraphParameters(G1, G2, None, None, None, None, None)
        assert len(set(_matching_order(gparams))) == 0

    def test_single_node(self):
        G1 = nx.Graph()
        G2 = nx.Graph()
        G1.add_node(1)
        G2.add_node(1)

        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_different))), "label"
        )
        nx.set_node_attributes(
            G2,
            dict(zip(G2, itertools.cycle(utils.labels_different))),
            "label",
        )
        l1, l2 = nx.get_node_attributes(G1, "label"), nx.get_node_attributes(
            G2, "label"
        )

        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )
        m = _matching_order(gparams)
        assert m == [1]

    def test_matching_order(self):
        labels = [
            "blue",
            "blue",
            "red",
            "red",
            "red",
            "red",
            "green",
            "green",
            "green",
            "yellow",
            "purple",
            "purple",
            "blue",
            "blue",
        ]
        G1 = nx.Graph(
            [
                (0, 1),
                (0, 2),
                (1, 2),
                (2, 5),
                (2, 4),
                (1, 3),
                (1, 4),
                (3, 6),
                (4, 6),
                (6, 7),
                (7, 8),
                (9, 10),
                (9, 11),
                (11, 12),
                (11, 13),
                (12, 13),
                (10, 13),
            ]
        )
        G2 = G1.copy()
        nx.set_node_attributes(G1, dict(zip(G1, itertools.cycle(labels))), "label")
        nx.set_node_attributes(
            G2,
            dict(zip(G2, itertools.cycle(labels))),
            "label",
        )
        l1, l2 = nx.get_node_attributes(G1, "label"), nx.get_node_attributes(
            G2, "label"
        )
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )

        expected = [9, 11, 10, 13, 12, 1, 2, 4, 0, 3, 6, 5, 7, 8]
        assert _matching_order(gparams) == expected

    def test_matching_order_all_branches(self):
        G1 = nx.Graph(
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)]
        )
        G1.add_node(5)
        G2 = G1.copy()

        G1.nodes[0]["label"] = "black"
        G1.nodes[1]["label"] = "blue"
        G1.nodes[2]["label"] = "blue"
        G1.nodes[3]["label"] = "red"
        G1.nodes[4]["label"] = "red"
        G1.nodes[5]["label"] = "blue"

        G2.nodes[0]["label"] = "black"
        G2.nodes[1]["label"] = "blue"
        G2.nodes[2]["label"] = "blue"
        G2.nodes[3]["label"] = "red"
        G2.nodes[4]["label"] = "red"
        G2.nodes[5]["label"] = "blue"

        l1, l2 = nx.get_node_attributes(G1, "label"), nx.get_node_attributes(
            G2, "label"
        )
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )

        expected = [0, 4, 1, 3, 2, 5]
        assert _matching_order(gparams) == expected
