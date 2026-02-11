"""Tests for hybrid backbone methods.

Covers: glab_filter (Globally and Locally Adaptive Backbone).
"""

import pytest
import networkx as nx

from backbone.hybrid import glab_filter
from backbone.filters import threshold_filter


def test_glab_pvalues_added(two_cluster_undirected):
    H = glab_filter(two_cluster_undirected)
    for u, v, d in H.edges(data=True):
        assert "glab_pvalue" in d
        assert 0 <= d["glab_pvalue"] <= 1


def test_glab_preserves_structure(two_cluster_undirected):
    H = glab_filter(two_cluster_undirected)
    assert H.number_of_nodes() == two_cluster_undirected.number_of_nodes()
    assert H.number_of_edges() == two_cluster_undirected.number_of_edges()


def test_glab_bridge_significant(two_cluster_undirected):
    """The bridge between clusters should be significant (high betweenness)."""
    H = glab_filter(two_cluster_undirected)
    bridge_pval = H[3][4]["glab_pvalue"]
    assert bridge_pval < 0.5


def test_glab_c_parameter(two_cluster_undirected):
    """Different c values should produce different scores."""
    H1 = glab_filter(two_cluster_undirected, c=0.0)
    H2 = glab_filter(two_cluster_undirected, c=1.0)
    pvals1 = [d["glab_pvalue"] for _, _, d in H1.edges(data=True)]
    pvals2 = [d["glab_pvalue"] for _, _, d in H2.edges(data=True)]
    assert pvals1 != pvals2


def test_glab_raises_on_directed(two_cluster_directed):
    with pytest.raises(nx.NetworkXError):
        glab_filter(two_cluster_directed)


def test_glab_filtering_pipeline(two_cluster_undirected):
    H = glab_filter(two_cluster_undirected)
    bb = threshold_filter(H, "glab_pvalue", 0.1, "below")
    for u, v in bb.edges():
        assert two_cluster_undirected.has_edge(u, v)
