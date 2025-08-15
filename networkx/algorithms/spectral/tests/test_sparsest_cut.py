"""Unit tests for sparsest"""

import math

import pytest

import networkx as nx
from networkx.algorithms.spectral.sparsest_cut import (
    balanced_sparse_cut,
    sparse_cut,
    sparsest_cut,
)


def test_sparse_cut_ladder_graph():
    G = nx.ladder_graph(20)
    n = len(G)
    S, T = sparse_cut(G, 1 / 5, "_s", "_t")

    assert nx.cut_size(G, S, T) / len(S) < 1 / 5
    assert len(S) > 1 / 12 / math.log(n) ** 2 * n
    assert S.union(T) == set(G)


def test_sparse_cut_barbell_graph():
    G = nx.barbell_graph(40, 1)
    n = len(G)
    S, T = sparse_cut(G, 1 / 5, "_s", "_t")

    assert nx.cut_size(G, S, T) / len(S) < 1 / 5
    assert len(S) > 1 / 12 / math.log(n) ** 2 * n
    assert S.union(T) == set(G)


def test_sparse_cut_expander():
    G = nx.gnp_random_graph(100, 0.2)
    S, _ = sparse_cut(G, 15, "_s", "_t")

    assert len(S) == 0


def test_sparse_cut_negative_balance():
    G = nx.gnp_random_graph(100, 0.2)
    pytest.raises(nx.NetworkXError, sparse_cut, G, 0.1, "_s", "_t", b=-1)


def test_sparse_cut_high_balance():
    G = nx.gnp_random_graph(100, 0.2)
    pytest.raises(nx.NetworkXError, sparse_cut, G, 0.1, "_s", "_t", b=1)


def test_sparse_cut_bad_source_key():
    G = nx.gnp_random_graph(100, 0.2)
    pytest.raises(nx.NetworkXError, sparse_cut, G, 0.1, 0, "_t", b=-1)


def test_sparse_cut_bad_target_key():
    G = nx.gnp_random_graph(100, 0.2)
    pytest.raises(nx.NetworkXError, sparse_cut, G, 0.1, "_s", 0, b=-1)


def test_sparsest_cut_barbell_graph():
    G = nx.barbell_graph(40, 1)
    S, T = sparsest_cut(G, "_s", "_t")

    assert nx.cut_size(G, S, T) / len(S) < 2 * 0.965
    assert S.union(T) == set(G)


def test_sparsest_cut_ladder_graph():
    G = nx.ladder_graph(50)
    S, T = sparsest_cut(G, "_s", "_t")

    assert nx.cut_size(G, S, T) / len(S) < 2 * 0.848
    assert S.union(T) == set(G)
