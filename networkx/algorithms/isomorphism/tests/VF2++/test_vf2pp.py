import networkx as nx
import random
from networkx.algorithms.isomorphism.VF2pp import isomorphic_VF2pp


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
    for node in G1.nodes():
        color = colors[random.randrange(0, len(colors))]
        G1.nodes[node]["label"] = color
        G2.nodes[node]["label"] = color

    return G1, G2


def get_labes(G1, G2):
    return nx.get_node_attributes(G1, "label"), nx.get_node_attributes(G2, "label")


class TestVF2pp:
    def test_disconnected_graph_iso(self):
        num_nodes = [100, 330, 579, 631, 799]
        for Vi in num_nodes:
            nodes = [i for i in range(Vi)]
            G1 = nx.Graph()
            G2 = nx.Graph()

            G1.add_nodes_from(nodes)
            G2.add_nodes_from(nodes)

            G1, G2 = assign_labels(G1, G2)
            l1, l2 = get_labes(G1, G2)

            isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
            assert isomorphic

    def test_complete_graph_iso(self):
        num_nodes = [100, 330, 411]
        for Vi in num_nodes:
            G1 = nx.complete_graph(Vi)
            G2 = nx.complete_graph(Vi)

            G1, G2 = assign_labels(G1, G2)
            l1, l2 = get_labes(G1, G2)

            isomorphic, mapping = isomorphic_VF2pp(G1, G2, l1, l2)
            assert isomorphic

    def test_cases_iso(self):
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
