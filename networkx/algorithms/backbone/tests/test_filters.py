"""Tests for filtering utilities.

Covers: threshold_filter, fraction_filter, boolean_filter, and
consensus_backbone.
"""

import pytest
from backbone.filters import (
    boolean_filter,
    consensus_backbone,
    fraction_filter,
    threshold_filter,
)

import networkx as nx

# ── Threshold Filter ─────────────────────────────────────────────────────


def test_threshold_below_mode():
    G = nx.Graph()
    G.add_edge(0, 1, pval=0.01)
    G.add_edge(1, 2, pval=0.5)
    bb = threshold_filter(G, "pval", 0.05, mode="below")
    assert bb.has_edge(0, 1)
    assert not bb.has_edge(1, 2)


def test_threshold_above_mode():
    G = nx.Graph()
    G.add_edge(0, 1, score=0.9)
    G.add_edge(1, 2, score=0.3)
    bb = threshold_filter(G, "score", 0.5, mode="above")
    assert bb.has_edge(0, 1)
    assert not bb.has_edge(1, 2)


def test_threshold_node_filter():
    G = nx.Graph()
    G.add_node(0, importance=10)
    G.add_node(1, importance=1)
    G.add_node(2, importance=8)
    G.add_edge(0, 1)
    G.add_edge(0, 2)
    G.add_edge(1, 2)
    bb = threshold_filter(G, "importance", 5, mode="above", filter_on="nodes")
    assert 0 in bb.nodes()
    assert 2 in bb.nodes()
    assert 1 not in bb.nodes()
    assert bb.has_edge(0, 2)
    assert not bb.has_edge(0, 1)


def test_threshold_preserves_all_nodes_for_edge_filter():
    G = nx.Graph()
    G.add_node("isolated")
    G.add_edge(0, 1, score=0.9)
    bb = threshold_filter(G, "score", 0.5, mode="above")
    assert "isolated" in bb.nodes()


def test_threshold_invalid_mode():
    G = nx.Graph()
    with pytest.raises(ValueError):
        threshold_filter(G, "x", 0.5, mode="invalid")


# ── Fraction Filter ───────────────────────────────────────────────────────


def test_fraction_half():
    G = nx.Graph()
    G.add_edge(0, 1, score=0.1)
    G.add_edge(1, 2, score=0.5)
    G.add_edge(2, 3, score=0.9)
    G.add_edge(3, 4, score=0.3)
    # Keep lowest 50% -> 2 edges with smallest scores
    bb = fraction_filter(G, "score", 0.5, ascending=True)
    assert bb.number_of_edges() == 2
    assert bb.has_edge(0, 1)  # score=0.1
    assert bb.has_edge(3, 4)  # score=0.3


def test_fraction_keeps_highest():
    G = nx.Graph()
    G.add_edge(0, 1, score=0.1)
    G.add_edge(1, 2, score=0.9)
    G.add_edge(2, 3, score=0.5)
    bb = fraction_filter(G, "score", 0.34, ascending=False)
    # 34% of 3 edges -> 1 edge, highest score
    assert bb.number_of_edges() == 1
    assert bb.has_edge(1, 2)


def test_fraction_one_keeps_all(triangle_unequal):
    for u, v, d in triangle_unequal.edges(data=True):
        d["score"] = d["weight"]
    bb = fraction_filter(triangle_unequal, "score", 1.0, ascending=True)
    assert bb.number_of_edges() == 3


def test_fraction_invalid_fraction():
    G = nx.Graph()
    with pytest.raises(ValueError):
        fraction_filter(G, "score", 0.0)
    with pytest.raises(ValueError):
        fraction_filter(G, "score", 1.5)


# ── Boolean Filter ────────────────────────────────────────────────────────


def test_boolean_basic():
    G = nx.Graph()
    G.add_edge(0, 1, keep=True)
    G.add_edge(1, 2, keep=False)
    G.add_edge(2, 3, keep=True)
    bb = boolean_filter(G, "keep")
    assert bb.has_edge(0, 1)
    assert not bb.has_edge(1, 2)
    assert bb.has_edge(2, 3)


def test_boolean_preserves_nodes():
    G = nx.Graph()
    G.add_node("extra")
    G.add_edge(0, 1, keep=True)
    bb = boolean_filter(G, "keep")
    assert "extra" in bb.nodes()


# ── Consensus Backbone ───────────────────────────────────────────────────


def test_consensus_intersection():
    G1 = nx.Graph()
    G1.add_edge(0, 1, weight=10)
    G1.add_edge(1, 2, weight=20)

    G2 = nx.Graph()
    G2.add_edge(1, 2, weight=20)
    G2.add_edge(2, 3, weight=30)

    cc = consensus_backbone(G1, G2)
    assert cc.has_edge(1, 2)
    assert cc.number_of_edges() == 1


def test_consensus_three_graphs():
    G1 = nx.Graph([(0, 1), (1, 2), (2, 3)])
    G2 = nx.Graph([(0, 1), (1, 2)])
    G3 = nx.Graph([(1, 2), (2, 3), (3, 4)])
    cc = consensus_backbone(G1, G2, G3)
    assert cc.number_of_edges() == 1
    assert cc.has_edge(1, 2)


def test_consensus_directed():
    G1 = nx.DiGraph([(0, 1), (1, 2)])
    G2 = nx.DiGraph([(1, 0), (1, 2)])
    cc = consensus_backbone(G1, G2)
    # Only (1,2) is common in same direction
    assert cc.has_edge(1, 2)
    assert not cc.has_edge(0, 1)  # G2 has (1,0) not (0,1)


def test_consensus_requires_two_graphs():
    G1 = nx.Graph([(0, 1)])
    with pytest.raises(ValueError):
        consensus_backbone(G1)
