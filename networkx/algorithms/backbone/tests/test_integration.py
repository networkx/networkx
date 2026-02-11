"""End-to-end integration tests, edge cases, and all-methods smoke tests.

These tests combine multiple backbone methods and verify structural
invariants across the full pipeline.
"""

import pytest
import networkx as nx

from backbone.statistical import (
    disparity_filter,
    noise_corrected_filter,
    marginal_likelihood_filter,
    ecm_filter,
    lans_filter,
)
from backbone.structural import (
    global_threshold_filter,
    high_salience_skeleton,
    metric_backbone,
    ultrametric_backbone,
    maximum_spanning_tree_backbone,
    strongest_n_ties,
    doubly_stochastic_filter,
    h_backbone,
    modularity_backbone,
    planar_maximally_filtered_graph,
)
from backbone.proximity import (
    neighborhood_overlap,
    jaccard_backbone,
    dice_backbone,
    cosine_backbone,
)
from backbone.hybrid import glab_filter
from backbone.filters import (
    threshold_filter,
    fraction_filter,
    consensus_backbone,
)
from backbone.measures import (
    node_fraction,
    edge_fraction,
    weight_fraction,
    compare_backbones,
)


# ── End-to-end pipelines ─────────────────────────────────────────────────


def test_disparity_then_threshold_is_subgraph(two_cluster_undirected):
    H = disparity_filter(two_cluster_undirected)
    bb = threshold_filter(H, "disparity_pvalue", 0.05, "below")
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)


def test_salience_then_fraction(two_cluster_undirected):
    H = high_salience_skeleton(two_cluster_undirected)
    bb = fraction_filter(H, "salience", 0.3, ascending=False)
    assert bb.number_of_edges() > 0
    assert bb.number_of_edges() <= two_cluster_undirected.number_of_edges()


def test_consensus_of_multiple_methods(two_cluster_undirected):
    bb_thresh = global_threshold_filter(two_cluster_undirected, threshold=5)
    bb_strong = strongest_n_ties(two_cluster_undirected, n=2)
    cc = consensus_backbone(bb_thresh, bb_strong)
    for u, v in cc.edges():
        assert bb_thresh.has_edge(u, v)
        assert bb_strong.has_edge(u, v)


def test_compare_multiple_backbones(two_cluster_undirected):
    G = two_cluster_undirected
    methods = {
        "threshold_50": global_threshold_filter(G, 50),
        "threshold_5": global_threshold_filter(G, 5),
        "strongest_1": strongest_n_ties(G, n=1),
        "strongest_2": strongest_n_ties(G, n=2),
        "mst": maximum_spanning_tree_backbone(G),
    }
    results = compare_backbones(G, methods)
    # threshold_5 should keep more edges than threshold_50
    assert (
        results["threshold_5"]["edge_fraction"]
        >= results["threshold_50"]["edge_fraction"]
    )
    # MST should preserve all nodes (as a tree on connected graph)
    assert results["mst"]["node_fraction"] == pytest.approx(1.0)


def test_directed_pipeline(two_cluster_directed):
    """Full pipeline on a directed graph: disparity -> threshold."""
    H = disparity_filter(two_cluster_directed)
    bb = threshold_filter(H, "disparity_pvalue", 0.1, "below")
    assert bb.is_directed()
    for u, v in bb.edges():
        assert two_cluster_directed.has_edge(u, v)


def test_backbone_sparser_than_original(two_cluster_undirected):
    """Any reasonable backbone should be sparser than the original."""
    bb = global_threshold_filter(two_cluster_undirected, threshold=50)
    assert bb.number_of_edges() < two_cluster_undirected.number_of_edges()


def test_monotonicity_of_threshold(two_cluster_undirected):
    """Increasing threshold should monotonically decrease edges."""
    prev_edges = two_cluster_undirected.number_of_edges() + 1
    for t in [0, 1, 5, 10, 50, 100, 200]:
        bb = global_threshold_filter(two_cluster_undirected, threshold=t)
        assert bb.number_of_edges() <= prev_edges
        prev_edges = bb.number_of_edges()


def test_monotonicity_of_strongest_n(two_cluster_undirected):
    """Increasing n should monotonically increase edges."""
    prev_edges = 0
    for n in [1, 2, 3, 4, 5]:
        bb = strongest_n_ties(two_cluster_undirected, n=n)
        assert bb.number_of_edges() >= prev_edges
        prev_edges = bb.number_of_edges()


# ── Edge cases and robustness ─────────────────────────────────────────────


def test_global_threshold_empty_graph():
    G = nx.Graph()
    bb = global_threshold_filter(G, threshold=0)
    assert bb.number_of_nodes() == 0


def test_strongest_n_no_edges():
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2])
    bb = strongest_n_ties(G, n=1)
    assert bb.number_of_edges() == 0
    assert set(bb.nodes()) == {0, 1, 2}


