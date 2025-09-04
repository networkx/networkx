"""Unit tests for low conductance cut"""

import math

import pytest

import networkx as nx
from networkx.algorithms.spectral.low_conductance_cut import lowest_conductance_cut


def test_low_conductance_cut_barbell_balanced():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.barbell_graph(30, 5)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.007, "_s", "_t")

    assert nx.conductance(G, S, T) <= 0.007 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_lolipop_balanced():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.lollipop_graph(30, 10)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.3, "_s", "_t")

    assert nx.conductance(G, S, T) <= 0.3 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_expander_balanced():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.margulis_gabber_galil_graph(20)
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t")

    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_near_expander_balanced():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.margulis_gabber_galil_graph(20)
    G.add_edge("a", "b")
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t")
    assert S == {"a", "b"}
    assert nx.volume(G, S) < m / 10 / math.log(m) ** 2
    assert nx.conductance(G, S, T) < 0.005 * math.log(m) ** 2


def test_low_conductance_cut_barbell_unbalanced():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    """As the unbalanced strategy mixes much more slowly than the balanced strategy,
    we need to adjust the values of t_const and t_slope in order to get the
    expected behaviour. The barbell graph mixes especially slowly, so the values
    emperically determined in Isaac Arvestad's thesis (170, 17.2) are sometimes
    insufficient. The value of allpha isn't the same as in the balanced case for
    the sake of the running time.
    """
    G = nx.barbell_graph(30, 5)
    m = len(G.edges())
    S, T = lowest_conductance_cut(
        G, 0.02, "_s", "_t", strategy="unbalanced", t_const=200, t_slope=20.2
    )

    assert nx.conductance(G, S, T) <= 0.02 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_lolipop_unbalanced():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.lollipop_graph(30, 10)
    m = len(G.edges())
    S, T = lowest_conductance_cut(
        G, 0.3, "_s", "_t", strategy="unbalanced", t_const=170, t_slope=17.2
    )

    assert nx.conductance(G, S, T) <= 0.3 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_expander_unbalanced():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.margulis_gabber_galil_graph(20)
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t", strategy="unbalanced")

    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_near_expander_unbalanced():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.margulis_gabber_galil_graph(20)
    G.add_edge("a", "b")
    m = len(G.edges())
    S, T = lowest_conductance_cut(
        G, 0.005, "_s", "_t", strategy="unbalanced", t_const=170, t_slope=17.2
    )
    assert S == {"a", "b"}
    assert nx.volume(G, S) < m / 10 / math.log(m) ** 2
    assert nx.conductance(G, S, T) < 0.005 * math.log(m) ** 2


def test_low_conductance_cut_high_balance():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.ladder_graph(50)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.14, "_s", "_t", b=0.45)

    assert nx.conductance(G, S, T) <= 0.14 * math.log(m) ** 2
    assert nx.volume(G, S) > 0.225 * (2 * m)
    assert S.union(T) == set(G)


def test_low_conductance_cut_single_candidate():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.ladder_graph(50)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.08, "_s", "_t", num_candidates=1)

    assert nx.conductance(G, S, T) <= 0.08 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_single_candidate_expander():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.margulis_gabber_galil_graph(20)
    S, T = lowest_conductance_cut(G, 0.01, "_s", "_t", num_candidates=1)

    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_no_edges():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.trivial_graph()
    S, T = lowest_conductance_cut(G, 0.01, "_s", "_t")
    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_negative_t_factor():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.complete_graph(20)
    pytest.raises(
        nx.NetworkXError, lowest_conductance_cut, G, 0.005, "_s", "_t", t_slope=-1
    )


def test_low_conductance_cut_negative_t_value():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
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
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.complete_graph(10)
    pytest.raises(nx.NetworkXError, lowest_conductance_cut, G, 0.005, 0, "_t")


def test_low_conductance_cut_bad_target_key():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.complete_graph(10)
    pytest.raises(nx.NetworkXError, lowest_conductance_cut, G, 0.005, "_s", 0)


def test_low_conductance_cut_bad_subdiv_format():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
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
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
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
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    G = nx.complete_graph(10)
    pytest.raises(nx.NetworkXError, lowest_conductance_cut, G, 0.005, "_s", "_t", b=1.3)
