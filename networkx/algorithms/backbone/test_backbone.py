"""
Tests for the backbone extraction module.

Test fixtures include:
- Small hand-crafted undirected weighted graphs with known structure
- Small hand-crafted directed weighted graphs
- Hub-and-spoke topology (star graph)
- Two-cluster (barbell-like) topology with multi-scale weights
- Complete graphs with uniform / non-uniform weights
- Edge cases: single-node, single-edge, disconnected components

Each test class verifies both the scoring/annotation step and the
filtering step, checking node/edge sets, attribute presence, and
structural invariants.
"""

import math
import pytest
import networkx as nx

# ── Import the backbone module ──────────────────────────────────────────
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
    neighborhood_overlap,
    jaccard_backbone,
    dice_backbone,
    cosine_backbone,
)
from backbone.hybrid import glab_filter
from backbone.bipartite import sdsm, fdsm
from backbone.unweighted import sparsify, lspar, local_degree
from backbone.filters import (
    threshold_filter,
    fraction_filter,
    boolean_filter,
    consensus_backbone,
)
from backbone.measures import (
    node_fraction,
    edge_fraction,
    weight_fraction,
    reachability,
    ks_degree,
    ks_weight,
    compare_backbones,
)


# ========================================================================
# Fixtures: reusable graph builders
# ========================================================================

def _make_two_cluster_undirected():
    """Two 4-cliques joined by a single weak bridge.

    Cluster A (nodes 0-3): internal weights = 10
    Cluster B (nodes 4-7): internal weights = 100
    Bridge: (3, 4) weight = 1

    This creates a multi-scale network: cluster B's edges are much
    stronger globally, but cluster A's edges are locally significant.
    """
    G = nx.Graph()
    # Cluster A
    for i in range(4):
        for j in range(i + 1, 4):
            G.add_edge(i, j, weight=10)
    # Cluster B
    for i in range(4, 8):
        for j in range(i + 1, 8):
            G.add_edge(i, j, weight=100)
    # Bridge
    G.add_edge(3, 4, weight=1)
    return G


def _make_two_cluster_directed():
    """Directed version of the two-cluster graph.

    Same structure but with directed edges (both directions for
    intra-cluster, single direction for bridge: 3 → 4).
    """
    G = nx.DiGraph()
    for i in range(4):
        for j in range(4):
            if i != j:
                G.add_edge(i, j, weight=10)
    for i in range(4, 8):
        for j in range(4, 8):
            if i != j:
                G.add_edge(i, j, weight=100)
    G.add_edge(3, 4, weight=1)
    return G


def _make_star_undirected(n=6, hub_weight=100, spoke_weight=5):
    """Star graph with node 0 as hub.

    Hub-spoke edges have `hub_weight`, and optional spoke-to-spoke
    edges around the rim have `spoke_weight`.
    """
    G = nx.Graph()
    for i in range(1, n):
        G.add_edge(0, i, weight=hub_weight)
    # Add a rim so spokes aren't degree-1
    for i in range(1, n):
        j = (i % (n - 1)) + 1
        if i != j:
            G.add_edge(i, j, weight=spoke_weight)
    return G


def _make_star_directed(n=6, hub_weight=100, spoke_weight=5):
    """Directed star: hub 0 → spokes, plus directed rim."""
    G = nx.DiGraph()
    for i in range(1, n):
        G.add_edge(0, i, weight=hub_weight)
    for i in range(1, n):
        j = (i % (n - 1)) + 1
        if i != j:
            G.add_edge(i, j, weight=spoke_weight)
    return G


def _make_path_weighted(n=5):
    """Weighted path graph: 0 --10-- 1 --20-- 2 --30-- 3 --40-- 4."""
    G = nx.Graph()
    for i in range(n - 1):
        G.add_edge(i, i + 1, weight=(i + 1) * 10)
    return G


def _make_complete_uniform(n=5, w=10):
    """Complete undirected graph with uniform weight."""
    G = nx.complete_graph(n)
    for u, v in G.edges():
        G[u][v]["weight"] = w
    return G


def _make_triangle_unequal():
    """Triangle: edges with weights 1, 2, 3."""
    G = nx.Graph()
    G.add_edge("A", "B", weight=1)
    G.add_edge("B", "C", weight=2)
    G.add_edge("A", "C", weight=3)
    return G


def _make_disconnected():
    """Two disconnected components: (0-1, w=10) and (2-3, w=20)."""
    G = nx.Graph()
    G.add_edge(0, 1, weight=10)
    G.add_edge(2, 3, weight=20)
    return G


def _make_single_edge():
    """Graph with one edge."""
    G = nx.Graph()
    G.add_edge("x", "y", weight=42)
    return G


def _make_single_node():
    """Graph with one node, no edges."""
    G = nx.Graph()
    G.add_node("alone")
    return G


# ========================================================================
# Tests: Global Threshold Filter
# ========================================================================

class TestGlobalThresholdFilter:
    """Tests for the simplest backbone method: global weight threshold."""

    def test_threshold_keeps_heavy_edges(self):
        G = _make_two_cluster_undirected()
        bb = global_threshold_filter(G, threshold=50)
        # Only cluster B edges (weight=100) survive
        assert bb.number_of_edges() == 6  # C(4,2)
        for u, v, d in bb.edges(data=True):
            assert d["weight"] >= 50

    def test_threshold_zero_keeps_everything(self):
        G = _make_two_cluster_undirected()
        bb = global_threshold_filter(G, threshold=0)
        assert bb.number_of_edges() == G.number_of_edges()

    def test_threshold_very_high_removes_all_edges(self):
        G = _make_two_cluster_undirected()
        bb = global_threshold_filter(G, threshold=999)
        assert bb.number_of_edges() == 0
        # But all nodes are preserved
        assert set(bb.nodes()) == set(G.nodes())

    def test_threshold_preserves_node_set(self):
        G = _make_two_cluster_undirected()
        bb = global_threshold_filter(G, threshold=50)
        assert set(bb.nodes()) == set(G.nodes())

    def test_threshold_on_path_graph(self):
        G = _make_path_weighted(5)
        # Weights: 10, 20, 30, 40 → threshold=25 keeps edges with w>=25
        bb = global_threshold_filter(G, threshold=25)
        assert bb.number_of_edges() == 2  # (2,3,w=30), (3,4,w=40)

    def test_threshold_boundary_inclusive(self):
        """Edges with weight exactly equal to threshold are retained."""
        G = _make_path_weighted(5)
        bb = global_threshold_filter(G, threshold=20)
        assert bb.has_edge(1, 2)  # weight=20, exactly at threshold
        assert bb.number_of_edges() == 3

    def test_threshold_directed(self):
        G = _make_two_cluster_directed()
        bb = global_threshold_filter(G, threshold=50)
        assert bb.is_directed()
        # Only cluster B directed edges survive (12 directed edges in K4)
        assert bb.number_of_edges() == 12
        for u, v, d in bb.edges(data=True):
            assert d["weight"] >= 50

    def test_threshold_directed_bridge_excluded(self):
        G = _make_two_cluster_directed()
        bb = global_threshold_filter(G, threshold=2)
        # Bridge (3→4, w=1) should be excluded
        assert not bb.has_edge(3, 4)

    def test_threshold_single_edge(self):
        G = _make_single_edge()
        bb_keep = global_threshold_filter(G, threshold=42)
        assert bb_keep.has_edge("x", "y")
        bb_drop = global_threshold_filter(G, threshold=43)
        assert not bb_drop.has_edge("x", "y")

    def test_threshold_single_node(self):
        G = _make_single_node()
        bb = global_threshold_filter(G, threshold=0)
        assert "alone" in bb.nodes()
        assert bb.number_of_edges() == 0

    def test_threshold_disconnected(self):
        G = _make_disconnected()
        bb = global_threshold_filter(G, threshold=15)
        assert bb.number_of_edges() == 1
        assert bb.has_edge(2, 3)
        assert not bb.has_edge(0, 1)

    def test_threshold_preserves_attributes(self):
        G = nx.Graph()
        G.add_edge(0, 1, weight=10, color="red")
        bb = global_threshold_filter(G, threshold=5)
        assert bb[0][1]["color"] == "red"

    def test_threshold_custom_weight_key(self):
        G = nx.Graph()
        G.add_edge(0, 1, flow=100)
        G.add_edge(1, 2, flow=5)
        bb = global_threshold_filter(G, threshold=50, weight="flow")
        assert bb.has_edge(0, 1)
        assert not bb.has_edge(1, 2)


# ========================================================================
# Tests: Strongest-N Ties (per-node)
# ========================================================================

