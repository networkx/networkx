import random

import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import isomorphic_VF2pp


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
    ]
    for node in G1.nodes():
        color = colors[random.randrange(0, len(colors))]
        G1.nodes[node]["label"] = color
        if mapped_nodes:
            node = mapped_nodes[node]
        G2.nodes[node]["label"] = color

    return G1, G2


def get_labes(G1, G2):
    return nx.get_node_attributes(G1, "label"), nx.get_node_attributes(G2, "label")


class TestVF2pp:
    def test_both_graphs_empty(self):
        G = nx.Graph()
        H = nx.Graph()
        isomorphic, mapping = isomorphic_VF2pp(G, H, {}, {})
        assert isomorphic
        assert mapping == {}

    def test_first_graph_empty(self):
        G = nx.Graph()
        H = nx.Graph([(0, 1)])
        isomorphic, mapping = isomorphic_VF2pp(G, H, {}, {})
        assert not isomorphic
        assert mapping is None

    def test_second_graph_empty(self):
        G = nx.Graph([(0, 1)])
        H = nx.Graph()
        isomorphic, mapping = isomorphic_VF2pp(G, H, {}, {})
        assert not isomorphic
        assert mapping is None

    # def test_disconnected_graph(self):
    #     num_nodes = [100, 330, 579, 631, 799]
    #     for Vi in num_nodes:
    #         nodes = [i for i in range(Vi)]
    #         G1 = nx.Graph()
    #         G2 = nx.Graph()
    #
    #         G1.add_nodes_from(nodes)
    #         G2.add_nodes_from(nodes)
    #
    #         G1, G2 = assign_labels(G1, G2)
    #         l1, l2 = get_labes(G1, G2)
    #
    #         isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
    #         assert isomorphic
    #         assert len(set(mapping)) == G1.number_of_nodes()

    def test_custom_graph1(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
        edges1 = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 6), (3, 4), (5, 1), (5, 2)]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        G1, G2 = assign_labels(G1, G2, mapped)
        l1, l2 = get_labes(G1, G2)

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic
        assert mapping == mapped

    def test_complete_graph_exhaustive(self):
        num_nodes = [100, 330, 411]
        for Vi in num_nodes:
            G1 = nx.complete_graph(Vi)
            G2 = nx.complete_graph(Vi)

            G1, G2 = assign_labels(G1, G2)
            l1, l2 = get_labes(G1, G2)

            isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
            assert isomorphic

    def test_custom_graph2(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        G1, G2 = assign_labels(G1, G2, mapped)
        l1, l2 = get_labes(G1, G2)

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic
        assert mapping == mapped

    def test_custom_graph2_cases(self):
        G1 = nx.Graph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]

        colors = ["white", "black", "green", "purple", "orange", "red", "blue"]
        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        for node in G1.nodes():
            color = colors.pop()
            G1.nodes[node]["label"] = color
            G2.nodes[mapped[node]]["label"] = color

        # Adding new nodes
        G1.add_node(0)
        G2.add_node("Z")
        G1.nodes[0]["label"] = G1.nodes[1]["label"]
        G2.nodes["Z"]["label"] = G1.nodes[1]["label"]
        l1, l2 = get_labes(G1, G2)
        mapped.update({0: "Z"})

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic
        assert mapping == mapped

        # Change the color of one of the nodes
        G2.nodes["Z"]["label"] = G1.nodes[2]["label"]
        l1, l2 = get_labes(G1, G2)

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert not isomorphic
        assert not mapping

        # Add an extra edge
        G1.nodes[0]["label"] = "blue"
        G2.nodes["Z"]["label"] = "blue"
        l1, l2 = get_labes(G1, G2)
        G1.add_edge(0, 0)

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert not isomorphic
        assert not mapping

        # Add extra edge to both
        G2.add_edge("Z", "Z")
        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic
        assert mapping == mapped

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
        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic
        assert mapping == mapped

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
        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert not isomorphic
        assert not mapping

        # Compensate in G2
        G2.add_edge(9, 1)
        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic
        assert mapping == mapped

        # Add extra node
        G1.add_node("A")
        G2.add_node("K")
        G1.nodes["A"]["label"] = "green"
        G2.nodes["K"]["label"] = "green"
        l1, l2 = get_labes(G1, G2)
        mapped.update({"A": "K"})

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic
        assert mapping == mapped

        # Connect A to one side of G1 and K to the opposite
        G1.add_edge("A", 6)
        G2.add_edge("K", 5)
        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert not isomorphic
        assert not mapping

        # Make the graphs symmetrical
        G1.add_edge(1, 5)
        G1.add_edge(2, 9)
        G2.add_edge(9, 3)
        G2.add_edge(8, 4)
        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert not isomorphic
        assert not mapping

        # Assign same colors so the two opposite sides are identical
        for node in G1.nodes():
            color = "red"
            G1.nodes[node]["label"] = color
            G2.nodes[mapped[node]]["label"] = color

        l1, l2 = get_labes(G1, G2)
        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic
        assert mapping

    def test_random_graph_cases(self):
        # Two isomorphic GNP graphs
        G1 = nx.gnp_random_graph(300, 0.4, 23)
        G2 = nx.gnp_random_graph(300, 0.4, 23)

        G1, G2 = assign_labels(G1, G2)
        l1, l2 = get_labes(G1, G2)

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic

        # Add one node per graph and give different labels
        G1.add_node(400)
        G2.add_node(400)
        G1.nodes[400]["label"] = "blue"
        G2.nodes[400]["label"] = "red"
        l1.update({400: "blue"})
        l2.update({400: "red"})

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert not isomorphic

        # Add same number of edges between the new node and the rest of the graph
        G1.add_edges_from([(400, i) for i in range(73)])
        G2.add_edges_from([(400, i) for i in range(73)])

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert not isomorphic

        # Assign same label to the new node in G1 and G2
        G2.nodes[400]["label"] = "blue"
        l2.update({400: "blue"})

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic

        # Add an extra edge between the new node and itself in one graph
        G1.add_edge(400, 400)
        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert not isomorphic

        # Add two edges between the new node and itself in both graphs
        G1.add_edge(400, 400)
        G2.add_edge(400, 400)
        G2.add_edge(400, 400)

        isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
        assert isomorphic
