import unittest
from random import randint

import networkx as nx
import networkx.algorithms.maximum_weight_fractional_matching as mw


class MyTestCase(unittest.TestCase):
    def test_empty_graph(self):
        G = nx.Graph()
        res = mw.maximum_weight_fractional_matching(G)
        self.assertEqual({}, res)

    def test_graph_without_edges(self):
        G = nx.Graph()
        G.add_nodes_from([i for i in range(0, 10)])
        res = mw.maximum_weight_fractional_matching(G)
        self.assertEqual({}, res)

    def test_simple_graph_without_weights(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2"])
        G.add_edge("a1", "a2")
        res = mw.maximum_weight_fractional_matching(G)
        self.assertEqual({("a1", "a2"): 1.0}, res)

    def test_simple_graph_with_weight(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2"])
        G.add_edge("a1", "a2", weight=3)
        res = mw.maximum_weight_fractional_matching(G)
        self.assertEqual({("a1", "a2"): 0.333}, res)

    def test_simple_graph_with_negative_weight(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2"])
        G.add_edge("a1", "a2", weight=-1)
        res = mw.maximum_weight_fractional_matching(G)
        self.assertEqual({("a1", "a2"): 0}, res)

    def test_3_nodes_graph_without_weights(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"])
        G.add_edges_from([("a1", "a2"), ("a1", "a3"), ("a2", "a3")])
        res = mw.maximum_weight_fractional_matching(G)
        self.assertEqual({("a1", "a2"): 0.5, ("a1", "a3"): 0.5, ("a2", "a3"): 0.5}, res)

    def test_3_nodes_graph_with_weights(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"])
        G.add_weighted_edges_from([("a1", "a2", 1), ("a1", "a3", 2), ("a2", "a3", 3)])
        res = mw.maximum_weight_fractional_matching(G)
        self.assertEqual(
            {("a1", "a2"): 0.5, ("a1", "a3"): 0.25, ("a2", "a3"): 0.167}, res
        )

    def test_3_nodes_graph_with_negative_weights(self):
        G = nx.Graph()
        G.add_nodes_from(["a1", "a2", "a3"])
        G.add_weighted_edges_from([("a1", "a2", -1), ("a1", "a3", 5), ("a2", "a3", 10)])
        res = mw.maximum_weight_fractional_matching(G)
        self.assertEqual(
            {("a1", "a2"): 0.0, ("a1", "a3"): 0.101, ("a2", "a3"): 0.05}, res
        )

    def test_6_nodes_graph_without_weights(self):
        exp_value = {
            (0, 1): 0.25,
            (0, 2): 0.25,
            (0, 6): 0.25,
            (0, 5): 0.25,
            (1, 6): 0.5,
            (2, 3): 0.25,
            (2, 4): 0.25,
            (2, 6): 0.25,
            (3, 4): 0.75,
        }
        G = nx.Graph()
        G.add_nodes_from([i for i in range(0, 10)])
        G.add_edges_from(
            [(0, 1), (0, 2), (0, 6), (0, 5), (1, 6), (2, 3), (2, 4), (2, 6), (3, 4)]
        )
        res = mw.maximum_weight_fractional_matching(G)
        for edge in exp_value:
            self.assertEqual(exp_value[edge], res[edge])

    def test_completes_graph_without_weights(self):
        for i in range(0, 5):
            n = randint(0, 30)
            G = nx.complete_graph(n)
            res = mw.maximum_weight_fractional_matching(G)
            for edge in res.values():
                self.assertEqual(edge, 1 / (n - 1))

    def test_sum_of_weights_in_every_node_in_random_graph_is_less_than_1(self):
        seed = 1
        for i in range(0, 5):
            n = randint(0, 7)
            d = randint(0, 5)
            G = nx.random_regular_graph(4, 6, seed)
            res = mw.maximum_weight_fractional_matching(G)
            for node in G.nodes:
                sum = 0
                for edge in G.edges(node):
                    if edge in res:
                        sum += res[edge]
                    else:
                        sum += res[(edge[1], edge[0])]
                self.assertLessEqual(sum, 1)


if __name__ == "__main__":
    unittest.main()