class TestStrongestNTies:
    """Tests for the per-node strongest-n-ties backbone."""

    def test_n1_on_path(self):
        """Each node keeps its single strongest edge."""
        G = _make_path_weighted(5)
        # Weights: 10, 20, 30, 40
        bb = strongest_n_ties(G, n=1)
        # Node 0 (deg 1): keeps (0,1,10)
        # Node 1: keeps (1,2,20)
        # Node 2: keeps (2,3,30)
        # Node 3: keeps (3,4,40)
        # Node 4 (deg 1): keeps (3,4,40)
        # Unique edges kept: (1,2), (2,3), (3,4) — and (0,1) by node 0
        assert bb.has_edge(3, 4)
        assert bb.has_edge(2, 3)
        assert bb.has_edge(0, 1)  # node 0 only has this edge

    def test_n1_on_triangle(self):
        """In a triangle with weights 1, 2, 3, n=1 keeps the two strongest."""
        G = _make_triangle_unequal()
        bb = strongest_n_ties(G, n=1)
        # A picks (A,C,3), B picks (B,C,2), C picks (A,C,3)
        assert bb.has_edge("A", "C")
        assert bb.has_edge("B", "C")
        # (A,B,1) is nobody's strongest
        assert not bb.has_edge("A", "B")

    def test_n2_on_triangle_keeps_all(self):
        """n=2 on a triangle (max deg 2) keeps everything."""
        G = _make_triangle_unequal()
        bb = strongest_n_ties(G, n=2)
        assert bb.number_of_edges() == 3

    def test_n_exceeds_degree(self):
        """If n > max degree, all edges are retained."""
        G = _make_path_weighted(5)
        bb = strongest_n_ties(G, n=100)
        assert bb.number_of_edges() == G.number_of_edges()

    def test_n1_star_keeps_hub(self):
        """In a star, each spoke's strongest edge is to the hub."""
        G = _make_star_undirected(n=6, hub_weight=100, spoke_weight=5)
        bb = strongest_n_ties(G, n=1)
        # Every spoke should keep its hub edge
        for i in range(1, 6):
            assert bb.has_edge(0, i)

    def test_preserves_all_nodes(self):
        G = _make_two_cluster_undirected()
        bb = strongest_n_ties(G, n=1)
        assert set(bb.nodes()) == set(G.nodes())

    def test_directed_n1(self):
        """Directed: per-node strongest based on out-edges."""
        G = _make_star_directed(n=4, hub_weight=100, spoke_weight=5)
        bb = strongest_n_ties(G, n=1)
        assert bb.is_directed()
        # Hub 0 has out-edges to 1,2,3 all with w=100, picks 1 (arbitrary but consistent)
        # Each spoke i has out-edge to next spoke with w=5 — that's its only out-edge
        out_0 = list(bb.successors(0))
        assert len(out_0) == 1  # n=1 → hub keeps only one

    def test_directed_n2(self):
        G = _make_star_directed(n=4, hub_weight=100, spoke_weight=5)
        bb = strongest_n_ties(G, n=2)
        out_0 = list(bb.successors(0))
        assert len(out_0) == 2

    def test_invalid_n(self):
        G = _make_triangle_unequal()
        with pytest.raises(ValueError):
            strongest_n_ties(G, n=0)

    def test_n1_uniform_weights(self):
        """With uniform weights, each node still keeps exactly 1 edge."""
        G = _make_complete_uniform(5, w=10)
        bb = strongest_n_ties(G, n=1)
        # Each of 5 nodes picks 1 edge → at most 5 edges, but edges are
        # shared so could be fewer.  Every node must have degree ≥ 1.
        for node in bb.nodes():
            assert bb.degree(node) >= 1
        assert bb.number_of_edges() <= 5

    def test_preserves_edge_attributes(self):
        G = nx.Graph()
        G.add_edge(0, 1, weight=10, label="a")
        G.add_edge(0, 2, weight=20, label="b")
        bb = strongest_n_ties(G, n=1)
        # Node 0 picks (0,2) with w=20
        assert bb.has_edge(0, 2)
        assert bb[0][2]["label"] == "b"

    def test_disconnected_components(self):
        G = _make_disconnected()
        bb = strongest_n_ties(G, n=1)
        # Each component has 1 edge, both should survive
        assert bb.has_edge(0, 1)
        assert bb.has_edge(2, 3)

    def test_single_edge_graph(self):
        G = _make_single_edge()
        bb = strongest_n_ties(G, n=1)
        assert bb.has_edge("x", "y")

    def test_custom_weight_key(self):
        G = nx.Graph()
        G.add_edge(0, 1, capacity=100)
        G.add_edge(0, 2, capacity=5)
        G.add_edge(1, 2, capacity=50)
        bb = strongest_n_ties(G, n=1, weight="capacity")
        assert bb.has_edge(0, 1)


# ========================================================================
# Tests: Disparity Filter (statistical)
# ========================================================================

class TestDisparityFilter:
    """Tests for the Serrano et al. disparity filter."""

    def test_pvalues_added(self):
        G = _make_two_cluster_undirected()
        H = disparity_filter(G)
        for u, v, d in H.edges(data=True):
            assert "disparity_pvalue" in d
            assert 0 <= d["disparity_pvalue"] <= 1

    def test_preserves_original_attributes(self):
        G = _make_two_cluster_undirected()
        H = disparity_filter(G)
        for u, v, d in H.edges(data=True):
            assert "weight" in d

    def test_preserves_graph_structure(self):
        G = _make_two_cluster_undirected()
        H = disparity_filter(G)
        assert H.number_of_nodes() == G.number_of_nodes()
        assert H.number_of_edges() == G.number_of_edges()

    def test_uniform_weights_zero_pvalues(self):
        """In a complete graph with uniform weights, all edges get p=0.

        For K5 each node has degree k=4, strength s=40, each edge w=10.
        Normalised weight p = 10/40 = 0.25.  The disparity p-value is
        alpha = 1 - (k-1)*(1-p)^(k-2) = 1 - 3*0.75^2 = -0.6875, clamped
        to 0.  This means every edge is "maximally significant" — the
        disparity filter cannot distinguish edges when weights are uniform.
        """
        G = _make_complete_uniform(5, 10)
        H = disparity_filter(G)
        for u, v, d in H.edges(data=True):
            assert d["disparity_pvalue"] == 0.0
        # All edges pass: 0.0 < 0.01 is True, so all 10 edges remain
        bb = threshold_filter(H, "disparity_pvalue", 0.01, "below")
        assert bb.number_of_edges() == 10
        # But strict < 0.0 keeps nothing (no pvalue is negative)
        bb2 = threshold_filter(H, "disparity_pvalue", 0.0, "below")
        assert bb2.number_of_edges() == 0

    def test_multiscale_significance(self):
        """The bridge in a two-cluster graph should have low p-value
        from node 3's perspective (it's the only link to the other side)
        but high p-value from node 4's perspective (it's much weaker than
        the intra-cluster edges)."""
        G = _make_two_cluster_undirected()
        H = disparity_filter(G)
        # We just verify the bridge has *some* p-value < 1
        bridge_pval = H[3][4]["disparity_pvalue"]
        assert bridge_pval < 1.0

    def test_degree_one_node_pvalue_is_one(self):
        """A degree-1 node's only edge should get pvalue=1 (always expected)."""
        G = nx.Graph()
        G.add_edge(0, 1, weight=100)
        G.add_edge(1, 2, weight=50)
        H = disparity_filter(G)
        # From node 0 (degree 1): pvalue = 1.0
        # From node 2 (degree 1): pvalue = 1.0
        # Edge (0,1) pvalue = min(1.0, pval_from_node1)
        # Edge (1,2) pvalue = min(pval_from_node1, 1.0)
        # Node 1 has degree 2, strength 150
        # For edge (0,1): p=100/150, alpha = 1 - (2-1)*(1-100/150)^(2-2) = 1-1 = 0
        p01 = H[0][1]["disparity_pvalue"]
        p12 = H[1][2]["disparity_pvalue"]
        # Since node 0 and 2 are degree-1, both edges' pvalues come from node 1
        assert p01 < 1.0  # 100/150 is large proportion → small p-value
        assert p12 < 1.0

    def test_directed_graph(self):
        G = _make_two_cluster_directed()
        H = disparity_filter(G)
        assert H.is_directed()
        for u, v, d in H.edges(data=True):
            assert "disparity_pvalue" in d
            assert 0 <= d["disparity_pvalue"] <= 1

    def test_directed_pvalue_from_source_only(self):
        """In directed mode, p-value depends only on the source node.

        With out-degree 2 the disparity formula gives exponent (k-2)=0,
        so (1-p)^0 = 1 for any p, and alpha = 1 - 1*1 = 0 for both edges.
        We verify both edges get the same pvalue (source-only, not dest).
        """
        G = nx.DiGraph()
        G.add_edge("a", "b", weight=10)
        G.add_edge("a", "c", weight=90)
        G.add_edge("b", "a", weight=50)
        H = disparity_filter(G)
        # Both a→b and a→c computed from node a (out-deg 2) → both pval=0
        assert H["a"]["b"]["disparity_pvalue"] == H["a"]["c"]["disparity_pvalue"]
        assert H["a"]["b"]["disparity_pvalue"] == 0.0

    def test_directed_pvalue_varies_with_higher_outdegree(self):
        """With out-degree ≥ 3 the disparity filter differentiates edges."""
        G = nx.DiGraph()
        G.add_edge("a", "b", weight=10)
        G.add_edge("a", "c", weight=10)
        G.add_edge("a", "d", weight=80)
        H = disparity_filter(G)
        # Node a: out-deg=3, out-str=100
        # a→d: p=0.8, alpha = 1 - 2*(1-0.8)^1 = 1-0.4 = 0.6
        # a→b: p=0.1, alpha = 1 - 2*(1-0.1)^1 = 1-1.8 → clamped to 0
        assert H["a"]["d"]["disparity_pvalue"] > H["a"]["b"]["disparity_pvalue"]

    def test_raises_on_zero_weight(self):
        G = nx.Graph()
        G.add_edge(0, 1, weight=0)
        with pytest.raises(nx.NetworkXError):
            disparity_filter(G)

    def test_raises_on_missing_weight(self):
        G = nx.Graph()
        G.add_edge(0, 1)  # no weight attribute
        with pytest.raises(nx.NetworkXError):
            disparity_filter(G)

    def test_single_edge_pvalue(self):
        G = _make_single_edge()
        H = disparity_filter(G)
        # Both endpoints are degree 1 → pvalue = 1.0
        assert H["x"]["y"]["disparity_pvalue"] == 1.0

    def test_filtering_pipeline(self):
        """Full pipeline: disparity → threshold → verify backbone is a subgraph."""
        G = _make_two_cluster_undirected()
        H = disparity_filter(G)
        bb = threshold_filter(H, "disparity_pvalue", 0.05, "below")
        # Backbone should be a subgraph of original
        for u, v in bb.edges():
            assert G.has_edge(u, v)
        assert bb.number_of_edges() <= G.number_of_edges()


