"""Tests for statistical backbone methods.

Covers: disparity_filter, noise_corrected_filter, marginal_likelihood_filter,
ecm_filter, and lans_filter.
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
from backbone.filters import threshold_filter


# ── Disparity Filter ─────────────────────────────────────────────────────


def test_disparity_pvalues_added(two_cluster_undirected):
    H = disparity_filter(two_cluster_undirected)
    for u, v, d in H.edges(data=True):
        assert "disparity_pvalue" in d
        assert 0 <= d["disparity_pvalue"] <= 1


def test_disparity_preserves_original_attributes(two_cluster_undirected):
    H = disparity_filter(two_cluster_undirected)
    for u, v, d in H.edges(data=True):
        assert "weight" in d


def test_disparity_preserves_graph_structure(two_cluster_undirected):
    H = disparity_filter(two_cluster_undirected)
    assert H.number_of_nodes() == two_cluster_undirected.number_of_nodes()
    assert H.number_of_edges() == two_cluster_undirected.number_of_edges()


def test_disparity_uniform_weights_zero_pvalues(complete_uniform):
    """In a complete graph with uniform weights, all edges get p=0."""
    H = disparity_filter(complete_uniform)
    for u, v, d in H.edges(data=True):
        assert d["disparity_pvalue"] == 0.0
    # All edges pass: 0.0 < 0.01 is True
    bb = threshold_filter(H, "disparity_pvalue", 0.01, "below")
    assert bb.number_of_edges() == 10
    # Strict < 0.0 keeps nothing
    bb2 = threshold_filter(H, "disparity_pvalue", 0.0, "below")
    assert bb2.number_of_edges() == 0


def test_disparity_multiscale_significance(two_cluster_undirected):
    """The bridge in a two-cluster graph should have p-value < 1."""
    H = disparity_filter(two_cluster_undirected)
    bridge_pval = H[3][4]["disparity_pvalue"]
    assert bridge_pval < 1.0


def test_disparity_degree_one_node_pvalue():
    """A degree-1 node's only edge should get pvalue=1 (always expected)."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=100)
    G.add_edge(1, 2, weight=50)
    H = disparity_filter(G)
    p01 = H[0][1]["disparity_pvalue"]
    p12 = H[1][2]["disparity_pvalue"]
    assert p01 < 1.0
    assert p12 < 1.0


def test_disparity_directed_graph(two_cluster_directed):
    H = disparity_filter(two_cluster_directed)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "disparity_pvalue" in d
        assert 0 <= d["disparity_pvalue"] <= 1


def test_disparity_directed_pvalue_from_source_only():
    """In directed mode, p-value depends only on the source node."""
    G = nx.DiGraph()
    G.add_edge("a", "b", weight=10)
    G.add_edge("a", "c", weight=90)
    G.add_edge("b", "a", weight=50)
    H = disparity_filter(G)
    assert H["a"]["b"]["disparity_pvalue"] == H["a"]["c"]["disparity_pvalue"]
    assert H["a"]["b"]["disparity_pvalue"] == 0.0


def test_disparity_directed_pvalue_varies_with_higher_outdegree():
    """With out-degree >= 3 the disparity filter differentiates edges."""
    G = nx.DiGraph()
    G.add_edge("a", "b", weight=10)
    G.add_edge("a", "c", weight=10)
    G.add_edge("a", "d", weight=80)
    H = disparity_filter(G)
    assert H["a"]["d"]["disparity_pvalue"] > H["a"]["b"]["disparity_pvalue"]


def test_disparity_raises_on_zero_weight():
    G = nx.Graph()
    G.add_edge(0, 1, weight=0)
    with pytest.raises(nx.NetworkXError):
        disparity_filter(G)


def test_disparity_raises_on_missing_weight():
    G = nx.Graph()
    G.add_edge(0, 1)  # no weight attribute
    with pytest.raises(nx.NetworkXError):
        disparity_filter(G)


def test_disparity_single_edge_pvalue(single_edge_graph):
    H = disparity_filter(single_edge_graph)
    # Both endpoints are degree 1 -> pvalue = 1.0
    assert H["x"]["y"]["disparity_pvalue"] == 1.0


def test_disparity_filtering_pipeline(two_cluster_undirected):
    """Full pipeline: disparity -> threshold -> verify backbone is a subgraph."""
    H = disparity_filter(two_cluster_undirected)
    bb = threshold_filter(H, "disparity_pvalue", 0.05, "below")
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)
    assert bb.number_of_edges() <= two_cluster_undirected.number_of_edges()


# ── Noise-Corrected Filter ───────────────────────────────────────────────


def test_noise_corrected_scores_added(two_cluster_undirected):
    H = noise_corrected_filter(two_cluster_undirected)
    for u, v, d in H.edges(data=True):
        assert "nc_score" in d


