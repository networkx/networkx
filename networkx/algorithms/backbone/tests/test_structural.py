"""Tests for structural backbone methods.

Covers: global_threshold_filter, strongest_n_ties, high_salience_skeleton,
metric_backbone, ultrametric_backbone, maximum_spanning_tree_backbone,
doubly_stochastic_filter, h_backbone, modularity_backbone, and
planar_maximally_filtered_graph.
"""

import pytest
from backbone.filters import threshold_filter
from backbone.structural import (
    doubly_stochastic_filter,
    global_threshold_filter,
    h_backbone,
    high_salience_skeleton,
    maximum_spanning_tree_backbone,
    metric_backbone,
    modularity_backbone,
    planar_maximally_filtered_graph,
    strongest_n_ties,
    ultrametric_backbone,
)

import networkx as nx

# ── Global Threshold Filter ─────────────────────────────────────────────


def test_global_threshold_keeps_heavy_edges(two_cluster_undirected):
    bb = global_threshold_filter(two_cluster_undirected, threshold=50)
    # Only cluster B edges (weight=100) survive
    assert bb.number_of_edges() == 6  # C(4,2)
    for u, v, d in bb.edges(data=True):
        assert d["weight"] >= 50


def test_global_threshold_zero_keeps_everything(two_cluster_undirected):
    bb = global_threshold_filter(two_cluster_undirected, threshold=0)
    assert bb.number_of_edges() == two_cluster_undirected.number_of_edges()


def test_global_threshold_very_high_removes_all_edges(two_cluster_undirected):
    bb = global_threshold_filter(two_cluster_undirected, threshold=999)
    assert bb.number_of_edges() == 0
    # But all nodes are preserved
    assert set(bb.nodes()) == set(two_cluster_undirected.nodes())


def test_global_threshold_preserves_node_set(two_cluster_undirected):
    bb = global_threshold_filter(two_cluster_undirected, threshold=50)
    assert set(bb.nodes()) == set(two_cluster_undirected.nodes())


def test_global_threshold_on_path_graph(path_weighted):
    # Weights: 10, 20, 30, 40 -> threshold=25 keeps edges with w>=25
    bb = global_threshold_filter(path_weighted, threshold=25)
    assert bb.number_of_edges() == 2  # (2,3,w=30), (3,4,w=40)


def test_global_threshold_boundary_inclusive(path_weighted):
    """Edges with weight exactly equal to threshold are retained."""
    bb = global_threshold_filter(path_weighted, threshold=20)
    assert bb.has_edge(1, 2)  # weight=20, exactly at threshold
    assert bb.number_of_edges() == 3


def test_global_threshold_directed(two_cluster_directed):
    bb = global_threshold_filter(two_cluster_directed, threshold=50)
    assert bb.is_directed()
    # Only cluster B directed edges survive (12 directed edges in K4)
    assert bb.number_of_edges() == 12
    for u, v, d in bb.edges(data=True):
        assert d["weight"] >= 50


def test_global_threshold_directed_bridge_excluded(two_cluster_directed):
    bb = global_threshold_filter(two_cluster_directed, threshold=2)
    # Bridge (3->4, w=1) should be excluded
    assert not bb.has_edge(3, 4)


def test_global_threshold_single_edge(single_edge_graph):
    bb_keep = global_threshold_filter(single_edge_graph, threshold=42)
    assert bb_keep.has_edge("x", "y")
    bb_drop = global_threshold_filter(single_edge_graph, threshold=43)
    assert not bb_drop.has_edge("x", "y")


def test_global_threshold_single_node(single_node_graph):
    bb = global_threshold_filter(single_node_graph, threshold=0)
    assert "alone" in bb.nodes()
    assert bb.number_of_edges() == 0


def test_global_threshold_disconnected(disconnected_graph):
    bb = global_threshold_filter(disconnected_graph, threshold=15)
    assert bb.number_of_edges() == 1
    assert bb.has_edge(2, 3)
    assert not bb.has_edge(0, 1)


def test_global_threshold_preserves_attributes():
    G = nx.Graph()
    G.add_edge(0, 1, weight=10, color="red")
    bb = global_threshold_filter(G, threshold=5)
    assert bb[0][1]["color"] == "red"


def test_global_threshold_custom_weight_key():
    G = nx.Graph()
    G.add_edge(0, 1, flow=100)
    G.add_edge(1, 2, flow=5)
    bb = global_threshold_filter(G, threshold=50, weight="flow")
    assert bb.has_edge(0, 1)
    assert not bb.has_edge(1, 2)


# ── Strongest-N Ties ─────────────────────────────────────────────────────


