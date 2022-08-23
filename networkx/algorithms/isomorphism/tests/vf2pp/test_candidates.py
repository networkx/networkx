import collections

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp_helpers.candidates import _find_candidates


def compute_T(G1, G2, m, m_rev):
    T1 = {n for covered in m for n in G1[covered] if n not in m}
    T2 = {n for covered in m_rev for n in G2[covered] if n not in m_rev}
    T1_out = {n for n in G1.nodes() if n not in T1 and n not in m}
    T2_out = {n for n in G2.nodes() if n not in T2 and n not in m_rev}
    return T1, T2, T1_out, T2_out


class TestCandidateSelection:
    labels = [
        "white",
        "red",
        "blue",
        "green",
        "orange",
        "black",
        "purple",
        "yellow",
        "brown",
        "cyan",
    ]
    G1 = nx.Graph()
    G1_edges = [
        (1, 2),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 4),
        (3, 4),
        (4, 5),
        (1, 6),
        (6, 7),
        (6, 8),
        (8, 9),
        (7, 9),
    ]
    mapped = {
        0: "x",
        1: "a",
        2: "b",
        3: "c",
        4: "d",
        5: "e",
        6: "f",
        7: "g",
        8: "h",
        9: "i",
    }

    G1.add_edges_from(G1_edges)
    G1.add_node(0)
    G2 = nx.relabel_nodes(G1, mapped)

    GraphParameters = collections.namedtuple(
        "GraphParameters",
        [
            "G1",
            "G2",
            "G1_labels",
            "G2_labels",
            "nodes_of_G1Labels",
            "nodes_of_G2Labels",
            "G2_nodes_of_degree",
        ],
    )
    StateParameters = collections.namedtuple(
        "StateParameters",
        ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
    )

    def assign_labels(self):
        for i, n in enumerate(self.G1.nodes()):
            self.G1.nodes[n]["label"] = self.labels[i]
            self.G2.nodes[self.mapped[n]]["label"] = self.labels[i]

    def get_labels(self, has_labels=False):
        if not has_labels:
            G1_labels, G2_labels = {}, {}
            G1_labels.update(self.G1.nodes(data=None, default=-1))
            G2_labels.update(self.G2.nodes(data=None, default=-1))
            return G1_labels, G2_labels

        return (
            nx.get_node_attributes(self.G1, "label"),
            nx.get_node_attributes(self.G2, "label"),
        )

    def test_no_covered_neighbors_no_labels(self):
        l1, l2 = self.get_labels()
        gparams = self.GraphParameters(
            self.G1,
            self.G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in self.G2.degree()}),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}
        T1, T2, T1_out, T2_out = compute_T(self.G1, self.G2, m, m_rev)

        sparams = self.StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 3
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        u = 0
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        m.pop(9)
        m_rev.pop(self.mapped[9])
        T1, T2, T1_out, T2_out = compute_T(self.G1, self.G2, m, m_rev)

        sparams = self.StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 7
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {
            self.mapped[u],
            self.mapped[8],
            self.mapped[3],
            self.mapped[9],
        }

    def test_no_covered_neighbors_with_labels(self):
        self.assign_labels()
        l1, l2 = self.get_labels(has_labels=True)
        gparams = self.GraphParameters(
            self.G1,
            self.G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in self.G2.degree()}),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}
        T1, T2, T1_out, T2_out = compute_T(self.G1, self.G2, m, m_rev)

        sparams = self.StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 3
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        u = 0
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        # Change label of disconnected node
        self.G1.nodes[u]["label"] = "blue"
        l1, l2 = self.get_labels(has_labels=True)
        gparams = self.GraphParameters(
            self.G1,
            self.G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in self.G2.degree()}),
        )

        # No candidate
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == set()

        m.pop(9)
        m_rev.pop(self.mapped[9])
        T1, T2, T1_out, T2_out = compute_T(self.G1, self.G2, m, m_rev)

        sparams = self.StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 7
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        self.G1.nodes[8]["label"] = self.G1.nodes[7]["label"]
        self.G2.nodes[self.mapped[8]]["label"] = self.G1.nodes[7]["label"]
        l1, l2 = self.get_labels(has_labels=True)
        gparams = self.GraphParameters(
            self.G1,
            self.G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in self.G2.degree()}),
        )

        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u], self.mapped[8]}
