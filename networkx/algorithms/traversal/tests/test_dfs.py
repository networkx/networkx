#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestDFS:

    def setUp(self):
        # simple graph
        G=nx.Graph()
        G.add_edges_from([(0,1),(1,2),(1,3),(2,4),(3,4)])
        self.G=G


    def test_preorder(self):
        assert_equal(nx.dfs_preorder(self.G,source=0),[0, 1, 2, 4, 3])

    def test_postorder(self):
        assert_equal(nx.dfs_postorder(self.G,source=0),[3, 4, 2, 1, 0])

    def test_successor(self):
        assert_equal(nx.dfs_successor(self.G,source=0),
                     {0: [1], 1: [2], 2: [4], 3: [], 4: [3]})

    def test_predecessor(self):
        assert_equal(nx.dfs_predecessor(self.G,source=0),
                     {0: [], 1: [0], 2: [1], 3: [4], 4: [2]})

    def test_dfs_tree(self):
        T=nx.dfs_tree(self.G,source=0)
        assert_equal(sorted(T.nodes()),sorted(self.G.nodes()))
        assert_equal(sorted(T.edges()),[(0, 1), (1, 2), (2, 4), (4, 3)])

