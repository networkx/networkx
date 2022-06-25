class State:
    def __init__(self, G1, G2, u, node_order, mapping, reverse_mapping):
        self.u = u
        self.node_order = node_order
        self.mapping = mapping
        self.reverse_mapping = reverse_mapping

        # todo: store T1 and T2 in the state.
        # todo: should we keep the reverse mapping, instead of using values?
        self.T1 = {nbr for node in mapping for nbr in G1[node] if nbr not in mapping}
        self.T2 = {nbr for node in reverse_mapping for nbr in G2[node] if nbr not in reverse_mapping}

        self.T1_out = {n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in self.T1}
        self.T2_out = {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in self.T2}