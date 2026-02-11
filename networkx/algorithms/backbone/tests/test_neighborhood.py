"""Tests for neighborhood overlap and similarity backbone methods.

Covers: neighborhood_overlap, jaccard_backbone, dice_backbone,
cosine_backbone, and cross-method relationship properties.
"""

import math

import pytest
import networkx as nx

from backbone.structural import (
    neighborhood_overlap,
    jaccard_backbone,
    dice_backbone,
    cosine_backbone,
)
from backbone.filters import threshold_filter


def _make_overlap_graph():
    """Graph with known neighborhood overlaps.

    Nodes A-B-C form a triangle. D connects to B and C.
    """
    G = nx.Graph()
    G.add_edges_from([("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D")])
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
    G = nx.path_graph(3)  # 0-1-2
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
    # A-B: overlap=1, union=4 -> J = 0.25
    assert H["A"]["B"]["jaccard"] == pytest.approx(0.25)
    # B-C: overlap=2, union=4 -> J = 0.5
    assert H["B"]["C"]["jaccard"] == pytest.approx(0.5)


def test_jaccard_complete_graph():
    """In K_4: N(0)={1,2,3}, N(1)={0,2,3}, intersection={2,3}, union=4 -> J=0.5."""
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
    """A bridge between two cliques should get J=0 (no common neighbors)."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # triangle
    G.add_edges_from([(3, 4), (3, 5), (4, 5)])  # triangle
    G.add_edge(2, 3)  # bridge
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
    # A-B: overlap=1, deg(A)=2, deg(B)=3 -> D = 2*1/(2+3) = 0.4
    assert H["A"]["B"]["dice"] == pytest.approx(0.4)
    # B-C: overlap=2, deg(B)=3, deg(C)=3 -> D = 4/6
    assert H["B"]["C"]["dice"] == pytest.approx(4.0 / 6.0)


def test_dice_complete_graph():
    """In K_4: overlap=2, deg=3 for all -> D = 4/6 = 2/3."""
    G = nx.complete_graph(4)
    H = dice_backbone(G)
    for u, v, d in H.edges(data=True):
        assert d["dice"] == pytest.approx(2.0 / 3.0)


def test_dice_bridge_gets_zero():
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (1, 2)])
    G.add_edges_from([(3, 4), (3, 5), (4, 5)])
    G.add_edge(2, 3)
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
    # A-B: overlap=1, deg(A)=2, deg(B)=3 -> C = 1/sqrt(6)
    assert H["A"]["B"]["cosine"] == pytest.approx(1.0 / math.sqrt(6))
    # B-C: overlap=2, deg(B)=3, deg(C)=3 -> C = 2/3
    assert H["B"]["C"]["cosine"] == pytest.approx(2.0 / 3.0)


def test_cosine_complete_graph():
    """In K_4: overlap=2, deg=3 -> C = 2/sqrt(9) = 2/3."""
    G = nx.complete_graph(4)
    H = cosine_backbone(G)
    for u, v, d in H.edges(data=True):
        assert d["cosine"] == pytest.approx(2.0 / 3.0)


def test_cosine_bridge_gets_zero():
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (1, 2)])
    G.add_edges_from([(3, 4), (3, 5), (4, 5)])
    G.add_edge(2, 3)
    H = cosine_backbone(G)
    assert H[2][3]["cosine"] == pytest.approx(0.0)


def test_cosine_directed():
    G = nx.DiGraph([("a", "b"), ("a", "c"), ("b", "c")])
    H = cosine_backbone(G)
    assert H.is_directed()


# ── Cross-method relationships ───────────────────────────────────────────


def test_overlap_all_agree_on_zero():
    """Bridge edges with no common neighbors -> all measures = 0."""
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
