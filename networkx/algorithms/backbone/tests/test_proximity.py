"""Tests for proximity-based edge scoring methods.

Covers all local and quasi-local proximity indices:
neighborhood_overlap, jaccard_backbone, dice_backbone, cosine_backbone,
hub_promoted_index, hub_depressed_index, lhn_local_index,
preferential_attachment_score, adamic_adar_index, resource_allocation_index,
graph_distance_proximity, local_path_index,
and cross-method relationship properties.
"""

import math

import pytest
import networkx as nx

from backbone.proximity import (
    neighborhood_overlap,
    jaccard_backbone,
    dice_backbone,
    cosine_backbone,
    hub_promoted_index,
    hub_depressed_index,
    lhn_local_index,
    preferential_attachment_score,
    adamic_adar_index,
    resource_allocation_index,
    graph_distance_proximity,
    local_path_index,
)
from backbone.filters import threshold_filter


# ── Local fixtures ────────────────────────────────────────────────────────


def _make_overlap_graph():
    """Graph with known neighborhood overlaps.

    Nodes A-B-C form a triangle. D connects to B and C.
    N(A) = {B, C}, N(B) = {A, C, D}, N(C) = {A, B, D}, N(D) = {B, C}
    """
    G = nx.Graph()
    G.add_edges_from([("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D")])
    return G


def _make_bridge_graph():
    """Two triangles joined by a single bridge edge.

    Triangle 1: 0-1-2
    Triangle 2: 3-4-5
    Bridge: 2-3
    """
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (1, 2)])
    G.add_edges_from([(3, 4), (3, 5), (4, 5)])
    G.add_edge(2, 3)
    return G


# ── Neighborhood Overlap ─────────────────────────────────────────────────


def test_neighborhood_overlap_added():
    G = _make_overlap_graph()
    H = neighborhood_overlap(G)
    for u, v, d in H.edges(data=True):
        assert "overlap" in d


def test_neighborhood_overlap_values():
    G = _make_overlap_graph()
    H = neighborhood_overlap(G)
    assert H["A"]["B"]["overlap"] == 1
    assert H["A"]["C"]["overlap"] == 1
    assert H["B"]["C"]["overlap"] == 2
    assert H["B"]["D"]["overlap"] == 1
    assert H["C"]["D"]["overlap"] == 1


def test_neighborhood_overlap_complete_graph():
    """In K_n, every pair of adjacent nodes shares n-2 common neighbors."""
    G = nx.complete_graph(5)
    H = neighborhood_overlap(G)
    for u, v, d in H.edges(data=True):
        assert d["overlap"] == 3  # 5 - 2


def test_neighborhood_overlap_path_graph_no_overlap():
    """Path graph: interior edges have overlap 0."""
    G = nx.path_graph(3)
    H = neighborhood_overlap(G)
    assert H[0][1]["overlap"] == 0
    assert H[1][2]["overlap"] == 0


def test_neighborhood_overlap_preserves_structure():
    G = _make_overlap_graph()
    H = neighborhood_overlap(G)
    assert H.number_of_nodes() == G.number_of_nodes()
    assert H.number_of_edges() == G.number_of_edges()


