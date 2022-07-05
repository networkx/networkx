import networkx as nx
from networkx.algorithms.isomorphism.VF2pp_helpers.candidates import find_candidates


class TestCandidateSelection:
    G1 = nx.Graph()
    G2 = nx.Graph()

    G1_edges = [(1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (4, 5), (1, 6), (6, 7), (6, 8), (8, 9), (7, 9)]
    G2_edges = [(1, 2), (2, 3), (3, 4), (1, 4), (4, 9), (9, 8), (8, 7), (7, 6), (8, 6), (9, 6), (5, 6), (5, 9)]

    G1.add_edges_from(G1_edges)
    G2.add_edges_from(G2_edges)
    G1.add_node(0)
    G2.add_node(0)

    mapped_nodes = {0: 0, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 1, 8: 3, 9: 2}

    def get_labels(self):
        return {node: self.G1.nodes[node]["label"] for node in self.G1.nodes()}, {node: self.G2.nodes[node]["label"] for
                                                                                  node in self.G2.nodes()}

    def test_same_labels(self):
        for n in self.G1.nodes():
            self.G1.nodes[n]["label"] = "blue"
            self.G2.nodes[n]["label"] = "blue"

        G1_labels, G2_labels = self.get_labels()

        for node in self.G1.nodes():
            assert self.mapped_nodes[node] in find_candidates(self.G1, self.G2, G1_labels, G2_labels, node, dict(),
                                                              dict())

    def test_different_labels(self):
        colors = ["white", "black", "green", "purple", "orange", "red", "blue", "pink", "yellow", "none"]
        for node, color in zip(self.G1.nodes, colors):
            self.G1.nodes[node]["label"] = color
            self.G2.nodes[self.mapped_nodes[node]]["label"] = color

        G1_labels, G2_labels = self.get_labels()

        for node in self.G1.nodes():
            candidates = find_candidates(self.G1, self.G2, G1_labels, G2_labels, node, dict(), dict())
            assert len(candidates) == 1
            assert self.mapped_nodes[node] in candidates
