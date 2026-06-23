"""Tests for the PLL reachability index (``nx.pll_reachability_index``)."""

import pytest

import networkx as nx


def _first_mismatch_vs_has_path(G):
    """Return the first (s, t) where the index disagrees with has_path, or None."""
    idx = nx.pll_reachability_index(G)
    for s in G:
        for t in G:
            if idx.is_reachable(s, t) != nx.has_path(G, s, t):
                return (s, t, idx.is_reachable(s, t), nx.has_path(G, s, t))
    return None


class TestKnownAnswers:
    """Hand-checked small graphs with explicit expected reachabilities."""

    def test_simple_path(self):
        G = nx.DiGraph([(0, 1), (1, 2), (2, 3)])
        idx = nx.pll_reachability_index(G)
        assert idx.is_reachable(0, 3) is True
        assert idx.is_reachable(3, 0) is False
        assert idx.is_reachable(1, 2) is True
        assert idx.is_reachable(0, 0) is True  # a node reaches itself

    def test_branching_dag(self):
        G = nx.DiGraph([(0, 1), (0, 2), (1, 3), (2, 3)])
        idx = nx.pll_reachability_index(G)
        assert idx.is_reachable(0, 3) is True
        assert idx.is_reachable(1, 2) is False
        assert idx.is_reachable(3, 0) is False

    def test_cycle_is_mutually_reachable(self):
        # strongly connected {0,1,2}, then an edge out to 3
        G = nx.DiGraph([(0, 1), (1, 2), (2, 0), (2, 3)])
        idx = nx.pll_reachability_index(G)
        assert idx.is_reachable(0, 2) is True
        assert idx.is_reachable(2, 0) is True  # reachable around the cycle
        assert idx.is_reachable(1, 3) is True
        assert idx.is_reachable(3, 0) is False

    def test_string_node_labels(self):
        # graphs loaded from edge-list files use string node ids
        G = nx.DiGraph([("a", "b"), ("b", "c")])
        idx = nx.pll_reachability_index(G)
        assert idx.is_reachable("a", "c") is True
        assert idx.is_reachable("c", "a") is False


class TestCorrectness:
    """Exhaustive all-pairs agreement with has_path on generated graphs."""

    @pytest.mark.parametrize("seed", range(8))
    @pytest.mark.parametrize("acyclic", [True, False])
    def test_exhaustive_vs_has_path(self, seed, acyclic):
        n = 40
        H = nx.gnp_random_graph(n, 0.07, seed=seed, directed=True)
        if acyclic:
            G = nx.DiGraph((u, v) for u, v in H.edges() if u < v)
        else:
            G = H
        G.add_nodes_from(range(n))
        assert _first_mismatch_vs_has_path(G) is None

    @pytest.mark.parametrize("density", [0.02, 0.05, 0.15, 0.40])
    def test_exhaustive_varying_density(self, density):
        G = nx.gnp_random_graph(50, density, seed=11, directed=True)
        G.add_nodes_from(range(50))
        assert _first_mismatch_vs_has_path(G) is None


class TestEdgeCases:
    def test_empty_graph(self):
        nx.pll_reachability_index(
            nx.DiGraph()
        )  # builds without error; nothing to query

    def test_single_node(self):
        G = nx.DiGraph()
        G.add_node(0)
        idx = nx.pll_reachability_index(G)
        assert idx.is_reachable(0, 0) is True

    def test_self_loop(self):
        G = nx.DiGraph([(0, 0), (0, 1)])
        idx = nx.pll_reachability_index(G)
        assert idx.is_reachable(0, 1) is True
        assert idx.is_reachable(1, 0) is False
        assert idx.is_reachable(0, 0) is True

    def test_isolated_nodes(self):
        G = nx.DiGraph()
        G.add_nodes_from(range(5))
        idx = nx.pll_reachability_index(G)
        assert idx.is_reachable(0, 0) is True
        assert idx.is_reachable(0, 1) is False

    def test_disconnected_components(self):
        G = nx.DiGraph([(0, 1), (1, 2), (10, 11)])
        idx = nx.pll_reachability_index(G)
        assert idx.is_reachable(0, 2) is True
        assert idx.is_reachable(0, 10) is False
        assert idx.is_reachable(10, 11) is True

    def test_single_scc(self):
        G = nx.DiGraph([(i, (i + 1) % 6) for i in range(6)])  # 6-cycle
        idx = nx.pll_reachability_index(G)
        for s in range(6):
            for t in range(6):
                assert idx.is_reachable(s, t) is True

    def test_complete_digraph(self):
        G = nx.complete_graph(5, create_using=nx.DiGraph)
        assert _first_mismatch_vs_has_path(G) is None


class TestValidation:
    def test_missing_source_raises(self):
        idx = nx.pll_reachability_index(nx.DiGraph([(0, 1)]))
        with pytest.raises(nx.NodeNotFound):
            idx.is_reachable(99, 1)

    def test_missing_target_raises(self):
        idx = nx.pll_reachability_index(nx.DiGraph([(0, 1)]))
        with pytest.raises(nx.NodeNotFound):
            idx.is_reachable(0, 99)
