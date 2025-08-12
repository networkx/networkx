"""Unit tests for low conductance cut"""

import math

import pytest

import networkx as nx
from networkx.algorithms.spectral.low_conductance_cut import lowest_conductance_cut


def test_low_conductance_cut_barbell_balanced():
    G = nx.barbell_graph(30, 5)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t")

    assert nx.conductance(G, S, T) <= 0.005
    assert len(S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_lolipop_balanced():
    G = nx.lollipop_graph(30, 10)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t")

    assert nx.conductance(G, S, T) <= 0.005
    assert len(S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_expander_balanced():
    G = nx.margulis_gabber_galil_graph(20)
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t")

    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_near_expander_balanced():
    G = nx.margulis_gabber_galil_graph(20)
    G.add_edges_from(
        [
            ("x", 2),
            ("x", 4),
            ("x", 8),
            ("y", 3),
            ("y", 5),
            ("y", 7),
            ("y", 9),
            ("x", "y"),
        ]
    )
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t")
    assert S == {"x", "y"}


def test_low_conductance_cut_barbell_unbalanced():
    G = nx.barbell_graph(30, 5)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t", strategy="unbalanced")

    assert nx.conductance(G, S, T) <= 0.005
    assert len(S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_lolipop_unbalanced():
    G = nx.lollipop_graph(30, 10)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t", strategy="unbalanced")

    assert nx.conductance(G, S, T) <= 0.005
    assert len(S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_expander_unbalanced():
    G = nx.margulis_gabber_galil_graph(20)
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t", strategy="unbalanced")

    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_near_expander_unbalanced():
    G = nx.margulis_gabber_galil_graph(20)
    G.add_edges_from(
        [
            ("x", 2),
            ("x", 4),
            ("x", 8),
            ("y", 3),
            ("y", 5),
            ("y", 7),
            ("y", 9),
            ("x", "y"),
        ]
    )
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t", strategy="unbalanced")
    assert S == {"x", "y"}


def test_low_conductance_cut_high_balance():
    G = nx.ladder_graph(50)
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t", b=0.45)

    assert nx.conductance(G, S, T) <= 0.005
    assert len(S) > 45
    assert S.union(T) == set(G)


def test_low_conductance_cut_single_candidate():
    G = nx.ladder_graph(50)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.01, "_s", "_t", num_candidates=1)

    assert nx.conductance(G, S, T) <= 0.01
    assert len(S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_single_candidate_expander():
    G = nx.margulis_gabber_galil_graph(20)
    S, T = lowest_conductance_cut(G, 0.01, "_s", "_t", num_candidates=1)

    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_no_edges():
    G = nx.trivial_graph()
    pytest.raises(nx.NetworkXError, lowest_conductance_cut, G, 0.005, "_s", "_t")


def test_low_conductance_cut_negative_t_factor():
    G = nx.complete_graph(20)
    pytest.raises(
        nx.NetworkXError, lowest_conductance_cut, G, 0.005, "_s", "_t", t_slope=-1
    )


def test_low_conductance_cut_negative_t_value():
    G = nx.complete_graph(20)
    pytest.raises(
        nx.NetworkXError,
        lowest_conductance_cut,
        G,
        0.005,
        "_s",
        "_t",
        t_const=-100,
        t_slope=1,
    )


def test_low_conductance_cut_bad_source_key():
    G = nx.complete_graph(10)
    pytest.raises(nx.NetworkXError, lowest_conductance_cut, G, 0.005, 0, "_t")


def test_low_conductance_cut_bad_target_key():
    G = nx.complete_graph(10)
    pytest.raises(nx.NetworkXError, lowest_conductance_cut, G, 0.005, "_s", 0)


def test_low_conductance_cut_bad_subdiv_format():
    G = nx.complete_graph(10)
    pytest.raises(
        nx.NetworkXError,
        lowest_conductance_cut,
        G,
        0.005,
        "_s",
        "_t",
        subdiv_node_format="format",
    )


def test_low_conductance_cut_bad_strategy():
    G = nx.complete_graph(10)
    pytest.raises(
        nx.NetworkXError,
        lowest_conductance_cut,
        G,
        0.005,
        "_s",
        "_t",
        strategy="unsupported",
    )


def test_low_conductance_cut_bad_balance():
    G = nx.complete_graph(10)
    pytest.raises(nx.NetworkXError, lowest_conductance_cut, G, 0.005, "_s", "_t", b=1.3)