def test_strongest_n_ties_n1_on_path(path_weighted):
    """Each node keeps its single strongest edge."""
    bb = strongest_n_ties(path_weighted, n=1)
    assert bb.has_edge(3, 4)
    assert bb.has_edge(2, 3)
    assert bb.has_edge(0, 1)  # node 0 only has this edge


def test_strongest_n_ties_n1_on_triangle(triangle_unequal):
    """In a triangle with weights 1, 2, 3, n=1 keeps the two strongest."""
    bb = strongest_n_ties(triangle_unequal, n=1)
    # A picks (A,C,3), B picks (B,C,2), C picks (A,C,3)
    assert bb.has_edge("A", "C")
    assert bb.has_edge("B", "C")
    # (A,B,1) is nobody's strongest
    assert not bb.has_edge("A", "B")


def test_strongest_n_ties_n2_on_triangle_keeps_all(triangle_unequal):
    """n=2 on a triangle (max deg 2) keeps everything."""
    bb = strongest_n_ties(triangle_unequal, n=2)
    assert bb.number_of_edges() == 3


def test_strongest_n_ties_n_exceeds_degree(path_weighted):
    """If n > max degree, all edges are retained."""
    bb = strongest_n_ties(path_weighted, n=100)
    assert bb.number_of_edges() == path_weighted.number_of_edges()


def test_strongest_n_ties_n1_star_keeps_hub(star_undirected):
    """In a star, each spoke's strongest edge is to the hub."""
    bb = strongest_n_ties(star_undirected, n=1)
    for i in range(1, 6):
        assert bb.has_edge(0, i)


def test_strongest_n_ties_preserves_all_nodes(two_cluster_undirected):
    bb = strongest_n_ties(two_cluster_undirected, n=1)
    assert set(bb.nodes()) == set(two_cluster_undirected.nodes())


def test_strongest_n_ties_directed_n1():
    """Directed: per-node strongest based on out-edges."""
    G = nx.DiGraph()
    n, hub_weight, spoke_weight = 4, 100, 5
    for i in range(1, n):
        G.add_edge(0, i, weight=hub_weight)
    for i in range(1, n):
        j = (i % (n - 1)) + 1
        if i != j:
            G.add_edge(i, j, weight=spoke_weight)
    bb = strongest_n_ties(G, n=1)
    assert bb.is_directed()
    out_0 = list(bb.successors(0))
    assert len(out_0) == 1  # n=1 -> hub keeps only one


def test_strongest_n_ties_directed_n2():
    G = nx.DiGraph()
    n, hub_weight, spoke_weight = 4, 100, 5
    for i in range(1, n):
        G.add_edge(0, i, weight=hub_weight)
    for i in range(1, n):
        j = (i % (n - 1)) + 1
        if i != j:
            G.add_edge(i, j, weight=spoke_weight)
    bb = strongest_n_ties(G, n=2)
    out_0 = list(bb.successors(0))
    assert len(out_0) == 2


def test_strongest_n_ties_invalid_n(triangle_unequal):
    with pytest.raises(ValueError):
        strongest_n_ties(triangle_unequal, n=0)


def test_strongest_n_ties_n1_uniform_weights(complete_uniform):
    """With uniform weights, each node still keeps exactly 1 edge."""
    bb = strongest_n_ties(complete_uniform, n=1)
    for node in bb.nodes():
        assert bb.degree(node) >= 1
    assert bb.number_of_edges() <= 5


def test_strongest_n_ties_preserves_edge_attributes():
    G = nx.Graph()
    G.add_edge(0, 1, weight=10, label="a")
    G.add_edge(0, 2, weight=20, label="b")
    bb = strongest_n_ties(G, n=1)
    assert bb.has_edge(0, 2)
    assert bb[0][2]["label"] == "b"


def test_strongest_n_ties_disconnected_components(disconnected_graph):
    bb = strongest_n_ties(disconnected_graph, n=1)
    assert bb.has_edge(0, 1)
    assert bb.has_edge(2, 3)


def test_strongest_n_ties_single_edge(single_edge_graph):
    bb = strongest_n_ties(single_edge_graph, n=1)
    assert bb.has_edge("x", "y")


def test_strongest_n_ties_custom_weight_key():
    G = nx.Graph()
    G.add_edge(0, 1, capacity=100)
    G.add_edge(0, 2, capacity=5)
    G.add_edge(1, 2, capacity=50)
    bb = strongest_n_ties(G, n=1, weight="capacity")
    assert bb.has_edge(0, 1)


# ── High Salience Skeleton ───────────────────────────────────────────────


def test_high_salience_scores_added(two_cluster_undirected):
    H = high_salience_skeleton(two_cluster_undirected)
    for u, v, d in H.edges(data=True):
        assert "salience" in d
        assert 0 <= d["salience"] <= 1