# ========================================================================
# Tests: High Salience Skeleton
# ========================================================================

class TestHighSalienceSkeleton:
    """Tests for the shortest-path-tree-based salience scoring."""

    def test_salience_scores_added(self):
        G = _make_two_cluster_undirected()
        H = high_salience_skeleton(G)
        for u, v, d in H.edges(data=True):
            assert "salience" in d
            assert 0 <= d["salience"] <= 1

    def test_bridge_has_high_salience(self):
        """The bridge between two clusters should have high salience
        because it appears in many shortest-path trees."""
        G = _make_two_cluster_undirected()
        H = high_salience_skeleton(G)
        bridge_sal = H[3][4]["salience"]
        # The bridge is on the shortest path between any node in A
        # and any node in B, so it should appear in many SPTs.
        assert bridge_sal > 0.5

    def test_path_graph_all_high_salience(self):
        """In a path graph every edge is on every shortest path → high salience."""
        G = _make_path_weighted(5)
        H = high_salience_skeleton(G)
        for u, v, d in H.edges(data=True):
            assert d["salience"] > 0.3

    def test_complete_uniform_moderate_salience(self):
        """In K5 with uniform weights, salience should be moderate (not 0)."""
        G = _make_complete_uniform(5, 10)
        H = high_salience_skeleton(G)
        saliences = [d["salience"] for _, _, d in H.edges(data=True)]
        # Should be uniform across edges due to symmetry
        assert max(saliences) - min(saliences) < 0.01

    def test_raises_on_directed(self):
        G = _make_two_cluster_directed()
        with pytest.raises(nx.NetworkXError):
            high_salience_skeleton(G)

    def test_filtering_at_08(self):
        G = _make_two_cluster_undirected()
        H = high_salience_skeleton(G)
        bb = threshold_filter(H, "salience", 0.8, "above")
        # Backbone is a subgraph
        assert bb.number_of_edges() <= G.number_of_edges()


# ========================================================================
# Tests: Metric and Ultrametric Backbone
# ========================================================================

class TestMetricBackbone:
    """Tests for metric (sum-distance) backbone."""

    def test_path_graph_is_own_backbone(self):
        """Every edge in a path graph is a shortest path → all are metric."""
        G = _make_path_weighted(5)
        bb = metric_backbone(G)
        assert bb.number_of_edges() == G.number_of_edges()

    def test_triangle_removes_weakest(self):
        """In triangle A-B-C with w(AB)=1, w(BC)=2, w(AC)=3:
        dist(AB)=1, dist(BC)=0.5, dist(AC)=0.333.
        Shortest A→B via C: dist(AC)+dist(CB) = 0.333+0.5 = 0.833 < 1.0
        So direct A-B path is NOT shortest → (A,B) removed from metric backbone."""
        G = _make_triangle_unequal()
        bb = metric_backbone(G)
        assert not bb.has_edge("A", "B")
        assert bb.has_edge("A", "C")
        assert bb.has_edge("B", "C")

    def test_complete_uniform_is_spanning_tree(self):
        """In K_n with uniform weights, all shortest paths have equal length.
        Every direct edge is a shortest path → all edges are metric."""
        G = _make_complete_uniform(4, 10)
        bb = metric_backbone(G)
        # Actually with uniform weights d=1/10 for all edges, and the
        # direct path (length 1/10) is always <= any multi-hop path
        # (length >= 2/10). So all edges should be in the backbone.
        assert bb.number_of_edges() == G.number_of_edges()

    def test_raises_on_directed(self):
        G = _make_two_cluster_directed()
        with pytest.raises(nx.NetworkXError):
            metric_backbone(G)

    def test_is_subgraph(self):
        G = _make_two_cluster_undirected()
        bb = metric_backbone(G)
        for u, v in bb.edges():
            assert G.has_edge(u, v)


class TestUltrametricBackbone:
    """Tests for ultrametric (max-distance) backbone."""

    def test_path_graph(self):
        G = _make_path_weighted(5)
        bb = ultrametric_backbone(G)
        # In a path, the ultrametric path (minimax) between adjacent
        # nodes is just the direct edge itself, so all edges are kept.
        assert bb.number_of_edges() == G.number_of_edges()

    def test_is_subgraph(self):
        G = _make_two_cluster_undirected()
        bb = ultrametric_backbone(G)
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_raises_on_directed(self):
        G = _make_two_cluster_directed()
        with pytest.raises(nx.NetworkXError):
            ultrametric_backbone(G)


# ========================================================================
# Tests: Maximum Spanning Tree Backbone
# ========================================================================

class TestMaximumSpanningTreeBackbone:

    def test_is_tree(self):
        G = _make_two_cluster_undirected()
        bb = maximum_spanning_tree_backbone(G)
        assert nx.is_tree(bb)

    def test_has_n_minus_1_edges(self):
        G = _make_two_cluster_undirected()
        bb = maximum_spanning_tree_backbone(G)
        assert bb.number_of_edges() == G.number_of_nodes() - 1

    def test_preserves_all_nodes(self):
        G = _make_two_cluster_undirected()
        bb = maximum_spanning_tree_backbone(G)
        assert set(bb.nodes()) == set(G.nodes())

    def test_maximises_total_weight(self):
        G = _make_triangle_unequal()
        bb = maximum_spanning_tree_backbone(G)
        # MST should keep the two heaviest edges: (A,C,3) and (B,C,2)
        total = sum(d["weight"] for _, _, d in bb.edges(data=True))
        assert total == 5  # 3 + 2

    def test_raises_on_directed(self):
        G = _make_two_cluster_directed()
        with pytest.raises(nx.NetworkXError):
            maximum_spanning_tree_backbone(G)


# ========================================================================
# Tests: Filtering Utilities
# ========================================================================

class TestThresholdFilter:

    def test_below_mode(self):
        G = nx.Graph()
        G.add_edge(0, 1, pval=0.01)
        G.add_edge(1, 2, pval=0.5)
        bb = threshold_filter(G, "pval", 0.05, mode="below")
        assert bb.has_edge(0, 1)
        assert not bb.has_edge(1, 2)

    def test_above_mode(self):
        G = nx.Graph()
        G.add_edge(0, 1, score=0.9)
        G.add_edge(1, 2, score=0.3)
        bb = threshold_filter(G, "score", 0.5, mode="above")
        assert bb.has_edge(0, 1)
        assert not bb.has_edge(1, 2)

    def test_node_filter(self):
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

    def test_preserves_all_nodes_for_edge_filter(self):
        G = nx.Graph()
        G.add_node("isolated")
        G.add_edge(0, 1, score=0.9)
        bb = threshold_filter(G, "score", 0.5, mode="above")
        assert "isolated" in bb.nodes()

    def test_invalid_mode(self):
        G = nx.Graph()
        with pytest.raises(ValueError):
            threshold_filter(G, "x", 0.5, mode="invalid")


