"""Unit tests for low conductance cut"""

import math

import pytest

import networkx as nx
from networkx.algorithms.spectral.expander_decomposition import expander_decomposition
from networkx.utils import py_random_state

np = pytest.importorskip("numpy")
sp = pytest.importorskip("scipy")

_seed = np.random.RandomState(42)


@py_random_state(3)
def connected_cliques(n, k, r, _seed=1234):
    """Returns k cliques of size n, with r edges placed at random between the
    different cliques.
    """
    G = nx.Graph()
    for i in range(k):
        G.add_edges_from(nx.complete_graph(range(i * n, (i + 1) * n)).edges)

    for _ in range(r):
        clique_1, clique_2 = _seed.sample(range(k), 2)
        u = _seed.choice(range(clique_1 * n, (clique_1 + 1) * n))
        v = _seed.choice(range(clique_2 * n, (clique_2 + 1) * n))
        G.add_edge(u, v)

    return G


def intercluster_edges(G, clusters):
    total_edges = 0
    for i in range(len(clusters)):
        for j in range(i, len(clusters)):
            total_edges += nx.cut_size(G, clusters[i], clusters[j])
    return total_edges


def test_expander_decomposition_cliques_1():
    G = connected_cliques(10, 10, 20, _seed)
    m = len(G.edges())
    clusters = expander_decomposition(G, 0.1, "_s", "_t", _seed=_seed)

    assert len(clusters) == 10
    assert intercluster_edges(G, clusters) < 0.1 * m * math.log(m) ** 3


def test_expander_decomposition_cliques_2():
    G = connected_cliques(15, 20, 40, _seed)
    m = len(G.edges())
    clusters = expander_decomposition(
        G, 0.05, "_s", "_t", fast_randomization=True, _seed=_seed
    )

    assert len(clusters) == 20
    assert intercluster_edges(G, clusters) < 0.1 * m * math.log(m) ** 3


def test_expander_decomposition_random():
    G = nx.gnp_random_graph(200, 0.2, _seed)
    clusters = expander_decomposition(G, 0.001, "_s", "_t", _seed=_seed)

    assert len(clusters) == 1


def test_expander_decomposition_one_edge():
    """Should always certify that a graph with one edge is an expander."""

    G = nx.complete_graph(2)
    clusters = expander_decomposition(G, 0.01, "_s", "_t", _seed=_seed)

    assert len(clusters) == 1


def test_expander_decomposition_no_edges():
    G = nx.trivial_graph()
    clusters = expander_decomposition(G, 0.1, "_s", "_t", _seed=_seed)

    assert len(clusters) == 1


def test_expander_decomposition_bad_args():
    G = nx.complete_graph(10)
    pytest.raises(
        nx.NetworkXNotImplemented,
        expander_decomposition,
        G,
        0.1,
        "_s",
        "_t",
        False,
        _seed=_seed,
    )
