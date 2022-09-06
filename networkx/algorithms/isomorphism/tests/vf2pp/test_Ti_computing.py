import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import (
    _GraphParameters,
    _initialize_parameters,
    _StateParameters,
)
from networkx.algorithms.isomorphism.vf2pp_helpers.state import (
    _restore_Tinout,
    _update_Tinout,
)


class TestTinoutUpdating:
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
        gparams, sparams = _initialize_parameters(self.G1, self.G2)
        m, m_rev, T1, T1_tilde, T2, T2_tilde = sparams

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
        sparams = _StateParameters(m, m_rev, T1, T1_tilde, T2, T2_tilde)

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
