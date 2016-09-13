from nose.tools import assert_equal
import networkx as nx
from networkx.algorithms.steinertree import metric_closure, steiner_tree


class TestSteinerTree:
    def set_up(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=1)
        G.add_edge(2, 3, weight=1)
        G.add_edge(3, 4, weight=1)
        G.add_edge(4, 5, weight=1)
        G.add_edge(5, 6, weight=1)
        G.add_edge(2, 7, weight=0.1)
        G.add_edge(7, 5, weight=0.1)
        self.G = G
        self.term_nodes = [1, 2, 3, 4, 5]

    def test_metric_closure(self):
        M = metric_closure(self.G, self.term_nodes)
        expected_metric_closure = [(1, 2, {'distance': 1, 'path': [1, 2]}),
                                   (1, 3, {'distance': 2, 'path': [1, 2, 3]}),
                                   (1, 4, {'distance': 2.2, 'path': [1, 2, 7, 5, 4]}),
                                   (1, 5, {'distance': 1.2000000000000002, 'path': [1, 2, 7, 5]}),
                                   (2, 3, {'distance': 1, 'path': [2, 3]}),
                                   (2, 4, {'distance': 1.2, 'path': [2, 7, 5, 4]}),
                                   (2, 5, {'distance': 0.2, 'path': [2, 7, 5]}),
                                   (3, 4, {'distance': 1, 'path': [3, 4]}),
                                   (3, 5, {'distance': 1.2000000000000002, 'path': [3, 2, 7, 5]}),
                                   (4, 5, {'distance': 1, 'path': [4, 5]})]
        edges_of_M = [i for i in M.edges(data=True)]
        assert_equal(expected_metric_closure, edges_of_M)

    def test_steiner_tree(self):
        S = steiner_tree(self.G, self.term_nodes)
        expected_steiner_tree = [(1, 2, {'weight': 1}),
                                 (2, 3, {'weight': 1}),
                                 (2, 7, {'weight': 0.1}),
                                 (3, 4, {'weight': 1}),
                                 (5, 7, {'weight': 0.1})]
        edges_of_S = [i for i in S.edges(data=True)]
        assert_equal(expected_steiner_tree, edges_of_S)
