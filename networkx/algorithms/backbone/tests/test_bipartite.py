"""Tests for bipartite backbone methods.

Covers: sdsm (Stochastic Degree Sequence Model) and
fdsm (Fixed Degree Sequence Model).
"""

import pytest

import networkx as nx
from networkx.algorithms.backbone.bipartite import fdsm, sdsm

np = pytest.importorskip("numpy")
sp = pytest.importorskip("scipy")


def _make_bipartite():
    """Simple bipartite graph: 3 agents, 4 artifacts.

    Agent A1 connects to F1, F2, F3
    Agent A2 connects to F1, F2
    Agent A3 connects to F3, F4
    """
    B = nx.Graph()
    agents = ["A1", "A2", "A3"]
    artifacts = ["F1", "F2", "F3", "F4"]
    B.add_nodes_from(agents, bipartite=0)
    B.add_nodes_from(artifacts, bipartite=1)
    B.add_edges_from(
        [
            ("A1", "F1"),
            ("A1", "F2"),
            ("A1", "F3"),
            ("A2", "F1"),
            ("A2", "F2"),
            ("A3", "F3"),
            ("A3", "F4"),
        ]
    )
    return B, agents


# ── SDSM ─────────────────────────────────────────────────────────────────


def test_sdsm_returns_graph():
    B, agents = _make_bipartite()
    bb = sdsm(B, agents)
    assert isinstance(bb, nx.Graph)


def test_sdsm_agent_nodes_only():
    """Backbone should only contain agent nodes."""
    B, agents = _make_bipartite()
    bb = sdsm(B, agents)
    for node in bb.nodes():
        assert node in agents


def test_sdsm_pvalues_present():
    B, agents = _make_bipartite()
    bb = sdsm(B, agents)
    for u, v, d in bb.edges(data=True):
        assert "sdsm_pvalue" in d
        assert 0 <= d["sdsm_pvalue"] <= 1


def test_sdsm_high_cooccurrence_significant():
    """A1 and A2 share 2/4 artifacts -- should be among the most significant."""
    B, agents = _make_bipartite()
    bb = sdsm(B, agents, alpha=1.0)  # alpha=1 -> keep all for inspection
    p12 = bb["A1"]["A2"]["sdsm_pvalue"]
    if bb.has_edge("A2", "A3"):
        p23 = bb["A2"]["A3"]["sdsm_pvalue"]
        assert p12 <= p23


def test_sdsm_raises_non_bipartite():
    G = nx.Graph([(0, 1), (1, 2), (0, 2)])  # triangle -- not bipartite
    with pytest.raises(nx.NetworkXError):
        sdsm(G, [0])


# ── FDSM ─────────────────────────────────────────────────────────────────


def test_fdsm_returns_graph():
    B, agents = _make_bipartite()
    bb = fdsm(B, agents, trials=100, seed=42)
    assert isinstance(bb, nx.Graph)


def test_fdsm_agent_nodes_only():
    B, agents = _make_bipartite()
    bb = fdsm(B, agents, trials=100, seed=42)
    for node in bb.nodes():
        assert node in agents


def test_fdsm_pvalues_present():
    B, agents = _make_bipartite()
    bb = fdsm(B, agents, trials=100, seed=42)
    for u, v, d in bb.edges(data=True):
        assert "fdsm_pvalue" in d
        assert 0 <= d["fdsm_pvalue"] <= 1


def test_fdsm_reproducible_with_seed():
    B, agents = _make_bipartite()
    bb1 = fdsm(B, agents, trials=100, seed=42)
    bb2 = fdsm(B, agents, trials=100, seed=42)
    for u, v, d1 in bb1.edges(data=True):
        d2 = bb2[u][v]
        assert d1["fdsm_pvalue"] == d2["fdsm_pvalue"]


def test_fdsm_raises_non_bipartite():
    G = nx.Graph([(0, 1), (1, 2), (0, 2)])
    with pytest.raises(nx.NetworkXError):
        fdsm(G, [0])
