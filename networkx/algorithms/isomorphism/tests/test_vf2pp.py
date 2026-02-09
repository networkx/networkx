import itertools as it

import pytest

import networkx as nx
from networkx import vf2pp_all_isomorphisms, vf2pp_is_isomorphic, vf2pp_isomorphism

labels_same = ["blue"]

labels_many = [
    "white",
    "red",
    "blue",
    "green",
    "orange",
    "black",
    "purple",
    "yellow",
    "brown",
    "cyan",
    "solarized",
    "pink",
    "none",
]

graph_classes = [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]


class TestPreCheck:
    def test_first_graph_empty(self):
        SG = nx.Graph()
        FG = nx.Graph([(0, 1), (1, 2)])
        assert not vf2pp_is_isomorphic(FG, SG)

    def test_second_graph_empty(self):
        SG = nx.Graph([(0, 1), (1, 2)])
        FG = nx.Graph()
        assert not vf2pp_is_isomorphic(FG, SG)

    def test_different_order1(self):
        SG = nx.path_graph(5)
        FG = nx.path_graph(6)
        assert not vf2pp_is_isomorphic(FG, SG)

    def test_different_order2(self):
        SG = nx.barbell_graph(100, 20)
        FG = nx.barbell_graph(101, 20)
        assert not vf2pp_is_isomorphic(FG, SG)

    def test_different_order3(self):
        SG = nx.complete_graph(7)
        FG = nx.complete_graph(8)
        assert not vf2pp_is_isomorphic(FG, SG)

    def test_different_degree_sequences1(self):
        SG = nx.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (0, 4)])
        FG = nx.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (0, 4), (2, 5)])
        assert not vf2pp_is_isomorphic(FG, SG)

        FG.remove_node(3)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(["a"]))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle("a"))), "label")

        assert vf2pp_is_isomorphic(FG, SG)

    def test_different_degree_sequences2(self):
        SG = nx.Graph(
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
        FG = SG.copy()
        FG.add_edge(8, 0)
        assert not vf2pp_is_isomorphic(FG, SG)

        SG.add_edge(6, 1)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(["a"]))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle("a"))), "label")

        assert vf2pp_is_isomorphic(FG, SG)

    def test_different_degree_sequences3(self):
        SG = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)])
        FG = nx.Graph(
            [(0, 1), (0, 6), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)]
        )
        assert not vf2pp_is_isomorphic(FG, SG)

        SG.add_edge(3, 5)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(["a"]))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle("a"))), "label")

        assert vf2pp_is_isomorphic(FG, SG)

    def test_label_distribution(self):
        SG = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)])
        FG = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)])

        colors1 = ["blue", "blue", "blue", "yellow", "black", "purple", "purple"]
        colors2 = ["blue", "blue", "yellow", "yellow", "black", "purple", "purple"]

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(colors1[::-1]))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(colors2[::-1]))), "label")

        assert not vf2pp_is_isomorphic(FG, SG, node_label="label")
        FG.nodes[3]["label"] = "blue"
        assert vf2pp_is_isomorphic(FG, SG, node_label="label")


class TestAllGraphTypesEdgeCases:
    @pytest.mark.parametrize("graph_type", graph_classes)
    def test_both_graphs_empty(self, graph_type):
        G = graph_type()
        H = graph_type()
        assert vf2pp_isomorphism(G, H) is None

        G.add_node(0)

        assert vf2pp_isomorphism(G, H) is None
        assert vf2pp_isomorphism(H, G) is None

        H.add_node(0)
        assert vf2pp_isomorphism(G, H) == {0: 0}

    @pytest.mark.parametrize("graph_type", graph_classes)
    def test_first_graph_empty(self, graph_type):
        G = graph_type()
        H = graph_type([(0, 1)])
        assert vf2pp_isomorphism(G, H) is None

    @pytest.mark.parametrize("graph_type", graph_classes)
    def test_second_graph_empty(self, graph_type):
        G = graph_type([(0, 1)])
        H = graph_type()
        assert vf2pp_isomorphism(G, H) is None


