from math import isclose
from operator import eq

import pytest

import networkx as nx
from networkx.algorithms import isomorphism as iso


@pytest.mark.parametrize(
    "nm",
    [
        (iso.categorical_node_match(["x", "y", "z"], [None] * 3)),
        (iso.numerical_node_match(["x", "y", "z"], [None] * 3)),
    ],
)
def test_node_match(nm):
    assert nm(dict(x=1, y=2, z=3), dict(x=1, y=2, z=3))
    assert not nm(dict(x=1, y=2, z=2), dict(x=1, y=2, z=1))


@pytest.mark.parametrize(
    "full_match, flow_match, min_flow_match, id_match",
    [
        (
            iso.generic_multiedge_match(
                ["id", "flowMin", "flowMax"], [None] * 3, [eq] * 3
            ),
            iso.generic_multiedge_match(["flowMin", "flowMax"], [None] * 2, [eq] * 2),
            iso.generic_multiedge_match("flowMin", None, eq),
            iso.generic_multiedge_match("id", None, eq),
        ),
        (
            iso.numerical_multiedge_match(["id", "flowMin", "flowMax"], [3] * 3),
            iso.numerical_multiedge_match(["flowMin", "flowMax"], [4, 5]),
            iso.numerical_multiedge_match("flowMin", 1.6),
            iso.numerical_multiedge_match("id", 1.7),
        ),
    ],
)
class TestMultiEdgeMatch:
    def setup(self):
        self.G1 = nx.MultiDiGraph()
        self.G2 = nx.MultiDiGraph()
        self.G3 = nx.MultiDiGraph()
        self.G4 = nx.MultiDiGraph()
        attr_dict1 = {"id": 3, "minFlow": 0, "maxFlow": 10}
        attr_dict2 = {"id": 4, "minFlow": -3, "maxFlow": 7}
        attr_dict3 = {"id": 5, "minFlow": 13, "maxFlow": 117}
        attr_dict4 = {"id": 6, "minFlow": 13, "maxFlow": 117}
        attr_dict5 = {"id": 7, "minFlow": 8, "maxFlow": 12}
        attr_dict6 = {"id": 8, "minFlow": 8, "maxFlow": 12}
        for attr_dict in [
            attr_dict1,
            attr_dict2,
            attr_dict3,
            attr_dict4,
            attr_dict5,
            attr_dict6,
        ]:
            self.G1.add_edge(1, 2, **attr_dict)
        for attr_dict in [
            attr_dict5,
            attr_dict3,
            attr_dict6,
            attr_dict1,
            attr_dict4,
            attr_dict2,
        ]:
            self.G2.add_edge(2, 3, **attr_dict)
        for attr_dict in [attr_dict3, attr_dict5]:
            self.G3.add_edge(3, 4, **attr_dict)
        for attr_dict in [attr_dict6, attr_dict4]:
            self.G4.add_edge(4, 5, **attr_dict)

    def test_multiedge_match(self, full_match, flow_match, min_flow_match, id_match):
        assert flow_match(self.G1[1][2], self.G2[2][3])
        assert min_flow_match(self.G1[1][2], self.G2[2][3])
        assert id_match(self.G1[1][2], self.G2[2][3])
        assert full_match(self.G1[1][2], self.G2[2][3])
        assert flow_match(self.G3[3][4], self.G4[4][5])
        assert min_flow_match(self.G3[3][4], self.G4[4][5])
        assert not id_match(self.G3[3][4], self.G4[4][5])
        assert not full_match(self.G3[3][4], self.G4[4][5])


def test_generic_node_match():
    nm = iso.generic_node_match("weight", 1.0, isclose)
    assert nm(dict(weight=1.0), dict(weight=1.0))
    assert not nm(dict(weight=1.0), dict(weight=1.1))


def test_generic_node_match_with_list():
    nm = iso.generic_node_match(["weight", "color"], [1.0, "red"], [isclose, eq])
    assert nm(dict(weight=1.0, color="red"), dict(weight=1.0, color="red"))
    assert not nm(dict(weight=1.0, color="red"), dict(weight=1.1, color="red"))
