#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestBFS:

    def setUp(self):
        # simple graph
        G=nx.Graph()
        G.add_edges_from([(0,1),(1,2),(1,3),(2,4),(3,4)])
        self.G=G

    def test_successor(self):
        assert_equal(nx.bfs_successors(self.G,source=0),
                     {0: [1], 1: [2,3], 2:[4]})

    def test_predecessor(self):
        assert_equal(nx.bfs_predecessors(self.G,source=0),
                     {1: 0, 2: 1, 3: 1, 4: 2})

    def test_bfs_tree(self):
        T=nx.bfs_tree(self.G,source=0)
        assert_equal(sorted(T.nodes()),sorted(self.G.nodes()))
        assert_equal(sorted(T.edges()),[(0, 1), (1, 2), (1, 3), (2, 4)])

    def test_bfs_edges(self):
        edges=nx.bfs_edges(self.G,source=0)
        assert_equal(list(edges),[(0, 1), (1, 2), (1, 3), (2, 4)])

