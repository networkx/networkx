import random
import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import State, check_feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import prune_ISO


def compute_Ti(G1, G2, mapping, reverse_mapping):
    T1 = {nbr for node in mapping for nbr in G1[node] if nbr not in mapping}
    T2 = {nbr for node in reverse_mapping for nbr in G2[node] if nbr not in reverse_mapping}

    T1_out = {n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in T1}
    T2_out = {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in T2}
    return T1, T2, T1_out, T2_out


class TestFeasibilityISO:
    V = 2000
    G = nx.gnp_random_graph(V, 0.67, seed=42)
    colors = ["blue", "red", "green", "orange", "grey", "yellow", "purple", "black", "white"]
    for i in range(V):
        G.nodes[i]["label"] = colors[random.randrange(len(colors))]

    def test_prune_iso(self):
        G1_labels = {n: self.G.nodes[n]["label"] for n in self.G.nodes()}
        G2_labels = G1_labels

        m = {node: node for node in self.G.nodes() if node < self.G.number_of_nodes() // 4}
        T1, T2, T1_out, T2_out = compute_Ti(self.G, self.G, m, m)

        cnt = 0
        feasible = -1
        for n in self.G.nodes():
            if not prune_ISO(self.G, self.G, G1_labels, G2_labels, 1756, n, m, m, T1, T1_out, T2, T2_out):
                feasible = n
                cnt += 1
        assert cnt == 1
        assert feasible == 1756

    def test_iso_feasibility1(self):
        G1_labels = {n: self.G.nodes[n]["label"] for n in self.G.nodes()}
        G2_labels = G1_labels
        m = {node: node for node in self.G.nodes() if node < self.G.number_of_nodes() // 4}
        T1, T2, T1_out, T2_out = compute_Ti(self.G, self.G, m, m)

        cnt = 0
        feasible = -1
        for n in self.G.nodes():
            if check_feasibility(1999, n, self.G, self.G, G1_labels, G2_labels, m, m, T1, T1_out, T2, T2_out):
                feasible = n
                cnt += 1
        assert cnt == 1
        assert feasible == 1999

    def test_iso_feasibility2(self):
        G1 = nx.Graph()
        G2 = nx.Graph()

        G1_edges = [(1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5), (1, 6), (6, 7), (6, 8), (8, 9), (7, 9)]
        G2_edges = [(1, 2), (2, 3), (3, 4), (1, 4), (4, 9), (9, 8), (8, 7), (7, 6), (8, 6), (9, 6), (5, 6), (5, 9)]

        G1.add_edges_from(G1_edges)
        G2.add_edges_from(G2_edges)
        G1.add_node(0)
        G2.add_node(0)

        mapped_nodes = {0: 0, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 1, 8: 3, 9: 2}

        # same labels
        for n in G1.nodes():
            G1.nodes[n]["label"] = "blue"
            G2.nodes[n]["label"] = "blue"

        G1_labels = {node: G1.nodes[node]["label"] for node in G1.nodes()}
        G2_labels = {node: G2.nodes[node]["label"] for node in G2.nodes()}

        mapping = dict()
        reverse_mapping = dict()
        T1, T2, T1_out, T2_out = compute_Ti(G1, G2, mapping, reverse_mapping)

        for node1 in G1.nodes():
            for node2 in G2.nodes():
                if node2 == mapped_nodes[node1]:
                    assert check_feasibility(node1, node2, G1, G2, G1_labels, G2_labels, mapping, reverse_mapping, T1,
                                             T1_out, T2, T2_out)

    def test_iso_feasibility3(self):
        G1 = nx.Graph()
        G2 = nx.Graph()

        G1_edges = [(1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5), (1, 6), (6, 7), (6, 8), (8, 9), (7, 9)]
        G2_edges = [(1, 2), (2, 3), (3, 4), (1, 4), (4, 9), (9, 8), (8, 7), (7, 6), (8, 6), (9, 6), (5, 6), (5, 9)]

        G1.add_edges_from(G1_edges)
        G2.add_edges_from(G2_edges)
        G1.add_node(0)
        G2.add_node(0)

        mapped_nodes = {0: 0, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 1, 8: 3, 9: 2}

        # different labels
        colors = ["white", "black", "green", "purple", "orange", "red", "blue", "pink", "yellow", "none"]
        for node, color in zip(G1.nodes, colors):
            G1.nodes[node]["label"] = color
            G2.nodes[mapped_nodes[node]]["label"] = color

        G1_labels = {node: G1.nodes[node]["label"] for node in G1.nodes()}
        G2_labels = {node: G2.nodes[node]["label"] for node in G2.nodes()}

        mapping = dict()
        reverse_mapping = dict()
        T1, T2, T1_out, T2_out = compute_Ti(G1, G2, mapping, reverse_mapping)

        for node1 in G1.nodes():
            for node2 in G2.nodes():
                if node2 == mapped_nodes[node1]:
                    assert check_feasibility(node1, node2, G1, G2, G1_labels, G2_labels, mapping, reverse_mapping, T1,
                                             T1_out, T2, T2_out)
                else:
                    assert not check_feasibility(node1, node2, G1, G2, G1_labels, G2_labels, mapping, reverse_mapping,
                                                 T1, T1_out, T2, T2_out)
