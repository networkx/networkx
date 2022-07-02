import networkx as nx
from networkx.algorithms.isomorphism.VF2pp import update_Tinout


class TestTinoutUpdating:
    V = 500
    G = nx.gnp_random_graph(V, 0.6, seed=24)

    # initialize empty mapping
    mapping = dict()
    reverse_mapping = dict()

    # initialize Ti/Ti_out
    T1 = set()
    T2 = set()
    T1_out = set(G.nodes())
    T2_out = set(G.nodes())

    def compute_Ti(self, G1, G2):
        T1 = {nbr for node in self.mapping for nbr in G1[node] if nbr not in self.mapping}
        T2 = {nbr for node in self.reverse_mapping for nbr in G2[node] if nbr not in self.reverse_mapping}
        T1_out = {n1 for n1 in G1.nodes() if n1 not in self.mapping and n1 not in T1}
        T2_out = {n2 for n2 in G2.nodes() if n2 not in self.reverse_mapping and n2 not in T2}

        return T1, T2, T1_out, T2_out

    def test_incremental_updating(self):
        # Check initialial conditions
        correct_T1, correct_T2, correct_T1_out, correct_T2_out = self.compute_Ti(self.G, self.G)

        assert correct_T1 == self.T1
        assert correct_T2 == self.T2
        assert correct_T1_out == self.T1_out
        assert correct_T2_out == self.T2_out

        # Gradually update the mapping until all nodes are mapped, and validate the Ti updating
        for node in self.G.nodes():
            self.mapping.update({node: node})
            self.reverse_mapping.update({node: node})

            correct_T1, correct_T2, correct_T1_out, correct_T2_out = self.compute_Ti(self.G, self.G)
            self.T1, self.T2, self.T1_out, self.T2_out = update_Tinout(self.G, self.G, self.T1, self.T2, self.T1_out,
                                                                       self.T2_out, node, node, self.mapping,
                                                                       self.reverse_mapping)
            assert correct_T1 == self.T1
            assert correct_T2 == self.T2
            assert correct_T1_out == self.T1_out
            assert correct_T2_out == self.T2_out
