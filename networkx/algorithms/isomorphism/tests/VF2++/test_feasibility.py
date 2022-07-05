import random
import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import State, check_feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import prune_ISO


class TestFeasibilityISO:
    V = 2000
    G = nx.gnp_random_graph(V, 0.67, seed=42)
    colors = ["blue", "red", "green", "orange", "grey", "yellow", "purple", "black", "white"]
    for i in range(V):
        G.nodes[i]["label"] = colors[random.randrange(len(colors))]

    def compute_Ti(self, mapping, reverse_mapping):
        T1 = {nbr for node in mapping for nbr in self.G[node] if nbr not in mapping}
        T2 = {nbr for node in reverse_mapping for nbr in self.G[node] if nbr not in reverse_mapping}

        T1_out = {n1 for n1 in self.G.nodes() if n1 not in mapping and n1 not in T1}
        T2_out = {n2 for n2 in self.G.nodes() if n2 not in reverse_mapping and n2 not in T2}
        return T1, T2, T1_out, T2_out

    def test_prune_iso(self):
        G1_labels = {n: self.G.nodes[n]["label"] for n in self.G.nodes()}
        G2_labels = G1_labels

        m = {node: node for node in self.G.nodes() if node < self.G.number_of_nodes() // 4}
        T1, T2, T1_out, T2_out = self.compute_Ti(m, m)

        cnt = 0
        feasible = -1
        for n in self.G.nodes():
            if not prune_ISO(self.G, self.G, G1_labels, G2_labels, 1756, n, m, m, T1, T1_out, T2, T2_out):
                feasible = n
                cnt += 1
        assert cnt == 1
        assert feasible == 1756

    def test_iso_feasibility(self):
        G1_labels = {n: self.G.nodes[n]["label"] for n in self.G.nodes()}
        G2_labels = G1_labels
        m = {node: node for node in self.G.nodes() if node < self.G.number_of_nodes() // 4}
        T1, T2, T1_out, T2_out = self.compute_Ti(m, m)

        cnt = 0
        feasible = -1
        for n in self.G.nodes():
            if check_feasibility(1999, n, self.G, self.G, G1_labels, G2_labels, m, m, T1, T1_out, T2, T2_out):
                feasible = n
                cnt += 1
        assert cnt == 1
        assert feasible == 1999
