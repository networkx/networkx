from operator import eq

import pytest

import networkx as nx
from networkx.algorithms import isomorphism as iso


def test_categorical_node_match():
    nm = iso.categorical_node_match(["x", "y", "z"], None)
    assert nm({"x": 1, "y": 2, "z": 3}, {"x": 1, "y": 2, "z": 3})
    assert not nm({"x": 1, "y": 2, "z": 2}, {"x": 1, "y": 2, "z": 1})


def test_generic_multiedge_match():
    G = nx.MultiDiGraph()

    ad1 = {"id": "edge1", "minFlow": 0, "maxFlow": 10, "pos": (0, 10)}
    ad2 = {"id": "edge2", "minFlow": -3, "maxFlow": 7, "pos": (3, 10)}
    ad3 = {"id": "edge3", "minFlow": 13, "maxFlow": 117, "pos": (13, 17)}
    ad4 = {"id": "edge4", "minFlow": 13, "maxFlow": 117, "pos": (13, 17)}
    ad5 = {"id": "edge5", "minFlow": 8, "maxFlow": 12, "pos": (8, 12)}
    ad6 = {"id": "edge6", "minFlow": 8, "maxFlow": 12, "pos": (8, 12)}

    for attr_dict in [ad1, ad2, ad3, ad4, ad5, ad6]:
        G.add_edge(1, 2, **attr_dict)
    for attr_dict in [ad5, ad3, ad6, ad1, ad4, ad2]:
        G.add_edge(2, 3, **attr_dict)
    for attr_dict in [ad3, ad5]:
        G.add_edge(3, 4, **attr_dict)
    for attr_dict in [ad6, ad4]:
        G.add_edge(4, 5, **attr_dict)

    gmatch = iso.generic_multiedge_match
    id_match = gmatch("id", None, eq)
    full_match = gmatch(["id", "flowMin", "flowMax"], None, eq)
    flow_match = gmatch(["flowMin", "flowMax"], None, eq)
    flow_matcx = gmatch(["flowMin", "flowMax"], [None] * 2, [eq] * 2)
    minf_match = gmatch("flowMin", None, eq)

    def all_eq(x, y):
        return all(a == b for a, b in zip(x, y))

    diffops_id = gmatch(["id", "pos"], None, [eq, all_eq])
    diffops_fl = gmatch(["pos", "flowMin"], None, [all_eq, eq])

    assert id_match(G[1][2], G[2][3])
    assert flow_match(G[1][2], G[2][3])
    assert minf_match(G[1][2], G[2][3])
    assert full_match(G[1][2], G[2][3])
    assert diffops_id(G[1][2], G[2][3])
    assert diffops_fl(G[1][2], G[2][3])

    assert flow_match(G[3][4], G[4][5])
    assert flow_matcx(G[3][4], G[4][5])
    assert minf_match(G[3][4], G[4][5])
    assert diffops_fl(G[3][4], G[4][5])

    assert not id_match(G[3][4], G[4][5])
    assert not full_match(G[3][4], G[4][5])
    assert not diffops_id(G[3][4], G[4][5])


def test_input_length_exceptions():
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.categorical_node_match([0, 1, 2], [None])
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.categorical_node_match([0, 1, 2], [None] * 4)
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.categorical_multiedge_match([0, 1, 2], [None])
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.categorical_multiedge_match([0, 1, 2], [None] * 4)

    with pytest.raises(ValueError, match="zip.. argument "):
        iso.numerical_node_match([0, 1, 2], [None])
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.numerical_node_match([0, 1, 2], [None] * 4)
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.numerical_multiedge_match([0, 1, 2], [None])
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.numerical_multiedge_match([0, 1, 2], [None] * 4)

    # non-lists pass with value spread across attributes
    iso.generic_node_match([0, 1, 2], None, lambda x: x)
    iso.generic_node_match("color", None, lambda x: x)
    iso.generic_node_match("color", [None], [lambda x: x])

    with pytest.raises(ValueError, match="zip.. argument "):
        iso.generic_node_match([0, 1, 2], [None], [lambda x: x] * 3)
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.generic_node_match([0, 1, 2], [None] * 3, [lambda x: x])
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.generic_node_match([0, 1, 2], [None] * 4, [lambda x: x] * 3)
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.generic_node_match([0, 1, 2], [None] * 3, [lambda x: x] * 4)

    # non-lists pass with value spread across attributes
    iso.generic_multiedge_match([0, 1, 2], None, lambda x: x)
    iso.generic_multiedge_match("color", None, lambda x: x)
    iso.generic_multiedge_match("color", [None], [lambda x: x])

    with pytest.raises(ValueError, match="zip.. argument "):
        iso.generic_multiedge_match([0, 1, 2], [None], [lambda x: x] * 3)
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.generic_multiedge_match([0, 1, 2], [None] * 3, [lambda x: x])
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.generic_multiedge_match([0, 1, 2], [None] * 4, [lambda x: x] * 3)
    with pytest.raises(ValueError, match="zip.. argument "):
        iso.generic_multiedge_match([0, 1, 2], [None] * 3, [lambda x: x] * 4)
