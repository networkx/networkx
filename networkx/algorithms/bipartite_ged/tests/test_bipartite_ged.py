"""
Test for the GED approximation
"""

import pytest

import networkx as nx
from networkx.algorithms.bipartite_ged.bipartite_ged import BipartiteGED
from networkx.algorithms.bipartite_ged.costfunctions import ConstantCostFunction
from networkx.algorithms.bipartite_ged.tests.test_utils import *

pytest.importorskip("numpy")
pytest.importorskip("scipy")


def test_wrong_mapping_missing_node_u():
    g1, g2 = load_test_graphs()
    bpged = BipartiteGED("const", 1, 1, 1, 1, comp_nodes, comp_edges)
    g12 = {"u1": "v1", "u2": "v2", "u3": None}
    g21 = {"v1": "u1", "v2": "u2", "v3": "u4"}
    with pytest.raises(ValueError):
        bpged._valid_mapping(g12, g21, g1, g2)


def test_wrong_mapping_missing_node_v():
    g1, g2 = load_test_graphs()
    bpged = BipartiteGED("const", 1, 1, 1, 1, comp_nodes, comp_edges)
    g12 = {"u1": "v1", "u2": "v2", "u3": None, "u4": "v3"}
    g21 = {"v1": "u1", "v3": "u4"}
    with pytest.raises(ValueError):
        bpged._valid_mapping(g12, g21, g1, g2)


def test_wrong_mapping_extra_node_u():
    g1, g2 = load_test_graphs()
    bpged = BipartiteGED("const", 1, 1, 1, 1, comp_nodes, comp_edges)
    g12 = {"u1": "v1", "u2": "v2", "u3": None, "u4": "v3", "u5": None}
    g21 = {"v1": "u1", "v2": "u2", "v3": "u4"}
    with pytest.raises(KeyError):
        bpged._valid_mapping(g12, g21, g1, g2)


def test_wrong_mapping_extra_node_v():
    g1, g2 = load_test_graphs()
    bpged = BipartiteGED("const", 1, 1, 1, 1, comp_nodes, comp_edges)
    g12 = {"u1": "v1", "u2": "v2", "u3": None, "u4": "v3"}
    g21 = {"v1": "u1", "v2": "u2", "v3": "u4", "v4": None}
    with pytest.raises(KeyError):
        bpged._valid_mapping(g12, g21, g1, g2)


def test_wrong_mapping_asymetric():
    g1, g2 = load_test_graphs()
    bpged = BipartiteGED("const", 1, 1, 1, 1, comp_nodes, comp_edges)
    g12 = {"u1": "v1", "u2": "v2", "u3": "v3", "u4": None}
    g21 = {"v1": "u1", "v2": "u2", "v3": "u4"}
    with pytest.raises(ValueError):
        bpged._valid_mapping(g12, g21, g1, g2)


def test_ged():
    g1, g2 = load_test_graphs()
    bpged = BipartiteGED("const", 1, 1, 1, 1, comp_nodes, comp_edges)
    g12 = {"u1": "v1", "u2": "v2", "u3": None, "u4": "v3"}
    g21 = {"v1": "u1", "v2": "u2", "v3": "u4"}
    assert bpged.ged(g1, g2, g12, g21) == 4


def test_ged_empty_graphs():
    bpged = BipartiteGED()
    assert bpged.ged(nx.Graph(), nx.Graph()) == 0


def test_invalid_cf():
    with pytest.raises(ValueError):
        BipartiteGED("invalid_cf")


def test_invalid_solver():
    with pytest.raises(ValueError):
        BipartiteGED(solver="invalid_colver")


def test_invalid_substitution_cost():
    with pytest.raises(ValueError):
        BipartiteGED(cns=-1)


def test_invalid_deletion_cost():
    with pytest.raises(ValueError):
        BipartiteGED(cni=0)
