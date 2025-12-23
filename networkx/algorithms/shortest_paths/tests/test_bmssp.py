import pytest

import networkx as nx

from networkx.algorithms.shortest_paths.bmssp import (
    single_source_bmssp_path,
    single_source_bmssp_path_length,
    multi_source_bmssp_path,
    multi_source_bmssp_path_length,
    bmssp,
)

class TestSingleSourceBMSSPPath:
    def test_simple_path(self):
        G = nx.DiGraph(nx.path_graph(5))
        path = single_source_bmssp_path(G, 0, 4, precision=0)
        assert path == [0, 1, 2, 3, 4]

    def test_weighted_graph(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=1)
        G.add_edge(1, 2, weight=2)
        G.add_edge(0, 2, weight=5)
        path = single_source_bmssp_path(G, 0, 2, precision=0)
        assert path == [0, 1, 2]

    def test_string_nodes(self):
        G = nx.DiGraph()
        G.add_edge("A", "B", weight=1)
        G.add_edge("B", "C", weight=2)
        G.add_edge("A", "C", weight=10)
        path = single_source_bmssp_path(G, "A", "C", precision=0)
        assert path == ["A", "B", "C"]

    def test_source_not_in_graph(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        pytest.raises(nx.NodeNotFound, single_source_bmssp_path, G, 99, 1)

    def test_target_not_in_graph(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        pytest.raises(nx.NodeNotFound, single_source_bmssp_path, G, 0, 99)

    def test_no_path(self):
        G = nx.DiGraph()
        G.add_node(0)
        G.add_node(1)
        pytest.raises(nx.NetworkXNoPath, single_source_bmssp_path, G, 0, 1)


class TestSingleSourceBMSSPPathLength:
    def test_simple_path(self):
        G = nx.DiGraph(nx.path_graph(5))
        length = single_source_bmssp_path_length(G, 0, 4, precision=0)
        assert length == 4

    def test_same_node(self):
        G = nx.DiGraph(nx.path_graph(5))
        length = single_source_bmssp_path_length(G, 2, 2, precision=0)
        assert length == 0

    def test_weighted_graph(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=3)
        G.add_edge(1, 2, weight=4)
        G.add_edge(0, 2, weight=10)
        length = single_source_bmssp_path_length(G, 0, 2, precision=0)
        assert length == 7

    def test_source_not_in_graph(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        pytest.raises(nx.NodeNotFound, single_source_bmssp_path_length, G, 99, 1)

    def test_no_path(self):
        G = nx.DiGraph()
        G.add_node(0)
        G.add_node(1)
        pytest.raises(nx.NetworkXNoPath, single_source_bmssp_path_length, G, 0, 1)


class TestMultiSourceBMSSPPath:
    def test_multiple_sources(self):
        G = nx.DiGraph()
        G.add_edge(0, 2, weight=3)
        G.add_edge(1, 2, weight=1)
        G.add_edge(2, 3, weight=2)
        paths = multi_source_bmssp_path(G, {0, 1}, precision=0)
        assert paths[2] == [1, 2]

    def test_single_source(self):
        G = nx.DiGraph(nx.path_graph(4))
        paths = multi_source_bmssp_path(G, {0}, precision=0)
        assert paths[3] == [0, 1, 2, 3]

    def test_empty_sources(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        pytest.raises(ValueError, multi_source_bmssp_path, G, set())

    def test_source_not_in_graph(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        pytest.raises(nx.NodeNotFound, multi_source_bmssp_path, G, {99})


class TestMultiSourceBMSSPPathLength:
    def test_multiple_sources(self):
        G = nx.DiGraph()
        G.add_edge(0, 2, weight=5)
        G.add_edge(1, 2, weight=2)
        G.add_edge(2, 3, weight=3)
        lengths = multi_source_bmssp_path_length(G, {0, 1}, precision=0)
        assert lengths[0] == 0
        assert lengths[1] == 0
        assert lengths[2] == 2
        assert lengths[3] == 5

    def test_empty_sources(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        pytest.raises(ValueError, multi_source_bmssp_path_length, G, set())


class TestBMSSP:
    def test_basic(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=1)
        G.add_edge(1, 2, weight=2)
        G.add_edge(0, 2, weight=4)
        distances, paths = bmssp(G, {0}, precision=0)
        assert distances[0] == 0
        assert distances[1] == 1
        assert distances[2] == 3
        assert paths[2] == [0, 1, 2]

    def test_with_target(self):
        G = nx.DiGraph(nx.path_graph(10))
        distances, paths = bmssp(G, {0}, target=3, precision=0)
        assert 3 in distances
        assert distances[3] == 3

    def test_custom_weight_attribute(self):
        G = nx.DiGraph()
        G.add_edge("A", "B", cost=2)
        G.add_edge("B", "C", cost=3)
        G.add_edge("A", "C", cost=10)
        distances, paths = bmssp(G, {"A"}, weight="cost", precision=0)
        assert distances["C"] == 5
        assert paths["C"] == ["A", "B", "C"]

    def test_undirected_graph_raises(self):
        G = nx.Graph()
        G.add_edge(0, 1)
        pytest.raises(nx.NetworkXNotImplemented, bmssp, G, {0})

    def test_negative_weight_raises(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=-1)
        pytest.raises(ValueError, bmssp, G, {0})

    def test_cycle_graph(self):
        G = nx.DiGraph()
        nx.add_cycle(G, [0, 1, 2, 3])
        distances, paths = bmssp(G, {0}, precision=0)
        assert distances[0] == 0
        assert distances[1] == 1
        assert distances[2] == 2
        assert distances[3] == 3

    def test_weighted_three_edges(self):
        G = nx.DiGraph()
        G.add_weighted_edges_from(
            [[0, 1, 2], [1, 2, 12], [2, 3, 1], [3, 4, 5], [4, 5, 1], [5, 0, 10]]
        )
        distances, paths = bmssp(G, {0}, precision=0)
        assert distances[3] == 15

    def test_weighted_two_edges(self):
        G = nx.DiGraph()
        G.add_weighted_edges_from(
            [
                [0, 1, 2],
                [1, 2, 2],
                [2, 3, 1],
                [3, 4, 1],
                [4, 5, 1],
                [5, 6, 1],
                [6, 7, 1],
                [7, 0, 1],
            ]
        )
        distances, paths = bmssp(G, {0}, precision=0)
        assert distances[2] == 4


class TestBMSSPWeightFunction:
    def test_callable_weight(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, color="red", weight=1)
        G.add_edge(1, 2, color="red", weight=1)
        G.add_edge(0, 2, color="blue", weight=1)
        def red_only(u, v, d):
            if d.get("color") == "red":
                return d.get("weight", 1)
            return None
        distances, paths = bmssp(G, {0}, weight=red_only, precision=0)
        assert paths[2] == [0, 1, 2]
        assert distances[2] == 2

    def test_node_weight_function(self):
        G = nx.DiGraph()
        G.add_node(0, node_weight=2)
        G.add_node(1, node_weight=4)
        G.add_node(2, node_weight=6)
        G.add_edge(0, 1, weight=1)
        G.add_edge(1, 2, weight=1)
        def func(u, v, d):
            node_u_wt = G.nodes[u].get("node_weight", 1)
            node_v_wt = G.nodes[v].get("node_weight", 1)
            edge_wt = d.get("weight", 1)
            return node_u_wt / 2 + node_v_wt / 2 + edge_wt
        distances, paths = bmssp(G, {0}, weight=func, precision=0)
        # Edge 0->1: 2/2 + 4/2 + 1 = 4
        # Edge 1->2: 4/2 + 6/2 + 1 = 6
        # Total 0->2: 10
        assert distances[1] == 4
        assert distances[2] == 10


class TestBMSSPValidation:
    def test_compare_with_dijkstra(self):
        """Validate BMSSP results against Dijkstra's algorithm."""
        import random
        random.seed(42)
        G = nx.gnm_random_graph(50, 150, directed=True, seed=42)
        for u, v in G.edges():
            G[u][v]["weight"] = random.randint(1, 10)
        distances, paths = bmssp(G, {0}, precision=0)
        for target in distances:
            if target == 0:
                continue
            try:
                dijkstra_len = nx.dijkstra_path_length(G, 0, target)
                assert abs(distances[target] - dijkstra_len) < 0.001
            except nx.NetworkXNoPath:
                pass


    def test_larger_graph(self):
        """Test with a larger 100-node graph."""
        import random
        random.seed(123)
        G = nx.gnm_random_graph(100, 400, directed=True, seed=123)
        for u, v in G.edges():
            G[u][v]["weight"] = random.randint(1, 20)
        distances, paths = bmssp(G, {0}, precision=0)
        assert len(distances) > 0
        # Spot check a few nodes
        for target in [10, 25, 50]:
            if target in distances:
                try:
                    dijkstra_len = nx.dijkstra_path_length(G, 0, target)
                    assert abs(distances[target] - dijkstra_len) < 0.001
                except nx.NetworkXNoPath:
                    pass