class TestFractionFilter:

    def test_fraction_half(self):
        G = nx.Graph()
        G.add_edge(0, 1, score=0.1)
        G.add_edge(1, 2, score=0.5)
        G.add_edge(2, 3, score=0.9)
        G.add_edge(3, 4, score=0.3)
        # Keep lowest 50% → 2 edges with smallest scores
        bb = fraction_filter(G, "score", 0.5, ascending=True)
        assert bb.number_of_edges() == 2
        assert bb.has_edge(0, 1)  # score=0.1
        assert bb.has_edge(3, 4)  # score=0.3

    def test_fraction_keeps_highest(self):
        G = nx.Graph()
        G.add_edge(0, 1, score=0.1)
        G.add_edge(1, 2, score=0.9)
        G.add_edge(2, 3, score=0.5)
        bb = fraction_filter(G, "score", 0.34, ascending=False)
        # 34% of 3 edges → 1 edge, highest score
        assert bb.number_of_edges() == 1
        assert bb.has_edge(1, 2)

    def test_fraction_one_keeps_all(self):
        G = _make_triangle_unequal()
        for u, v, d in G.edges(data=True):
            d["score"] = d["weight"]
        bb = fraction_filter(G, "score", 1.0, ascending=True)
        assert bb.number_of_edges() == 3

    def test_invalid_fraction(self):
        G = nx.Graph()
        with pytest.raises(ValueError):
            fraction_filter(G, "score", 0.0)
        with pytest.raises(ValueError):
            fraction_filter(G, "score", 1.5)


class TestBooleanFilter:

    def test_basic(self):
        G = nx.Graph()
        G.add_edge(0, 1, keep=True)
        G.add_edge(1, 2, keep=False)
        G.add_edge(2, 3, keep=True)
        bb = boolean_filter(G, "keep")
        assert bb.has_edge(0, 1)
        assert not bb.has_edge(1, 2)
        assert bb.has_edge(2, 3)

    def test_preserves_nodes(self):
        G = nx.Graph()
        G.add_node("extra")
        G.add_edge(0, 1, keep=True)
        bb = boolean_filter(G, "keep")
        assert "extra" in bb.nodes()


class TestConsensusBackbone:

    def test_intersection(self):
        G1 = nx.Graph()
        G1.add_edge(0, 1, weight=10)
        G1.add_edge(1, 2, weight=20)

        G2 = nx.Graph()
        G2.add_edge(1, 2, weight=20)
        G2.add_edge(2, 3, weight=30)

        cc = consensus_backbone(G1, G2)
        assert cc.has_edge(1, 2)
        assert cc.number_of_edges() == 1

    def test_three_graphs(self):
        G1 = nx.Graph([(0, 1), (1, 2), (2, 3)])
        G2 = nx.Graph([(0, 1), (1, 2)])
        G3 = nx.Graph([(1, 2), (2, 3), (3, 4)])
        cc = consensus_backbone(G1, G2, G3)
        assert cc.number_of_edges() == 1
        assert cc.has_edge(1, 2)

    def test_directed(self):
        G1 = nx.DiGraph([(0, 1), (1, 2)])
        G2 = nx.DiGraph([(1, 0), (1, 2)])
        cc = consensus_backbone(G1, G2)
        # Only (1,2) is common in same direction
        assert cc.has_edge(1, 2)
        assert not cc.has_edge(0, 1)  # G2 has (1,0) not (0,1)

    def test_requires_two_graphs(self):
        G1 = nx.Graph([(0, 1)])
        with pytest.raises(ValueError):
            consensus_backbone(G1)


# ========================================================================
# Tests: Evaluation Measures
# ========================================================================

class TestMeasures:

    def test_node_fraction_full(self):
        G = _make_triangle_unequal()
        assert node_fraction(G, G) == 1.0

    def test_node_fraction_partial(self):
        G = _make_path_weighted(5)
        bb = nx.Graph()
        bb.add_nodes_from(G.nodes())
        bb.add_edge(0, 1, weight=10)
        # Only nodes 0,1 have edges in backbone; original has 5
        assert node_fraction(G, bb) == pytest.approx(2 / 5)

    def test_edge_fraction(self):
        G = _make_path_weighted(5)  # 4 edges
        bb = nx.Graph()
        bb.add_nodes_from(G.nodes())
        bb.add_edge(0, 1, weight=10)
        bb.add_edge(3, 4, weight=40)
        assert edge_fraction(G, bb) == pytest.approx(2 / 4)

    def test_weight_fraction(self):
        G = _make_path_weighted(5)  # weights: 10+20+30+40 = 100
        bb = nx.Graph()
        bb.add_nodes_from(G.nodes())
        bb.add_edge(3, 4, weight=40)
        assert weight_fraction(G, bb) == pytest.approx(40 / 100)

    def test_reachability_connected(self):
        G = _make_two_cluster_undirected()
        assert reachability(G) == pytest.approx(1.0)

    def test_reachability_disconnected(self):
        G = _make_disconnected()  # (0,1) and (2,3) — two components of size 2
        # Reachable pairs: 1*2 + 1*2 = 2+2 = 4 (directed pairs)
        # Total pairs: 4*3 = 12
        assert reachability(G) == pytest.approx(4 / 12)

    def test_reachability_isolated(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2])
        # No edges → 0 reachable pairs
        assert reachability(G) == pytest.approx(0.0)

    def test_reachability_single_node(self):
        G = _make_single_node()
        assert reachability(G) == 1.0

    def test_compare_backbones(self):
        G = _make_path_weighted(5)
        bb1 = global_threshold_filter(G, threshold=25)
        bb2 = strongest_n_ties(G, n=1)
        results = compare_backbones(
            G,
            {"threshold": bb1, "strongest1": bb2},
            measures=[node_fraction, edge_fraction, weight_fraction],
        )
        assert "threshold" in results
        assert "strongest1" in results
        assert "node_fraction" in results["threshold"]
        assert 0 <= results["threshold"]["edge_fraction"] <= 1


# ========================================================================
# Tests: End-to-end pipelines
# ========================================================================

class TestEndToEndPipelines:
    """Integration tests combining multiple backbone methods and filters."""

    def test_disparity_then_threshold_is_subgraph(self):
        G = _make_two_cluster_undirected()
        H = disparity_filter(G)
        bb = threshold_filter(H, "disparity_pvalue", 0.05, "below")
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_salience_then_fraction(self):
        G = _make_two_cluster_undirected()
        H = high_salience_skeleton(G)
        bb = fraction_filter(H, "salience", 0.3, ascending=False)
        assert bb.number_of_edges() > 0
        assert bb.number_of_edges() <= G.number_of_edges()

    def test_consensus_of_multiple_methods(self):
        G = _make_two_cluster_undirected()
        bb_thresh = global_threshold_filter(G, threshold=5)
        bb_strong = strongest_n_ties(G, n=2)
        cc = consensus_backbone(bb_thresh, bb_strong)
        # Consensus edges must be in both
        for u, v in cc.edges():
            assert bb_thresh.has_edge(u, v)
            assert bb_strong.has_edge(u, v)

    def test_compare_multiple_backbones(self):
        G = _make_two_cluster_undirected()
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

    def test_directed_pipeline(self):
        """Full pipeline on a directed graph: disparity → threshold."""
        G = _make_two_cluster_directed()
        H = disparity_filter(G)
        bb = threshold_filter(H, "disparity_pvalue", 0.1, "below")
        assert bb.is_directed()
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_backbone_sparser_than_original(self):
        """Any reasonable backbone should be sparser than the original."""
        G = _make_two_cluster_undirected()
        bb = global_threshold_filter(G, threshold=50)
        assert bb.number_of_edges() < G.number_of_edges()

    def test_monotonicity_of_threshold(self):
        """Increasing threshold should monotonically decrease edges."""
        G = _make_two_cluster_undirected()
        prev_edges = G.number_of_edges() + 1
        for t in [0, 1, 5, 10, 50, 100, 200]:
            bb = global_threshold_filter(G, threshold=t)
            assert bb.number_of_edges() <= prev_edges
            prev_edges = bb.number_of_edges()

    def test_monotonicity_of_strongest_n(self):
        """Increasing n should monotonically increase edges."""
        G = _make_two_cluster_undirected()
        prev_edges = 0
        for n in [1, 2, 3, 4, 5]:
            bb = strongest_n_ties(G, n=n)
            assert bb.number_of_edges() >= prev_edges
            prev_edges = bb.number_of_edges()


# ========================================================================
# Tests: Edge Cases and Robustness
# ========================================================================