class TestGraphISOVF2pp:
    def test_custom_grapSH_same_labels(self):
        SG = nx.Graph()

        mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
        edges1 = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 6), (3, 4), (5, 1), (5, 2)]
        # 5-1   5-1   D-A
        # |/|\  |/|\  |/|\    6-X; 2-C; 5-D; 1-A; 3-B; 7-E; 4-Z
        # 2-3-4 2-3-4 C-B-Z
        # |     | |/  | |/
        # 6     6 7   X E

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_many))), "label")
        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")
        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

        # Add edge making SG symmetrical
        SG.add_edge(3, 7)
        SG.nodes[7]["label"] = "blue"
        assert vf2pp_isomorphism(FG, SG, node_label="label") is None

        all_self_mappings = list(vf2pp_all_isomorphisms(SG, SG))
        assert len(all_self_mappings) == 2
        # check that one of the mappings is not the identity for node 2
        assert sum(1 for m in all_self_mappings if m[2] == 2) == 1

        # Make FG isomorphic to SG
        FG.add_edges_from([(mapped[3], "X"), (mapped[6], mapped[5])])
        SG.add_edge(4, 7)
        FG.nodes["X"]["label"] = "blue"
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Re-structure maintaining isomorphism
        SG.remove_edges_from([(1, 4), (1, 3)])
        FG.remove_edges_from([(mapped[1], mapped[5]), (mapped[1], mapped[2])])
        assert vf2pp_isomorphism(FG, SG, node_label="label")

    def test_custom_grapFH_same_labels(self):
        SG = nx.Graph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]
        # 6-5
        #  /|\    6-F; 2-C; 3-D; 1-A; 7-B; 4-E; 5-G
        # 1-2-4
        #  /|/
        # 7 3

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")

        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Obtain two isomorphic subgraphs from the graph
        FG.remove_edge(mapped[1], mapped[2])
        FG.add_edge(mapped[1], mapped[4])
        SH = nx.Graph(SG.subgraph([2, 3, 4, 7]))
        FH = nx.Graph(FG.subgraph([mapped[1], mapped[4], mapped[5], mapped[6]]))
        assert vf2pp_isomorphism(FH, SH, node_label="label")

        # Add edges maintaining isomorphism
        SH.add_edges_from([(3, 7), (4, 7)])
        FH.add_edges_from([(mapped[1], mapped[6]), (mapped[4], mapped[6])])
        assert vf2pp_isomorphism(FH, SH, node_label="label")

    def test_custom_grapFH_different_labels(self):
        SG = nx.Graph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )

        # Adding new nodes
        SG.add_node(0)
        FG.add_node("Z")
        SG.nodes[0]["label"] = SG.nodes[1]["label"]
        FG.nodes["Z"]["label"] = SG.nodes[1]["label"]
        mapped.update({0: "Z"})

        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

        # Change the color of one of the nodes
        FG.nodes["Z"]["label"] = SG.nodes[2]["label"]
        assert vf2pp_isomorphism(FG, SG, node_label="label") is None

        # Add an extra edge
        SG.nodes[0]["label"] = "blue"
        FG.nodes["Z"]["label"] = "blue"
        SG.add_edge(0, 1)

        assert vf2pp_isomorphism(FG, SG, node_label="label") is None

        # Add extra edge to both
        FG.add_edge("Z", "A")
        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

    def test_custom_graph3_same_labels(self):
        SG = nx.Graph()

        mapped = {1: 9, 2: 8, 3: 7, 4: 6, 5: 3, 8: 5, 9: 4, 7: 1, 6: 2}
        #        3---4
        #       /|  /|\
        #      / | 9 | 7
        #     1  | | | |
        #      \ | 8 | 6
        #       \|  \|/
        #        2---5
        edges1 = [
            (1, 2),
            (1, 3),
            (2, 3),
            (3, 4),
            (4, 5),
            (4, 7),
            (4, 9),
            (5, 8),
            (8, 9),
            (5, 6),
            (6, 7),
            (5, 2),
        ]
        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Connect nodes maintaining symmetry
        SG.add_edges_from([(6, 9), (7, 8)])
        FG.add_edges_from([(mapped[6], mapped[8]), (mapped[7], mapped[9])])
        assert vf2pp_isomorphism(FG, SG, node_label="label") is None

        # Make isomorphic
        SG.add_edges_from([(6, 8), (7, 9)])
        FG.add_edges_from([(mapped[6], mapped[9]), (mapped[7], mapped[8])])
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Connect more nodes
        SG.add_edges_from([(2, 7), (3, 6)])
        FG.add_edges_from([(mapped[2], mapped[7]), (mapped[3], mapped[6])])
        SG.add_node(10)
        FG.add_node("Z")
        SG.nodes[10]["label"] = "blue"
        FG.nodes["Z"]["label"] = "blue"

        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Connect the newly added node, to opposite sides of the graph
        SG.add_edges_from([(10, 1), (10, 5), (10, 8)])
        FG.add_edges_from([("Z", mapped[1]), ("Z", mapped[4]), ("Z", mapped[9])])
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Get two subgraphs that are not isomorphic but are easy to make
        SH = nx.Graph(SG.subgraph([2, 3, 4, 5, 6, 7, 10]))
        FH = nx.Graph(
            FG.subgraph(
                [mapped[4], mapped[5], mapped[6], mapped[7], mapped[8], mapped[9], "Z"]
            )
        )
        assert vf2pp_isomorphism(FH, SH, node_label="label") is None

        # Restructure both to make them isomorphic
        SH.add_edges_from([(10, 2), (10, 6), (3, 6), (2, 7), (2, 6), (3, 7)])
        FH.add_edges_from(
            [("Z", mapped[7]), (mapped[6], mapped[9]), (mapped[7], mapped[8])]
        )
        assert vf2pp_isomorphism(FH, SH, node_label="label")

        # Add edges with opposite direction in each Graph
        SH.add_edge(3, 5)
        FH.add_edge(mapped[5], mapped[7])
        assert vf2pp_isomorphism(FH, SH, node_label="label") is None

    def test_custom_graph3_different_labels(self):
        SG = nx.Graph()

        mapped = {1: 9, 2: 8, 3: 7, 4: 6, 5: 3, 8: 5, 9: 4, 7: 1, 6: 2}
        edges1 = [
            (1, 2),
            (1, 3),
            (2, 3),
            (3, 4),
            (4, 5),
            (4, 7),
            (4, 9),
            (5, 8),
            (8, 9),
            (5, 6),
            (6, 7),
            (5, 2),
        ]
        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )
        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

        # Add extra edge to SG
        SG.add_edge(1, 7)
        assert vf2pp_isomorphism(FG, SG, node_label="label") is None

        # Compensate in FG
        FG.add_edge(9, 1)
        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

        # Add extra node
        SG.add_node("A")
        FG.add_node("K")
        SG.nodes["A"]["label"] = "green"
        FG.nodes["K"]["label"] = "green"
        mapped.update({"A": "K"})

        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

        # Connect A to one side of SG and K to the opposite
        SG.add_edge("A", 6)
        FG.add_edge("K", 5)
        assert vf2pp_isomorphism(FG, SG, node_label="label") is None

        # Make the graphs symmetrical
        SG.add_edge(1, 5)
        SG.add_edge(2, 9)
        FG.add_edge(9, 3)
        FG.add_edge(8, 4)
        assert vf2pp_isomorphism(FG, SG, node_label="label") is None

        # Assign same colors so the two opposite sides are identical
        for node in SG.nodes():
            color = "red"
            SG.nodes[node]["label"] = color
            FG.nodes[mapped[node]]["label"] = color

        assert vf2pp_isomorphism(FG, SG, node_label="label")

    def test_custom_graph4_different_labels(self):
        #  1-2-3-4    10-11-12
        #      |\|\        \|
        #    7-8 6 5        13
        #       \ /
        #        9
        SG = nx.Graph()
        edges1 = [
            (1, 2),
            (2, 3),
            (3, 8),
            (3, 4),
            (4, 5),
            (4, 6),
            (3, 6),
            (8, 7),
            (8, 9),
            (5, 9),
            (10, 11),
            (11, 12),
            (12, 13),
            (11, 13),
        ]

        mapped = {
            1: "n",
            2: "m",
            3: "l",
            4: "j",
            5: "k",
            6: "i",
            7: "g",
            8: "h",
            9: "f",
            10: "b",
            11: "a",
            12: "d",
            13: "e",
        }

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )
        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

    def test_custom_graph4_same_labels(self):
        SG = nx.Graph()
        edges1 = [
            (1, 2),
            (2, 3),
            (3, 8),
            (3, 4),
            (4, 5),
            (4, 6),
            (3, 6),
            (8, 7),
            (8, 9),
            (5, 9),
            (10, 11),
            (11, 12),
            (12, 13),
            (11, 13),
        ]

        mapped = {
            1: "n",
            2: "m",
            3: "l",
            4: "j",
            5: "k",
            6: "i",
            7: "g",
            8: "h",
            9: "f",
            10: "b",
            11: "a",
            12: "d",
            13: "e",
        }

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        all_self_mappings = list(vf2pp_all_isomorphisms(SG, SG))
        assert len(all_self_mappings) == 2
        # check that one of the mappings is not the identity for node 2
        assert sum(1 for m in all_self_mappings if m[12] == 12) == 1

        # Add nodes of different label
        SG.add_node(0)
        FG.add_node("z")
        SG.nodes[0]["label"] = "green"
        FG.nodes["z"]["label"] = "blue"

        assert vf2pp_isomorphism(FG, SG, node_label="label") is None

        # Make the labels identical
        FG.nodes["z"]["label"] = "green"
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Change the structure of the graphs, keeping them isomorphic
        SG.add_edge(2, 5)
        FG.remove_edge("i", "l")
        FG.add_edge("g", "l")
        FG.add_edge("m", "f")
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Change the structure of the disconnected sub-graph, keeping it isomorphic
        SG.remove_node(13)
        FG.remove_node("d")
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Connect the newly added node to the disconnected graph, which now is just a path of size 3
        SG.add_edge(0, 10)
        FG.add_edge("e", "z")
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Connect the two disconnected sub-graphs, forming a single graph
        SG.add_edge(11, 3)
        SG.add_edge(0, 8)
        FG.add_edge("a", "l")
        FG.add_edge("z", "j")
        assert vf2pp_isomorphism(FG, SG, node_label="label")

    def test_custom_graph5_same_labels(self):
        # Lots of symmetries
        #      1
        #     /|\
        #    / 2 \
        #   | / \ |
        #   5-6 3-4
        #   | \ / |
        #    \ 7 /
        #     \|/
        #      8
        SG = nx.Graph()
        edges1 = [
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
        mapped = {1: "a", 2: "h", 3: "d", 4: "i", 5: "g", 6: "b", 7: "j", 8: "c"}

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        all_self_mappings = list(vf2pp_all_isomorphisms(SG, SG))
        assert len(all_self_mappings) == 48
        # check that one of the mappings is not the identity for node 2
        assert all(sum(1 for m in all_self_mappings if m[u] == u) == 6 for u in SG)

        # Add different edges in each graph, maintaining symmetry
        SG.add_edges_from([(3, 6), (2, 7), (2, 5), (1, 3), (4, 7), (6, 8)])
        FG.add_edges_from(
            [
                (mapped[6], mapped[3]),
                (mapped[2], mapped[7]),
                (mapped[1], mapped[6]),
                (mapped[5], mapped[7]),
                (mapped[3], mapped[8]),
                (mapped[2], mapped[4]),
            ]
        )
        assert vf2pp_isomorphism(FG, SG, node_label="label")

        # Obtain two different but isomorphic subgraphs from SG and FG
        SH = nx.Graph(SG.subgraph([1, 5, 8, 6, 7, 3]))
        FH = nx.Graph(
            FG.subgraph(
                [mapped[1], mapped[4], mapped[8], mapped[7], mapped[3], mapped[5]]
            )
        )
        assert vf2pp_isomorphism(FH, SH, node_label="label")

        # Delete corresponding node from the two graphs
        SH.remove_node(8)
        FH.remove_node(mapped[7])
        assert vf2pp_isomorphism(FH, SH, node_label="label")

        # Re-orient, maintaining isomorphism
        SH.add_edge(1, 6)
        SH.remove_edge(3, 6)
        assert vf2pp_isomorphism(FH, SH, node_label="label")

    def test_custom_graph5_different_labels(self):
        SG = nx.Graph()
        edges1 = [
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
        mapped = {1: "a", 2: "h", 3: "d", 4: "i", 5: "g", 6: "b", 7: "j", 8: "c"}

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        colors = ["red", "blue", "grey", "none", "brown", "solarized", "yellow", "pink"]
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )
        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

        # Assign different colors to matching nodes
        c = 0
        for node in SG.nodes():
            color1 = colors[c]
            color2 = colors[(c + 3) % len(colors)]
            SG.nodes[node]["label"] = color1
            FG.nodes[mapped[node]]["label"] = color2
            c += 1

        assert vf2pp_isomorphism(FG, SG, node_label="label") is None

        # Get symmetrical sub-graphs of SG,FG and compare them
        SH = SG.subgraph([1, 5])
        FH = FG.subgraph(["i", "c"])
        c = 0
        for node1, node2 in zip(SH.nodes(), FH.nodes()):
            SH.nodes[node1]["label"] = "red"
            FH.nodes[node2]["label"] = "red"
            c += 1

        assert vf2pp_isomorphism(FH, SH, node_label="label")

    def test_disconnected_graph_all_same_labels(self):
        SG = nx.Graph()
        SG.add_nodes_from(list(range(10)))

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        FG = nx.relabel_nodes(SG, mapped)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")
        assert vf2pp_isomorphism(FG, SG, node_label="label")

    def test_disconnected_graph_all_different_labels(self):
        SG = nx.Graph()
        SG.add_nodes_from(list(range(10)))

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )
        assert vf2pp_isomorphism(FG, SG, node_label="label") == mapped

    def test_disconnected_graph_some_same_labels(self):
        SG = nx.Graph()
        SG.add_nodes_from(list(range(10)))

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        FG = nx.relabel_nodes(SG, mapped)

        colors = [
            "white",
            "white",
            "white",
            "purple",
            "purple",
            "red",
            "red",
            "pink",
            "pink",
            "pink",
        ]

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(colors))), "label")
        nx.set_node_attributes(
            FG, dict(zip([mapped[n] for n in SG], it.cycle(colors))), "label"
        )

        assert vf2pp_isomorphism(FG, SG, node_label="label")


