import pytest

pytest.importorskip("numpy")
pytest.importorskip("scipy")

from contextlib import nullcontext as does_not_raise

import networkx as nx


class TestFlowClosenessCentrality:
    def test_K4(self):
        """Current flow closeness centrality: K4"""
        G = nx.complete_graph(4)
        b = nx.current_flow_closeness_centrality(G)
        b_answer = {0: 2.0 / 3, 1: 2.0 / 3, 2: 2.0 / 3, 3: 2.0 / 3}
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_P4(self):
        """Current flow closeness centrality: P4"""
        G = nx.path_graph(4)
        b = nx.current_flow_closeness_centrality(G)
        b_answer = {0: 1.0 / 6, 1: 1.0 / 4, 2: 1.0 / 4, 3: 1.0 / 6}
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_star(self):
        """Current flow closeness centrality: star"""
        G = nx.Graph()
        nx.add_star(G, ["a", "b", "c", "d"])
        b = nx.current_flow_closeness_centrality(G)
        b_answer = {"a": 1.0 / 3, "b": 0.6 / 3, "c": 0.6 / 3, "d": 0.6 / 3}
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    @pytest.mark.parametrize(
        ("G", "result"),
        [
            (nx.Graph(), {}),
            (nx.path_graph(1), {0: 1.0}),
            (nx.path_graph(2), {0: 1.0, 1: 1.0}),
        ],
    )
    def test_small(self, G, result):
        """Current flow closeness centrality: small graphs"""
        b = nx.current_flow_closeness_centrality(G)
        for n in sorted(G):
            assert b[n] == pytest.approx(result[n], abs=1e-7)

    @pytest.mark.parametrize(
        ("G", "expectation", "msg"),
        [
            (nx.Graph(), does_not_raise(), None),
            (nx.DiGraph(), nx.NetworkXNotImplemented, "not implemented for directed"),
            (
                nx.MultiGraph(),
                nx.NetworkXNotImplemented,
                "not implemented for multigraph",
            ),
            (
                nx.MultiDiGraph(),
                nx.NetworkXNotImplemented,
                "not implemented for multigraph",
            ),
        ],
    )
    def test_cfcc_type_exceptions(self, G, expectation, msg):
        """Current flow closeness centrality: type exceptions"""
        if msg is not None:
            with pytest.raises(expectation, match=msg):
                nx.current_flow_closeness_centrality(G)
        else:
            with does_not_raise():
                nx.current_flow_closeness_centrality(G)

    @pytest.mark.parametrize("n", range(5))
    def test_cfcc_connectivity_exceptions(self, n):
        """Current flow closeness centrality: connectivity exceptions"""
        G = nx.empty_graph(n)
        H = nx.path_graph(n)

        if n < 2:
            with does_not_raise():
                nx.current_flow_closeness_centrality(G)
        else:
            with pytest.raises(nx.NetworkXError, match="graph is not connected"):
                nx.current_flow_closeness_centrality(G)

        with does_not_raise():
            nx.current_flow_closeness_centrality(H)


class TestWeightedFlowClosenessCentrality:
    pass
