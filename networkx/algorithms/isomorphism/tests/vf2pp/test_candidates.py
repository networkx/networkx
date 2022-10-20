import itertools

import utils

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import _GraphParameters, _StateParameters
from networkx.algorithms.isomorphism.vf2pp_helpers.candidates import (
    _find_candidates,
    _find_candidates_Di,
)


class TestGraphCandidateSelection:
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

    def test_no_covered_neighbors_no_labels(self):
        G1 = nx.Graph()
        G1.add_edges_from(self.G1_edges)
        G1.add_node(0)
        G2 = nx.relabel_nodes(G1, self.mapped)

        G1_degree = dict(G1.degree)
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}

        T1 = {7, 8, 2, 4, 5}
        T1_tilde = {0, 3, 6}
        T2 = {"g", "h", "b", "d", "e"}
        T2_tilde = {"x", "c", "f"}

        sparams = _StateParameters(
            m, m_rev, T1, None, T1_tilde, None, T2, None, T2_tilde, None
        )

        u = 3
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        u = 0
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        m.pop(9)
        m_rev.pop(self.mapped[9])

        T1 = {2, 4, 5, 6}
        T1_tilde = {0, 3, 7, 8, 9}
        T2 = {"g", "h", "b", "d", "e", "f"}
        T2_tilde = {"x", "c", "g", "h", "i"}

        sparams = _StateParameters(
            m, m_rev, T1, None, T1_tilde, None, T2, None, T2_tilde, None
        )

        u = 7
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {
            self.mapped[u],
            self.mapped[8],
            self.mapped[3],
            self.mapped[9],
        }

    def test_no_covered_neighbors_with_labels(self):
        G1 = nx.Graph()
        G1.add_edges_from(self.G1_edges)
        G1.add_node(0)
        G2 = nx.relabel_nodes(G1, self.mapped)

        G1_degree = dict(G1.degree)
        nx.set_node_attributes(
            G1,
            dict(zip(G1, itertools.cycle(utils.labels_different))),
            "label",
        )
        nx.set_node_attributes(
            G2,
            dict(
                zip(
                    [self.mapped[n] for n in G1],
                    itertools.cycle(utils.labels_different),
                )
            ),
            "label",
        )
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}

        T1 = {7, 8, 2, 4, 5, 6}
        T1_tilde = {0, 3}
        T2 = {"g", "h", "b", "d", "e", "f"}
        T2_tilde = {"x", "c"}

        sparams = _StateParameters(
            m, m_rev, T1, None, T1_tilde, None, T2, None, T2_tilde, None
        )

        u = 3
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        u = 0
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        # Change label of disconnected node
        G1.nodes[u]["label"] = "blue"
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )

        # No candidate
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == set()

        m.pop(9)
        m_rev.pop(self.mapped[9])

        T1 = {2, 4, 5, 6}
        T1_tilde = {0, 3, 7, 8, 9}
        T2 = {"b", "d", "e", "f"}
        T2_tilde = {"x", "c", "g", "h", "i"}

        sparams = _StateParameters(
            m, m_rev, T1, None, T1_tilde, None, T2, None, T2_tilde, None
        )

        u = 7
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        G1.nodes[8]["label"] = G1.nodes[7]["label"]
        G2.nodes[self.mapped[8]]["label"] = G1.nodes[7]["label"]
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )

        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u], self.mapped[8]}

    def test_covered_neighbors_no_labels(self):
        G1 = nx.Graph()
        G1.add_edges_from(self.G1_edges)
        G1.add_node(0)
        G2 = nx.relabel_nodes(G1, self.mapped)

        G1_degree = dict(G1.degree)
        l1 = dict(G1.nodes(data=None, default=-1))
        l2 = dict(G2.nodes(data=None, default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}

        T1 = {7, 8, 2, 4, 5, 6}
        T1_tilde = {0, 3}
        T2 = {"g", "h", "b", "d", "e", "f"}
        T2_tilde = {"x", "c"}

        sparams = _StateParameters(
            m, m_rev, T1, None, T1_tilde, None, T2, None, T2_tilde, None
        )

        u = 5
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        u = 6
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u], self.mapped[2]}

    def test_covered_neighbors_with_labels(self):
        G1 = nx.Graph()
        G1.add_edges_from(self.G1_edges)
        G1.add_node(0)
        G2 = nx.relabel_nodes(G1, self.mapped)

        G1_degree = dict(G1.degree)
        nx.set_node_attributes(
            G1,
            dict(zip(G1, itertools.cycle(utils.labels_different))),
            "label",
        )
        nx.set_node_attributes(
            G2,
            dict(
                zip(
                    [self.mapped[n] for n in G1],
                    itertools.cycle(utils.labels_different),
                )
            ),
            "label",
        )
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}

        T1 = {7, 8, 2, 4, 5, 6}
        T1_tilde = {0, 3}
        T2 = {"g", "h", "b", "d", "e", "f"}
        T2_tilde = {"x", "c"}

        sparams = _StateParameters(
            m, m_rev, T1, None, T1_tilde, None, T2, None, T2_tilde, None
        )

        u = 5
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        u = 6
        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        # Assign to 2, the same label as 6
        G1.nodes[2]["label"] = G1.nodes[u]["label"]
        G2.nodes[self.mapped[2]]["label"] = G1.nodes[u]["label"]
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups({node: degree for node, degree in G2.degree()}),
        )

        candidates = _find_candidates(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u], self.mapped[2]}