class TestEdgeCases:
    """Edge cases: empty graphs, single nodes, etc."""

    def test_global_threshold_empty_graph(self):
        G = nx.Graph()
        bb = global_threshold_filter(G, threshold=0)
        assert bb.number_of_nodes() == 0

    def test_strongest_n_no_edges(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2])
        bb = strongest_n_ties(G, n=1)
        assert bb.number_of_edges() == 0
        assert set(bb.nodes()) == {0, 1, 2}

    def test_disparity_on_single_edge(self):
        G = _make_single_edge()
        H = disparity_filter(G)
        # Both nodes degree 1 → pvalue = 1.0
        assert H["x"]["y"]["disparity_pvalue"] == 1.0

    def test_measures_on_empty_backbone(self):
        G = _make_two_cluster_undirected()
        bb = nx.Graph()
        bb.add_nodes_from(G.nodes())
        assert edge_fraction(G, bb) == 0.0
        assert weight_fraction(G, bb) == 0.0
        assert node_fraction(G, bb) == 0.0

    def test_reachability_directed(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        G.add_edge(2, 3)
        # Weakly connected components: {0,1} and {2,3}
        r = reachability(G)
        assert r == pytest.approx(4 / 12)

    def test_large_graph_smoke(self):
        """Smoke test on a moderately sized graph (200 nodes)."""
        G = nx.barabasi_albert_graph(200, 3, seed=42)
        for u, v in G.edges():
            G[u][v]["weight"] = abs(hash((u, v))) % 100 + 1
        # Should run without errors
        bb1 = global_threshold_filter(G, threshold=50)
        bb2 = strongest_n_ties(G, n=2)
        H = disparity_filter(G)
        bb3 = threshold_filter(H, "disparity_pvalue", 0.05, "below")
        assert bb1.number_of_edges() < G.number_of_edges()
        assert bb2.number_of_edges() < G.number_of_edges()
        assert bb3.number_of_edges() < G.number_of_edges()

    def test_self_loop_handling(self):
        """Self-loops should be handled gracefully."""
        G = nx.Graph()
        G.add_edge(0, 0, weight=5)
        G.add_edge(0, 1, weight=10)
        bb = global_threshold_filter(G, threshold=7)
        assert bb.has_edge(0, 1)
        assert not bb.has_edge(0, 0)


# ========================================================================
# Tests: Noise-Corrected Filter (statistical)
# ========================================================================

class TestNoiseCorrectedFilter:
    """Tests for the Coscia & Neffke noise-corrected filter."""

    def test_scores_added(self):
        G = _make_two_cluster_undirected()
        H = noise_corrected_filter(G)
        for u, v, d in H.edges(data=True):
            assert "nc_score" in d

    def test_preserves_structure(self):
        G = _make_two_cluster_undirected()
        H = noise_corrected_filter(G)
        assert H.number_of_nodes() == G.number_of_nodes()
        assert H.number_of_edges() == G.number_of_edges()

    def test_strong_edges_score_higher(self):
        """Edges in the heavy cluster should score higher than the bridge."""
        G = _make_two_cluster_undirected()
        H = noise_corrected_filter(G)
        bridge_score = H[3][4]["nc_score"]
        cluster_b_score = H[4][5]["nc_score"]
        assert cluster_b_score > bridge_score

    def test_directed(self):
        G = _make_two_cluster_directed()
        H = noise_corrected_filter(G)
        assert H.is_directed()
        for u, v, d in H.edges(data=True):
            assert "nc_score" in d

    def test_filtering_pipeline(self):
        G = _make_two_cluster_undirected()
        H = noise_corrected_filter(G)
        bb = threshold_filter(H, "nc_score", 2.0, "above")
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_uniform_weights_low_scores(self):
        """Uniform weights should yield scores near 0 (nothing unexpected)."""
        G = _make_complete_uniform(5, 10)
        H = noise_corrected_filter(G)
        scores = [d["nc_score"] for _, _, d in H.edges(data=True)]
        # All scores should be similar (symmetric graph)
        assert max(scores) - min(scores) < 1e-6


# ========================================================================
# Tests: Marginal Likelihood Filter (statistical)
# ========================================================================

class TestMarginalLikelihoodFilter:
    """Tests for the Dianati marginal likelihood filter."""

    def test_pvalues_added(self):
        G = _make_two_cluster_undirected()
        H = marginal_likelihood_filter(G)
        for u, v, d in H.edges(data=True):
            assert "ml_pvalue" in d
            assert 0 <= d["ml_pvalue"] <= 1

    def test_preserves_structure(self):
        G = _make_two_cluster_undirected()
        H = marginal_likelihood_filter(G)
        assert H.number_of_edges() == G.number_of_edges()

    def test_heavy_edges_significant(self):
        """Cluster B edges (w=100) should generally be significant."""
        G = _make_two_cluster_undirected()
        H = marginal_likelihood_filter(G)
        # Just verify the bridge (w=1) gets a high p-value (not significant)
        bridge_pval = H[3][4]["ml_pvalue"]
        assert bridge_pval > 0.5

    def test_directed(self):
        G = _make_two_cluster_directed()
        H = marginal_likelihood_filter(G)
        assert H.is_directed()
        for u, v, d in H.edges(data=True):
            assert "ml_pvalue" in d

    def test_single_edge(self):
        G = _make_single_edge()
        H = marginal_likelihood_filter(G)
        assert "ml_pvalue" in H["x"]["y"]


# ========================================================================
# Tests: ECM Filter (statistical)
# ========================================================================

class TestECMFilter:
    """Tests for the Enhanced Configuration Model filter."""

    def test_pvalues_added(self):
        G = _make_triangle_unequal()
        H = ecm_filter(G)
        for u, v, d in H.edges(data=True):
            assert "ecm_pvalue" in d
            assert 0 <= d["ecm_pvalue"] <= 1

    def test_preserves_structure(self):
        G = _make_triangle_unequal()
        H = ecm_filter(G)
        assert H.number_of_edges() == G.number_of_edges()

    def test_directed(self):
        G = _make_two_cluster_directed()
        H = ecm_filter(G)
        assert H.is_directed()
        for u, v, d in H.edges(data=True):
            assert "ecm_pvalue" in d

    def test_small_graph(self):
        """Should work on very small graphs without crashing."""
        G = _make_single_edge()
        H = ecm_filter(G)
        assert "ecm_pvalue" in H["x"]["y"]


# ========================================================================
# Tests: LANS Filter (statistical)
# ========================================================================

class TestLANSFilter:
    """Tests for the Locally Adaptive Network Sparsification filter."""

    def test_pvalues_added(self):
        G = _make_two_cluster_undirected()
        H = lans_filter(G)
        for u, v, d in H.edges(data=True):
            assert "lans_pvalue" in d
            assert 0 <= d["lans_pvalue"] <= 1

    def test_strongest_edge_most_significant(self):
        """In a triangle, the strongest edge should have the lowest p-value."""
        G = _make_triangle_unequal()
        H = lans_filter(G)
        pvals = {(u, v): d["lans_pvalue"] for u, v, d in H.edges(data=True)}
        # (A,C) has weight 3 (strongest) → should be most significant
        ac_pval = pvals.get(("A", "C"), pvals.get(("C", "A")))
        ab_pval = pvals.get(("A", "B"), pvals.get(("B", "A")))
        assert ac_pval <= ab_pval

    def test_directed(self):
        G = _make_two_cluster_directed()
        H = lans_filter(G)
        assert H.is_directed()
        for u, v, d in H.edges(data=True):
            assert "lans_pvalue" in d

    def test_preserves_structure(self):
        G = _make_two_cluster_undirected()
        H = lans_filter(G)
        assert H.number_of_edges() == G.number_of_edges()

    def test_filtering_pipeline(self):
        G = _make_two_cluster_undirected()
        H = lans_filter(G)
        bb = threshold_filter(H, "lans_pvalue", 0.3, "below")
        for u, v in bb.edges():
            assert G.has_edge(u, v)


# ========================================================================
# Tests: Doubly Stochastic Filter (structural)
# ========================================================================

class TestDoublyStochasticFilter:
    """Tests for the Sinkhorn-Knopp doubly-stochastic backbone."""

    def test_ds_weight_added(self):
        G = _make_two_cluster_undirected()
        H = doubly_stochastic_filter(G)
        for u, v, d in H.edges(data=True):
            assert "ds_weight" in d
            assert d["ds_weight"] >= 0

    def test_preserves_structure(self):
        G = _make_two_cluster_undirected()
        H = doubly_stochastic_filter(G)
        assert H.number_of_nodes() == G.number_of_nodes()
        assert H.number_of_edges() == G.number_of_edges()

    def test_complete_uniform_symmetric(self):
        """K5 with uniform weights: all ds_weights should be equal."""
        G = _make_complete_uniform(5, 10)
        H = doubly_stochastic_filter(G)
        weights = [d["ds_weight"] for _, _, d in H.edges(data=True)]
        assert max(weights) - min(weights) < 1e-4

    def test_raises_on_directed(self):
        G = _make_two_cluster_directed()
        with pytest.raises(nx.NetworkXError):
            doubly_stochastic_filter(G)

    def test_filtering_by_ds_weight(self):
        G = _make_two_cluster_undirected()
        H = doubly_stochastic_filter(G)
        bb = threshold_filter(H, "ds_weight", 0.1, "above")
        assert bb.number_of_edges() <= G.number_of_edges()


# ========================================================================
# Tests: h-backbone (structural)
# ========================================================================

class TestHBackbone:
    """Tests for the h-index inspired backbone."""

    def test_is_subgraph(self):
        G = _make_two_cluster_undirected()
        bb = h_backbone(G)
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_nonempty(self):
        G = _make_two_cluster_undirected()
        bb = h_backbone(G)
        assert bb.number_of_edges() > 0

    def test_preserves_nodes(self):
        G = _make_two_cluster_undirected()
        bb = h_backbone(G)
        assert set(bb.nodes()) == set(G.nodes())

    def test_triangle(self):
        G = _make_triangle_unequal()
        bb = h_backbone(G)
        # h-index: weights [3,2,1] sorted desc → h=1 (1 edge with w>=1) or h=2 (2 edges with w>=2)
        # Actually: w[0]=3>=1, w[1]=2>=2, w[2]=1<3 → h=2
        # h-strength: edges with weight >= 2: (A,C,3) and (B,C,2)
        assert bb.has_edge("A", "C")
        assert bb.has_edge("B", "C")

    def test_raises_on_directed(self):
        G = _make_two_cluster_directed()
        with pytest.raises(nx.NetworkXError):
            h_backbone(G)


# ========================================================================
# Tests: Modularity Backbone (structural)
# ========================================================================

class TestModularityBackbone:
    """Tests for the modularity vitality backbone."""

    def test_vitality_added(self):
        G = _make_two_cluster_undirected()
        H = modularity_backbone(G)
        for node in H.nodes():
            assert "vitality" in H.nodes[node]

    def test_preserves_structure(self):
        G = _make_two_cluster_undirected()
        H = modularity_backbone(G)
        assert H.number_of_nodes() == G.number_of_nodes()
        assert H.number_of_edges() == G.number_of_edges()

    def test_node_filtering(self):
        """Can filter nodes by vitality."""
        G = _make_two_cluster_undirected()
        H = modularity_backbone(G)
        bb = threshold_filter(H, "vitality", 0.0, "above", filter_on="nodes")
        assert bb.number_of_nodes() <= G.number_of_nodes()

    def test_raises_on_directed(self):
        G = _make_two_cluster_directed()
        with pytest.raises(nx.NetworkXError):
            modularity_backbone(G)


# ========================================================================
# Tests: Planar Maximally Filtered Graph (structural)
# ========================================================================

class TestPlanarMaximallyFilteredGraph:
    """Tests for the PMFG."""

    def test_is_planar(self):
        G = _make_two_cluster_undirected()
        bb = planar_maximally_filtered_graph(G)
        is_planar, _ = nx.check_planarity(bb)
        assert is_planar

    def test_is_subgraph(self):
        G = _make_two_cluster_undirected()
        bb = planar_maximally_filtered_graph(G)
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_max_edges(self):
        """A planar graph on n nodes has at most 3(n-2) edges."""
        G = _make_two_cluster_undirected()
        bb = planar_maximally_filtered_graph(G)
        n = bb.number_of_nodes()
        assert bb.number_of_edges() <= 3 * (n - 2)

    def test_prefers_heavy_edges(self):
        """PMFG should include the heaviest edges."""
        G = _make_two_cluster_undirected()
        bb = planar_maximally_filtered_graph(G)
        # Cluster B edges (w=100) should all be in the PMFG
        for i in range(4, 8):
            for j in range(i + 1, 8):
                assert bb.has_edge(i, j)

    def test_raises_on_directed(self):
        G = _make_two_cluster_directed()
        with pytest.raises(nx.NetworkXError):
            planar_maximally_filtered_graph(G)

    def test_small_graph(self):
        """Triangle: always planar, all edges kept."""
        G = _make_triangle_unequal()
        bb = planar_maximally_filtered_graph(G)
        assert bb.number_of_edges() == 3

    def test_preserves_edge_attributes(self):
        G = _make_triangle_unequal()
        bb = planar_maximally_filtered_graph(G)
        for u, v, d in bb.edges(data=True):
            assert "weight" in d


# ========================================================================
# Tests: GLAB Filter (hybrid)
# ========================================================================

class TestGLABFilter:
    """Tests for the Globally and Locally Adaptive Backbone."""

    def test_pvalues_added(self):
        G = _make_two_cluster_undirected()
        H = glab_filter(G)
        for u, v, d in H.edges(data=True):
            assert "glab_pvalue" in d
            assert 0 <= d["glab_pvalue"] <= 1

    def test_preserves_structure(self):
        G = _make_two_cluster_undirected()
        H = glab_filter(G)
        assert H.number_of_nodes() == G.number_of_nodes()
        assert H.number_of_edges() == G.number_of_edges()

    def test_bridge_significant(self):
        """The bridge between clusters should be significant (high betweenness)."""
        G = _make_two_cluster_undirected()
        H = glab_filter(G)
        bridge_pval = H[3][4]["glab_pvalue"]
        # Bridge has very high betweenness → should have low p-value
        assert bridge_pval < 0.5

    def test_c_parameter(self):
        """Different c values should produce different scores."""
        G = _make_two_cluster_undirected()
        H1 = glab_filter(G, c=0.0)
        H2 = glab_filter(G, c=1.0)
        pvals1 = [d["glab_pvalue"] for _, _, d in H1.edges(data=True)]
        pvals2 = [d["glab_pvalue"] for _, _, d in H2.edges(data=True)]
        assert pvals1 != pvals2

    def test_raises_on_directed(self):
        G = _make_two_cluster_directed()
        with pytest.raises(nx.NetworkXError):
            glab_filter(G)

    def test_filtering_pipeline(self):
        G = _make_two_cluster_undirected()
        H = glab_filter(G)
        bb = threshold_filter(H, "glab_pvalue", 0.1, "below")
        for u, v in bb.edges():
            assert G.has_edge(u, v)


# ========================================================================
# Tests: SDSM (bipartite)
# ========================================================================

def _make_bipartite():
    """Simple bipartite graph: 3 agents, 4 artifacts.

    Agent A1 connects to F1, F2, F3
    Agent A2 connects to F1, F2
    Agent A3 connects to F3, F4

    Expected: A1 and A2 co-occur on 2 artifacts (F1, F2) → significant.
    A1 and A3 co-occur on 1 artifact (F3) → less significant.
    A2 and A3 co-occur on 0 → not significant.
    """
    B = nx.Graph()
    agents = ["A1", "A2", "A3"]
    artifacts = ["F1", "F2", "F3", "F4"]
    B.add_nodes_from(agents, bipartite=0)
    B.add_nodes_from(artifacts, bipartite=1)
    B.add_edges_from([
        ("A1", "F1"), ("A1", "F2"), ("A1", "F3"),
        ("A2", "F1"), ("A2", "F2"),
        ("A3", "F3"), ("A3", "F4"),
    ])
    return B, agents


class TestSDSM:
    """Tests for the Stochastic Degree Sequence Model."""

    def test_returns_graph(self):
        B, agents = _make_bipartite()
        bb = sdsm(B, agents)
        assert isinstance(bb, nx.Graph)

    def test_agent_nodes_only(self):
        """Backbone should only contain agent nodes."""
        B, agents = _make_bipartite()
        bb = sdsm(B, agents)
        for node in bb.nodes():
            assert node in agents

    def test_pvalues_present(self):
        B, agents = _make_bipartite()
        bb = sdsm(B, agents)
        for u, v, d in bb.edges(data=True):
            assert "sdsm_pvalue" in d
            assert 0 <= d["sdsm_pvalue"] <= 1

    def test_high_cooccurrence_significant(self):
        """A1 and A2 share 2/4 artifacts — should be among the most significant."""
        B, agents = _make_bipartite()
        bb = sdsm(B, agents, alpha=1.0)  # alpha=1 → keep all for inspection
        # A1-A2 should have a lower pvalue than A2-A3 (0 co-occurrences)
        p12 = bb["A1"]["A2"]["sdsm_pvalue"]
        if bb.has_edge("A2", "A3"):
            p23 = bb["A2"]["A3"]["sdsm_pvalue"]
            assert p12 <= p23

    def test_raises_non_bipartite(self):
        G = nx.Graph([(0, 1), (1, 2), (0, 2)])  # triangle — not bipartite
        with pytest.raises(nx.NetworkXError):
            sdsm(G, [0])


# ========================================================================
# Tests: FDSM (bipartite)
# ========================================================================

class TestFDSM:
    """Tests for the Fixed Degree Sequence Model."""

    def test_returns_graph(self):
        B, agents = _make_bipartite()
        bb = fdsm(B, agents, trials=100, seed=42)
        assert isinstance(bb, nx.Graph)

    def test_agent_nodes_only(self):
        B, agents = _make_bipartite()
        bb = fdsm(B, agents, trials=100, seed=42)
        for node in bb.nodes():
            assert node in agents

    def test_pvalues_present(self):
        B, agents = _make_bipartite()
        bb = fdsm(B, agents, trials=100, seed=42)
        for u, v, d in bb.edges(data=True):
            assert "fdsm_pvalue" in d
            assert 0 <= d["fdsm_pvalue"] <= 1

    def test_reproducible_with_seed(self):
        B, agents = _make_bipartite()
        bb1 = fdsm(B, agents, trials=100, seed=42)
        bb2 = fdsm(B, agents, trials=100, seed=42)
        for u, v, d1 in bb1.edges(data=True):
            d2 = bb2[u][v]
            assert d1["fdsm_pvalue"] == d2["fdsm_pvalue"]

    def test_raises_non_bipartite(self):
        G = nx.Graph([(0, 1), (1, 2), (0, 2)])
        with pytest.raises(nx.NetworkXError):
            fdsm(G, [0])


# ========================================================================
# Tests: Unweighted backbones (sparsify, lspar, local_degree)
# ========================================================================

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


class TestSparsify:
    """Tests for the generic sparsification framework."""

    def test_jaccard_score(self):
        G = _make_unweighted_community()
        bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=0.5)
        assert 0 < bb.number_of_edges() < G.number_of_edges()

    def test_degree_score(self):
        G = _make_unweighted_community()
        bb = sparsify(G, escore="degree", normalize="rank", filter="degree", s=0.5)
        assert 0 < bb.number_of_edges() < G.number_of_edges()

    def test_triangles_score(self):
        G = _make_unweighted_community()
        bb = sparsify(G, escore="triangles", normalize="rank", filter="degree", s=0.5)
        assert bb.number_of_edges() > 0

    def test_quadrangles_score(self):
        G = _make_unweighted_community()
        bb = sparsify(G, escore="quadrangles", normalize="rank", filter="degree", s=0.5)
        assert bb.number_of_edges() > 0

    def test_random_score(self):
        G = _make_unweighted_community()
        bb = sparsify(G, escore="random", normalize="rank", filter="degree", s=0.5)
        assert bb.number_of_edges() > 0

    def test_threshold_filter_mode(self):
        G = _make_unweighted_community()
        bb = sparsify(G, escore="jaccard", normalize="rank", filter="threshold", s=0.5)
        assert bb.number_of_edges() <= G.number_of_edges()

    def test_no_normalisation(self):
        G = _make_unweighted_community()
        bb = sparsify(G, escore="jaccard", normalize=None, filter="degree", s=0.5)
        assert bb.number_of_edges() > 0

    def test_s_zero_very_sparse(self):
        """s=0 should produce a very sparse backbone."""
        G = _make_unweighted_community()
        bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=0.01)
        assert bb.number_of_edges() <= G.number_of_edges()

    def test_s_one_keeps_most(self):
        """s=1.0 with degree filter keeps ceil(d^1) = d edges per node → all."""
        G = _make_unweighted_community()
        bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=1.0)
        assert bb.number_of_edges() == G.number_of_edges()

    def test_is_subgraph(self):
        G = _make_unweighted_community()
        bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=0.5)
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_preserves_nodes(self):
        G = _make_unweighted_community()
        bb = sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=0.5)
        assert set(bb.nodes()) == set(G.nodes())

    def test_raises_on_directed(self):
        G = nx.DiGraph([(0, 1), (1, 2)])
        with pytest.raises(nx.NetworkXError):
            sparsify(G)