def test_neighborhood_overlap_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = neighborhood_overlap(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "overlap" in d


# ── Jaccard Backbone ─────────────────────────────────────────────────────


def test_jaccard_added():
    G = _make_overlap_graph()
    H = jaccard_backbone(G)
    for u, v, d in H.edges(data=True):
        assert "jaccard" in d
        assert 0 <= d["jaccard"] <= 1


def test_jaccard_values():
    G = _make_overlap_graph()
    H = jaccard_backbone(G)
    assert H["A"]["B"]["jaccard"] == pytest.approx(0.25)
    assert H["B"]["C"]["jaccard"] == pytest.approx(0.5)


def test_jaccard_complete_graph():
    """In K_4: intersection=2, union=4 -> J=0.5."""
    G = nx.complete_graph(4)
    H = jaccard_backbone(G)
    for u, v, d in H.edges(data=True):
        assert d["jaccard"] == pytest.approx(0.5)


def test_jaccard_structurally_equivalent_nodes():
    """Nodes with identical neighbor sets."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)])
    H = jaccard_backbone(G)
    assert H[0][1]["jaccard"] == pytest.approx(0.5)

    G2 = nx.Graph()
    G2.add_edges_from([(0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    H2 = jaccard_backbone(G2)
    assert H2[2][3]["jaccard"] == pytest.approx(0.5)


def test_jaccard_bridge_gets_zero():
    """A bridge between two cliques should get J=0."""
    G = _make_bridge_graph()
    H = jaccard_backbone(G)
    assert H[2][3]["jaccard"] == pytest.approx(0.0)


def test_jaccard_filtering_pipeline(two_cluster_undirected):
    H = jaccard_backbone(two_cluster_undirected)
    bb = threshold_filter(H, "jaccard", 0.5, "above")
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)


def test_jaccard_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = jaccard_backbone(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "jaccard" in d
        assert 0 <= d["jaccard"] <= 1


# ── Dice Backbone ────────────────────────────────────────────────────────


def test_dice_added():
    G = _make_overlap_graph()
    H = dice_backbone(G)
    for u, v, d in H.edges(data=True):
        assert "dice" in d
        assert 0 <= d["dice"] <= 1


def test_dice_values():
    G = _make_overlap_graph()
    H = dice_backbone(G)
    assert H["A"]["B"]["dice"] == pytest.approx(0.4)
    assert H["B"]["C"]["dice"] == pytest.approx(4.0 / 6.0)


def test_dice_complete_graph():
    """In K_4: overlap=2, deg=3 -> D = 4/6 = 2/3."""
    G = nx.complete_graph(4)
    H = dice_backbone(G)
    for u, v, d in H.edges(data=True):
        assert d["dice"] == pytest.approx(2.0 / 3.0)


def test_dice_bridge_gets_zero():
    G = _make_bridge_graph()
    H = dice_backbone(G)
    assert H[2][3]["dice"] == pytest.approx(0.0)


def test_dice_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = dice_backbone(G)
    assert H.is_directed()


# ── Cosine Backbone ──────────────────────────────────────────────────────


def test_cosine_added():
    G = _make_overlap_graph()
    H = cosine_backbone(G)
    for u, v, d in H.edges(data=True):
        assert "cosine" in d
        assert 0 <= d["cosine"] <= 1


def test_cosine_values():
    G = _make_overlap_graph()
    H = cosine_backbone(G)
    assert H["A"]["B"]["cosine"] == pytest.approx(1.0 / math.sqrt(6))
    assert H["B"]["C"]["cosine"] == pytest.approx(2.0 / 3.0)


def test_cosine_complete_graph():
    """In K_4: overlap=2, deg=3 -> C = 2/sqrt(9) = 2/3."""
    G = nx.complete_graph(4)
    H = cosine_backbone(G)
    for u, v, d in H.edges(data=True):
        assert d["cosine"] == pytest.approx(2.0 / 3.0)


def test_cosine_bridge_gets_zero():
    G = _make_bridge_graph()
    H = cosine_backbone(G)
    assert H[2][3]["cosine"] == pytest.approx(0.0)


def test_cosine_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = cosine_backbone(G)
    assert H.is_directed()


# ── Hub Promoted Index ───────────────────────────────────────────────────


def test_hpi_added():
    G = _make_overlap_graph()
    H = hub_promoted_index(G)
    for u, v, d in H.edges(data=True):
        assert "hpi" in d
        assert 0 <= d["hpi"] <= 1


def test_hpi_values():
    G = _make_overlap_graph()
    H = hub_promoted_index(G)
    # A-B: overlap=1, min(deg(A)=2, deg(B)=3)=2 -> 1/2
    assert H["A"]["B"]["hpi"] == pytest.approx(0.5)
    # B-C: overlap=2, min(3,3)=3 -> 2/3
    assert H["B"]["C"]["hpi"] == pytest.approx(2.0 / 3.0)
    # C-D: overlap=1, min(3,2)=2 -> 1/2
    assert H["C"]["D"]["hpi"] == pytest.approx(0.5)


def test_hpi_complete_graph():
    G = nx.complete_graph(4)
    H = hub_promoted_index(G)
    for u, v, d in H.edges(data=True):
        assert d["hpi"] == pytest.approx(2.0 / 3.0)


def test_hpi_bridge_gets_zero():
    G = _make_bridge_graph()
    H = hub_promoted_index(G)
    assert H[2][3]["hpi"] == pytest.approx(0.0)


def test_hpi_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = hub_promoted_index(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "hpi" in d


# ── Hub Depressed Index ──────────────────────────────────────────────────


def test_hdi_added():
    G = _make_overlap_graph()
    H = hub_depressed_index(G)
    for u, v, d in H.edges(data=True):
        assert "hdi" in d
        assert 0 <= d["hdi"] <= 1


def test_hdi_values():
    G = _make_overlap_graph()
    H = hub_depressed_index(G)
    # A-B: overlap=1, max(2,3)=3 -> 1/3
    assert H["A"]["B"]["hdi"] == pytest.approx(1.0 / 3.0)
    # B-C: overlap=2, max(3,3)=3 -> 2/3
    assert H["B"]["C"]["hdi"] == pytest.approx(2.0 / 3.0)
    # C-D: overlap=1, max(3,2)=3 -> 1/3
    assert H["C"]["D"]["hdi"] == pytest.approx(1.0 / 3.0)


def test_hdi_complete_graph():
    G = nx.complete_graph(4)
    H = hub_depressed_index(G)
    for u, v, d in H.edges(data=True):
        assert d["hdi"] == pytest.approx(2.0 / 3.0)


def test_hdi_bridge_gets_zero():
    G = _make_bridge_graph()
    H = hub_depressed_index(G)
    assert H[2][3]["hdi"] == pytest.approx(0.0)


def test_hdi_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = hub_depressed_index(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "hdi" in d


# ── LHN Local Index ─────────────────────────────────────────────────────


def test_lhn_added():
    G = _make_overlap_graph()
    H = lhn_local_index(G)
    for u, v, d in H.edges(data=True):
        assert "lhn_local" in d
        assert d["lhn_local"] >= 0


def test_lhn_values():
    G = _make_overlap_graph()
    H = lhn_local_index(G)
    # A-B: overlap=1, 2*3=6 -> 1/6
    assert H["A"]["B"]["lhn_local"] == pytest.approx(1.0 / 6.0)
    # B-C: overlap=2, 3*3=9 -> 2/9
    assert H["B"]["C"]["lhn_local"] == pytest.approx(2.0 / 9.0)


def test_lhn_complete_graph():
    G = nx.complete_graph(4)
    H = lhn_local_index(G)
    for u, v, d in H.edges(data=True):
        assert d["lhn_local"] == pytest.approx(2.0 / 9.0)


def test_lhn_bridge_gets_zero():
    G = _make_bridge_graph()
    H = lhn_local_index(G)
    assert H[2][3]["lhn_local"] == pytest.approx(0.0)


def test_lhn_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = lhn_local_index(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "lhn_local" in d


# ── Preferential Attachment ──────────────────────────────────────────────


def test_pa_added():
    G = _make_overlap_graph()
    H = preferential_attachment_score(G)
    for u, v, d in H.edges(data=True):
        assert "pa" in d
        assert d["pa"] >= 0


def test_pa_values():
    G = _make_overlap_graph()
    H = preferential_attachment_score(G)
    assert H["A"]["B"]["pa"] == 6   # 2 * 3
    assert H["B"]["C"]["pa"] == 9   # 3 * 3
    assert H["B"]["D"]["pa"] == 6   # 3 * 2


def test_pa_complete_graph():
    G = nx.complete_graph(4)
    H = preferential_attachment_score(G)
    for u, v, d in H.edges(data=True):
        assert d["pa"] == 9  # 3 * 3


def test_pa_path_graph():
    """Endpoint nodes have degree 1, interior have degree 2."""
    G = nx.path_graph(4)
    H = preferential_attachment_score(G)
    assert H[0][1]["pa"] == 2   # 1 * 2
    assert H[1][2]["pa"] == 4   # 2 * 2
    assert H[2][3]["pa"] == 2   # 2 * 1


def test_pa_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = preferential_attachment_score(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "pa" in d


# ── Adamic-Adar Index ────────────────────────────────────────────────────


def test_aa_added():
    G = _make_overlap_graph()
    H = adamic_adar_index(G)
    for u, v, d in H.edges(data=True):
        assert "adamic_adar" in d
        assert d["adamic_adar"] >= 0


def test_aa_values():
    G = _make_overlap_graph()
    H = adamic_adar_index(G)
    # A-B: common={C}, deg(C)=3 -> 1/log(3)
    assert H["A"]["B"]["adamic_adar"] == pytest.approx(1.0 / math.log(3))
    # B-C: common={A,D}, deg(A)=2, deg(D)=2 -> 2/log(2)
    assert H["B"]["C"]["adamic_adar"] == pytest.approx(2.0 / math.log(2))


def test_aa_complete_graph():
    G = nx.complete_graph(4)
    H = adamic_adar_index(G)
    for u, v, d in H.edges(data=True):
        assert d["adamic_adar"] == pytest.approx(2.0 / math.log(3))


def test_aa_bridge_gets_zero():
    G = _make_bridge_graph()
    H = adamic_adar_index(G)
    assert H[2][3]["adamic_adar"] == pytest.approx(0.0)


def test_aa_path_graph():
    """No common neighbors in path -> all AA scores = 0."""
    G = nx.path_graph(4)
    H = adamic_adar_index(G)
    for u, v, d in H.edges(data=True):
        assert d["adamic_adar"] == pytest.approx(0.0)


def test_aa_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = adamic_adar_index(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "adamic_adar" in d


# ── Resource Allocation Index ────────────────────────────────────────────


def test_ra_added():
    G = _make_overlap_graph()
    H = resource_allocation_index(G)
    for u, v, d in H.edges(data=True):
        assert "resource_allocation" in d
        assert d["resource_allocation"] >= 0


def test_ra_values():
    G = _make_overlap_graph()
    H = resource_allocation_index(G)
    # A-B: common={C}, deg(C)=3 -> 1/3
    assert H["A"]["B"]["resource_allocation"] == pytest.approx(1.0 / 3.0)
    # B-C: common={A,D}, deg(A)=2, deg(D)=2 -> 1/2 + 1/2 = 1.0
    assert H["B"]["C"]["resource_allocation"] == pytest.approx(1.0)


def test_ra_complete_graph():
    G = nx.complete_graph(4)
    H = resource_allocation_index(G)
    for u, v, d in H.edges(data=True):
        assert d["resource_allocation"] == pytest.approx(2.0 / 3.0)


def test_ra_bridge_gets_zero():
    G = _make_bridge_graph()
    H = resource_allocation_index(G)
    assert H[2][3]["resource_allocation"] == pytest.approx(0.0)


def test_ra_path_graph():
    """No common neighbors in path -> all RA scores = 0."""
    G = nx.path_graph(4)
    H = resource_allocation_index(G)
    for u, v, d in H.edges(data=True):
        assert d["resource_allocation"] == pytest.approx(0.0)


def test_ra_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = resource_allocation_index(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "resource_allocation" in d


# ── Graph Distance Proximity ─────────────────────────────────────────────


def test_dist_added():
    G = _make_overlap_graph()
    H = graph_distance_proximity(G)
    for u, v, d in H.edges(data=True):
        assert "dist" in d
        assert d["dist"] > 0


def test_dist_values():
    """Adjacent nodes have distance 1, so proximity = 1.0."""
    G = nx.path_graph(4)
    H = graph_distance_proximity(G)
    for u, v, d in H.edges(data=True):
        assert d["dist"] == pytest.approx(1.0)


def test_dist_complete_graph():
    G = nx.complete_graph(4)
    H = graph_distance_proximity(G)
    for u, v, d in H.edges(data=True):
        assert d["dist"] == pytest.approx(1.0)


def test_dist_preserves_structure():
    G = _make_overlap_graph()
    H = graph_distance_proximity(G)
    assert H.number_of_nodes() == G.number_of_nodes()
    assert H.number_of_edges() == G.number_of_edges()


def test_dist_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = graph_distance_proximity(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "dist" in d


# ── Local Path Index ─────────────────────────────────────────────────────


def test_lp_added():
    G = _make_overlap_graph()
    H = local_path_index(G)
    for u, v, d in H.edges(data=True):
        assert "lp" in d
        assert d["lp"] >= 0


def test_lp_values_triangle():
    """In K_3, each edge has 1 common neighbor (A^2 score = 1)."""
    G = nx.complete_graph(3)
    H = local_path_index(G, epsilon=0.0)
    for u, v, d in H.edges(data=True):
        assert d["lp"] == pytest.approx(1.0)


def test_lp_complete_graph():
    G = nx.complete_graph(4)
    H = local_path_index(G, epsilon=0.0)
    for u, v, d in H.edges(data=True):
        assert d["lp"] == pytest.approx(2.0)


def test_lp_epsilon_increases_score():
    """Positive epsilon should increase scores when A^3 > 0."""
    G = _make_overlap_graph()
    H0 = local_path_index(G, epsilon=0.0)
    H1 = local_path_index(G, epsilon=1.0)
    for u, v in G.edges():
        assert H1[u][v]["lp"] >= H0[u][v]["lp"]


def test_lp_path_graph():
    """In a path graph, adjacent nodes have A^2 = 0 (no common neighbors)."""
    G = nx.path_graph(3)
    H = local_path_index(G, epsilon=0.0)
    assert H[0][1]["lp"] == pytest.approx(0.0)
    assert H[1][2]["lp"] == pytest.approx(0.0)


def test_lp_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = local_path_index(G)
    assert H.is_directed()
    for u, v, d in H.edges(data=True):
        assert "lp" in d


# ── Cross-method relationships (original four) ──────────────────────────


def test_overlap_all_agree_on_zero():
    """Bridge edges with no common neighbors -> all measures = 0."""
    G = _make_bridge_graph()
    Hj = jaccard_backbone(G)
    Hd = dice_backbone(G)
    Hc = cosine_backbone(G)
    assert Hj[2][3]["jaccard"] == 0.0
    assert Hd[2][3]["dice"] == 0.0
    assert Hc[2][3]["cosine"] == 0.0


def test_overlap_ordering_consistent():
    """If edge A has higher Jaccard than edge B, Dice and Cosine agree."""
    G = _make_overlap_graph()
    Hj = jaccard_backbone(G)
    Hd = dice_backbone(G)
    Hc = cosine_backbone(G)
    assert Hj["B"]["C"]["jaccard"] > Hj["A"]["B"]["jaccard"]
    assert Hd["B"]["C"]["dice"] > Hd["A"]["B"]["dice"]
    assert Hc["B"]["C"]["cosine"] > Hc["A"]["B"]["cosine"]


def test_overlap_dice_geq_jaccard():
    """Dice coefficient is always >= Jaccard for the same edge."""
    G = _make_overlap_graph()
    Hj = jaccard_backbone(G)
    Hd = dice_backbone(G)
    for u, v in G.edges():
        assert Hd[u][v]["dice"] >= Hj[u][v]["jaccard"] - 1e-10


def test_overlap_cosine_geq_jaccard():
    """Cosine similarity is always >= Jaccard for the same edge."""
    G = _make_overlap_graph()
    Hj = jaccard_backbone(G)
    Hc = cosine_backbone(G)
    for u, v in G.edges():
        assert Hc[u][v]["cosine"] >= Hj[u][v]["jaccard"] - 1e-10


def test_overlap_on_weighted_graph(two_cluster_undirected):
    """Neighborhood overlap ignores weights (topology-only)."""
    Hj = jaccard_backbone(two_cluster_undirected)
    for u, v, d in Hj.edges(data=True):
        assert "jaccard" in d
        assert 0 <= d["jaccard"] <= 1


def test_overlap_filtering_keeps_embedded_edges(two_cluster_undirected):
    """Filtering by high Jaccard should keep intra-cluster edges."""
    Hj = jaccard_backbone(two_cluster_undirected)
    bb = threshold_filter(Hj, "jaccard", 0.3, "above")
    assert not bb.has_edge(3, 4)


# ── Cross-method relationships (all proximity indices) ───────────────────


def test_all_overlap_indices_agree_on_zero_for_bridge():
    """Bridge edges with no common neighbors -> all overlap-based measures = 0."""
    G = _make_bridge_graph()
    for method, attr in [
        (jaccard_backbone, "jaccard"),
        (dice_backbone, "dice"),
        (cosine_backbone, "cosine"),
        (hub_promoted_index, "hpi"),
        (hub_depressed_index, "hdi"),
        (lhn_local_index, "lhn_local"),
        (adamic_adar_index, "adamic_adar"),
        (resource_allocation_index, "resource_allocation"),
    ]:
        H = method(G)
        assert H[2][3][attr] == pytest.approx(0.0), (
            f"{method.__name__} bridge score should be 0"
        )


def test_hpi_geq_hdi():
    """HPI >= HDI because min(k) <= max(k)."""
    G = _make_overlap_graph()
    Hp = hub_promoted_index(G)
    Hd = hub_depressed_index(G)
    for u, v in G.edges():
        assert Hp[u][v]["hpi"] >= Hd[u][v]["hdi"] - 1e-10


def test_ordering_consistent_across_new_indices():
    """If B-C has more overlap than A-B, all measures should agree."""
    G = _make_overlap_graph()
    for method, attr in [
        (hub_promoted_index, "hpi"),
        (hub_depressed_index, "hdi"),
        (lhn_local_index, "lhn_local"),
        (adamic_adar_index, "adamic_adar"),
        (resource_allocation_index, "resource_allocation"),
    ]:
        H = method(G)
        assert H["B"]["C"][attr] > H["A"]["B"][attr], (
            f"{method.__name__}: B-C should score higher than A-B"
        )


def test_pa_independent_of_overlap():
    """PA only depends on degrees, not common neighbors."""
    G = _make_bridge_graph()
    H = preferential_attachment_score(G)
    # Bridge 2-3: deg(2)=3, deg(3)=3 -> PA=9
    # Intra-triangle 0-1: deg(0)=2, deg(1)=2 -> PA=4
    # Despite different overlap (0 vs 1), PA is the same for edges
    # with same degree product. Check 0-2 and 3-5 which have same degrees.
    # 0-2: deg(0)=2, deg(2)=3 -> PA=6
    # 3-5: deg(3)=3, deg(5)=2 -> PA=6
    assert H[0][2]["pa"] == H[3][5]["pa"]


# ── Integration smoke tests ─────────────────────────────────────────────


def test_all_proximity_undirected(two_cluster_undirected):
    """Smoke test: run every proximity method on an undirected graph."""
    for method, attr in [
        (neighborhood_overlap, "overlap"),
        (jaccard_backbone, "jaccard"),
        (dice_backbone, "dice"),
        (cosine_backbone, "cosine"),
        (hub_promoted_index, "hpi"),
        (hub_depressed_index, "hdi"),
        (lhn_local_index, "lhn_local"),
        (preferential_attachment_score, "pa"),
        (adamic_adar_index, "adamic_adar"),
        (resource_allocation_index, "resource_allocation"),
        (graph_distance_proximity, "dist"),
        (local_path_index, "lp"),
    ]:
        H = method(two_cluster_undirected)
        assert H.number_of_edges() == two_cluster_undirected.number_of_edges()
        for u, v, d in H.edges(data=True):
            assert attr in d, f"{method.__name__} missing attr {attr}"


def test_all_proximity_directed():
    """Smoke test: run every proximity method on a directed graph."""
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c"), ("c", "a")])
    for method, attr in [
        (neighborhood_overlap, "overlap"),
        (jaccard_backbone, "jaccard"),
        (dice_backbone, "dice"),
        (cosine_backbone, "cosine"),
        (hub_promoted_index, "hpi"),
        (hub_depressed_index, "hdi"),
        (lhn_local_index, "lhn_local"),
        (preferential_attachment_score, "pa"),
        (adamic_adar_index, "adamic_adar"),
        (resource_allocation_index, "resource_allocation"),
        (graph_distance_proximity, "dist"),
        (local_path_index, "lp"),
    ]:
        H = method(G)
        assert H.is_directed()
        for u, v, d in H.edges(data=True):
            assert attr in d, f"{method.__name__} missing attr {attr}"
