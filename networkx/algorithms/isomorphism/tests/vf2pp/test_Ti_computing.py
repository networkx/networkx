import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import (
    _GraphParameters,
    _initialize_parameters,
    _StateParameters,
)
from networkx.algorithms.isomorphism.vf2pp_helpers.state import (
    _restore_Tinout,
    _restore_Tinout_Di,
    _update_Tinout,
)


class TestGraphTinoutUpdating:
    edges = [
        (1, 3),
        (2, 3),
        (3, 4),
        (4, 9),
        (4, 5),
        (3, 9),
        (5, 8),
        (5, 7),
        (8, 7),
        (6, 7),
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
    G1 = nx.Graph()
    G1.add_edges_from(edges)
    G1.add_node(0)
    G2 = nx.relabel_nodes(G1, mapping=mapped)

    def test_updating(self):
        G2_degree = dict(self.G2.degree)
        gparams, sparams = _initialize_parameters(self.G1, self.G2, G2_degree)
        m, m_rev, T1, _, T1_tilde, _, T2, _, T2_tilde, _ = sparams

        # Add node to the mapping
        m[4] = self.mapped[4]
        m_rev[self.mapped[4]] = 4
        _update_Tinout(4, self.mapped[4], gparams, sparams)

        assert T1 == {3, 5, 9}
        assert T2 == {"c", "i", "e"}
        assert T1_tilde == {0, 1, 2, 6, 7, 8}
        assert T2_tilde == {"x", "a", "b", "f", "g", "h"}

        # Add node to the mapping
        m[5] = self.mapped[5]
        m_rev.update({self.mapped[5]: 5})
        _update_Tinout(5, self.mapped[5], gparams, sparams)

        assert T1 == {3, 9, 8, 7}
        assert T2 == {"c", "i", "h", "g"}
        assert T1_tilde == {0, 1, 2, 6}
        assert T2_tilde == {"x", "a", "b", "f"}

        # Add node to the mapping
        m[6] = self.mapped[6]
        m_rev.update({self.mapped[6]: 6})
        _update_Tinout(6, self.mapped[6], gparams, sparams)

        assert T1 == {3, 9, 8, 7}
        assert T2 == {"c", "i", "h", "g"}
        assert T1_tilde == {0, 1, 2}
        assert T2_tilde == {"x", "a", "b"}

        # Add node to the mapping
        m[3] = self.mapped[3]
        m_rev.update({self.mapped[3]: 3})
        _update_Tinout(3, self.mapped[3], gparams, sparams)

        assert T1 == {1, 2, 9, 8, 7}
        assert T2 == {"a", "b", "i", "h", "g"}
        assert T1_tilde == {0}
        assert T2_tilde == {"x"}

        # Add node to the mapping
        m[0] = self.mapped[0]
        m_rev.update({self.mapped[0]: 0})
        _update_Tinout(0, self.mapped[0], gparams, sparams)

        assert T1 == {1, 2, 9, 8, 7}
        assert T2 == {"a", "b", "i", "h", "g"}
        assert T1_tilde == set()
        assert T2_tilde == set()

    def test_restoring(self):
        m = {0: "x", 3: "c", 4: "d", 5: "e", 6: "f"}
        m_rev = {"x": 0, "c": 3, "d": 4, "e": 5, "f": 6}

        T1 = {1, 2, 7, 9, 8}
        T2 = {"a", "b", "g", "i", "h"}
        T1_tilde = set()
        T2_tilde = set()

        gparams = _GraphParameters(self.G1, self.G2, {}, {}, {}, {}, {})
        sparams = _StateParameters(
            m, m_rev, T1, None, T1_tilde, None, T2, None, T2_tilde, None
        )

        # Remove a node from the mapping
        m.pop(0)
        m_rev.pop("x")
        _restore_Tinout(0, self.mapped[0], gparams, sparams)

        assert T1 == {1, 2, 7, 9, 8}
        assert T2 == {"a", "b", "g", "i", "h"}
        assert T1_tilde == {0}
        assert T2_tilde == {"x"}

        # Remove a node from the mapping
        m.pop(6)
        m_rev.pop("f")
        _restore_Tinout(6, self.mapped[6], gparams, sparams)

        assert T1 == {1, 2, 7, 9, 8}
        assert T2 == {"a", "b", "g", "i", "h"}
        assert T1_tilde == {0, 6}
        assert T2_tilde == {"x", "f"}

        # Remove a node from the mapping
        m.pop(3)
        m_rev.pop("c")
        _restore_Tinout(3, self.mapped[3], gparams, sparams)

        assert T1 == {7, 9, 8, 3}
        assert T2 == {"g", "i", "h", "c"}
        assert T1_tilde == {0, 6, 1, 2}
        assert T2_tilde == {"x", "f", "a", "b"}

        # Remove a node from the mapping
        m.pop(5)
        m_rev.pop("e")
        _restore_Tinout(5, self.mapped[5], gparams, sparams)

        assert T1 == {9, 3, 5}
        assert T2 == {"i", "c", "e"}
        assert T1_tilde == {0, 6, 1, 2, 7, 8}
        assert T2_tilde == {"x", "f", "a", "b", "g", "h"}

        # Remove a node from the mapping
        m.pop(4)
        m_rev.pop("d")
        _restore_Tinout(4, self.mapped[4], gparams, sparams)

        assert T1 == set()
        assert T2 == set()
        assert T1_tilde == set(self.G1.nodes())
        assert T2_tilde == set(self.G2.nodes())


class TestDiGraphTinoutUpdating:
    edges = [
        (1, 3),
        (3, 2),
        (3, 4),
        (4, 9),
        (4, 5),
        (3, 9),
        (5, 8),
        (5, 7),
        (8, 7),
        (7, 6),
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
    G1 = nx.DiGraph(edges)
    G1.add_node(0)
    G2 = nx.relabel_nodes(G1, mapping=mapped)

    def test_updating(self):
        G2_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(
                self.G2.in_degree, self.G2.out_degree
            )
        }
        gparams, sparams = _initialize_parameters(self.G1, self.G2, G2_degree)
        m, m_rev, T1_out, T1_in, T1_tilde, _, T2_out, T2_in, T2_tilde, _ = sparams

        # Add node to the mapping
        m[4] = self.mapped[4]
        m_rev[self.mapped[4]] = 4
        _update_Tinout(4, self.mapped[4], gparams, sparams)

        assert T1_out == {5, 9}
        assert T1_in == {3}
        assert T2_out == {"i", "e"}
        assert T2_in == {"c"}
        assert T1_tilde == {0, 1, 2, 6, 7, 8}
        assert T2_tilde == {"x", "a", "b", "f", "g", "h"}

        # Add node to the mapping
        m[5] = self.mapped[5]
        m_rev[self.mapped[5]] = 5
        _update_Tinout(5, self.mapped[5], gparams, sparams)

        assert T1_out == {9, 8, 7}
        assert T1_in == {3}
        assert T2_out == {"i", "g", "h"}
        assert T2_in == {"c"}
        assert T1_tilde == {0, 1, 2, 6}
        assert T2_tilde == {"x", "a", "b", "f"}

        # Add node to the mapping
        m[6] = self.mapped[6]
        m_rev[self.mapped[6]] = 6
        _update_Tinout(6, self.mapped[6], gparams, sparams)

        assert T1_out == {9, 8, 7}
        assert T1_in == {3, 7}
        assert T2_out == {"i", "g", "h"}
        assert T2_in == {"c", "g"}
        assert T1_tilde == {0, 1, 2}
        assert T2_tilde == {"x", "a", "b"}

        # Add node to the mapping
        m[3] = self.mapped[3]
        m_rev[self.mapped[3]] = 3
        _update_Tinout(3, self.mapped[3], gparams, sparams)

        assert T1_out == {9, 8, 7, 2}
        assert T1_in == {7, 1}
        assert T2_out == {"i", "g", "h", "b"}
        assert T2_in == {"g", "a"}
        assert T1_tilde == {0}
        assert T2_tilde == {"x"}

        # Add node to the mapping
        m[0] = self.mapped[0]
        m_rev[self.mapped[0]] = 0
        _update_Tinout(0, self.mapped[0], gparams, sparams)

        assert T1_out == {9, 8, 7, 2}
        assert T1_in == {7, 1}
        assert T2_out == {"i", "g", "h", "b"}
        assert T2_in == {"g", "a"}
        assert T1_tilde == set()
        assert T2_tilde == set()

    def test_restoring(self):
        m = {0: "x", 3: "c", 4: "d", 5: "e", 6: "f"}
        m_rev = {"x": 0, "c": 3, "d": 4, "e": 5, "f": 6}

        T1_out = {2, 7, 9, 8}
        T1_in = {1, 7}
        T2_out = {"b", "g", "i", "h"}
        T2_in = {"a", "g"}
        T1_tilde = set()
        T2_tilde = set()

        gparams = _GraphParameters(self.G1, self.G2, {}, {}, {}, {}, {})
        sparams = _StateParameters(
            m, m_rev, T1_out, T1_in, T1_tilde, None, T2_out, T2_in, T2_tilde, None
        )

        # Remove a node from the mapping
        m.pop(0)
        m_rev.pop("x")
        _restore_Tinout_Di(0, self.mapped[0], gparams, sparams)

        assert T1_out == {2, 7, 9, 8}
        assert T1_in == {1, 7}
        assert T2_out == {"b", "g", "i", "h"}
        assert T2_in == {"a", "g"}
        assert T1_tilde == {0}
        assert T2_tilde == {"x"}

        # Remove a node from the mapping
        m.pop(6)
        m_rev.pop("f")
        _restore_Tinout_Di(6, self.mapped[6], gparams, sparams)

        assert T1_out == {2, 9, 8, 7}
        assert T1_in == {1}
        assert T2_out == {"b", "i", "h", "g"}
        assert T2_in == {"a"}
        assert T1_tilde == {0, 6}
        assert T2_tilde == {"x", "f"}

        # Remove a node from the mapping
        m.pop(3)
        m_rev.pop("c")
        _restore_Tinout_Di(3, self.mapped[3], gparams, sparams)

        assert T1_out == {9, 8, 7}
        assert T1_in == {3}
        assert T2_out == {"i", "h", "g"}
        assert T2_in == {"c"}
        assert T1_tilde == {0, 6, 1, 2}
        assert T2_tilde == {"x", "f", "a", "b"}

        # Remove a node from the mapping
        m.pop(5)
        m_rev.pop("e")
        _restore_Tinout_Di(5, self.mapped[5], gparams, sparams)

        assert T1_out == {9, 5}
        assert T1_in == {3}
        assert T2_out == {"i", "e"}
        assert T2_in == {"c"}
        assert T1_tilde == {0, 6, 1, 2, 8, 7}
        assert T2_tilde == {"x", "f", "a", "b", "h", "g"}

        # Remove a node from the mapping
        m.pop(4)
        m_rev.pop("d")
        _restore_Tinout_Di(4, self.mapped[4], gparams, sparams)

        assert T1_out == set()
        assert T1_in == set()
        assert T2_out == set()
        assert T2_in == set()
        assert T1_tilde == set(self.G1.nodes())
        assert T2_tilde == set(self.G2.nodes())