class TestLSpar:
    """Tests for the L-Spar convenience wrapper."""

    def test_is_subgraph(self):
        G = _make_unweighted_community()
        bb = lspar(G, s=0.5)
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_sparser_than_original(self):
        G = _make_unweighted_community()
        bb = lspar(G, s=0.5)
        assert bb.number_of_edges() < G.number_of_edges()

    def test_monotonic_in_s(self):
        """Increasing s should monotonically increase edge count."""
        G = _make_unweighted_community()
        prev = 0
        for s in [0.1, 0.3, 0.5, 0.7, 1.0]:
            bb = lspar(G, s=s)
            assert bb.number_of_edges() >= prev
            prev = bb.number_of_edges()


class TestLocalDegree:
    """Tests for the Local Degree convenience wrapper."""

    def test_is_subgraph(self):
        G = _make_unweighted_community()
        bb = local_degree(G, s=0.5)
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_sparser_than_original(self):
        G = _make_unweighted_community()
        bb = local_degree(G, s=0.3)
        assert bb.number_of_edges() < G.number_of_edges()


# ========================================================================
# Tests: KS measures
# ========================================================================

class TestKSMeasures:
    """Tests for the Kolmogorov-Smirnov distribution comparison measures."""

    def test_ks_degree_identical(self):
        """KS degree stat of a graph with itself should be 0."""
        G = _make_two_cluster_undirected()
        assert ks_degree(G, G) == pytest.approx(0.0)

    def test_ks_degree_different(self):
        G = _make_two_cluster_undirected()
        bb = global_threshold_filter(G, threshold=50)
        stat = ks_degree(G, bb)
        assert 0 <= stat <= 1

    def test_ks_weight_identical(self):
        G = _make_two_cluster_undirected()
        assert ks_weight(G, G) == pytest.approx(0.0)

    def test_ks_weight_different(self):
        G = _make_two_cluster_undirected()
        bb = global_threshold_filter(G, threshold=50)
        stat = ks_weight(G, bb)
        assert 0 < stat <= 1

    def test_ks_empty_backbone(self):
        G = _make_two_cluster_undirected()
        bb = nx.Graph()
        assert ks_degree(G, bb) == 1.0
        assert ks_weight(G, bb) == 1.0