def test_high_salience_bridge_has_high_salience(two_cluster_undirected):
    """The bridge between two clusters should have high salience."""
    H = high_salience_skeleton(two_cluster_undirected)
    bridge_sal = H[3][4]["salience"]
    assert bridge_sal > 0.5


def test_high_salience_path_graph_all_high(path_weighted):
    """In a path graph every edge is on every shortest path."""
    H = high_salience_skeleton(path_weighted)
    for u, v, d in H.edges(data=True):
        assert d["salience"] > 0.3


def test_high_salience_complete_uniform_moderate(complete_uniform):
    """In K5 with uniform weights, salience should be moderate (not 0)."""
    H = high_salience_skeleton(complete_uniform)
    saliences = [d["salience"] for _, _, d in H.edges(data=True)]
    assert max(saliences) - min(saliences) < 0.01


def test_high_salience_raises_on_directed(two_cluster_directed):
    with pytest.raises(nx.NetworkXError):
        high_salience_skeleton(two_cluster_directed)


def test_high_salience_filtering_at_08(two_cluster_undirected):
    H = high_salience_skeleton(two_cluster_undirected)
    bb = threshold_filter(H, "salience", 0.8, "above")
    assert bb.number_of_edges() <= two_cluster_undirected.number_of_edges()


# ── Metric Backbone ──────────────────────────────────────────────────────


def test_metric_path_graph_is_own_backbone(path_weighted):
    """Every edge in a path graph is a shortest path -> all are metric."""
    bb = metric_backbone(path_weighted)
    assert bb.number_of_edges() == path_weighted.number_of_edges()


def test_metric_triangle_removes_weakest(triangle_unequal):
    """In triangle with w(AB)=1, w(BC)=2, w(AC)=3: A-B is not metric."""
    bb = metric_backbone(triangle_unequal)
    assert not bb.has_edge("A", "B")
    assert bb.has_edge("A", "C")
    assert bb.has_edge("B", "C")


def test_metric_complete_uniform_keeps_all():
    """With uniform weights, direct path always shortest -> all metric."""
    G = nx.complete_graph(4)
    for u, v in G.edges():
        G[u][v]["weight"] = 10
    bb = metric_backbone(G)
    assert bb.number_of_edges() == G.number_of_edges()


def test_metric_raises_on_directed(two_cluster_directed):
    with pytest.raises(nx.NetworkXError):
        metric_backbone(two_cluster_directed)


def test_metric_is_subgraph(two_cluster_undirected):
    bb = metric_backbone(two_cluster_undirected)
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)


# ── Ultrametric Backbone ─────────────────────────────────────────────────


def test_ultrametric_path_graph(path_weighted):
    bb = ultrametric_backbone(path_weighted)
    assert bb.number_of_edges() == path_weighted.number_of_edges()


def test_ultrametric_is_subgraph(two_cluster_undirected):
    bb = ultrametric_backbone(two_cluster_undirected)
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)


def test_ultrametric_raises_on_directed(two_cluster_directed):
    with pytest.raises(nx.NetworkXError):
        ultrametric_backbone(two_cluster_directed)


# ── Maximum Spanning Tree Backbone ───────────────────────────────────────


def test_mst_is_tree(two_cluster_undirected):
    bb = maximum_spanning_tree_backbone(two_cluster_undirected)
    assert nx.is_tree(bb)


def test_mst_has_n_minus_1_edges(two_cluster_undirected):
    bb = maximum_spanning_tree_backbone(two_cluster_undirected)
    assert bb.number_of_edges() == two_cluster_undirected.number_of_nodes() - 1


def test_mst_preserves_all_nodes(two_cluster_undirected):
    bb = maximum_spanning_tree_backbone(two_cluster_undirected)
    assert set(bb.nodes()) == set(two_cluster_undirected.nodes())


def test_mst_maximises_total_weight(triangle_unequal):
    bb = maximum_spanning_tree_backbone(triangle_unequal)
    # MST should keep the two heaviest edges: (A,C,3) and (B,C,2)
    total = sum(d["weight"] for _, _, d in bb.edges(data=True))
    assert total == 5  # 3 + 2


def test_mst_raises_on_directed(two_cluster_directed):
    with pytest.raises(nx.NetworkXError):
        maximum_spanning_tree_backbone(two_cluster_directed)


# ── Doubly Stochastic Filter ─────────────────────────────────────────────


def test_doubly_stochastic_weight_added(two_cluster_undirected):
    H = doubly_stochastic_filter(two_cluster_undirected)
    for u, v, d in H.edges(data=True):
        assert "ds_weight" in d
        assert d["ds_weight"] >= 0


