from operator import eq

import pytest

import networkx as nx
from networkx.algorithms import isomorphism as iso


# NODE_MATCH TESTS
def test_node_match_to_label_uniform():
    G = nx.path_graph(9)

    def node_match(n1d, n2d):
        return True

    iso.node_match_to_label(node_match, G, "labels")
    labels_dict = nx.get_node_attributes(G, "labels")
    assert labels_dict == {n: 0 for n in G}


def test_node_match_to_label_simple_attribute():
    G = nx.path_graph(9)
    nx.set_node_attributes(G, {n: n % 2 for n in G}, "parity")

    def node_match(n1d, n2d):
        return n1d["parity"] == n2d["parity"]

    iso.node_match_to_label(node_match, G, "new_parity")
    labels_dict = nx.get_node_attributes(G, "new_parity")
    assert labels_dict == nx.get_node_attributes(G, "parity")


def test_node_match_to_label_two_attributes():
    G = nx.path_graph(9)
    nx.set_node_attributes(G, {n: n % 2 for n in G}, "parity")
    nx.set_node_attributes(G, {n: n < 4 for n in G}, "small")

    def node_match(n1d, n2d):
        return n1d["parity"] == n2d["parity"] and n1d["small"] == n2d["small"]

    iso.node_match_to_label(node_match, G, "label")
    labels_dict = nx.get_node_attributes(G, "label")
    assert labels_dict == {0: 0, 1: 1, 2: 0, 3: 1, 4: 2, 5: 3, 6: 2, 7: 3, 8: 2}


# EDGE_MATCH TESTS
def test_edge_match_to_label_uniform():
    G = nx.path_graph(9)

    def edge_match(e1d, e2d):
        return True

    iso.edge_match_to_label(edge_match, G, "labels")
    labels_dict = nx.get_edge_attributes(G, "labels")
    assert labels_dict == {e: 0 for e in G.edges}


def test_edge_match_to_label_simple_attribute():
    G = nx.path_graph(9)
    nx.set_edge_attributes(G, {e: 1 - (sum(e) % 2) for e in G.edges}, "parity")

    def edge_match(e1d, e2d):
        return e1d["parity"] == e2d["parity"]

    iso.edge_match_to_label(edge_match, G, "new_parity")
    labels_dict = nx.get_edge_attributes(G, "new_parity")
    assert labels_dict == nx.get_edge_attributes(G, "parity")


def test_edge_match_to_label_two_attributes():
    G = nx.path_graph(9)
    nx.set_edge_attributes(G, {e: (sum(e) % 4) // 2 for e in G.edges}, "parity")
    nx.set_edge_attributes(G, {e: sum(e) < 9 for e in G.edges}, "small")

    def edge_match(e1d, e2d):
        return e1d["parity"] == e2d["parity"] and e1d["small"] == e2d["small"]

    iso.edge_match_to_label(edge_match, G, "combined")
    labels_dict = nx.get_edge_attributes(G, "combined")
    assert labels_dict == {
        (0, 1): 0,
        (1, 2): 1,
        (2, 3): 0,
        (3, 4): 1,
        (4, 5): 2,
        (5, 6): 3,
        (6, 7): 2,
        (7, 8): 3,
    }


# TEST NODE_MATCH Creation functions
def test_categorical_node_match():
    nm = iso.categorical_node_match(["x", "y", "z"], [None] * 3)
    assert nm({"x": 1, "y": 2, "z": 3}, {"x": 1, "y": 2, "z": 3})
    assert not nm({"x": 1, "y": 2, "z": 2}, {"x": 1, "y": 2, "z": 1})


# TEST MULTIEDGE_MATCH Creation functions
class TestGenericMultiEdgeMatch:
    def setup_method(self):
        self.G1 = nx.MultiDiGraph()
        self.G2 = nx.MultiDiGraph()
        self.G3 = nx.MultiDiGraph()
        self.G4 = nx.MultiDiGraph()
        attr_dict1 = {"id": "edge1", "minFlow": 0, "maxFlow": 10}
        attr_dict2 = {"id": "edge2", "minFlow": -3, "maxFlow": 7}
        attr_dict3 = {"id": "edge3", "minFlow": 13, "maxFlow": 117}
        attr_dict4 = {"id": "edge4", "minFlow": 13, "maxFlow": 117}
        attr_dict5 = {"id": "edge5", "minFlow": 8, "maxFlow": 12}
        attr_dict6 = {"id": "edge6", "minFlow": 8, "maxFlow": 12}
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

    def test_generic_multiedge_match(self):
        full_match = iso.generic_multiedge_match(
            ["id", "flowMin", "flowMax"], [None] * 3, [eq] * 3
        )
        flow_match = iso.generic_multiedge_match(
            ["flowMin", "flowMax"], [None] * 2, [eq] * 2
        )
        min_flow_match = iso.generic_multiedge_match("flowMin", None, eq)
        id_match = iso.generic_multiedge_match("id", None, eq)
        assert flow_match(self.G1[1][2], self.G2[2][3])
        assert min_flow_match(self.G1[1][2], self.G2[2][3])
        assert id_match(self.G1[1][2], self.G2[2][3])
        assert full_match(self.G1[1][2], self.G2[2][3])
        assert flow_match(self.G3[3][4], self.G4[4][5])
        assert min_flow_match(self.G3[3][4], self.G4[4][5])
        assert not id_match(self.G3[3][4], self.G4[4][5])
        assert not full_match(self.G3[3][4], self.G4[4][5])
