import random
import pytest
import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import State, check_feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import prune_ISO


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
        s = State(G1=self.G, G2=self.G, u=0, node_order=None, mapping=m, reverse_mapping=m)

        cnt = 0
        feasible = -1
        for n in self.G.nodes():
            if not prune_ISO(G1=self.G, G2=self.G, G1_labels=G1_labels, G2_labels=G2_labels, u=1756, v=n, state=s):
                feasible = n
                cnt += 1
        assert cnt == 1
        assert feasible == 1756

    def test_iso_feasibility(self):
        G1_labels = {n: self.G.nodes[n]["label"] for n in self.G.nodes()}
        G2_labels = G1_labels
        m = {node: node for node in self.G.nodes() if node < self.G.number_of_nodes() // 4}
        s = State(G1=self.G, G2=self.G, u=0, node_order=None, mapping=m, reverse_mapping=m)

        cnt = 0
        feasible = -1
        for n in self.G.nodes():
            if check_feasibility(node1=1999, node2=n, G1=self.G, G2=self.G, G1_labels=G1_labels,
                                 G2_labels=G2_labels, state=s):
                feasible = n
                cnt += 1
        assert cnt == 1
        assert feasible == 1999
