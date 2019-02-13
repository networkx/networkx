from nose.tools import assert_raises, raises
import networkx as nx
from networkx.algorithms.approximation.steinertree import metric_closure
from networkx.algorithms.approximation.steinertree import steiner_tree
from networkx.testing.utils import assert_edges_equal

class TestSteinerTree:
    def setUp(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=10)
        G.add_edge(2, 3, weight=10)
        G.add_edge(3, 4, weight=10)
        G.add_edge(4, 5, weight=10)
        G.add_edge(5, 6, weight=10)
        G.add_edge(2, 7, weight=1)
        G.add_edge(7, 5, weight=1)

        M = nx.MultiGraph()

        M.add_edges_from([
            ('A', 'B', 'k1', {'weight': 2}),
            ('A', 'B', 'k2', {'weight': 999}),
            ('B', 'C', 'k3', {'weight': 999}),
            ('B', 'C', 'k4', {'weight': 2}),
            ('B', 'C', 'k5', {'weight': 2}),
            ('C', 'D', 'k6', {'weight': 2}),
            ('C', 'E', 'k7', {'weight': 2}),
            ('D', 'F', 'k8', {'weight': 2}),
            ('D', 'F', 'k9', {'weight': 999}),
            ('F', 'H', 'k10', {'weight': 2}),
            ('E', 'H', 'k12', {'weight': 5}),
            # ('Q', 'W', 'k8', {'weight': 1}),
        ])

        self.G = G
        self.M = M

        self.term_nodes = [1, 2, 3, 4, 5]

    def test_connected_metric_closure(self):
        G = self.G.copy()
        G.add_node(100)
        assert_raises(nx.NetworkXError, metric_closure, G)

    def test_metric_closure(self):
        M = metric_closure(self.G)
        mc = [(1, 2, {'distance': 10, 'path': [1, 2], 'keys': None, }),
              (1, 3, {'distance': 20, 'path': [1, 2, 3], 'keys': None, }),
              (1, 4, {'distance': 22, 'path': [1, 2, 7, 5, 4], 'keys': None, }),
              (1, 5, {'distance': 12, 'path': [1, 2, 7, 5], 'keys': None, }),
              (1, 6, {'distance': 22, 'path': [1, 2, 7, 5, 6], 'keys': None, }),
              (1, 7, {'distance': 11, 'path': [1, 2, 7], 'keys': None, }),
              (2, 3, {'distance': 10, 'path': [2, 3], 'keys': None, }),
              (2, 4, {'distance': 12, 'path': [2, 7, 5, 4], 'keys': None, }),
              (2, 5, {'distance': 2, 'path': [2, 7, 5], 'keys': None, }),
              (2, 6, {'distance': 12, 'path': [2, 7, 5, 6], 'keys': None, }),
              (2, 7, {'distance': 1, 'path': [2, 7], 'keys': None, }),
              (3, 4, {'distance': 10, 'path': [3, 4], 'keys': None, }),
              (3, 5, {'distance': 12, 'path': [3, 2, 7, 5], 'keys': None, }),
              (3, 6, {'distance': 22, 'path': [3, 2, 7, 5, 6], 'keys': None, }),
              (3, 7, {'distance': 11, 'path': [3, 2, 7], 'keys': None, }),
              (4, 5, {'distance': 10, 'path': [4, 5], 'keys': None, }),
              (4, 6, {'distance': 20, 'path': [4, 5, 6], 'keys': None, }),
              (4, 7, {'distance': 11, 'path': [4, 5, 7], 'keys': None, }),
              (5, 6, {'distance': 10, 'path': [5, 6], 'keys': None, }),
              (5, 7, {'distance': 1, 'path': [5, 7], 'keys': None, }),
              (6, 7, {'distance': 11, 'path': [6, 5, 7], 'keys': None, })]

        assert_edges_equal(list(M.edges(data=True)), mc)

    def test_metric_closure_multigraph(self):
        M = metric_closure(self.M)

        mc = [
            ('A', 'C', {'distance': 4, 'keys': ['k1', 'k4'], 'path': ['A', 'B', 'C']}),
            ('A', 'D', {'distance': 6, 'keys': ['k1', 'k4', 'k6'], 'path': ['A', 'B', 'C', 'D']}),
            ('A', 'B', {'distance': 2, 'keys': ['k1'], 'path': ['A', 'B']}),
            ('A', 'F', {'distance': 8, 'keys': ['k1', 'k4', 'k6', 'k8'], 'path': ['A', 'B', 'C', 'D', 'F']}),
            ('A', 'H', {'distance': 10, 'keys': ['k1', 'k4', 'k6', 'k8', 'k10'], 'path': ['A', 'B', 'C', 'D', 'F', 'H']}),
            ('A', 'E', {'distance': 6, 'keys': ['k1', 'k4', 'k7'], 'path': ['A', 'B', 'C', 'E']}),
            ('C', 'B', {'distance': 2, 'keys': ['k4'], 'path': ['B', 'C']}),
            ('C', 'D', {'distance': 2, 'keys': ['k6'], 'path': ['C', 'D']}),
            ('C', 'F', {'distance': 4, 'keys': ['k6', 'k8'], 'path': ['C', 'D', 'F']}),
            ('C', 'H', {'distance': 6, 'keys': ['k6', 'k8', 'k10'], 'path': ['C', 'D', 'F', 'H']}),
            ('C', 'E', {'distance': 2, 'keys': ['k7'], 'path': ['C', 'E']}),
            ('D', 'B', {'distance': 4, 'keys': ['k4', 'k6'], 'path': ['B', 'C', 'D']}),
            ('D', 'F', {'distance': 2, 'keys': ['k8'], 'path': ['D', 'F']}),
            ('D', 'H', {'distance': 4, 'keys': ['k8', 'k10'], 'path': ['D', 'F', 'H']}),
            ('D', 'E', {'distance': 4, 'keys': ['k6', 'k7'], 'path': ['D', 'C', 'E']}),
            ('B', 'F', {'distance': 6, 'keys': ['k4', 'k6', 'k8'], 'path': ['B', 'C', 'D', 'F']}),
            ('B', 'H', {'distance': 8, 'keys': ['k4', 'k6', 'k8', 'k10'], 'path': ['B', 'C', 'D', 'F', 'H']}),
            ('B', 'E', {'distance': 4, 'keys': ['k4', 'k7'], 'path': ['B', 'C', 'E']}),
            ('F', 'E', {'distance': 6, 'keys': ['k7', 'k6', 'k8'], 'path': ['E', 'C', 'D', 'F']}),
            ('F', 'H', {'distance': 2, 'keys': ['k10'], 'path': ['F', 'H']}),
            ('H', 'E', {'distance': 5, 'keys': ['k12'], 'path': ['E', 'H']})
        ]

        assert_edges_equal(list(M.edges(data=True)), mc)

    def test_metric_closure_no_weight(self):
        M = metric_closure(self.M, weight=None)

        mc = [
            ('A', 'C', {'distance': 2, 'keys': ['k1', 'k3'], 'path': ['A', 'B', 'C']}),
            ('A', 'E', {'distance': 3, 'keys': ['k1', 'k3', 'k7'], 'path': ['A', 'B', 'C', 'E']}),
            ('A', 'F', {'distance': 4, 'keys': ['k1', 'k3', 'k6', 'k8'], 'path': ['A', 'B', 'C', 'D', 'F']}),
            ('A', 'B', {'distance': 1, 'keys': ['k1'], 'path': ['A', 'B']}),
            ('A', 'H', {'distance': 4, 'keys': ['k1', 'k3', 'k7', 'k12'], 'path': ['A', 'B', 'C', 'E', 'H']}),
            ('A', 'D', {'distance': 3, 'keys': ['k1', 'k3', 'k6'], 'path': ['A', 'B', 'C', 'D']}),
            ('C', 'B', {'distance': 1, 'keys': ['k3'], 'path': ['B', 'C']}),
            ('C', 'E', {'distance': 1, 'keys': ['k7'], 'path': ['C', 'E']}),
            ('C', 'F', {'distance': 2, 'keys': ['k6', 'k8'], 'path': ['C', 'D', 'F']}),
            ('C', 'H', {'distance': 2, 'keys': ['k7', 'k12'], 'path': ['C', 'E', 'H']}),
            ('C', 'D', {'distance': 1, 'keys': ['k6'], 'path': ['C', 'D']}),
            ('E', 'B', {'distance': 2, 'keys': ['k3', 'k7'], 'path': ['B', 'C', 'E']}),
            ('E', 'D', {'distance': 2, 'keys': ['k6', 'k7'], 'path': ['D', 'C', 'E']}),
            ('E', 'F', {'distance': 2, 'keys': ['k12', 'k10'], 'path': ['E', 'H', 'F']}),
            ('E', 'H', {'distance': 1, 'keys': ['k12'], 'path': ['E', 'H']}),
            ('F', 'B', {'distance': 3, 'keys': ['k3', 'k6', 'k8'], 'path': ['B', 'C', 'D', 'F']}),
            ('F', 'D', {'distance': 1, 'keys': ['k8'], 'path': ['D', 'F']}),
            ('F', 'H', {'distance': 1, 'keys': ['k10'], 'path': ['F', 'H']}),
            ('B', 'H', {'distance': 3, 'keys': ['k3', 'k7', 'k12'], 'path': ['B', 'C', 'E', 'H']}),
            ('B', 'D', {'distance': 2, 'keys': ['k3', 'k6'], 'path': ['B', 'C', 'D']}),
            ('H', 'D', {'distance': 2, 'keys': ['k8', 'k10'], 'path': ['D', 'F', 'H']})
        ]

        assert_edges_equal(list(M.edges(data=True)), mc)

    def test_steiner_tree(self):
        S = steiner_tree(self.G, self.term_nodes)
        expected_steiner_tree = [(1, 2, {'weight': 10}),
                                 (2, 3, {'weight': 10}),
                                 (2, 7, {'weight': 1}),
                                 (3, 4, {'weight': 10}),
                                 (5, 7, {'weight': 1})]
        assert_edges_equal(list(S.edges(data=True)), expected_steiner_tree)

    def test_multigraph_steiner_tree(self):
        terminal_nodes = ['A', 'D']
        expected_edges = [
            ('A', 'B', 'k1', {'weight': 2}),
            ('B', 'C', 'k4', {'weight': 2}),
            ('C', 'D', 'k6', {'weight': 2})
        ]
        T = steiner_tree(self.M, terminal_nodes)

        assert_edges_equal(list(T.edges(keys=True, data=True)), expected_edges)

    def test_multigraph_steiner_tree_adjacent(self):
        terminal_nodes = ['A', 'B']
        expected_edges = [
            ('A', 'B', 'k1', {'weight': 2}),
        ]
        T = steiner_tree(self.M, terminal_nodes)

        assert_edges_equal(list(T.edges(keys=True, data=True)), expected_edges)

    def test_multigraph_steiner_tree_multiple_terminals(self):
        terminal_nodes = ['A', 'C', 'H']
        expected_edges = [
            ('A', 'B', 'k1', {'weight': 2}),
            ('B', 'C', 'k4', {'weight': 2}),
            ('C', 'D', 'k6', {'weight': 2}),
            ('D', 'F', 'k8', {'weight': 2}),
            ('F', 'H', 'k10', {'weight': 2})
        ]

        T = steiner_tree(self.M, terminal_nodes)

        assert_edges_equal(list(T.edges(keys=True, data=True)), expected_edges)

    def test_multigraph_steiner_tree_no_weight(self):
        terminal_nodes = ['A', 'D']
        expected_edges = [
            ('A', 'B', 'k1', {'weight': 2}),
            ('B', 'C', 'k4', {'weight': 2}),
            ('C', 'D', 'k6', {'weight': 2})
        ]
        T = steiner_tree(self.M, terminal_nodes)


        assert_edges_equal(list(T.edges(keys=True, data=True)), expected_edges)