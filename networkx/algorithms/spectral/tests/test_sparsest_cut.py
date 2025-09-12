"""Unit tests for sparsest"""

import math

import pytest

import networkx as nx
from networkx.algorithms.spectral.sparsest_cut import (
    balanced_sparse_cut,
    sparse_cut,
    sparsest_cut,
)

np = pytest.importorskip("numpy")
sp = pytest.importorskip("scipy")

_seed = np.random.RandomState(42)


def test_sparse_cut_ladder_graph():
    G = nx.ladder_graph(20)
    n = len(G)
    S, T = sparse_cut(G, 1 / 5, "_s", "_t", _seed=_seed)

    assert nx.cut_size(G, S, T) / len(S) < 1 / 5
    assert len(S) > 1 / 12 / math.log(n) ** 2 * n
    assert S.union(T) == set(G)


def test_sparse_cut_barbell_graph():
    G = nx.barbell_graph(40, 1)
    n = len(G)
    S, T = sparse_cut(G, 1 / 5, "_s", "_t", _seed=_seed)

    assert nx.cut_size(G, S, T) / len(S) < 1 / 5
    assert len(S) > 1 / 12 / math.log(n) ** 2 * n
    assert S.union(T) == set(G)


def test_sparse_cut_expander():
    G = nx.gnp_random_graph(100, 0.2)
    S, _ = sparse_cut(G, 15, "_s", "_t", _seed=_seed)

    assert len(S) == 0


def test_sparse_cut_negative_balance():
    G = nx.gnp_random_graph(100, 0.2)
    pytest.raises(nx.NetworkXError, sparse_cut, G, 0.1, "_s", "_t", b=-1, _seed=_seed)


def test_sparse_cut_high_balance():
    G = nx.gnp_random_graph(100, 0.2)
    pytest.raises(nx.NetworkXError, sparse_cut, G, 0.1, "_s", "_t", b=1, _seed=_seed)


def test_sparse_cut_bad_source_key():
    G = nx.gnp_random_graph(100, 0.2)
    pytest.raises(nx.NetworkXError, sparse_cut, G, 0.1, 0, "_t", b=-1, _seed=_seed)


def test_sparse_cut_bad_target_key():
    G = nx.gnp_random_graph(100, 0.2)
    pytest.raises(nx.NetworkXError, sparse_cut, G, 0.1, "_s", 0, b=-1, _seed=_seed)


def test_sparsest_cut_barbell_graph():
    G = nx.barbell_graph(40, 1)
    S, T = sparsest_cut(G, "_s", "_t", _seed=_seed)

    assert nx.cut_size(G, S, T) / len(S) < 0.965
    assert S.union(T) == set(G)


def test_sparsest_cut_ladder_graph():
    G = nx.ladder_graph(50)
    S, T = sparsest_cut(G, "_s", "_t", _seed=_seed)

    assert nx.cut_size(G, S, T) / len(S) < 0.848
    assert S.union(T) == set(G)


def test_balanced_sparse_cut_barbell_graph():
    G = nx.barbell_graph(40, 1)
    S, T = balanced_sparse_cut(G, 1 / 5, "_s", "_t", 1 / 6, _seed=_seed)

    assert nx.edge_expansion(G, S, T) < 1 / 5
    assert len(S) > len(G) // 6


def test_balanced_sparse_cut_ternary_tree():
    G = nx.balanced_tree(3, 6)
    S, T = balanced_sparse_cut(G, 0.18, "_s", "_t", 1 / 4, _seed=_seed)

    assert nx.edge_expansion(G, S, T) < 0.18
    assert len(S) > len(G) // 4


def test_balanced_sparse_cut_random_graph():
    G = nx.gnp_random_graph(400, 0.1)
    S, T = balanced_sparse_cut(G, 0.6, "_s", "_t", 1 / 4, _seed=_seed)

    assert len(S) == 0
