from random import randint

import pytest

np = pytest.importorskip("numpy")

import networkx as nx
import networkx.algorithms.maximum_weight_fractional_matching as mw


def get_max_weight_frac(res, G=nx.Graph()):
    return sum(frac * G.edges[edge]["weight"] for edge, frac in res.items())


class TestMaximumWeightFractionalMatching:
    def test_empty_graph(self):
        G = nx.Graph()
        res = mw.maximum_weight_fractional_matching(G)
        assert {} == res

    def test_graph_without_edges(self):
        G = nx.Graph()
        G.add_nodes_from([i for i in range(0, 10)])
        res = mw.maximum_weight_fractional_matching(G)
        assert {} == res

    def test_simple_graph_without_weights(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2"])
        G.add_edge("a1", "a2")
        res = mw.maximum_weight_fractional_matching(G)
        assert {("a1", "a2"): 1.0} == res

    def test_simple_graph_with_weight(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2"])
        G.add_edge("a1", "a2", weight=3)
        res = mw.maximum_weight_fractional_matching(G)
        assert {("a1", "a2"): 1.0} == res

    def test_simple_graph_with_negative_weight(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2"])
        G.add_edge("a1", "a2", weight=-1)
        res = mw.maximum_weight_fractional_matching(G)
        assert {("a1", "a2"): 0} == res

    def test_3_nodes_graph_without_weights(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"])
        G.add_edges_from([("a1", "a2"), ("a1", "a3"), ("a2", "a3")])
        res = mw.maximum_weight_fractional_matching(G)
        max_weight = np.round(sum(frac for frac in res.values()), 3)
        exp_val = {("a1", "a2"): 0.5, ("a1", "a3"): 0.5, ("a2", "a3"): 0.5}
        weight = np.round(sum(frac for frac in exp_val.values()), 3)
        assert weight == max_weight

    def test_simple_graph_with_equal_weights(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"])
        G.add_weighted_edges_from([("a1", "a2", 5), ("a1", "a3", 5), ("a2", "a3", 5)])
        res = mw.maximum_weight_fractional_matching(G)
        max_weight = get_max_weight_frac(res, G)
        exp_val = {("a1", "a2"): 0.5, ("a1", "a3"): 0.5, ("a2", "a3"): 0.5}
        weight = get_max_weight_frac(exp_val, G)
        assert weight == max_weight

    def test_3_nodes_graph_1_3_weights(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"])
        G.add_weighted_edges_from([("a1", "a2", 1), ("a1", "a3", 2), ("a2", "a3", 3)])
        res = mw.maximum_weight_fractional_matching(G)
        max_weight = get_max_weight_frac(res, G)
        exp_val = {("a1", "a2"): 0.5, ("a1", "a3"): 0.5, ("a2", "a3"): 0.5}
        weight = get_max_weight_frac(exp_val, G)
        assert weight == max_weight

    def test_3_nodes_graph_with_weights(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"])
        G.add_weighted_edges_from([("a1", "a2", 1), ("a1", "a3", 2), ("a2", "a3", 4)])
        res = mw.maximum_weight_fractional_matching(G)
        max_weight = get_max_weight_frac(res, G)
        exp_val = {("a1", "a2"): 0.0, ("a1", "a3"): 0.0, ("a2", "a3"): 1.0}
        weight = get_max_weight_frac(exp_val, G)
        assert weight == max_weight

    def test_3_nodes_graph_with_negative_weight(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"])
        G.add_weighted_edges_from([("a1", "a2", -1), ("a1", "a3", 5), ("a2", "a3", 10)])
        res = mw.maximum_weight_fractional_matching(G)
        max_weight = get_max_weight_frac(res, G)
        exp_val = {("a1", "a2"): 0.0, ("a1", "a3"): 0.0, ("a2", "a3"): 1.0}
        weight = get_max_weight_frac(exp_val, G)
        assert weight == max_weight

    def test_7_nodes_graph_without_weights(self):
        G = nx.Graph()
        G.add_nodes_from([i for i in range(0, 7)])
        G.add_edges_from(
            [(0, 1), (0, 2), (0, 6), (0, 5), (1, 6), (2, 3), (2, 4), (2, 6), (3, 4)]
        )
        res = mw.maximum_weight_fractional_matching(G)
        max_weight = np.round(sum(frac for frac in res.values()), 3)
        exp_val = {
            (0, 1): 0.0,
            (0, 2): 0.0,
            (0, 6): 0.0,
            (0, 5): 1.0,
            (1, 6): 1.0,
            (2, 3): 0.5,
            (2, 4): 0.5,
            (2, 6): 0.0,
            (3, 4): 0.5,
        }
        weight = np.round(sum(frac for frac in exp_val.values()), 3)
        assert weight == max_weight

    def test_7_nodes_graph_with_weights(self):
        G = nx.Graph()
        G.add_nodes_from([i for i in range(0, 7)])
        G.add_weighted_edges_from(
            [
                (0, 1, 12),
                (0, 2, 7),
                (0, 6, 21),
                (0, 5, 6),
                (1, 6, 1),
                (2, 3, 23),
                (2, 4, 5),
                (2, 6, 8),
                (3, 4, 19),
            ]
        )
        res = mw.maximum_weight_fractional_matching(G)
        max_weight = get_max_weight_frac(res, G)
        exp_val = {
            (0, 1): 0.0,
            (0, 2): 0.0,
            (0, 6): 1.0,
            (0, 5): 0.0,
            (1, 6): 0.0,
            (2, 3): 0.5,
            (2, 4): 0.5,
            (2, 6): 0.0,
            (3, 4): 0.5,
        }
        weight = get_max_weight_frac(exp_val, G)
        assert weight == max_weight

    def test_completes_graph_without_weights(self):
        for i in range(0, 5):
            n = randint(2, 30)
            G = nx.complete_graph(n)
            res = mw.maximum_weight_fractional_matching(G)
            max_weight = np.round(sum(frac for frac in res.values()), 3)
            weight = np.round((1 / (n - 1)) * len(G.edges()), 3)
            assert weight == max_weight

    def test_sum_of_weights_in_every_node_in_random_graph_is_less_than_1(self):
        seed = 1
        for i in range(0, 5):
            G = nx.random_regular_graph(4, 6, seed)
            res = mw.maximum_weight_fractional_matching(G)
            for node in G.nodes:
                sum_adj = 0
                for edge in G.edges(node):
                    if edge in res:
                        sum_adj += res[edge]
                    else:
                        sum_adj += res[(edge[1], edge[0])]
                assert sum_adj == 1
