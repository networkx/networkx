"""Unit tests for low conductance cut"""

import math

import pytest

import networkx as nx
from networkx.algorithms.spectral.low_conductance_cut import lowest_conductance_cut

np = pytest.importorskip("numpy")
sp = pytest.importorskip("scipy")

_seed = np.random.RandomState(42)


def test_low_conductance_cut_barbell_balanced():
    G = nx.barbell_graph(30, 5)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.007, "_s", "_t", _seed=_seed)

    assert nx.conductance(G, S, T) <= 0.007 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_lolipop_balanced():
    G = nx.lollipop_graph(30, 10)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.3, "_s", "_t", _seed=_seed)

    assert nx.conductance(G, S, T) <= 0.3 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_expander_balanced():
    G = nx.margulis_gabber_galil_graph(20)
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t", _seed=_seed)

    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_near_expander_balanced():
    G = nx.margulis_gabber_galil_graph(20)
    G.add_edge("a", "b")
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.005, "_s", "_t", _seed=_seed)
    assert S == {"a", "b"}
    assert nx.volume(G, S) < m / 10 / math.log(m) ** 2
    assert nx.conductance(G, S, T) < 0.005 * math.log(m) ** 2


def test_low_conductance_cut_barbell_unbalanced():
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
        G,
        0.02,
        "_s",
        "_t",
        _seed=_seed,
        strategy="unbalanced",
        t_const=200,
        t_slope=20.2,
    )

    assert nx.conductance(G, S, T) <= 0.02 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_lolipop_unbalanced():
    G = nx.lollipop_graph(30, 10)
    m = len(G.edges())
    S, T = lowest_conductance_cut(
        G,
        0.3,
        "_s",
        "_t",
        _seed=_seed,
        strategy="unbalanced",
        t_const=170,
        t_slope=17.2,
    )

    assert nx.conductance(G, S, T) <= 0.3 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_expander_unbalanced():
    G = nx.margulis_gabber_galil_graph(20)
    S, T = lowest_conductance_cut(
        G, 0.005, "_s", "_t", _seed=_seed, strategy="unbalanced"
    )

    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_near_expander_unbalanced():
    G = nx.margulis_gabber_galil_graph(20)
    G.add_edge("a", "b")
    m = len(G.edges())
    S, T = lowest_conductance_cut(
        G,
        0.005,
        "_s",
        "_t",
        _seed=_seed,
        strategy="unbalanced",
        t_const=170,
        t_slope=17.2,
    )
    assert S == {"a", "b"}
    assert nx.volume(G, S) < m / 10 / math.log(m) ** 2
    assert nx.conductance(G, S, T) < 0.005 * math.log(m) ** 2


def test_low_conductance_cut_high_balance():
    G = nx.ladder_graph(50)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.14, "_s", "_t", _seed=_seed, b=0.45)

    assert nx.conductance(G, S, T) <= 0.14 * math.log(m) ** 2
    assert nx.volume(G, S) > 0.225 * (2 * m)
    assert S.union(T) == set(G)


def test_low_conductance_cut_single_candidate():
    G = nx.ladder_graph(50)
    m = len(G.edges())
    S, T = lowest_conductance_cut(G, 0.08, "_s", "_t", _seed=_seed, num_candidates=1)

    assert nx.conductance(G, S, T) <= 0.08 * math.log(m) ** 2
    assert nx.volume(G, S) > m / 10 / math.log(m) ** 2
    assert S.union(T) == set(G)


def test_low_conductance_cut_single_candidate_expander():
    G = nx.margulis_gabber_galil_graph(20)
    S, T = lowest_conductance_cut(G, 0.01, "_s", "_t", _seed=_seed, num_candidates=1)

    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_no_edges():
    G = nx.trivial_graph()
    S, T = lowest_conductance_cut(G, 0.01, "_s", "_t", _seed=_seed)
    assert len(S) == 0
    assert T == set(G)


def test_low_conductance_cut_negative_t_factor():
    G = nx.complete_graph(20)
    pytest.raises(
        nx.NetworkXError,
        lowest_conductance_cut,
        G,
        0.005,
        "_s",
        "_t",
        _seed=_seed,
        t_slope=-1,
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
        _seed=_seed,
        t_const=-100,
        t_slope=1,
    )


def test_low_conductance_cut_bad_source_key():
    G = nx.complete_graph(10)
    pytest.raises(
        nx.NetworkXError, lowest_conductance_cut, G, 0.005, 0, "_t", _seed=_seed
    )


def test_low_conductance_cut_bad_target_key():
    G = nx.complete_graph(10)
    pytest.raises(
        nx.NetworkXError, lowest_conductance_cut, G, 0.005, "_s", 0, _seed=_seed
    )


def test_low_conductance_cut_bad_subdiv_format():
    G = nx.complete_graph(10)
    pytest.raises(
        nx.NetworkXError,
        lowest_conductance_cut,
        G,
        0.005,
        "_s",
        "_t",
        _seed=_seed,
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
        _seed=_seed,
        strategy="unsupported",
    )


def test_low_conductance_cut_bad_balance():
    G = nx.complete_graph(10)
    pytest.raises(
        nx.NetworkXError,
        lowest_conductance_cut,
        G,
        0.005,
        "_s",
        "_t",
        _seed=_seed,
        b=1.3,
    )
