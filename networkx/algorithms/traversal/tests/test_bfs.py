from nose.tools import *
import networkx as nx
from networkx.testing.utils import *


class TestBFS:

    def setUp(self):
        # simple graph
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4)])
        self.G = G

    def test_successor(self):
        assert_in(dict(nx.bfs_successors(self.G, source=0)), [
                     {0: [1], 1: [2, 3], 2: [4]},
                     {0: [1], 1: [2, 3], 3: [4]},
                     {0: [1], 1: [3, 2], 2: [4]},
                     {0: [1], 1: [3, 2], 3: [4]}])

    def test_predecessor(self):
        assert_in(dict(nx.bfs_predecessors(self.G, source=0)), [
                     {1: 0, 2: 1, 3: 1, 4: 2},
                     {1: 0, 2: 1, 3: 1, 4: 3}])

    def test_bfs_tree(self):
        T = nx.bfs_tree(self.G, source=0)
        assert_equal(sorted(T.nodes()), sorted(self.G.nodes()))
        edges = list(T.edges())
        print(edges)
        try:
            assert_edges_equal(edges, [(0, 1), (1, 2), (1, 3), (2, 4)])
        except AssertionError:
            assert_edges_equal(edges, [(0, 1), (1, 3), (1, 2), (3, 4)])

    def test_bfs_edges(self):
        edges = list(nx.bfs_edges(self.G, source=0))
        assert_in(edges, [
            [(0, 1), (1, 2), (1, 3), (2, 4)],
            [(0, 1), (1, 3), (1, 2), (3, 4)]])

    def test_bfs_edges_reverse(self):
        D = nx.DiGraph()
        D.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4)])
        edges = nx.bfs_edges(D, source=4, reverse=True)
        assert_in(list(edges), [
            [(4, 2), (4, 3), (2, 1), (1, 0)],
            [(4, 3), (4, 2), (3, 1), (1, 0)]])

    def test_bfs_tree_isolates(self):
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        T = nx.bfs_tree(G, source=1)
        assert_equal(sorted(T.nodes()), [1])
        assert_equal(sorted(T.edges()), [])
