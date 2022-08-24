import utils

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import _GraphParameters, _StateParameters
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
        m = dict()
        m_rev = dict()
        T1, T2, T1out, T2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)

        assert T1 == T2 == set()
        assert T1out == set(self.G1.nodes())
        assert T2out == set(self.G2.nodes())

        gparams = _GraphParameters(self.G1, self.G2, {}, {}, {}, {}, {})
        sparams = _StateParameters(m, m_rev, T1, T1out, T2, T2out)

        # Add node to the mapping
        m.update({4: self.mapped[4]})
        m_rev.update({self.mapped[4]: 4})
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _update_Tinout(4, self.mapped[4], gparams, sparams)

        assert t1 == T1 == {3, 5, 9}
        assert t2 == T2 == {"c", "i", "e"}
        assert t1out == T1out == {0, 1, 2, 6, 7, 8}
        assert t2out == T2out == {"x", "a", "b", "f", "g", "h"}

        # Add node to the mapping
        m.update({5: self.mapped[5]})
        m_rev.update({self.mapped[5]: 5})
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _update_Tinout(5, self.mapped[5], gparams, sparams)

        assert t1 == T1 == {3, 9, 8, 7}
        assert t2 == T2 == {"c", "i", "h", "g"}
        assert t1out == T1out == {0, 1, 2, 6}
        assert t2out == T2out == {"x", "a", "b", "f"}

        # Add node to the mapping
        m.update({6: self.mapped[6]})
        m_rev.update({self.mapped[6]: 6})
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _update_Tinout(6, self.mapped[6], gparams, sparams)

        assert t1 == T1 == {3, 9, 8, 7}
        assert t2 == T2 == {"c", "i", "h", "g"}
        assert t1out == T1out == {0, 1, 2}
        assert t2out == T2out == {"x", "a", "b"}

        # Add node to the mapping
        m.update({3: self.mapped[3]})
        m_rev.update({self.mapped[3]: 3})
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _update_Tinout(3, self.mapped[3], gparams, sparams)

        assert t1 == T1 == {1, 2, 9, 8, 7}
        assert t2 == T2 == {"a", "b", "i", "h", "g"}
        assert t1out == T1out == {0}
        assert t2out == T2out == {"x"}

        # Add node to the mapping
        m.update({0: self.mapped[0]})
        m_rev.update({self.mapped[0]: 0})
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _update_Tinout(0, self.mapped[0], gparams, sparams)

        assert t1 == T1 == {1, 2, 9, 8, 7}
        assert t2 == T2 == {"a", "b", "i", "h", "g"}
        assert t1out == T1out == set()
        assert t2out == T2out == set()

    def test_restoring(self):
        m = {0: "x", 3: "c", 4: "d", 5: "e", 6: "f"}
        m_rev = {"x": 0, "c": 3, "d": 4, "e": 5, "f": 6}
        T1, T2, T1out, T2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)

        assert T1 == {1, 2, 7, 9, 8}
        assert T2 == {"a", "b", "g", "i", "h"}
        assert T1out == set()
        assert T2out == set()

        gparams = _GraphParameters(self.G1, self.G2, {}, {}, {}, {}, {})
        sparams = _StateParameters(m, m_rev, T1, T1out, T2, T2out)

        # Remove a node from the mapping
        m.pop(0)
        m_rev.pop("x")
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _restore_Tinout(0, self.mapped[0], gparams, sparams)

        assert t1 == T1 == {1, 2, 7, 9, 8}
        assert t2 == T2 == {"a", "b", "g", "i", "h"}
        assert t1out == T1out == {0}
        assert t2out == T2out == {"x"}

        # Remove a node from the mapping
        m.pop(6)
        m_rev.pop("f")
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _restore_Tinout(6, self.mapped[6], gparams, sparams)

        assert t1 == T1 == {1, 2, 7, 9, 8}
        assert t2 == T2 == {"a", "b", "g", "i", "h"}
        assert t1out == T1out == {0, 6}
        assert t2out == T2out == {"x", "f"}

        # Remove a node from the mapping
        m.pop(3)
        m_rev.pop("c")
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _restore_Tinout(3, self.mapped[3], gparams, sparams)

        assert t1 == T1 == {7, 9, 8, 3}
        assert t2 == T2 == {"g", "i", "h", "c"}
        assert t1out == T1out == {0, 6, 1, 2}
        assert t2out == T2out == {"x", "f", "a", "b"}

        # Remove a node from the mapping
        m.pop(5)
        m_rev.pop("e")
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _restore_Tinout(5, self.mapped[5], gparams, sparams)

        assert t1 == T1 == {9, 3, 5}
        assert t2 == T2 == {"i", "c", "e"}
        assert t1out == T1out == {0, 6, 1, 2, 7, 8}
        assert t2out == T2out == {"x", "f", "a", "b", "g", "h"}

        # Remove a node from the mapping
        m.pop(4)
        m_rev.pop("d")
        t1, t2, t1out, t2out = utils.compute_Ti(self.G1, self.G2, m, m_rev)
        _restore_Tinout(4, self.mapped[4], gparams, sparams)

        assert t1 == T1 == set()
        assert t2 == T2 == set()
        assert t1out == T1out == set(self.G1.nodes())
        assert t2out == T2out == set(self.G2.nodes())