class TestDiGraphCandidateSelection:
    G1_edges = [
        (1, 2),
        (1, 4),
        (5, 1),
        (2, 3),
        (4, 2),
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

    def test_no_covered_neighbors_no_labels(self):
        G1 = nx.DiGraph()
        G1.add_edges_from(self.G1_edges)
        G1.add_node(0)
        G2 = nx.relabel_nodes(G1, self.mapped)

        G1_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(G1.in_degree, G1.out_degree)
        }

        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        G2.in_degree(), G2.out_degree()
                    )
                }
            ),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}

        T1_out = {2, 4, 6}
        T1_in = {5, 7, 8}
        T1_tilde = {0, 3}
        T2_out = {"b", "d", "f"}
        T2_in = {"e", "g", "h"}
        T2_tilde = {"x", "c"}

        sparams = _StateParameters(
            m, m_rev, T1_out, T1_in, T1_tilde, None, T2_out, T2_in, T2_tilde, None
        )

        u = 3
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        u = 0
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        m.pop(9)
        m_rev.pop(self.mapped[9])

        T1_out = {2, 4, 6}
        T1_in = {5}
        T1_tilde = {0, 3, 7, 8, 9}
        T2_out = {"b", "d", "f"}
        T2_in = {"e"}
        T2_tilde = {"x", "c", "g", "h", "i"}

        sparams = _StateParameters(
            m, m_rev, T1_out, T1_in, T1_tilde, None, T2_out, T2_in, T2_tilde, None
        )

        u = 7
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u], self.mapped[8], self.mapped[3]}

    def test_no_covered_neighbors_with_labels(self):
        G1 = nx.DiGraph()
        G1.add_edges_from(self.G1_edges)
        G1.add_node(0)
        G2 = nx.relabel_nodes(G1, self.mapped)

        G1_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(G1.in_degree, G1.out_degree)
        }
        nx.set_node_attributes(
            G1,
            dict(zip(G1, itertools.cycle(utils.labels_different))),
            "label",
        )
        nx.set_node_attributes(
            G2,
            dict(
                zip(
                    [self.mapped[n] for n in G1],
                    itertools.cycle(utils.labels_different),
                )
            ),
            "label",
        )
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        G2.in_degree(), G2.out_degree()
                    )
                }
            ),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}

        T1_out = {2, 4, 6}
        T1_in = {5, 7, 8}
        T1_tilde = {0, 3}
        T2_out = {"b", "d", "f"}
        T2_in = {"e", "g", "h"}
        T2_tilde = {"x", "c"}

        sparams = _StateParameters(
            m, m_rev, T1_out, T1_in, T1_tilde, None, T2_out, T2_in, T2_tilde, None
        )

        u = 3
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        u = 0
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        # Change label of disconnected node
        G1.nodes[u]["label"] = "blue"
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        G2.in_degree(), G2.out_degree()
                    )
                }
            ),
        )

        # No candidate
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == set()

        m.pop(9)
        m_rev.pop(self.mapped[9])

        T1_out = {2, 4, 6}
        T1_in = {5}
        T1_tilde = {0, 3, 7, 8, 9}
        T2_out = {"b", "d", "f"}
        T2_in = {"e"}
        T2_tilde = {"x", "c", "g", "h", "i"}

        sparams = _StateParameters(
            m, m_rev, T1_out, T1_in, T1_tilde, None, T2_out, T2_in, T2_tilde, None
        )

        u = 7
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        G1.nodes[8]["label"] = G1.nodes[7]["label"]
        G2.nodes[self.mapped[8]]["label"] = G1.nodes[7]["label"]
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        G2.in_degree(), G2.out_degree()
                    )
                }
            ),
        )

        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u], self.mapped[8]}

    def test_covered_neighbors_no_labels(self):
        G1 = nx.DiGraph()
        G1.add_edges_from(self.G1_edges)
        G1.add_node(0)
        G2 = nx.relabel_nodes(G1, self.mapped)

        G1_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(G1.in_degree, G1.out_degree)
        }

        l1 = dict(G1.nodes(data=None, default=-1))
        l2 = dict(G2.nodes(data=None, default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        G2.in_degree(), G2.out_degree()
                    )
                }
            ),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}

        T1_out = {2, 4, 6}
        T1_in = {5, 7, 8}
        T1_tilde = {0, 3}
        T2_out = {"b", "d", "f"}
        T2_in = {"e", "g", "h"}
        T2_tilde = {"x", "c"}

        sparams = _StateParameters(
            m, m_rev, T1_out, T1_in, T1_tilde, None, T2_out, T2_in, T2_tilde, None
        )

        u = 5
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        u = 6
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        # Change the direction of an edge to make the degree orientation same as first candidate of u.
        G1.remove_edge(4, 2)
        G1.add_edge(2, 4)
        G2.remove_edge("d", "b")
        G2.add_edge("b", "d")

        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        G2.in_degree(), G2.out_degree()
                    )
                }
            ),
        )

        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u], self.mapped[2]}

    def test_covered_neighbors_with_labels(self):
        G1 = nx.DiGraph()
        G1.add_edges_from(self.G1_edges)
        G1.add_node(0)
        G2 = nx.relabel_nodes(G1, self.mapped)

        G1.remove_edge(4, 2)
        G1.add_edge(2, 4)
        G2.remove_edge("d", "b")
        G2.add_edge("b", "d")

        G1_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(G1.in_degree, G1.out_degree)
        }

        nx.set_node_attributes(
            G1,
            dict(zip(G1, itertools.cycle(utils.labels_different))),
            "label",
        )
        nx.set_node_attributes(
            G2,
            dict(
                zip(
                    [self.mapped[n] for n in G1],
                    itertools.cycle(utils.labels_different),
                )
            ),
            "label",
        )
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        G2.in_degree(), G2.out_degree()
                    )
                }
            ),
        )

        m = {9: self.mapped[9], 1: self.mapped[1]}
        m_rev = {self.mapped[9]: 9, self.mapped[1]: 1}

        T1_out = {2, 4, 6}
        T1_in = {5, 7, 8}
        T1_tilde = {0, 3}
        T2_out = {"b", "d", "f"}
        T2_in = {"e", "g", "h"}
        T2_tilde = {"x", "c"}

        sparams = _StateParameters(
            m, m_rev, T1_out, T1_in, T1_tilde, None, T2_out, T2_in, T2_tilde, None
        )

        u = 5
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        u = 6
        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

        # Assign to 2, the same label as 6
        G1.nodes[2]["label"] = G1.nodes[u]["label"]
        G2.nodes[self.mapped[2]]["label"] = G1.nodes[u]["label"]
        l1 = dict(G1.nodes(data="label", default=-1))
        l2 = dict(G2.nodes(data="label", default=-1))
        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        G2.in_degree(), G2.out_degree()
                    )
                }
            ),
        )

        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u], self.mapped[2]}

        # Change the direction of an edge to make the degree orientation same as first candidate of u.
        G1.remove_edge(2, 4)
        G1.add_edge(4, 2)
        G2.remove_edge("b", "d")
        G2.add_edge("d", "b")

        gparams = _GraphParameters(
            G1,
            G2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        G2.in_degree(), G2.out_degree()
                    )
                }
            ),
        )

        candidates = _find_candidates_Di(u, gparams, sparams, G1_degree)
        assert candidates == {self.mapped[u]}

    def test_same_in_out_degrees_no_candidate(self):
        g1 = nx.DiGraph([(4, 1), (4, 2), (3, 4), (5, 4), (6, 4)])
        g2 = nx.DiGraph([(1, 4), (2, 4), (3, 4), (4, 5), (4, 6)])

        l1 = dict(g1.nodes(data=None, default=-1))
        l2 = dict(g2.nodes(data=None, default=-1))
        gparams = _GraphParameters(
            g1,
            g2,
            l1,
            l2,
            nx.utils.groups(l1),
            nx.utils.groups(l2),
            nx.utils.groups(
                {
                    node: (in_degree, out_degree)
                    for (node, in_degree), (_, out_degree) in zip(
                        g2.in_degree(), g2.out_degree()
                    )
                }
            ),
        )

        g1_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(g1.in_degree, g1.out_degree)
        }

        m = {1: 1, 2: 2, 3: 3}
        m_rev = m.copy()

        T1_out = {4}
        T1_in = {4}
        T1_tilde = {5, 6}
        T2_out = {4}
        T2_in = {4}
        T2_tilde = {5, 6}

        sparams = _StateParameters(
            m, m_rev, T1_out, T1_in, T1_tilde, None, T2_out, T2_in, T2_tilde, None
        )

        u = 4
        # despite the same in and out degree, there's no candidate for u=4
        candidates = _find_candidates_Di(u, gparams, sparams, g1_degree)
        assert candidates == set()
        # Notice how the regular candidate selection method returns wrong result.
        assert _find_candidates(u, gparams, sparams, g1_degree) == {4}
