#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestDFS:

    def setUp(self):
        # simple graph
        G=nx.Graph()
        G.add_edges_from([(0,1),(1,2),(1,3),(2,4),(3,4)])
        self.G=G
        # simple graph, disconnected
        D=nx.Graph()
        D.add_edges_from([(0,1),(2,3)])
        self.D=D


    def test_preorder_nodes(self):
        assert_equal(list(nx.dfs_preorder_nodes(self.G,source=0)),
                     [0, 1, 2, 4, 3])
        assert_equal(list(nx.dfs_preorder_nodes(self.D)),[0, 1, 2, 3])

    def test_postorder_nodes(self):
        assert_equal(list(nx.dfs_postorder_nodes(self.G,source=0)),
                     [3, 4, 2, 1, 0])
        assert_equal(list(nx.dfs_postorder_nodes(self.D)),[1, 0, 3, 2])

    def test_successor(self):
        assert_equal(nx.dfs_successors(self.G,source=0),
                     {0: [1], 1: [2], 2: [4], 4: [3]})
        assert_equal(nx.dfs_successors(self.D), {0: [1], 2: [3]})

    def test_predecessor(self):
        assert_equal(nx.dfs_predecessors(self.G,source=0),
                     {1: 0, 2: 1, 3: 4, 4: 2})
        assert_equal(nx.dfs_predecessors(self.D), {1: 0, 3: 2})

    def test_dfs_tree(self):
        T=nx.dfs_tree(self.G,source=0)
        assert_equal(sorted(T.nodes()),sorted(self.G.nodes()))
        assert_equal(sorted(T.edges()),[(0, 1), (1, 2), (2, 4), (4, 3)])

    def test_dfs_edges(self):
        edges=nx.dfs_edges(self.G,source=0)
        assert_equal(list(edges),[(0, 1), (1, 2), (2, 4), (4, 3)])
        edges=nx.dfs_edges(self.D)
        assert_equal(list(edges),[(0, 1), (2, 3)])

    def test_dfs_labeled_edges(self):
        edges=list(nx.dfs_labeled_edges(self.G,source=0))
        forward=[(u,v) for (u,v,d) in edges if d['dir']=='forward']
        assert_equal(forward,[(0,0), (0, 1), (1, 2), (2, 4), (4, 3)])

    def test_dfs_labeled_disconnected_edges(self):
        edges=list(nx.dfs_labeled_edges(self.D))
        forward=[(u,v) for (u,v,d) in edges if d['dir']=='forward']
        assert_equal(forward,[(0, 0), (0, 1), (2, 2), (2, 3)])
    
