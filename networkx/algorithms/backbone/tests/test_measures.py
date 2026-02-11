"""Tests for backbone evaluation measures.

Covers: node_fraction, edge_fraction, weight_fraction, reachability,
ks_degree, ks_weight, and compare_backbones.
"""

import pytest
import networkx as nx

from backbone.structural import global_threshold_filter, strongest_n_ties
from backbone.measures import (
    node_fraction,
    edge_fraction,
    weight_fraction,
    reachability,
    ks_degree,
    ks_weight,
    compare_backbones,
)


# ── Node / Edge / Weight Fraction ─────────────────────────────────────────


def test_node_fraction_full(triangle_unequal):
    assert node_fraction(triangle_unequal, triangle_unequal) == 1.0


def test_node_fraction_partial(path_weighted):
    bb = nx.Graph()
    bb.add_nodes_from(path_weighted.nodes())
    bb.add_edge(0, 1, weight=10)
    assert node_fraction(path_weighted, bb) == pytest.approx(2 / 5)


def test_edge_fraction(path_weighted):
    bb = nx.Graph()
    bb.add_nodes_from(path_weighted.nodes())
    bb.add_edge(0, 1, weight=10)
    bb.add_edge(3, 4, weight=40)
    assert edge_fraction(path_weighted, bb) == pytest.approx(2 / 4)


def test_weight_fraction(path_weighted):
    # weights: 10+20+30+40 = 100
    bb = nx.Graph()
    bb.add_nodes_from(path_weighted.nodes())
    bb.add_edge(3, 4, weight=40)
    assert weight_fraction(path_weighted, bb) == pytest.approx(40 / 100)


# ── Reachability ──────────────────────────────────────────────────────────


def test_reachability_connected(two_cluster_undirected):
    assert reachability(two_cluster_undirected) == pytest.approx(1.0)


def test_reachability_disconnected(disconnected_graph):
    # (0,1) and (2,3) -- two components of size 2
    # Reachable pairs: 4, Total pairs: 12
    assert reachability(disconnected_graph) == pytest.approx(4 / 12)


def test_reachability_isolated():
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2])
    assert reachability(G) == pytest.approx(0.0)


def test_reachability_single_node(single_node_graph):
    assert reachability(single_node_graph) == 1.0


def test_reachability_directed():
    G = nx.DiGraph()
    G.add_edge(0, 1)
    G.add_edge(2, 3)
    r = reachability(G)
    assert r == pytest.approx(4 / 12)


# ── KS Measures ───────────────────────────────────────────────────────────


def test_ks_degree_identical(two_cluster_undirected):
    """KS degree stat of a graph with itself should be 0."""
    assert ks_degree(two_cluster_undirected, two_cluster_undirected) == pytest.approx(
        0.0
    )


def test_ks_degree_different(two_cluster_undirected):
    bb = global_threshold_filter(two_cluster_undirected, threshold=50)
    stat = ks_degree(two_cluster_undirected, bb)
    assert 0 <= stat <= 1


def test_ks_weight_identical(two_cluster_undirected):
    assert ks_weight(two_cluster_undirected, two_cluster_undirected) == pytest.approx(
        0.0
    )


def test_ks_weight_different(two_cluster_undirected):
    bb = global_threshold_filter(two_cluster_undirected, threshold=50)
    stat = ks_weight(two_cluster_undirected, bb)
    assert 0 < stat <= 1


def test_ks_empty_backbone(two_cluster_undirected):
    bb = nx.Graph()
    assert ks_degree(two_cluster_undirected, bb) == 1.0
    assert ks_weight(two_cluster_undirected, bb) == 1.0


# ── Compare Backbones ─────────────────────────────────────────────────────


def test_compare_backbones(path_weighted):
    bb1 = global_threshold_filter(path_weighted, threshold=25)
    bb2 = strongest_n_ties(path_weighted, n=1)
    results = compare_backbones(
        path_weighted,
        {"threshold": bb1, "strongest1": bb2},
        measures=[node_fraction, edge_fraction, weight_fraction],
    )
    assert "threshold" in results
    assert "strongest1" in results
    assert "node_fraction" in results["threshold"]
    assert 0 <= results["threshold"]["edge_fraction"] <= 1