def test_disparity_on_single_edge(single_edge_graph):
    H = disparity_filter(single_edge_graph)
    assert H["x"]["y"]["disparity_pvalue"] == 1.0


def test_measures_on_empty_backbone(two_cluster_undirected):
    bb = nx.Graph()
    bb.add_nodes_from(two_cluster_undirected.nodes())
    assert edge_fraction(two_cluster_undirected, bb) == 0.0
    assert weight_fraction(two_cluster_undirected, bb) == 0.0
    assert node_fraction(two_cluster_undirected, bb) == 0.0


def test_large_graph_smoke():
    """Smoke test on a moderately sized graph (200 nodes)."""
    G = nx.barabasi_albert_graph(200, 3, seed=42)
    for u, v in G.edges():
        G[u][v]["weight"] = abs(hash((u, v))) % 100 + 1
    bb1 = global_threshold_filter(G, threshold=50)
    bb2 = strongest_n_ties(G, n=2)
    H = disparity_filter(G)
    bb3 = threshold_filter(H, "disparity_pvalue", 0.05, "below")
    assert bb1.number_of_edges() < G.number_of_edges()
    assert bb2.number_of_edges() < G.number_of_edges()
    assert bb3.number_of_edges() < G.number_of_edges()


def test_self_loop_handling():
    """Self-loops should be handled gracefully."""
    G = nx.Graph()
    G.add_edge(0, 0, weight=5)
    G.add_edge(0, 1, weight=10)
    bb = global_threshold_filter(G, threshold=7)
    assert bb.has_edge(0, 1)
    assert not bb.has_edge(0, 0)


# ── All-methods integration smoke tests ───────────────────────────────────


def test_all_statistical_undirected(two_cluster_undirected):
    G = two_cluster_undirected
    for method, attr in [
        (disparity_filter, "disparity_pvalue"),
        (noise_corrected_filter, "nc_score"),
        (marginal_likelihood_filter, "ml_pvalue"),
        (ecm_filter, "ecm_pvalue"),
        (lans_filter, "lans_pvalue"),
    ]:
        H = method(G)
        assert H.number_of_edges() == G.number_of_edges()
        for u, v, d in H.edges(data=True):
            assert attr in d


def test_all_statistical_directed(two_cluster_directed):
    G = two_cluster_directed
    for method, attr in [
        (disparity_filter, "disparity_pvalue"),
        (noise_corrected_filter, "nc_score"),
        (marginal_likelihood_filter, "ml_pvalue"),
        (ecm_filter, "ecm_pvalue"),
        (lans_filter, "lans_pvalue"),
    ]:
        H = method(G)
        assert H.is_directed()
        assert H.number_of_edges() == G.number_of_edges()
        for u, v, d in H.edges(data=True):
            assert attr in d


def test_all_structural_scored_undirected(two_cluster_undirected):
    """Structural methods that return scored graphs."""
    G = two_cluster_undirected
    for method, attr in [
        (high_salience_skeleton, "salience"),
        (doubly_stochastic_filter, "ds_weight"),
        (modularity_backbone, "vitality"),
        (neighborhood_overlap, "overlap"),
        (jaccard_backbone, "jaccard"),
        (dice_backbone, "dice"),
        (cosine_backbone, "cosine"),
    ]:
        H = method(G)
        if attr == "vitality":
            for n in H.nodes():
                assert attr in H.nodes[n]
        else:
            for u, v, d in H.edges(data=True):
                assert attr in d


def test_all_structural_subgraph_undirected(two_cluster_undirected):
    """Structural methods that return subgraphs directly."""
    G = two_cluster_undirected
    for method in [
        lambda g: global_threshold_filter(g, 50),
        lambda g: strongest_n_ties(g, n=2),
        metric_backbone,
        ultrametric_backbone,
        h_backbone,
        planar_maximally_filtered_graph,
        maximum_spanning_tree_backbone,
    ]:
        bb = method(G)
        for u, v in bb.edges():
            assert G.has_edge(u, v)


def test_glab_undirected(two_cluster_undirected):
    H = glab_filter(two_cluster_undirected)
    for u, v, d in H.edges(data=True):
        assert "glab_pvalue" in d


def test_compare_all_backbones(two_cluster_undirected):
    """Compare many backbone methods side by side."""
    G = two_cluster_undirected
    backbones = {
        "threshold_50": global_threshold_filter(G, 50),
        "strongest_2": strongest_n_ties(G, n=2),
        "mst": maximum_spanning_tree_backbone(G),
        "h_bb": h_backbone(G),
        "pmfg": planar_maximally_filtered_graph(G),
    }
    results = compare_backbones(G, backbones)
    for name in backbones:
        assert name in results
        assert "edge_fraction" in results[name]
        ef = results[name]["edge_fraction"]
        assert 0 <= ef <= 1