def test_noise_corrected_preserves_structure(two_cluster_undirected):
    H = noise_corrected_filter(two_cluster_undirected)
    assert H.number_of_nodes() == two_cluster_undirected.number_of_nodes()
    assert H.number_of_edges() == two_cluster_undirected.number_of_edges()


def test_noise_corrected_strong_edges_score_higher(two_cluster_undirected):
    """Edges in the heavy cluster should score higher than the bridge."""
    H = noise_corrected_filter(two_cluster_undirected)
    bridge_score = H[3][4]["nc_score"]
    cluster_b_score = H[4][5]["nc_score"]
    assert cluster_b_score > bridge_score


def test_noise_corrected_directed(two_cluster_directed):
    H = noise_corrected_filter(two_cluster_directed)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "nc_score" in d


def test_noise_corrected_filtering_pipeline(two_cluster_undirected):
    H = noise_corrected_filter(two_cluster_undirected)
    bb = threshold_filter(H, "nc_score", 2.0, "above")
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)


def test_noise_corrected_uniform_weights_low_scores(complete_uniform):
    """Uniform weights should yield scores near 0 (nothing unexpected)."""
    H = noise_corrected_filter(complete_uniform)
    scores = [d["nc_score"] for _, _, d in H.edges(data=True)]
    assert max(scores) - min(scores) < 1e-6


# ── Marginal Likelihood Filter ───────────────────────────────────────────


def test_marginal_likelihood_pvalues_added(two_cluster_undirected):
    H = marginal_likelihood_filter(two_cluster_undirected)
    for u, v, d in H.edges(data=True):
        assert "ml_pvalue" in d
        assert 0 <= d["ml_pvalue"] <= 1


def test_marginal_likelihood_preserves_structure(two_cluster_undirected):
    H = marginal_likelihood_filter(two_cluster_undirected)
    assert H.number_of_edges() == two_cluster_undirected.number_of_edges()


def test_marginal_likelihood_heavy_edges_significant(two_cluster_undirected):
    """The bridge (w=1) should get a high p-value (not significant)."""
    H = marginal_likelihood_filter(two_cluster_undirected)
    bridge_pval = H[3][4]["ml_pvalue"]
    assert bridge_pval > 0.5


def test_marginal_likelihood_directed(two_cluster_directed):
    H = marginal_likelihood_filter(two_cluster_directed)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "ml_pvalue" in d


def test_marginal_likelihood_single_edge(single_edge_graph):
    H = marginal_likelihood_filter(single_edge_graph)
    assert "ml_pvalue" in H["x"]["y"]


# ── ECM Filter ────────────────────────────────────────────────────────────


def test_ecm_pvalues_added(triangle_unequal):
    H = ecm_filter(triangle_unequal)
    for u, v, d in H.edges(data=True):
        assert "ecm_pvalue" in d
        assert 0 <= d["ecm_pvalue"] <= 1


def test_ecm_preserves_structure(triangle_unequal):
    H = ecm_filter(triangle_unequal)
    assert H.number_of_edges() == triangle_unequal.number_of_edges()


def test_ecm_directed(two_cluster_directed):
    H = ecm_filter(two_cluster_directed)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "ecm_pvalue" in d


def test_ecm_small_graph(single_edge_graph):
    """Should work on very small graphs without crashing."""
    H = ecm_filter(single_edge_graph)
    assert "ecm_pvalue" in H["x"]["y"]


# ── LANS Filter ───────────────────────────────────────────────────────────


def test_lans_pvalues_added(two_cluster_undirected):
    H = lans_filter(two_cluster_undirected)
    for u, v, d in H.edges(data=True):
        assert "lans_pvalue" in d
        assert 0 <= d["lans_pvalue"] <= 1


def test_lans_strongest_edge_most_significant(triangle_unequal):
    """In a triangle, the strongest edge should have the lowest p-value."""
    H = lans_filter(triangle_unequal)
    pvals = {(u, v): d["lans_pvalue"] for u, v, d in H.edges(data=True)}
    ac_pval = pvals.get(("A", "C"), pvals.get(("C", "A")))
    ab_pval = pvals.get(("A", "B"), pvals.get(("B", "A")))
    assert ac_pval <= ab_pval


def test_lans_directed(two_cluster_directed):
    H = lans_filter(two_cluster_directed)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "lans_pvalue" in d


def test_lans_preserves_structure(two_cluster_undirected):
    H = lans_filter(two_cluster_undirected)
    assert H.number_of_edges() == two_cluster_undirected.number_of_edges()


def test_lans_filtering_pipeline(two_cluster_undirected):
    H = lans_filter(two_cluster_undirected)
    bb = threshold_filter(H, "lans_pvalue", 0.3, "below")
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)
