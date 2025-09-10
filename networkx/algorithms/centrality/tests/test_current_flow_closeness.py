import pytest

pytest.importorskip("numpy")
pytest.importorskip("scipy")

import networkx as nx


class TestFlowClosenessCentrality:
    @pytest.mark.parametrize(
        ("G", "answer"),
        [
            (nx.complete_graph(4), {0: 2.0 / 3, 1: 2.0 / 3, 2: 2.0 / 3, 3: 2.0 / 3}),
            (nx.path_graph(4), {0: 1.0 / 6, 1: 1.0 / 4, 2: 1.0 / 4, 3: 1.0 / 6}),
            (
                nx.path_graph(4, create_using=nx.MultiGraph),
                {0: 1.0 / 6, 1: 1.0 / 4, 2: 1.0 / 4, 3: 1.0 / 6},
            ),
            (
                nx.star_graph(["a", "b", "c", "d"]),
                {"a": 1.0 / 3, "b": 1.0 / 5, "c": 1.0 / 5, "d": 1.0 / 5},
            ),
            (nx.Graph(), {}),
            (nx.empty_graph(1), {0: 1.0}),
            (nx.Graph([(0, 0)]), {0: 1.0}),
            (nx.path_graph(2), {0: 1.0, 1: 1.0}),
        ],
    )
    def test_cfcc(self, G, answer):
        """Current-flow closeness centrality: basic tests."""
        b = nx.current_flow_closeness_centrality(G)
        assert all(b[n] == pytest.approx(answer[n], abs=1e-7) for n in G)

    @pytest.mark.parametrize("G", [nx.empty_graph(3), nx.Graph([(0, 1), (2, 3)])])
    def test_cfcc_not_connected(self, G):
        """Current-flow closeness centrality: not connected exceptions."""
        with pytest.raises(nx.NetworkXError, match=r"not connected"):
            nx.current_flow_closeness_centrality(G)

    @pytest.mark.parametrize("G", [nx.DiGraph(), nx.MultiDiGraph()])
    def test_cfcc_not_implemented(self, G):
        """Current-flow closeness centrality: not implemented exceptions."""
        with pytest.raises(
            nx.NetworkXNotImplemented, match=r"not implemented for directed"
        ):
            nx.current_flow_closeness_centrality(G)


class TestWeightedFlowClosenessCentrality:
    pass
