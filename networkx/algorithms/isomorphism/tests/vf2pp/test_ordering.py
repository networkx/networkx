import collections

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp_helpers.node_ordering import (
    _all_argmax,
    _matching_order,
)


def assign_labels(G1, G2):
    colors = [
        "white",
        "black",
        "green",
        "purple",
        "orange",
        "red",
        "blue",
        "pink",
        "yellow",
        "none",
    ]

    c = 0
    for node in G1.nodes():
        color = colors[c % len(colors)]
        G1.nodes[node]["label"] = color
        G2.nodes[node]["label"] = color
        c += 1

    return G1, G2


def get_labes(G1, G2):
    return nx.get_node_attributes(G1, "label"), nx.get_node_attributes(G2, "label")


class TestNodeOrdering:
    GraphParameters = collections.namedtuple(
        "GraphParameters",
        [
            "G1",
            "G2",
            "G1_labels",
            "G2_labels",
            "nodes_of_G1Labels",
            "nodes_of_G2Labels",
            "G2_nodes_of_degree",
        ],
    )

    def test_rare_nodes_custom_graph(self):
        G = nx.Graph()
        V = G.nodes()
        edges = [
            (1, 5),
            (1, 2),
            (1, 4),
            (2, 3),
            (2, 6),
            (3, 4),
            (3, 7),
            (4, 8),
            (5, 8),
            (5, 6),
            (6, 7),
            (7, 8),
        ]
        colors = ["blue", "blue", "red", "red", "red", "green", "green", "green"]

        G.add_edges_from(edges)
        for n in V:
            G.nodes[n]["label"] = colors.pop()

        l1, l2 = get_labes(G, G)
        rarity = {label: len(nodes) for label, nodes in nx.utils.groups(l2).items()}

        rarest_node = min(V, key=lambda x: rarity[l1[x]])
        rare_nodes = [n for n in V if rarity[l1[n]] == rarity[l1[rarest_node]]]
        # todo: how am i gonna know the order of nodes in G.nodes() so i can test the explicit result?
        assert set(_all_argmax(V, key_function=lambda x: -rarity[l1[x]])) == set(
            rare_nodes
        )

    def test_rare_nodes_exhaustive(self):
        for p in [0.04, 0.1, 0.25, 0.4, 0.65, 0.87, 1]:
            G1 = nx.gnp_random_graph(500, p, seed=12)
            G2 = nx.gnp_random_graph(500, p, seed=12)

            G1, G2 = assign_labels(G1, G2)
            l1, l2 = get_labes(G1, G2)
            rarity = {label: len(nodes) for label, nodes in nx.utils.groups(l2).items()}

            rarest_node = min(G1.nodes(), key=lambda x: rarity[l1[x]])
            rare_nodes = [
                n for n in G1.nodes() if rarity[l1[n]] == rarity[l1[rarest_node]]
            ]

            assert set(
                _all_argmax(G1.nodes(), key_function=lambda x: -rarity[l1[x]])
            ) == set(rare_nodes)

    def test_empty_graph(self):
        G1 = nx.Graph()
        G2 = nx.Graph()
        gparams = self.GraphParameters(G1, G2, None, None, None, None, None)
        assert len(set(_matching_order(gparams))) == 0

    def test_disconnected_graph(self):
        G1 = nx.Graph()
        G2 = nx.Graph()
        G1.add_node(1)
        G2.add_node(1)

        G1, G2 = assign_labels(G1, G2)
        l1, l2 = get_labes(G1, G2)

        gparams = self.GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )
        size = len(set(_matching_order(gparams)))
        assert size == 1

        for i in range(50, 300):
            G1.add_node(i)
            G2.add_node(i)
            G1, G2 = assign_labels(G1, G2)
            l1, l2 = get_labes(G1, G2)
            gparams = self.GraphParameters(
                G1,
                G2,
                l1,
                l2,
                nx.utils.groups(l1),
                nx.utils.groups(l2),
                nx.utils.groups({node: degree for node, degree in G2.degree()}),
            )
            assert len(set(_matching_order(gparams))) == size + 1
            size += 1

    def test_gnp_graph(self):
        num_nodes = [138, 155, 197, 201, 216, 244, 231, 265, 300, 333, 499]
        probabilities = [0.01, 0.067, 0.1, 0.32, 0.5, 0.78, 1]

        for Vi in num_nodes:
            for p in probabilities:
                G1 = nx.gnp_random_graph(Vi, p, seed=12)
                G2 = nx.gnp_random_graph(Vi, p, seed=12)

                G1, G2 = assign_labels(G1, G2)
                l1, l2 = get_labes(G1, G2)
                gparams = self.GraphParameters(
                    G1,
                    G2,
                    l1,
                    l2,
                    nx.utils.groups(l1),
                    nx.utils.groups(l2),
                    nx.utils.groups({node: degree for node, degree in G2.degree()}),
                )
                assert len(set(_matching_order(gparams))) == Vi

    def test_barbel_graph(self):
        G1 = nx.barbell_graph(100, 250)
        G2 = nx.barbell_graph(100, 250)

        G1, G2 = assign_labels(G1, G2)
        l1, l2 = get_labes(G1, G2)
        gparams = self.GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )
        assert len(set(_matching_order(gparams))) == 100 + 250 + 100