def test_doubly_stochastic_preserves_structure(two_cluster_undirected):
    H = doubly_stochastic_filter(two_cluster_undirected)
    assert H.number_of_nodes() == two_cluster_undirected.number_of_nodes()
    assert H.number_of_edges() == two_cluster_undirected.number_of_edges()


def test_doubly_stochastic_complete_uniform_symmetric(complete_uniform):
    """K5 with uniform weights: all ds_weights should be equal."""
    H = doubly_stochastic_filter(complete_uniform)
    weights = [d["ds_weight"] for _, _, d in H.edges(data=True)]
    assert max(weights) - min(weights) < 1e-4


def test_doubly_stochastic_raises_on_directed(two_cluster_directed):
    with pytest.raises(nx.NetworkXError):
        doubly_stochastic_filter(two_cluster_directed)


def test_doubly_stochastic_filtering_by_ds_weight(two_cluster_undirected):
    H = doubly_stochastic_filter(two_cluster_undirected)
    bb = threshold_filter(H, "ds_weight", 0.1, "above")
    assert bb.number_of_edges() <= two_cluster_undirected.number_of_edges()


# ── h-Backbone ────────────────────────────────────────────────────────────


def test_h_backbone_is_subgraph(two_cluster_undirected):
    bb = h_backbone(two_cluster_undirected)
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)


def test_h_backbone_nonempty(two_cluster_undirected):
    bb = h_backbone(two_cluster_undirected)
    assert bb.number_of_edges() > 0


def test_h_backbone_preserves_nodes(two_cluster_undirected):
    bb = h_backbone(two_cluster_undirected)
    assert set(bb.nodes()) == set(two_cluster_undirected.nodes())


def test_h_backbone_triangle(triangle_unequal):
    bb = h_backbone(triangle_unequal)
    # h=2 (2 edges with w>=2): (A,C,3) and (B,C,2)
    assert bb.has_edge("A", "C")
    assert bb.has_edge("B", "C")


def test_h_backbone_raises_on_directed(two_cluster_directed):
    with pytest.raises(nx.NetworkXError):
        h_backbone(two_cluster_directed)


# ── Modularity Backbone ──────────────────────────────────────────────────


def test_modularity_vitality_added(two_cluster_undirected):
    H = modularity_backbone(two_cluster_undirected)
    for node in H.nodes():
        assert "vitality" in H.nodes[node]


def test_modularity_preserves_structure(two_cluster_undirected):
    H = modularity_backbone(two_cluster_undirected)
    assert H.number_of_nodes() == two_cluster_undirected.number_of_nodes()
    assert H.number_of_edges() == two_cluster_undirected.number_of_edges()


def test_modularity_node_filtering(two_cluster_undirected):
    """Can filter nodes by vitality."""
    H = modularity_backbone(two_cluster_undirected)
    bb = threshold_filter(H, "vitality", 0.0, "above", filter_on="nodes")
    assert bb.number_of_nodes() <= two_cluster_undirected.number_of_nodes()


def test_modularity_raises_on_directed(two_cluster_directed):
    with pytest.raises(nx.NetworkXError):
        modularity_backbone(two_cluster_directed)


# ── Planar Maximally Filtered Graph ──────────────────────────────────────


def test_pmfg_is_planar(two_cluster_undirected):
    bb = planar_maximally_filtered_graph(two_cluster_undirected)
    is_planar, _ = nx.check_planarity(bb)
    assert is_planar


def test_pmfg_is_subgraph(two_cluster_undirected):
    bb = planar_maximally_filtered_graph(two_cluster_undirected)
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)


def test_pmfg_max_edges(two_cluster_undirected):
    """A planar graph on n nodes has at most 3(n-2) edges."""
    bb = planar_maximally_filtered_graph(two_cluster_undirected)
    n = bb.number_of_nodes()
    assert bb.number_of_edges() <= 3 * (n - 2)


def test_pmfg_prefers_heavy_edges(two_cluster_undirected):
    """PMFG should include the heaviest edges."""
    bb = planar_maximally_filtered_graph(two_cluster_undirected)
    for i in range(4, 8):
        for j in range(i + 1, 8):
            assert bb.has_edge(i, j)


def test_pmfg_raises_on_directed(two_cluster_directed):
    with pytest.raises(nx.NetworkXError):
        planar_maximally_filtered_graph(two_cluster_directed)


def test_pmfg_small_graph(triangle_unequal):
    """Triangle: always planar, all edges kept."""
    bb = planar_maximally_filtered_graph(triangle_unequal)
    assert bb.number_of_edges() == 3


def test_pmfg_preserves_edge_attributes(triangle_unequal):
    bb = planar_maximally_filtered_graph(triangle_unequal)
    for u, v, d in bb.edges(data=True):
        assert "weight" in d