# ========================================================================
# Tests: Neighborhood Overlap
# ========================================================================

def _make_overlap_graph():
    """Graph with known neighborhood overlaps.

    Nodes A-B-C form a triangle. D connects to B and C.
    N(A) = {B, C}, N(B) = {A, C, D}, N(C) = {A, B, D}, N(D) = {B, C}
    Overlap(A,B): {C}=1, Overlap(B,C): {A, D}=2, Overlap(A,D): {B, C}=2 (not edge)
    """
    G = nx.Graph()
    G.add_edges_from([("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D")])
    return G


class TestNeighborhoodOverlap:
    """Tests for raw neighborhood overlap scoring."""

    def test_overlap_added(self):
        G = _make_overlap_graph()
        H = neighborhood_overlap(G)
        for u, v, d in H.edges(data=True):
            assert "overlap" in d

    def test_overlap_values(self):
        G = _make_overlap_graph()
        H = neighborhood_overlap(G)
        # A-B: common = {C} -> 1
        assert H["A"]["B"]["overlap"] == 1
        # A-C: common = {B} -> 1
        assert H["A"]["C"]["overlap"] == 1
        # B-C: common = {A, D} -> 2
        assert H["B"]["C"]["overlap"] == 2
        # B-D: common = {C} -> 1
        assert H["B"]["D"]["overlap"] == 1
        # C-D: common = {B} -> 1
        assert H["C"]["D"]["overlap"] == 1

    def test_complete_graph(self):
        """In K_n, every pair of adjacent nodes shares n-2 common neighbors."""
        G = nx.complete_graph(5)
        H = neighborhood_overlap(G)
        for u, v, d in H.edges(data=True):
            assert d["overlap"] == 3  # 5 - 2

    def test_path_graph_no_overlap(self):
        """Path graph: interior edges have overlap 0 (or 1 for length > 3)."""
        G = nx.path_graph(3)  # 0-1-2
        H = neighborhood_overlap(G)
        assert H[0][1]["overlap"] == 0  # N(0)={1}, N(1)={0,2}, common={}
        assert H[1][2]["overlap"] == 0

    def test_preserves_structure(self):
        G = _make_overlap_graph()
        H = neighborhood_overlap(G)
        assert H.number_of_nodes() == G.number_of_nodes()
        assert H.number_of_edges() == G.number_of_edges()

    def test_directed(self):
        G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
        H = neighborhood_overlap(G)
        assert H.is_directed()
        for u, v, d in H.edges(data=True):
            assert "overlap" in d


