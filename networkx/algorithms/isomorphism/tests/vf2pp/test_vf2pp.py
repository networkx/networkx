import itertools

import utils

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import vf2pp_mapping


class TestGraphISOVF2pp:
    def test_both_graphs_empty(self):
        G = nx.Graph()
        H = nx.Graph()

        m = vf2pp_mapping(G, H, None)
        assert m is None

        G.add_node(0)
        m = vf2pp_mapping(G, H, None)
        assert m is None
        m = vf2pp_mapping(H, G, None)
        assert m is None

        H.add_node(0)
        m = vf2pp_mapping(G, H, None)
        assert m == {0: 0}

    def test_first_graph_empty(self):
        G = nx.Graph()
        H = nx.Graph([(0, 1)])
        m = vf2pp_mapping(G, H, None)
        assert m is None

    def test_second_graph_empty(self):
        G = nx.Graph([(0, 1)])
        H = nx.Graph()
        m = vf2pp_mapping(G, H, None)
        assert m is None

    def test_custom_graph1_same_labels(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
        edges1 = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 6), (3, 4), (5, 1), (5, 2)]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_same))), "label"
        )
        nx.set_node_attributes(
            G2, dict(zip(G2, itertools.cycle(utils.labels_same))), "label"
        )

        m = vf2pp_mapping(G1, G2, node_labels=None)
        assert m

        # Add edge making G1 symmetrical
        G1.add_edge(3, 7)
        G1.nodes[7]["label"] = "blue"
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Make G2 isomorphic to G1
        G2.add_edges_from([(mapped[3], "X"), (mapped[6], mapped[5])])
        G1.add_edge(4, 7)
        G2.nodes["X"]["label"] = "blue"
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Re-structure maintaining isomorphism
        G1.remove_edges_from([(1, 4), (1, 3)])
        G2.remove_edges_from([(mapped[1], mapped[5]), (mapped[1], mapped[2])])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

    def test_custom_graph1_different_labels(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
        edges1 = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 6), (3, 4), (5, 1), (5, 2)]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_different))), "label"
        )
        nx.set_node_attributes(
            G2,
            dict(zip([mapped[n] for n in G1], itertools.cycle(utils.labels_different))),
            "label",
        )

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m == mapped

    def test_custom_graph2_same_labels(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_same))), "label"
        )
        nx.set_node_attributes(
            G2, dict(zip(G2, itertools.cycle(utils.labels_same))), "label"
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Obtain two isomorphic subgraphs from the graph
        G2.remove_edge(mapped[1], mapped[2])
        G2.add_edge(mapped[1], mapped[4])
        H1 = nx.Graph(G1.subgraph([2, 3, 4, 7]))
        H2 = nx.Graph(G2.subgraph([mapped[1], mapped[4], mapped[5], mapped[6]]))

        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Add edges maintaining isomorphism
        H1.add_edges_from([(3, 7), (4, 7)])
        H2.add_edges_from([(mapped[1], mapped[6]), (mapped[4], mapped[6])])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

    def test_custom_graph2_different_labels(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_different))), "label"
        )
        nx.set_node_attributes(
            G2,
            dict(zip([mapped[n] for n in G1], itertools.cycle(utils.labels_different))),
            "label",
        )

        # Adding new nodes
        G1.add_node(0)
        G2.add_node("Z")
        G1.nodes[0]["label"] = G1.nodes[1]["label"]
        G2.nodes["Z"]["label"] = G1.nodes[1]["label"]
        mapped.update({0: "Z"})

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Change the color of one of the nodes
        G2.nodes["Z"]["label"] = G1.nodes[2]["label"]
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Add an extra edge
        G1.nodes[0]["label"] = "blue"
        G2.nodes["Z"]["label"] = "blue"
        G1.add_edge(0, 1)

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Add extra edge to both
        G2.add_edge("Z", "A")
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

    def test_custom_graph3_same_labels(self):
        G1 = nx.Graph()

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
        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_same))), "label"
        )
        nx.set_node_attributes(
            G2, dict(zip(G2, itertools.cycle(utils.labels_same))), "label"
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Connect nodes maintaining symmetry
        G1.add_edges_from([(6, 9), (7, 8)])
        G2.add_edges_from([(mapped[6], mapped[8]), (mapped[7], mapped[9])])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Make isomorphic
        G1.add_edges_from([(6, 8), (7, 9)])
        G2.add_edges_from([(mapped[6], mapped[9]), (mapped[7], mapped[8])])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Connect more nodes
        G1.add_edges_from([(2, 7), (3, 6)])
        G2.add_edges_from([(mapped[2], mapped[7]), (mapped[3], mapped[6])])
        G1.add_node(10)
        G2.add_node("Z")
        G1.nodes[10]["label"] = "blue"
        G2.nodes["Z"]["label"] = "blue"

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Connect the newly added node, to opposite sides of the graph
        G1.add_edges_from([(10, 1), (10, 5), (10, 8)])
        G2.add_edges_from([("Z", mapped[1]), ("Z", mapped[4]), ("Z", mapped[9])])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Get two subgraphs that are not isomorphic but are easy to make
        H1 = nx.Graph(G1.subgraph([2, 3, 4, 5, 6, 7, 10]))
        H2 = nx.Graph(
            G2.subgraph(
                [mapped[4], mapped[5], mapped[6], mapped[7], mapped[8], mapped[9], "Z"]
            )
        )
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m is None

        # Restructure both to make them isomorphic
        H1.add_edges_from([(10, 2), (10, 6), (3, 6), (2, 7), (2, 6), (3, 7)])
        H2.add_edges_from(
            [("Z", mapped[7]), (mapped[6], mapped[9]), (mapped[7], mapped[8])]
        )
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Add edges with opposite direction in each Graph
        H1.add_edge(3, 5)
        H2.add_edge(mapped[5], mapped[7])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m is None

    def test_custom_graph3_different_labels(self):
        G1 = nx.Graph()

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
        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_different))), "label"
        )
        nx.set_node_attributes(
            G2,
            dict(zip([mapped[n] for n in G1], itertools.cycle(utils.labels_different))),
            "label",
        )

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Add extra edge to G1
        G1.add_edge(1, 7)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Compensate in G2
        G2.add_edge(9, 1)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Add extra node
        G1.add_node("A")
        G2.add_node("K")
        G1.nodes["A"]["label"] = "green"
        G2.nodes["K"]["label"] = "green"
        mapped.update({"A": "K"})

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Connect A to one side of G1 and K to the opposite
        G1.add_edge("A", 6)
        G2.add_edge("K", 5)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Make the graphs symmetrical
        G1.add_edge(1, 5)
        G1.add_edge(2, 9)
        G2.add_edge(9, 3)
        G2.add_edge(8, 4)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Assign same colors so the two opposite sides are identical
        for node in G1.nodes():
            color = "red"
            G1.nodes[node]["label"] = color
            G2.nodes[mapped[node]]["label"] = color

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

    def test_custom_graph4_different_labels(self):
        G1 = nx.Graph()
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

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_different))), "label"
        )
        nx.set_node_attributes(
            G2,
            dict(zip([mapped[n] for n in G1], itertools.cycle(utils.labels_different))),
            "label",
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m == mapped

    def test_custom_graph4_same_labels(self):
        G1 = nx.Graph()
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

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_same))), "label"
        )
        nx.set_node_attributes(
            G2, dict(zip(G2, itertools.cycle(utils.labels_same))), "label"
        )

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Add nodes of different label
        G1.add_node(0)
        G2.add_node("z")
        G1.nodes[0]["label"] = "green"
        G2.nodes["z"]["label"] = "blue"

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Make the labels identical
        G2.nodes["z"]["label"] = "green"
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Change the structure of the graphs, keeping them isomorphic
        G1.add_edge(2, 5)
        G2.remove_edge("i", "l")
        G2.add_edge("g", "l")
        G2.add_edge("m", "f")

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Change the structure of the disconnected sub-graph, keeping it isomorphic
        G1.remove_node(13)
        G2.remove_node("d")

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Connect the newly added node to the disconnected graph, which now is just a path of size 3
        G1.add_edge(0, 10)
        G2.add_edge("e", "z")

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Connect the two disconnected sub-graphs, forming a single graph
        G1.add_edge(11, 3)
        G1.add_edge(0, 8)
        G2.add_edge("a", "l")
        G2.add_edge("z", "j")

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

    def test_custom_graph5_same_labels(self):
        G1 = nx.Graph()
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

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_same))), "label"
        )
        nx.set_node_attributes(
            G2, dict(zip(G2, itertools.cycle(utils.labels_same))), "label"
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Add different edges in each graph, maintaining symmetry
        G1.add_edges_from([(3, 6), (2, 7), (2, 5), (1, 3), (4, 7), (6, 8)])
        G2.add_edges_from(
            [
                (mapped[6], mapped[3]),
                (mapped[2], mapped[7]),
                (mapped[1], mapped[6]),
                (mapped[5], mapped[7]),
                (mapped[3], mapped[8]),
                (mapped[2], mapped[4]),
            ]
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Obtain two different but isomorphic subgraphs from G1 and G2
        H1 = nx.Graph(G1.subgraph([1, 5, 8, 6, 7, 3]))
        H2 = nx.Graph(
            G2.subgraph(
                [mapped[1], mapped[4], mapped[8], mapped[7], mapped[3], mapped[5]]
            )
        )
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Delete corresponding node from the two graphs
        H1.remove_node(8)
        H2.remove_node(mapped[7])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Re-orient, maintaining isomorphism
        H1.add_edge(1, 6)
        H1.remove_edge(3, 6)
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

    def test_custom_graph5_different_labels(self):
        G1 = nx.Graph()
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

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        colors = ["red", "blue", "grey", "none", "brown", "solarized", "yellow", "pink"]
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_different))), "label"
        )
        nx.set_node_attributes(
            G2,
            dict(zip([mapped[n] for n in G1], itertools.cycle(utils.labels_different))),
            "label",
        )

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Assign different colors to matching nodes
        c = 0
        for node in G1.nodes():
            color1 = colors[c]
            color2 = colors[(c + 3) % len(colors)]
            G1.nodes[node]["label"] = color1
            G2.nodes[mapped[node]]["label"] = color2
            c += 1

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Get symmetrical sub-graphs of G1,G2 and compare them
        H1 = G1.subgraph([1, 5])
        H2 = G2.subgraph(["i", "c"])
        c = 0
        for node1, node2 in zip(H1.nodes(), H2.nodes()):
            H1.nodes[node1]["label"] = "red"
            H2.nodes[node2]["label"] = "red"
            c += 1

        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

    def test_disconnected_graph_all_same_labels(self):
        G1 = nx.Graph()
        G1.add_nodes_from([i for i in range(10)])

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        G2 = nx.relabel_nodes(G1, mapped)
        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_same))), "label"
        )
        nx.set_node_attributes(
            G2, dict(zip(G2, itertools.cycle(utils.labels_same))), "label"
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

    def test_disconnected_graph_all_different_labels(self):
        G1 = nx.Graph()
        G1.add_nodes_from([i for i in range(10)])

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        G2 = nx.relabel_nodes(G1, mapped)

        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_different))), "label"
        )
        nx.set_node_attributes(
            G2,
            dict(zip([mapped[n] for n in G1], itertools.cycle(utils.labels_different))),
            "label",
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

    def test_disconnected_graph_some_same_labels(self):
        G1 = nx.Graph()
        G1.add_nodes_from([i for i in range(10)])

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        G2 = nx.relabel_nodes(G1, mapped)

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

        nx.set_node_attributes(G1, dict(zip(G1, itertools.cycle(colors))), "label")
        nx.set_node_attributes(
            G2, dict(zip([mapped[n] for n in G1], itertools.cycle(colors))), "label"
        )

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m


class TestDiGraphISOVF2pp:
    def test_both_graphs_empty(self):
        G = nx.DiGraph()
        H = nx.DiGraph()

        m = vf2pp_mapping(G, H, None)
        assert m is None

    def test_first_graph_empty(self):
        G = nx.DiGraph()
        H = nx.DiGraph([(0, 1)])
        m = vf2pp_mapping(G, H, None)
        assert m is None

    def test_second_graph_empty(self):
        G = nx.DiGraph([(0, 1)])
        H = nx.DiGraph()
        m = vf2pp_mapping(G, H, None)
        assert m is None

    def test_wiki_graph_no_labels(self):
        G1 = nx.DiGraph(
            [
                [1, 2],
                [2, 3],
                [3, 4],
                [4, 1],
                [5, 6],
                [6, 7],
                [7, 8],
                [8, 5],
                [1, 5],
                [2, 6],
                [3, 7],
                [4, 8],
            ]
        )
        G2 = nx.DiGraph(
            [
                ["a", "g"],
                ["a", "h"],
                ["i", "a"],
                ["g", "b"],
                ["h", "b"],
                ["b", "j"],
                ["c", "g"],
                ["i", "c"],
                ["j", "c"],
                ["h", "d"],
                ["d", "i"],
                ["d", "j"],
            ]
        )

        m = vf2pp_mapping(G1, G2, node_labels=None)
        assert m

        # Change the direction of an edge in one graph
        G1.remove_edge(5, 6)
        G1.add_edge(6, 5)
        m = vf2pp_mapping(G1, G2, node_labels=None)
        assert m is None

        # Do the same in G2 but in different edge
        G2.remove_edge("g", "b")
        G2.add_edge("b", "g")
        m = vf2pp_mapping(G1, G2, node_labels=None)
        assert m

        # Add new node in both graphs but connect with different direction
        G1.add_node(100)
        G2.add_node("X")
        G1.add_edge(100, 1)
        G2.add_edge("a", "X")

        m = vf2pp_mapping(G1, G2, node_labels=None)
        assert m is None

        # Fix all directions
        G1.remove_edge(100, 1)
        G1.add_edge(1, 100)
        m = vf2pp_mapping(G1, G2, node_labels=None)
        assert m

    def test_wiki_graph_with_labels(self):
        G1 = nx.DiGraph(
            [
                [1, 2],
                [2, 3],
                [3, 4],
                [4, 1],
                [5, 6],
                [6, 7],
                [7, 8],
                [8, 5],
                [1, 5],
                [2, 6],
                [3, 7],
                [4, 8],
            ]
        )
        G2 = nx.DiGraph(
            [
                ["a", "g"],
                ["a", "h"],
                ["i", "a"],
                ["g", "b"],
                ["h", "b"],
                ["b", "j"],
                ["c", "g"],
                ["i", "c"],
                ["j", "c"],
                ["h", "d"],
                ["d", "i"],
                ["d", "j"],
            ]
        )
        mapped = {1: "a", 2: "h", 3: "d", 4: "i", 5: "g", 6: "b", 7: "j", 8: "c"}

        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_different))), "label"
        )
        nx.set_node_attributes(
            G2,
            dict(zip([mapped[n] for n in G1], itertools.cycle(utils.labels_different))),
            "label",
        )

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m == mapped

        # Change the direction of an edge in one graph
        G1.remove_edge(3, 7)
        G1.add_edge(7, 3)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Undo
        G1.remove_edge(7, 3)
        G1.add_edge(3, 7)

        # Change label of one node
        temp = G1.nodes[7]["label"]
        G1.nodes[7]["label"] = "some color"
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Undo
        G1.nodes[7]["label"] = temp
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m == mapped

        # Connect two far nodes, with different direction for each graph
        G1.add_edge(1, 3)
        G2.add_edge(mapped[3], mapped[1])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

    def test_same_degree_sequence_no_labels(self):
        G1 = nx.DiGraph([(1, 2), (1, 3), (3, 2), (4, 5)])
        G2 = nx.DiGraph([(2, 1), (2, 3), (4, 3), (5, 4)])

        # Two different, non-isomorphic graphs with same degree sequences
        m = vf2pp_mapping(G1, G2, node_labels=None)
        assert m is None

        # Delete edge and add edge with different direction in each graph
        G2.remove_edge(2, 3)
        G2.add_edge(3, 5)
        m = vf2pp_mapping(G1, G2, node_labels=None)
        assert m is None

        # Fix wrong direction
        G2.remove_edge(3, 5)
        G2.add_edge(5, 3)
        m = vf2pp_mapping(G1, G2, node_labels=None)
        assert m

    def test_same_degree_sequence_with_labels(self):
        G1 = nx.DiGraph([(1, 2), (1, 3), (3, 2), (4, 5)])
        G2 = nx.DiGraph([(2, 1), (2, 3), (4, 3), (5, 4)])

        mapped = {1: 5, 3: 4, 2: 3, 4: 2, 5: 1}

        nx.set_node_attributes(
            G1, dict(zip(G1, itertools.cycle(utils.labels_different))), "label"
        )
        nx.set_node_attributes(
            G2,
            dict(zip([mapped[n] for n in G1], itertools.cycle(utils.labels_different))),
            "label",
        )

        # Two different, non-isomorphic graphs with same degree sequences
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m is None

        # Remove edge and make them isomorphic
        G2.remove_edge(2, 3)
        G2.add_edge(5, 3)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m == mapped
