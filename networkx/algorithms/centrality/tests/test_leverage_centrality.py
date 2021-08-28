import math
import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")

import networkx as nx


class TestLeverageCentrality:
    def test_K5(self):
        """Leverage centrality: K5"""
        G = nx.complete_graph(5)
        b = nx.leverage_centrality(G)
        b_answer = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_P3(self):
        """Leverage centrality: P3"""
        G = nx.path_graph(3)
        b_answer = {0: -0.333333, 1: 0.333333, 2: -0.333333}
        b = nx.leverage_centrality(G)
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-4)

    def test_P3_weighted(self):
        """Leverage centrality: P3"""
        G = nx.path_graph(3)
        G.edges[0, 1]["weight"] = 3
        G.edges[1, 2]["weight"] = 5
        b_answer = {0: -0.15151, 1: 0.0856643, 2: -0.0461538}
        b = nx.leverage_centrality(G, weight="weight")
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-4)


class TestLeverageCentralityExceptions:
    def test_multigraph(self):
        with pytest.raises(nx.NetworkXException):
            e = nx.leverage_centrality(nx.MultiGraph())

    def test_multigraph_numpy(self):
        with pytest.raises(nx.NetworkXException):
            e = nx.leverage_centrality(nx.MultiGraph())

    def test_empty(self):
        with pytest.raises(nx.NetworkXException):
            e = nx.leverage_centrality(nx.Graph())

    def test_empty_numpy(self):
        with pytest.raises(nx.NetworkXException):
            e = nx.leverage_centrality(nx.Graph())
