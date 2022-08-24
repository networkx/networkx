import utils

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import _GraphParameters, _StateParameters
from networkx.algorithms.isomorphism.vf2pp_helpers.candidates import _find_candidates


class TestCandidateSelection:
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

    def test_no_covered_neighbors_no_labels(self):
        l1, l2 = utils.get_labels(
            self.G1,
            self.G2,
        )
        gparams = _GraphParameters(
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
        T1, T2, T1_out, T2_out = utils.compute_Ti(self.G1, self.G2, m, m_rev)

        sparams = _StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 3
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        u = 0
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        m.pop(9)
        m_rev.pop(self.mapped[9])
        T1, T2, T1_out, T2_out = utils.compute_Ti(self.G1, self.G2, m, m_rev)

        sparams = _StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 7
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {
            self.mapped[u],
            self.mapped[8],
            self.mapped[3],
            self.mapped[9],
        }

    def test_no_covered_neighbors_with_labels(self):
        utils.assign_labels(self.G1, self.G2, mapped=self.mapped)
        l1, l2 = utils.get_labels(self.G1, self.G2, has_labels=True)
        gparams = _GraphParameters(
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
        T1, T2, T1_out, T2_out = utils.compute_Ti(self.G1, self.G2, m, m_rev)

        sparams = _StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 3
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        u = 0
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        # Change label of disconnected node
        self.G1.nodes[u]["label"] = "blue"
        l1, l2 = utils.get_labels(self.G1, self.G2, has_labels=True)
        gparams = _GraphParameters(
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
        T1, T2, T1_out, T2_out = utils.compute_Ti(self.G1, self.G2, m, m_rev)

        sparams = _StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 7
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        self.G1.nodes[8]["label"] = self.G1.nodes[7]["label"]
        self.G2.nodes[self.mapped[8]]["label"] = self.G1.nodes[7]["label"]
        l1, l2 = utils.get_labels(self.G1, self.G2, has_labels=True)
        gparams = _GraphParameters(
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

    def test_covered_neighbors_no_labels(self):
        l1, l2 = utils.get_labels(
            self.G1,
            self.G2,
        )
        gparams = _GraphParameters(
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
        T1, T2, T1_out, T2_out = utils.compute_Ti(self.G1, self.G2, m, m_rev)

        sparams = _StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 5
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        u = 6
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u], self.mapped[2]}

    def test_covered_neighbors_with_labels(self):
        utils.assign_labels(self.G1, self.G2, mapped=self.mapped)
        l1, l2 = utils.get_labels(self.G1, self.G2, has_labels=True)
        gparams = _GraphParameters(
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
        T1, T2, T1_out, T2_out = utils.compute_Ti(self.G1, self.G2, m, m_rev)

        sparams = _StateParameters(m, m_rev, T1, T1_out, T2, T2_out)

        u = 5
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        u = 6
        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u]}

        # Assign to 2, the same label as 6
        self.G1.nodes[2]["label"] = self.G1.nodes[u]["label"]
        self.G2.nodes[self.mapped[2]]["label"] = self.G1.nodes[u]["label"]
        l1, l2 = utils.get_labels(self.G1, self.G2, has_labels=True)
        gparams = _GraphParameters(
            self.G1,
            self.G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in self.G2.degree()}),
        )

        candidates = _find_candidates(u, gparams, sparams)
        assert candidates == {self.mapped[u], self.mapped[2]}
