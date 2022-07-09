import networkx as nx
import random
from networkx.algorithms.isomorphism.VF2pp_helpers.node_ordering import matching_order


def assign_labels(G1, G2):
    colors = ["white", "black", "green", "purple", "orange", "red", "blue", "pink", "yellow", "none"]
    for node in G1.nodes():
        color = colors[random.randrange(0, len(colors))]
        G1.nodes[node]["label"] = color
        G2.nodes[node]["label"] = color

    return G1, G2


def get_labes(G1, G2):
    return nx.get_node_attributes(G1, "label"), nx.get_node_attributes(G2, "label")


class TestNodeOrdering:
    def test_empty_graph(self):
        G1 = nx.Graph()
        G2 = nx.Graph()
        assert len(set(matching_order(G1, G2, None, None))) == 0

    def test_disconnected_graph(self):
        G1 = nx.Graph()
        G2 = nx.Graph()
        G1.add_node(1)
        G2.add_node(1)

        G1, G2 = assign_labels(G1, G2)
        l1, l2 = get_labes(G1, G2)

        size = len(set(matching_order(G1, G2, l1, l2)))
        assert size == 1

        for i in range(50, 300):
            G1.add_node(i)
            G2.add_node(i)
            G1, G2 = assign_labels(G1, G2)
            l1, l2 = get_labes(G1, G2)
            assert len(set(matching_order(G1, G2, l1, l2))) == size + 1
            size += 1

    def test_gnp_graph(self):
        num_nodes = [138, 155, 197, 201, 216, 244, 231, 265, 300, 333, 499]
        probabilities = [0.01, 0.067, 0.1, 0.32, 0.5, 0.78, 1]

        for Vi in num_nodes:
            for p in probabilities:
                G1 = nx.gnp_random_graph(Vi, p, 12)
                G2 = nx.gnp_random_graph(Vi, p, 12)

                G1, G2 = assign_labels(G1, G2)
                l1, l2 = get_labes(G1, G2)
                assert len(set(matching_order(G1, G2, l1, l2))) == Vi

    def test_barbel_graph(self):
        G1 = nx.barbell_graph(100, 250)
        G2 = nx.barbell_graph(100, 250)

        G1, G2 = assign_labels(G1, G2)
        l1, l2 = get_labes(G1, G2)
        assert len(set(matching_order(G1, G2, l1, l2))) == 100 + 250 + 100