class TestJaccardBackbone:
    """Tests for Jaccard similarity backbone."""

    def test_jaccard_added(self):
        G = _make_overlap_graph()
        H = jaccard_backbone(G)
        for u, v, d in H.edges(data=True):
            assert "jaccard" in d
            assert 0 <= d["jaccard"] <= 1

    def test_jaccard_values(self):
        G = _make_overlap_graph()
        H = jaccard_backbone(G)
        # A-B: overlap=1, |N(A) ∪ N(B)| = |{B,C} ∪ {A,C,D}| = |{A,B,C,D}| = 4
        # J = 1/4 = 0.25
        # Or equivalently: 1 / (2 + 3 - 1) = 1/4
        assert H["A"]["B"]["jaccard"] == pytest.approx(0.25)
        # B-C: overlap=2, union = |{A,C,D} ∪ {A,B,D}| = |{A,B,C,D}| = 4
        # J = 2/4 = 0.5
        assert H["B"]["C"]["jaccard"] == pytest.approx(0.5)

    def test_complete_graph(self):
        """In K_n, J = (n-2) / (n-2) = 1 when n >= 2 (but union = N total)."""
        G = nx.complete_graph(4)
        H = jaccard_backbone(G)
        # Each node has degree 3. Overlap = 2. Union = |{all 4}| - but
        # neighbors exclude self, so union = {a,b,c,d} minus endpoints = all 4 nodes minus {u,v}
        # Actually: N(0) = {1,2,3}, N(1) = {0,2,3}, N(0)∪N(1) = {0,1,2,3} = 4
        # intersection = {2,3} = 2, J = 2/4 = 0.5
        for u, v, d in H.edges(data=True):
            assert d["jaccard"] == pytest.approx(0.5)

    def test_structurally_equivalent_nodes(self):
        """Nodes with identical neighbor sets → Jaccard = 1 for edges between them."""
        # Build a graph where nodes 0 and 1 both connect to {2, 3} and to each other
        # N(0) = {1, 2, 3}, N(1) = {0, 2, 3}
        # For edge (0,1): intersection = {2, 3}, union = {0, 1, 2, 3}, J = 2/4 = 0.5
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)])
        H = jaccard_backbone(G)
        assert H[0][1]["jaccard"] == pytest.approx(0.5)

        # Nodes NOT connected to each other but with identical neighborhoods:
        # N(0) = {2, 3}, N(1) = {2, 3} — but (0,1) not an edge, so no score.
        # Instead check nodes 2 and 3: N(2) = {0, 1}, N(3) = {0, 1}
        # edge (2,3) doesn't exist so we add it
        G2 = nx.Graph()
        G2.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
        H2 = jaccard_backbone(G2)
        # N(2) = {0, 1, 3}, N(3) = {0, 1, 2}, intersection = {0, 1}, union = {0, 1, 2, 3}
        assert H2[2][3]["jaccard"] == pytest.approx(0.5)

    def test_bridge_gets_zero(self):
        """A bridge between two cliques should get J=0 (no common neighbors)."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # triangle
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])  # triangle
        G.add_edge(2, 3)  # bridge
        H = jaccard_backbone(G)
        assert H[2][3]["jaccard"] == pytest.approx(0.0)

    def test_filtering_pipeline(self):
        G = _make_two_cluster_undirected()
        H = jaccard_backbone(G)
        bb = threshold_filter(H, "jaccard", 0.5, "above")
        for u, v in bb.edges():
            assert G.has_edge(u, v)

    def test_directed(self):
        G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
        H = jaccard_backbone(G)
        assert H.is_directed()
        for u, v, d in H.edges(data=True):
            assert "jaccard" in d
            assert 0 <= d["jaccard"] <= 1


class TestDiceBackbone:
    """Tests for Dice similarity backbone."""

    def test_dice_added(self):
        G = _make_overlap_graph()
        H = dice_backbone(G)
        for u, v, d in H.edges(data=True):
            assert "dice" in d
            assert 0 <= d["dice"] <= 1

    def test_dice_values(self):
        G = _make_overlap_graph()
        H = dice_backbone(G)
        # A-B: overlap=1, deg(A)=2, deg(B)=3 → D = 2*1/(2+3) = 0.4
        assert H["A"]["B"]["dice"] == pytest.approx(0.4)
        # B-C: overlap=2, deg(B)=3, deg(C)=3 → D = 2*2/(3+3) = 4/6 ≈ 0.6667
        assert H["B"]["C"]["dice"] == pytest.approx(4.0 / 6.0)

    def test_complete_graph(self):
        """In K_4: overlap=2, deg=3 for all → D = 4/6 = 2/3."""
        G = nx.complete_graph(4)
        H = dice_backbone(G)
        for u, v, d in H.edges(data=True):
            assert d["dice"] == pytest.approx(2.0 / 3.0)

    def test_bridge_gets_zero(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])
        G.add_edge(2, 3)
        H = dice_backbone(G)
        assert H[2][3]["dice"] == pytest.approx(0.0)

    def test_directed(self):
        G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
        H = dice_backbone(G)
        assert H.is_directed()


class TestCosineBackbone:
    """Tests for cosine similarity backbone."""

    def test_cosine_added(self):
        G = _make_overlap_graph()
        H = cosine_backbone(G)
        for u, v, d in H.edges(data=True):
            assert "cosine" in d
            assert 0 <= d["cosine"] <= 1

    def test_cosine_values(self):
        G = _make_overlap_graph()
        H = cosine_backbone(G)
        import math
        # A-B: overlap=1, deg(A)=2, deg(B)=3 → C = 1/sqrt(6) ≈ 0.4082
        assert H["A"]["B"]["cosine"] == pytest.approx(1.0 / math.sqrt(6))
        # B-C: overlap=2, deg(B)=3, deg(C)=3 → C = 2/sqrt(9) = 2/3
        assert H["B"]["C"]["cosine"] == pytest.approx(2.0 / 3.0)

    def test_complete_graph(self):
        """In K_4: overlap=2, deg=3 → C = 2/sqrt(9) = 2/3."""
        G = nx.complete_graph(4)
        H = cosine_backbone(G)
        for u, v, d in H.edges(data=True):
            assert d["cosine"] == pytest.approx(2.0 / 3.0)

    def test_bridge_gets_zero(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])
        G.add_edge(2, 3)
        H = cosine_backbone(G)
        assert H[2][3]["cosine"] == pytest.approx(0.0)

    def test_directed(self):
        G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
        H = cosine_backbone(G)
        assert H.is_directed()


class TestNeighborhoodOverlapRelationships:
    """Cross-method properties that should hold across all three measures."""

    def test_all_agree_on_zero(self):
        """Bridge edges with no common neighbors → all measures = 0."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])
        G.add_edge(2, 3)
        Hj = jaccard_backbone(G)
        Hd = dice_backbone(G)
        Hc = cosine_backbone(G)
        assert Hj[2][3]["jaccard"] == 0.0
        assert Hd[2][3]["dice"] == 0.0
        assert Hc[2][3]["cosine"] == 0.0

    def test_ordering_consistent(self):
        """If edge A has higher Jaccard than edge B, Dice and Cosine agree."""
        G = _make_overlap_graph()
        Hj = jaccard_backbone(G)
        Hd = dice_backbone(G)
        Hc = cosine_backbone(G)
        # B-C should score higher than A-B on all three
        assert Hj["B"]["C"]["jaccard"] > Hj["A"]["B"]["jaccard"]
        assert Hd["B"]["C"]["dice"] > Hd["A"]["B"]["dice"]
        assert Hc["B"]["C"]["cosine"] > Hc["A"]["B"]["cosine"]

    def test_dice_geq_jaccard(self):
        """Dice coefficient is always >= Jaccard for the same edge."""
        G = _make_overlap_graph()
        Hj = jaccard_backbone(G)
        Hd = dice_backbone(G)
        for u, v in G.edges():
            assert Hd[u][v]["dice"] >= Hj[u][v]["jaccard"] - 1e-10

    def test_cosine_geq_jaccard(self):
        """Cosine similarity is always >= Jaccard for the same edge."""
        G = _make_overlap_graph()
        Hj = jaccard_backbone(G)
        Hc = cosine_backbone(G)
        for u, v in G.edges():
            assert Hc[u][v]["cosine"] >= Hj[u][v]["jaccard"] - 1e-10

    def test_on_weighted_graph(self):
        """Neighborhood overlap ignores weights (topology-only)."""
        G = _make_two_cluster_undirected()
        Hj = jaccard_backbone(G)
        for u, v, d in Hj.edges(data=True):
            assert "jaccard" in d
            assert 0 <= d["jaccard"] <= 1

    def test_filtering_keeps_embedded_edges(self):
        """Filtering by high Jaccard should keep intra-cluster edges."""
        G = _make_two_cluster_undirected()
        Hj = jaccard_backbone(G)
        bb = threshold_filter(Hj, "jaccard", 0.3, "above")
        # The bridge edge (3,4) connects clusters and should have low overlap
        assert not bb.has_edge(3, 4)


# ========================================================================
# Tests: All-methods integration
# ========================================================================

class TestAllMethodsIntegration:
    """Run every method on the same graph as a comprehensive smoke test."""

    @pytest.fixture
    def weighted_graph(self):
        G = _make_two_cluster_undirected()
        return G

    @pytest.fixture
    def directed_graph(self):
        return _make_two_cluster_directed()

    def test_all_statistical_undirected(self, weighted_graph):
        G = weighted_graph
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

    def test_all_statistical_directed(self, directed_graph):
        G = directed_graph
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

    def test_all_structural_undirected(self, weighted_graph):
        G = weighted_graph
        # Methods that return scored graphs
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
            # Check attribute exists
            if attr == "vitality":
                for n in H.nodes():
                    assert attr in H.nodes[n]
            else:
                for u, v, d in H.edges(data=True):
                    assert attr in d

        # Methods that return subgraphs directly
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

    def test_glab_undirected(self, weighted_graph):
        H = glab_filter(weighted_graph)
        for u, v, d in H.edges(data=True):
            assert "glab_pvalue" in d

    def test_compare_all_backbones(self, weighted_graph):
        """Compare many backbone methods side by side."""
        G = weighted_graph
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
