import random

import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import isomorphic_VF2pp


def VF2pp(G1, G2, l1, l2):
    try:
        m = next(isomorphic_VF2pp(G1, G2, l1, l2))
        return m
    except StopIteration:
        return None


def assign_labels(G1, G2, mapped_nodes=None):
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
        "ocean",
        "brown",
        "solarized",
    ]

    c = 0
    for node in G1.nodes():
        color = colors[c % len(colors)]
        G1.nodes[node]["label"] = color
        if mapped_nodes:
            node = mapped_nodes[node]
        G2.nodes[node]["label"] = color
        c += 1


def get_labes(G1, G2):
    return nx.get_node_attributes(G1, "label"), nx.get_node_attributes(G2, "label")


class TestVF2pp:
    def test_both_graphs_empty(self):
        G = nx.Graph()
        H = nx.Graph()

        m = VF2pp(G, H, {}, {})
        assert not m

    def test_first_graph_empty(self):
        G = nx.Graph()
        H = nx.Graph([(0, 1)])
        m = VF2pp(G, H, {}, {})
        assert not m

    def test_second_graph_empty(self):
        G = nx.Graph([(0, 1)])
        H = nx.Graph()
        m = VF2pp(G, H, {}, {})
        assert not m

    def test_custom_graph1(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
        edges1 = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 6), (3, 4), (5, 1), (5, 2)]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        assign_labels(G1, G2, mapped)
        l1, l2 = get_labes(G1, G2)

        m = VF2pp(G1, G2, l1, l2)
        assert m
        assert m == mapped

    def test_custom_graph2(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        assign_labels(G1, G2, mapped)
        l1, l2 = get_labes(G1, G2)

        m = VF2pp(G1, G2, l1, l2)
        assert m
        assert m == mapped

    def test_custom_graph2_cases(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]

        colors = ["white", "black", "green", "purple", "orange", "red", "blue"]
        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        assign_labels(G1, G2, mapped)

        # Adding new nodes
        G1.add_node(0)
        G2.add_node("Z")
        G1.nodes[0]["label"] = G1.nodes[1]["label"]
        G2.nodes["Z"]["label"] = G1.nodes[1]["label"]
        l1, l2 = get_labes(G1, G2)
        mapped.update({0: "Z"})

        m = VF2pp(G1, G2, l1, l2)
        assert m
        assert m == mapped

        # Change the color of one of the nodes
        G2.nodes["Z"]["label"] = G1.nodes[2]["label"]
        l1, l2 = get_labes(G1, G2)

        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Add an extra edge
        G1.nodes[0]["label"] = "blue"
        G2.nodes["Z"]["label"] = "blue"
        l1, l2 = get_labes(G1, G2)
        G1.add_edge(0, 0)

        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Add extra edge to both
        G2.add_edge("Z", "Z")
        m = VF2pp(G1, G2, l1, l2)
        assert m
        assert m == mapped

    def test_custom_graph3(self):
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

        assign_labels(G1, G2, mapped)
        l1, l2 = get_labes(G1, G2)

        m = VF2pp(G1, G2, l1, l2)
        assert m
        assert m == mapped

    def test_custom_graph3_cases(self):
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

        colors = [
            "white",
            "black",
            "green",
            "purple",
            "orange",
            "red",
            "blue",
            "grey",
            "none",
        ]

        for node in G1.nodes():
            color = colors.pop()
            G1.nodes[node]["label"] = color
            G2.nodes[mapped[node]]["label"] = color

        l1, l2 = get_labes(G1, G2)

        # Add extra edge to G1
        G1.add_edge(1, 7)
        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Compensate in G2
        G2.add_edge(9, 1)
        m = VF2pp(G1, G2, l1, l2)
        assert m
        assert m == mapped

        # Add extra node
        G1.add_node("A")
        G2.add_node("K")
        G1.nodes["A"]["label"] = "green"
        G2.nodes["K"]["label"] = "green"
        l1, l2 = get_labes(G1, G2)
        mapped.update({"A": "K"})

        m = VF2pp(G1, G2, l1, l2)
        assert m
        assert m == mapped

        # Connect A to one side of G1 and K to the opposite
        G1.add_edge("A", 6)
        G2.add_edge("K", 5)
        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Make the graphs symmetrical
        G1.add_edge(1, 5)
        G1.add_edge(2, 9)
        G2.add_edge(9, 3)
        G2.add_edge(8, 4)
        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Assign same colors so the two opposite sides are identical
        for node in G1.nodes():
            color = "red"
            G1.nodes[node]["label"] = color
            G2.nodes[mapped[node]]["label"] = color

        l1, l2 = get_labes(G1, G2)
        m = VF2pp(G1, G2, l1, l2)
        assert m

    def test_custom_graph4(self):
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

        colors = [
            "white",
            "black",
            "green",
            "purple",
            "orange",
            "red",
            "blue",
            "grey",
            "none",
            "brown",
            "solarized",
            "yellow",
            "pink",
        ]

        for node in G1.nodes():
            color = colors.pop()
            G1.nodes[node]["label"] = color
            G2.nodes[mapped[node]]["label"] = color

        l1, l2 = get_labes(G1, G2)

        m = VF2pp(G1, G2, l1, l2)
        assert m == mapped

    def test_custom_graph4_cases(self):
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

        for node in G1.nodes():
            color = "green"
            G1.nodes[node]["label"] = color
            G2.nodes[mapped[node]]["label"] = color

        l1, l2 = get_labes(G1, G2)

        m = VF2pp(G1, G2, l1, l2)
        assert m

        # Add nodes of different label
        G1.add_node(0)
        G2.add_node("z")
        G1.nodes[0]["label"] = "green"
        G2.nodes["z"]["label"] = "blue"
        l1.update({0: "green"})
        l2.update({"z": "blue"})

        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Make the labels identical
        G2.nodes["z"]["label"] = "green"
        l2.update({"z": "green"})

        m = VF2pp(G1, G2, l1, l2)
        assert m

        # Change the structure of the graphs, keeping them isomorphic
        G1.add_edge(2, 5)
        G2.remove_edge("i", "l")
        G2.add_edge("g", "l")
        G2.add_edge("m", "f")

        m = VF2pp(G1, G2, l1, l2)
        assert m

        # Change the structure of the disconnected sub-graph, keeping it isomorphic
        G1.remove_node(13)
        G2.remove_node("d")
        l1.pop(13)
        l2.pop("d")

        m = VF2pp(G1, G2, l1, l2)
        assert m

        # Connect the newly added node to the disconnected graph, which now is just a path of size 3
        G1.add_edge(0, 10)
        G2.add_edge("e", "z")

        m = VF2pp(G1, G2, l1, l2)
        assert m

        # Connect the two disconnected sub-graphs, forming a single graph
        G1.add_edge(11, 3)
        G1.add_edge(0, 8)
        G2.add_edge("a", "l")
        G2.add_edge("z", "j")

        m = VF2pp(G1, G2, l1, l2)
        assert m

    def test_custom_graph5(self):
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

        assign_labels(G1, G2, mapped)
        l1, l2 = get_labes(G1, G2)

        m = VF2pp(G1, G2, l1, l2)
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

        l1, l2 = get_labes(G1, G2)
        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Get symmetrical sub-graphs of G1,G2 and compare them
        H1 = G1.subgraph([1, 5])
        H2 = G2.subgraph(["i", "c"])
        c = 0
        for node1, node2 in zip(H1.nodes(), H2.nodes()):
            H1.nodes[node1]["label"] = "red"
            H2.nodes[node2]["label"] = "red"
            c += 1

        l1, l2 = get_labes(H1, H2)
        m = VF2pp(H1, H2, l1, l2)
        assert m

    def test_random_graph_cases(self):
        # Two isomorphic GNP graphs
        G1 = nx.gnp_random_graph(300, 0.4, 23)
        G2 = nx.gnp_random_graph(300, 0.4, 23)

        assign_labels(G1, G2)
        l1, l2 = get_labes(G1, G2)

        m = VF2pp(G1, G2, l1, l2)
        assert m

        # Add one node per graph and give different labels
        G1.add_node(400)
        G2.add_node(400)
        G1.nodes[400]["label"] = "blue"
        G2.nodes[400]["label"] = "red"
        l1.update({400: "blue"})
        l2.update({400: "red"})

        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Add same number of edges between the new node and the rest of the graph
        G1.add_edges_from([(400, i) for i in range(73)])
        G2.add_edges_from([(400, i) for i in range(73)])

        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Assign same label to the new node in G1 and G2
        G2.nodes[400]["label"] = "blue"
        l2.update({400: "blue"})

        m = VF2pp(G1, G2, l1, l2)
        assert m

        # Add an extra edge between the new node and itself in one graph
        G1.add_edge(400, 400)
        m = VF2pp(G1, G2, l1, l2)
        assert not m

        # Add two edges between the new node and itself in both graphs
        G1.add_edge(400, 400)
        G2.add_edge(400, 400)
        G2.add_edge(400, 400)

        m = VF2pp(G1, G2, l1, l2)
        assert m

    def test_disconnected_graph(self):
        num_nodes = [100, 330, 579, 631, 799]

        for Vi in num_nodes:
            nodes = [i for i in range(Vi)]
            G1 = nx.Graph()
            G2 = nx.Graph()

            G1.add_nodes_from(nodes)
            G2.add_nodes_from(nodes)

            assign_labels(G1, G2)
            l1, l2 = get_labes(G1, G2)

            m = VF2pp(G1, G2, l1, l2)
            assert m

    def test_complete_graph_exhaustive(self):
        num_nodes = [100, 330, 411]
        for Vi in num_nodes:
            G1 = nx.complete_graph(Vi)
            G2 = nx.complete_graph(Vi)

            assign_labels(G1, G2)
            l1, l2 = get_labes(G1, G2)

            m = VF2pp(G1, G2, l1, l2)
            assert m
