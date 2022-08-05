import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import _precheck


class TestPreCheck:
    def test_first_graph_empty(self):
        G1 = nx.Graph()
        G2 = nx.Graph([(0, 1), (1, 2)])
        assert not _precheck(G1, G2, None, None)

    def test_second_graph_empty(self):
        G1 = nx.Graph([(0, 1), (1, 2)])
        G2 = nx.Graph()
        assert not _precheck(G1, G2, None, None)

    def test_different_order1(self):
        G1 = nx.path_graph(5)
        G2 = nx.path_graph(6)
        assert not _precheck(G1, G2, None, None)

    def test_different_order2(self):
        G1 = nx.barbell_graph(100, 20)
        G2 = nx.barbell_graph(101, 20)
        assert not _precheck(G1, G2, None, None)

    def test_different_order3(self):
        G1 = nx.complete_graph(780)
        G2 = nx.complete_graph(779)
        assert not _precheck(G1, G2, None, None)

    def test_different_degree_sequences1(self):
        G1 = nx.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (0, 4)])
        G2 = nx.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (0, 4), (2, 5)])
        assert not _precheck(G1, G2, None, None)

        G2.remove_node(3)
        for node1, node2 in zip(G1.nodes(), G2.nodes()):
            G1.nodes[node1]["label"] = "a"
            G2.nodes[node2]["label"] = "a"

        l1, l2 = dict(), dict()
        assert _precheck(G1, G2, l1, l2)

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
        G2 = nx.Graph(
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
                (8, 0),
            ]
        )
        assert not _precheck(G1, G2, None, None)

        G1.add_edge(6, 1)
        for node1, node2 in zip(G1.nodes(), G2.nodes()):
            G1.nodes[node1]["label"] = "a"
            G2.nodes[node2]["label"] = "a"

        l1, l2 = dict(), dict()
        assert _precheck(G1, G2, l1, l2)

    def test_different_degree_sequences3(self):
        G1 = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)])
        G2 = nx.Graph(
            [(0, 1), (0, 6), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)]
        )
        assert not _precheck(G1, G2, None, None)

        G1.add_edge(3, 5)
        for node1, node2 in zip(G1.nodes(), G2.nodes()):
            G1.nodes[node1]["label"] = "a"
            G2.nodes[node2]["label"] = "a"

        l1, l2 = dict(), dict()
        assert _precheck(G1, G2, l1, l2)

    def test_label_distribution1(self):
        G1 = nx.path_graph(5)
        G2 = nx.path_graph(5)

        colors = ["green", "blue", "red", "yellow", "black"]
        for n1, n2 in zip(G1.nodes, G2.nodes()):
            color = colors.pop()
            G1.nodes[n1]["label"] = color
            G2.nodes[n2]["label"] = color

        l1, l2 = dict(), dict()
        assert _precheck(G1, G2, l1, l2, node_labels="label")

        G1.nodes[0]["label"] = "orange"
        l1.update({0: "orange"})
        assert not _precheck(G1, G2, l1, l2, node_labels="label")

    def test_label_distribution2(self):
        G1 = nx.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (0, 4)])
        G2 = nx.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (0, 4)])

        colors = ["green", "green", "red", "red", "red"]
        for n1, n2 in zip(G1.nodes, G2.nodes()):
            color = colors.pop()
            G1.nodes[n1]["label"] = color
            G2.nodes[n2]["label"] = color

        l1, l2 = dict(), dict()
        assert _precheck(G1, G2, l1, l2, node_labels="label")

        G1.nodes[0]["label"] = "green"
        assert not _precheck(G1, G2, l1, l2, node_labels="label")

    def test_label_distribution3(self):
        G1 = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)])
        G2 = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (2, 5), (2, 6)])

        colors1 = ["blue", "blue", "blue", "yellow", "black", "purple", "purple"]
        colors2 = ["blue", "blue", "yellow", "yelow", "black", "purple", "purple"]

        for n1, n2 in zip(G1.nodes, G2.nodes()):
            color1 = colors1.pop()
            color2 = colors2.pop()
            G1.nodes[n1]["label"] = color1
            G2.nodes[n2]["label"] = color2

        l1, l2 = dict(), dict()
        assert not _precheck(G1, G2, l1, l2, node_labels="label")

        G2.nodes[3]["label"] = "blue"
        l2.update({3: "blue"})
        l1, l2 = dict(), dict()
        assert _precheck(G1, G2, l1, l2, node_labels="label")