class TestMultiGraphISOVF2pp:
    def test_custom_multigrapSH_same_labels(self):
        SG = nx.MultiGraph()

        mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
        edges1 = [
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 4),
            (1, 4),
            (2, 3),
            (2, 6),
            (2, 6),
            (3, 4),
            (3, 4),
            (5, 1),
            (5, 1),
            (5, 2),
            (5, 2),
        ]

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Transfer the 2-clique to the right side of SG
        SG.remove_edges_from([(2, 6), (2, 6)])
        SG.add_edges_from([(3, 6), (3, 6)])
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Delete an edges, making them symmetrical, so the position of the 2-clique doesn't matter
        FG.remove_edge(mapped[1], mapped[4])
        SG.remove_edge(1, 4)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Add self-loops
        SG.add_edges_from([(5, 5), (5, 5), (1, 1)])
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Compensate in FG
        FG.add_edges_from(
            [(mapped[1], mapped[1]), (mapped[4], mapped[4]), (mapped[4], mapped[4])]
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

    def test_custom_multigrapSH_different_labels(self):
        SG = nx.MultiGraph()

        mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
        edges1 = [
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 4),
            (1, 4),
            (2, 3),
            (2, 6),
            (2, 6),
            (3, 4),
            (3, 4),
            (5, 1),
            (5, 1),
            (5, 2),
            (5, 2),
        ]

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m
        assert m == mapped

        # Re-structure SG, maintaining the degree sequence
        SG.remove_edge(1, 4)
        SG.add_edge(1, 5)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Restructure FG, making it isomorphic to SG
        FG.remove_edge("A", "D")
        FG.add_edge("A", "Z")
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m
        assert m == mapped

        # Add edge from node to itself
        SG.add_edges_from([(6, 6), (6, 6), (6, 6)])
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Same for FG
        FG.add_edges_from([("E", "E"), ("E", "E"), ("E", "E")])
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m
        assert m == mapped

    def test_custom_multigrapFH_same_labels(self):
        SG = nx.MultiGraph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [
            (1, 2),
            (1, 2),
            (1, 5),
            (1, 5),
            (1, 5),
            (5, 6),
            (2, 3),
            (2, 3),
            (2, 4),
            (3, 4),
            (3, 4),
            (4, 5),
            (4, 5),
            (4, 5),
            (2, 7),
            (2, 7),
            (2, 7),
        ]

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Obtain two non-isomorphic subgraphs from the graph
        FG.add_edge(mapped[1], mapped[4])
        SH = nx.MultiGraph(SG.subgraph([2, 3, 4, 7]))
        FH = nx.MultiGraph(FG.subgraph([mapped[1], mapped[4], mapped[5], mapped[6]]))

        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert not m

        # Make them isomorphic
        SH.remove_edge(3, 4)
        SH.add_edges_from([(2, 3), (2, 4), (2, 4)])
        FH.add_edges_from([(mapped[5], mapped[6]), (mapped[5], mapped[6])])
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Remove triangle edge
        SH.remove_edges_from([(2, 3), (2, 3), (2, 3)])
        FH.remove_edges_from([(mapped[5], mapped[4])] * 3)
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Change the edge orientation such that SH is rotated FH
        SH.remove_edges_from([(2, 7), (2, 7)])
        SH.add_edges_from([(3, 4), (3, 4)])
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Add extra edges maintaining degree sequence, but in a non-symmetrical manner
        FH.add_edge(mapped[5], mapped[1])
        SH.add_edge(3, 4)
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert not m

    def test_custom_multigrapFH_different_labels(self):
        SG = nx.MultiGraph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [
            (1, 2),
            (1, 2),
            (1, 5),
            (1, 5),
            (1, 5),
            (5, 6),
            (2, 3),
            (2, 3),
            (2, 4),
            (3, 4),
            (3, 4),
            (4, 5),
            (4, 5),
            (4, 5),
            (2, 7),
            (2, 7),
            (2, 7),
        ]

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m
        assert m == mapped

        # Re-structure SG
        SG.remove_edge(2, 7)
        SG.add_edge(5, 6)

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Same for FG
        FG.remove_edge("B", "C")
        FG.add_edge("G", "F")

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m
        assert m == mapped

        # Delete node from SG and FG, keeping them isomorphic
        SG.remove_node(3)
        FG.remove_node("D")
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Change SG edges
        SG.remove_edge(1, 2)
        SG.remove_edge(2, 7)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Make FG identical to SG, but with different edge orientation and different labels
        FG.add_edges_from([("A", "C"), ("C", "E"), ("C", "E")])
        FG.remove_edges_from(
            [("A", "G"), ("A", "G"), ("F", "G"), ("E", "G"), ("E", "G")]
        )

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Make all labels the same, so SG and FG are also isomorphic
        for n1, n2 in zip(SG.nodes(), FG.nodes()):
            SG.nodes[n1]["label"] = "blue"
            FG.nodes[n2]["label"] = "blue"

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

    def test_custom_multigraph3_same_labels(self):
        SG = nx.MultiGraph()

        mapped = {1: 9, 2: 8, 3: 7, 4: 6, 5: 3, 8: 5, 9: 4, 7: 1, 6: 2}
        edges1 = [
            (1, 2),
            (1, 3),
            (1, 3),
            (2, 3),
            (2, 3),
            (3, 4),
            (4, 5),
            (4, 7),
            (4, 9),
            (4, 9),
            (4, 9),
            (5, 8),
            (5, 8),
            (8, 9),
            (8, 9),
            (5, 6),
            (6, 7),
            (6, 7),
            (6, 7),
            (5, 2),
        ]
        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Connect nodes maintaining symmetry
        SG.add_edges_from([(6, 9), (7, 8), (5, 8), (4, 9), (4, 9)])
        FG.add_edges_from(
            [
                (mapped[6], mapped[8]),
                (mapped[7], mapped[9]),
                (mapped[5], mapped[8]),
                (mapped[4], mapped[9]),
                (mapped[4], mapped[9]),
            ]
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Make isomorphic
        SG.add_edges_from([(6, 8), (6, 8), (7, 9), (7, 9), (7, 9)])
        FG.add_edges_from(
            [
                (mapped[6], mapped[8]),
                (mapped[6], mapped[9]),
                (mapped[7], mapped[8]),
                (mapped[7], mapped[9]),
                (mapped[7], mapped[9]),
            ]
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Connect more nodes
        SG.add_edges_from([(2, 7), (2, 7), (3, 6), (3, 6)])
        FG.add_edges_from(
            [
                (mapped[2], mapped[7]),
                (mapped[2], mapped[7]),
                (mapped[3], mapped[6]),
                (mapped[3], mapped[6]),
            ]
        )
        SG.add_node(10)
        FG.add_node("Z")
        SG.nodes[10]["label"] = "blue"
        FG.nodes["Z"]["label"] = "blue"

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Connect the newly added node, to opposite sides of the graph
        SG.add_edges_from([(10, 1), (10, 5), (10, 8), (10, 10), (10, 10)])
        FG.add_edges_from(
            [
                ("Z", mapped[1]),
                ("Z", mapped[4]),
                ("Z", mapped[9]),
                ("Z", "Z"),
                ("Z", "Z"),
            ]
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # We connected the new node to opposite sides, so SG must be symmetrical
        # to FG. Re-structure them to be so
        SG.remove_edges_from([(1, 3), (4, 9), (4, 9), (7, 9)])
        FG.remove_edges_from(
            [
                (mapped[1], mapped[3]),
                (mapped[4], mapped[9]),
                (mapped[4], mapped[9]),
                (mapped[7], mapped[9]),
            ]
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Get two subgraphs that are not isomorphic but are easy to make
        SH = nx.Graph(SG.subgraph([2, 3, 4, 5, 6, 7, 10]))
        FH = nx.Graph(
            FG.subgraph(
                [mapped[4], mapped[5], mapped[6], mapped[7], mapped[8], mapped[9], "Z"]
            )
        )

        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert not m

        # Restructure both to make them isomorphic
        SH.add_edges_from([(10, 2), (10, 6), (3, 6), (2, 7), (2, 6), (3, 7)])
        FH.add_edges_from(
            [("Z", mapped[7]), (mapped[6], mapped[9]), (mapped[7], mapped[8])]
        )
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Remove one self-loop in FH
        FH.remove_edge("Z", "Z")
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert not m

        # Compensate in SH
        SH.remove_edge(10, 10)
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

    def test_custom_multigraph3_different_labels(self):
        SG = nx.MultiGraph()

        mapped = {1: 9, 2: 8, 3: 7, 4: 6, 5: 3, 8: 5, 9: 4, 7: 1, 6: 2}
        edges1 = [
            (1, 2),
            (1, 3),
            (1, 3),
            (2, 3),
            (2, 3),
            (3, 4),
            (4, 5),
            (4, 7),
            (4, 9),
            (4, 9),
            (4, 9),
            (5, 8),
            (5, 8),
            (8, 9),
            (8, 9),
            (5, 6),
            (6, 7),
            (6, 7),
            (6, 7),
            (5, 2),
        ]

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m
        assert m == mapped

        # Delete edge maintaining isomorphism
        SG.remove_edge(4, 9)
        FG.remove_edge(4, 6)

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m
        assert m == mapped

        # Change edge orientation such that SG mirrors FG
        SG.add_edges_from([(4, 9), (1, 2), (1, 2)])
        SG.remove_edges_from([(1, 3), (1, 3)])
        FG.add_edges_from([(3, 5), (7, 9)])
        FG.remove_edge(8, 9)

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Make all labels the same, so SG and FG are also isomorphic
        for n1, n2 in zip(SG.nodes(), FG.nodes()):
            SG.nodes[n1]["label"] = "blue"
            FG.nodes[n2]["label"] = "blue"

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        SG.add_node(10)
        FG.add_node("Z")
        SG.nodes[10]["label"] = "green"
        FG.nodes["Z"]["label"] = "green"

        # Add different number of edges between the new nodes and themselves
        SG.add_edges_from([(10, 10), (10, 10)])
        FG.add_edges_from([("Z", "Z")])

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Make the number of self-edges equal
        SG.remove_edge(10, 10)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Connect the new node to the graph
        SG.add_edges_from([(10, 3), (10, 4)])
        FG.add_edges_from([("Z", 8), ("Z", 3)])

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Remove central node
        SG.remove_node(4)
        FG.remove_node(3)
        SG.add_edges_from([(5, 6), (5, 6), (5, 7)])
        FG.add_edges_from([(1, 6), (1, 6), (6, 2)])

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

    def test_custom_multigraph4_same_labels(self):
        SG = nx.MultiGraph()
        edges1 = [
            (1, 2),
            (1, 2),
            (2, 2),
            (2, 3),
            (3, 8),
            (3, 8),
            (3, 4),
            (4, 5),
            (4, 5),
            (4, 5),
            (4, 6),
            (3, 6),
            (3, 6),
            (6, 6),
            (8, 7),
            (7, 7),
            (8, 9),
            (9, 9),
            (8, 9),
            (8, 9),
            (5, 9),
            (10, 11),
            (11, 12),
            (12, 13),
            (11, 13),
            (10, 10),
            (10, 11),
            (11, 13),
        ]

        mapped = {
            1: "n",
            2: "m",
            3: "l",
            4: "j",
            5: "k",
            6: "i",
            7: "g",
            8: "h",
            9: "f",
            10: "b",
            11: "a",
            12: "d",
            13: "e",
        }

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Add extra but corresponding edges to both graphs
        SG.add_edges_from([(2, 2), (2, 3), (2, 8), (3, 4)])
        FG.add_edges_from([("m", "m"), ("m", "l"), ("m", "h"), ("l", "j")])
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Obtain subgraphs
        SH = nx.MultiGraph(SG.subgraph([2, 3, 4, 6, 10, 11, 12, 13]))
        FH = nx.MultiGraph(
            FG.subgraph(
                [
                    mapped[2],
                    mapped[3],
                    mapped[8],
                    mapped[9],
                    mapped[10],
                    mapped[11],
                    mapped[12],
                    mapped[13],
                ]
            )
        )

        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert not m

        # Make them isomorphic
        FH.remove_edges_from(
            [(mapped[3], mapped[2]), (mapped[9], mapped[8]), (mapped[2], mapped[2])]
        )
        FH.add_edges_from([(mapped[9], mapped[9]), (mapped[2], mapped[8])])
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Re-structure the disconnected sub-graph
        SH.remove_node(12)
        FH.remove_node(mapped[12])
        SH.add_edge(13, 13)
        FH.add_edge(mapped[13], mapped[13])

        # Connect the two disconnected components, forming a single graph
        SH.add_edges_from([(3, 13), (6, 11)])
        FH.add_edges_from([(mapped[8], mapped[10]), (mapped[2], mapped[11])])
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Change orientation of self-loops in one graph, maintaining the degree sequence
        SH.remove_edges_from([(2, 2), (3, 6)])
        SH.add_edges_from([(6, 6), (2, 3)])
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert not m

    def test_custom_multigraph4_different_labels(self):
        SG = nx.MultiGraph()
        edges1 = [
            (1, 2),
            (1, 2),
            (2, 2),
            (2, 3),
            (3, 8),
            (3, 8),
            (3, 4),
            (4, 5),
            (4, 5),
            (4, 5),
            (4, 6),
            (3, 6),
            (3, 6),
            (6, 6),
            (8, 7),
            (7, 7),
            (8, 9),
            (9, 9),
            (8, 9),
            (8, 9),
            (5, 9),
            (10, 11),
            (11, 12),
            (12, 13),
            (11, 13),
        ]

        mapped = {
            1: "n",
            2: "m",
            3: "l",
            4: "j",
            5: "k",
            6: "i",
            7: "g",
            8: "h",
            9: "f",
            10: "b",
            11: "a",
            12: "d",
            13: "e",
        }

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m == mapped

        # Add extra but corresponding edges to both graphs
        SG.add_edges_from([(2, 2), (2, 3), (2, 8), (3, 4)])
        FG.add_edges_from([("m", "m"), ("m", "l"), ("m", "h"), ("l", "j")])
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m == mapped

        # Obtain isomorphic subgraphs
        SH = nx.MultiGraph(SG.subgraph([2, 3, 4, 6]))
        FH = nx.MultiGraph(FG.subgraph(["m", "l", "j", "i"]))

        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Delete the 3-clique, keeping only the path-graph. Also, SH mirrors FH
        SH.remove_node(4)
        FH.remove_node("j")
        SH.remove_edges_from([(2, 2), (2, 3), (6, 6)])
        FH.remove_edges_from([("l", "i"), ("m", "m"), ("m", "m")])

        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert not m

        # Assign the same labels so that mirroring means isomorphic
        for n1, n2 in zip(SH.nodes(), FH.nodes()):
            SH.nodes[n1]["label"] = "red"
            FH.nodes[n2]["label"] = "red"

        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Leave only one node with self-loop
        SH.remove_nodes_from([3, 6])
        FH.remove_nodes_from(["m", "l"])
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Remove one self-loop from SH
        SH.remove_edge(2, 2)
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert not m

        # Same for FH
        FH.remove_edge("i", "i")
        m = vf2pp_isomorphism(FH, SH, node_label="label")
        assert m

        # Compose SH with the disconnected sub-graph of SG. Same for FH
        SHG = nx.compose(SH, nx.MultiGraph(SG.subgraph([10, 11, 12, 13])))
        FHG = nx.compose(FH, nx.MultiGraph(FG.subgraph(["a", "b", "d", "e"])))

        m = vf2pp_isomorphism(FH, SH, node_label="label")
        m = vf2pp_isomorphism(FHG, SHG, node_label="label")
        assert m

        # Connect the two components. Also test selfloops
        SHG.add_edges_from([(13, 13), (13, 13), (2, 13)])
        FHG.add_edges_from([("e", "e"), ("i", "e")])
        m = vf2pp_isomorphism(FHG, SHG, node_label="label")
        assert not m

        FHG.add_edges_from([("e", "e")])
        m = vf2pp_isomorphism(FHG, SHG, node_label="label")
        assert m

    def test_custom_multigraph5_same_labels(self):
        # Lots of symmetries
        #      1
        #     /|\
        #    / 2 \
        #   | / \ |
        #   5-6 3-4
        #   | \ / |
        #    \ 7 /
        #     \|/
        #      8
        SG = nx.MultiGraph()
        edges1 = [
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
        mapped = {1: "a", 2: "h", 3: "d", 4: "i", 5: "g", 6: "b", 7: "j", 8: "c"}

        SG.add_edges_from(edges1)
        FG = nx.relabel_nodes(SG, mapped)
        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Add multiple edges and self-loops, maintaining isomorphism
        SG.add_edges_from(
            [(1, 2), (1, 2), (3, 7), (8, 8), (8, 8), (7, 8), (2, 3), (5, 6)]
        )
        FG.add_edges_from(
            [
                ("a", "h"),
                ("a", "h"),
                ("d", "j"),
                ("c", "c"),
                ("c", "c"),
                ("j", "c"),
                ("d", "h"),
                ("g", "b"),
            ]
        )

        all_self_mappings = list(vf2pp_all_isomorphisms(SG, SG))
        assert len(all_self_mappings) == 1

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Make FG to be the rotated SG
        FG.remove_edges_from(
            [
                ("a", "h"),
                ("a", "h"),
                ("d", "j"),
                ("c", "c"),
                ("c", "c"),
                ("j", "c"),
                ("d", "h"),
                ("g", "b"),
            ]
        )
        FG.add_edges_from(
            [
                ("d", "i"),
                ("a", "h"),
                ("g", "b"),
                ("g", "b"),
                ("i", "i"),
                ("i", "i"),
                ("b", "j"),
                ("d", "j"),
            ]
        )

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

    def test_disconnected_multigraph_all_same_labels(self):
        SG = nx.MultiGraph()
        SG.add_nodes_from(list(range(10)))
        SG.add_edges_from([(i, i) for i in range(10)])

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_same))), "label")
        nx.set_node_attributes(FG, dict(zip(FG, it.cycle(labels_same))), "label")

        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Add self-loops to non-mapped nodes. Should be the same, as the graph is disconnected.
        SG.add_edges_from([(i, i) for i in range(5, 8)] * 3)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Compensate in FG
        FG.add_edges_from([(i, i) for i in range(3)] * 3)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

        # Add one more self-loop in FG
        FG.add_edges_from([(0, 0), (1, 1), (1, 1)])
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Compensate in SG
        SG.add_edges_from([(5, 5), (7, 7), (7, 7)])
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m

    def test_disconnected_multigraph_all_different_labels(self):
        SG = nx.MultiGraph()
        SG.add_nodes_from(list(range(10)))
        SG.add_edges_from([(i, i) for i in range(10)])

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        FG = nx.relabel_nodes(SG, mapped)

        nx.set_node_attributes(SG, dict(zip(SG, it.cycle(labels_many))), "label")
        nx.set_node_attributes(
            FG,
            dict(zip([mapped[n] for n in SG], it.cycle(labels_many))),
            "label",
        )
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m
        assert m == mapped

        # Add self-loops to non-mapped nodes. Now it is not the same, as there are different labels
        SG.add_edges_from([(i, i) for i in range(5, 8)] * 3)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Add self-loops to non mapped nodes in FG as well
        FG.add_edges_from([(mapped[i], mapped[i]) for i in range(3)] * 7)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Add self-loops to mapped nodes in FG
        FG.add_edges_from([(mapped[i], mapped[i]) for i in range(5, 8)] * 3)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert not m

        # Add self-loops to SG so that they are even in both graphs
        SG.add_edges_from([(i, i) for i in range(3)] * 7)
        m = vf2pp_isomorphism(FG, SG, node_label="label")
        assert m


class TestDiGraphISOVF2pp:
    def test_wikipedia_graph(self):
        edges1 = [
            (1, 5),
            (1, 2),
            (1, 4),
            (3, 2),
            (6, 2),
            (3, 4),
            (7, 3),
            (4, 8),
            (5, 8),
            (6, 5),
            (6, 7),
            (7, 8),
        ]
        mapped = {1: "a", 2: "h", 3: "d", 4: "i", 5: "g", 6: "b", 7: "j", 8: "c"}

        SG = nx.DiGraph(edges1)
        FG = nx.relabel_nodes(SG, mapped)

        assert vf2pp_isomorphism(FG, SG) == mapped

        # Change the direction of an edge
        SG.remove_edge(1, 5)
        SG.add_edge(5, 1)
        assert vf2pp_isomorphism(FG, SG) is None

    def test_non_isomorphic_same_degree_sequence(self):
        r"""
                SG                           FG
        1-------------2              1-------------2
        | \           |              | \           |
        |  5-------6  |              |  5-------6  |
        |  |       |  |              |  |       |  |
        |  8-------7  |              |  8-------7  |
        | /           |              |           \ |
        4-------------3              4-------------3
        """
        edges1 = [
            (1, 5),
            (1, 2),
            (4, 1),
            (3, 2),
            (3, 4),
            (5, 8),
            (6, 5),
            (6, 7),
            (7, 8),
            (4, 8),
        ]
        edges2 = [
            (1, 5),
            (1, 2),
            (4, 1),
            (3, 2),
            (3, 4),
            (5, 8),
            (6, 5),
            (6, 7),
            (7, 8),
            (3, 7),
        ]

        SG = nx.DiGraph(edges1)
        FG = nx.DiGraph(edges2)
        assert vf2pp_isomorphism(FG, SG) is None


def test_isomorphvf2pp_multidigraphs():
    g = nx.MultiDiGraph({0: [1, 1, 2, 2, 3], 1: [2, 3, 3], 2: [3]})
    h = nx.MultiDiGraph({0: [1, 1, 2, 2, 3], 1: [2, 3, 3], 2: [3]})
    assert nx.vf2pp_is_isomorphic(g, h)

    h = nx.MultiDiGraph({0: [1, 1, 2, 2, 3], 1: [2, 3, 3], 3: [2]})
    assert not nx.vf2pp_is_isomorphic(g, h)
