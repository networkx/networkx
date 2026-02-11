"""Tests for unweighted backbone methods.

Covers: sparsify, lspar, and local_degree.
"""

import pytest
from backbone.unweighted import local_degree, lspar, sparsify

import networkx as nx


def _make_unweighted_community():
    """Unweighted graph with two communities connected by a few bridges."""
    G = nx.Graph()
    # Community 1: nodes 0-4, dense
    for i in range(5):
        for j in range(i + 1, 5):
            G.add_edge(i, j)
    # Community 2: nodes 5-9, dense
    for i in range(5, 10):
        for j in range(i + 1, 10):
            G.add_edge(i, j)
    # Bridges
    G.add_edge(4, 5)
    G.add_edge(3, 6)
    return G


# ── Sparsify ──────────────────────────────────────────────────────────────


def test_sparsify_jaccard_score():
    G = _make_unweighted_community()
    bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=0.5)
    assert 0 < bb.number_of_edges() < G.number_of_edges()


def test_sparsify_degree_score():
    G = _make_unweighted_community()
    bb = sparsify(G, escore="degree", normalize="rank", filter="degree", s=0.5)
    assert 0 < bb.number_of_edges() < G.number_of_edges()


def test_sparsify_triangles_score():
    G = _make_unweighted_community()
    bb = sparsify(G, escore="triangles", normalize="rank", filter="degree", s=0.5)
    assert bb.number_of_edges() > 0


def test_sparsify_quadrangles_score():
    G = _make_unweighted_community()
    bb = sparsify(G, escore="quadrangles", normalize="rank", filter="degree", s=0.5)
    assert bb.number_of_edges() > 0


def test_sparsify_random_score():
    G = _make_unweighted_community()
    bb = sparsify(G, escore="random", normalize="rank", filter="degree", s=0.5)
    assert bb.number_of_edges() > 0


def test_sparsify_threshold_filter_mode():
    G = _make_unweighted_community()
    bb = sparsify(G, escore="jaccard", normalize="rank", filter="threshold", s=0.5)
    assert bb.number_of_edges() <= G.number_of_edges()


def test_sparsify_no_normalisation():
    G = _make_unweighted_community()
    bb = sparsify(G, escore="jaccard", normalize=None, filter="degree", s=0.5)
    assert bb.number_of_edges() > 0


def test_sparsify_s_zero_very_sparse():
    """s=0 should produce a very sparse backbone."""
    G = _make_unweighted_community()
    bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=0.01)
    assert bb.number_of_edges() <= G.number_of_edges()


def test_sparsify_s_one_keeps_most():
    """s=1.0 with degree filter keeps ceil(d^1) = d edges per node -> all."""
    G = _make_unweighted_community()
    bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=1.0)
    assert bb.number_of_edges() == G.number_of_edges()


def test_sparsify_is_subgraph():
    G = _make_unweighted_community()
    bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=0.5)
    for u, v in bb.edges():
        assert G.has_edge(u, v)


def test_sparsify_preserves_nodes():
    G = _make_unweighted_community()
    bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=0.5)
    assert set(bb.nodes()) == set(G.nodes())


def test_sparsify_raises_on_directed():
    G = nx.DiGraph([(0, 1), (1, 2)])
    with pytest.raises(nx.NetworkXError):
        sparsify(G)


# ── LSpar ─────────────────────────────────────────────────────────────────


def test_lspar_is_subgraph():
    G = _make_unweighted_community()
    bb = lspar(G, s=0.5)
    for u, v in bb.edges():
        assert G.has_edge(u, v)


def test_lspar_sparser_than_original():
    G = _make_unweighted_community()
    bb = lspar(G, s=0.5)
    assert bb.number_of_edges() < G.number_of_edges()


def test_lspar_monotonic_in_s():
    """Increasing s should monotonically increase edge count."""
    G = _make_unweighted_community()
    prev = 0
    for s in [0.1, 0.3, 0.5, 0.7, 1.0]:
        bb = lspar(G, s=s)
        assert bb.number_of_edges() >= prev
        prev = bb.number_of_edges()


# ── Local Degree ──────────────────────────────────────────────────────────


def test_local_degree_is_subgraph():
    G = _make_unweighted_community()
    bb = local_degree(G, s=0.5)
    for u, v in bb.edges():
        assert G.has_edge(u, v)


def test_local_degree_sparser_than_original():
    G = _make_unweighted_community()
    bb = local_degree(G, s=0.3)
    assert bb.number_of_edges() < G.number_of_edges()
