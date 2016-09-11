#!/usr/bin/env python
import itertools
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
        assert_in(list(nx.dfs_preorder_nodes(self.G,source=0)), [
                     [0, 1, 2, 4, 3],
                     [0, 1, 3, 4, 2]])
        assert_in(list(nx.dfs_preorder_nodes(self.D)), [
                [0, 1, 2, 3],
                [1, 0, 2, 3],
                [0, 1, 3, 2],
                [1, 0, 3, 2]])

    def test_postorder_nodes(self):
        assert_in(list(nx.dfs_postorder_nodes(self.G,source=0)), [
                 [3, 4, 2, 1, 0],
                 [2, 4, 3, 1, 0]])

        # Any order is valid, as there is no 3-path and sources are chosen
        # randomly.
        assert_in(tuple(nx.dfs_postorder_nodes(self.D)),
                itertools.permutations([0, 1, 2, 3]))

    def test_successor(self):
        successors = nx.dfs_successors(self.G,source=0)
        if successors[1] == [2]:
            assert_equal(successors,
                         {0: [1], 1: [2], 2: [4], 4: [3]})
        else:
            assert_equal(successors,
                         {0: [1], 1: [3], 3: [4], 4: [2]})
        assert_in(nx.dfs_successors(self.D), [
            {0: [1], 2: [3]},
            {1: [0], 2: [3]},
            {0: [1], 3: [2]},
            {1: [0], 3: [2]}])


    def test_predecessor(self):
        assert_in(nx.dfs_predecessors(self.G,source=0), [
                     {1: 0, 2: 1, 3: 4, 4: 2},
                     {1: 0, 3: 1, 4: 3, 2: 4}])
        assert_in(nx.dfs_predecessors(self.D), [
            {1: 0, 3: 2},
            {0: 1, 3: 2},
            {1: 0, 2: 3},
            {0: 1, 2: 3}])


    def test_dfs_tree(self):
        exp_nodes = sorted(self.G.nodes())
        exp_edges = [
                [(0, 1), (1, 2), (2, 4), (4, 3)],
                [(0, 1), (1, 3), (3, 4), (4, 2)]]
        # Search from first node
        T=nx.dfs_tree(self.G,source=0)
        assert_equal(sorted(T.nodes()), exp_nodes)
        assert_in(sorted(T.edges()), exp_edges)

        # Check source=None
        T = nx.dfs_tree(self.G, source=None)
        assert_equal(sorted(T.nodes()), exp_nodes)
        assert_in(sorted(T.edges()), exp_edges) # FIXME: may fail because of hash randomization
        # Check source=None is the default
        T = nx.dfs_tree(self.G)
        assert_equal(sorted(T.nodes()), exp_nodes)
        assert_in(sorted(T.edges()), exp_edges) # FIXME: may fail because of hash randomization

    def test_dfs_edges(self):
        edges=nx.dfs_edges(self.G,source=0)
        assert_in(list(edges), [
            [(0, 1), (1, 2), (2, 4), (4, 3)],
            [(0, 1), (1, 3), (3, 4), (4, 2)]])
        edges=nx.dfs_edges(self.D)
        assert_in(list(edges), [
                [(0, 1), (2, 3)],
                [(1, 0), (2, 3)],
                [(0, 1), (3, 2)],
                [(1, 0), (3, 2)]])

    def test_dfs_labeled_edges(self):
        edges=list(nx.dfs_labeled_edges(self.G,source=0))
        forward=[(u,v) for (u,v,d) in edges if d['dir']=='forward']
        assert_in (forward, [
                [(0,0), (0, 1), (1, 2), (2, 4), (4, 3)],
                [(0,0), (0, 1), (1, 3), (3, 4), (4, 2)]])

    def test_dfs_labeled_disconnected_edges(self):
        edges=list(nx.dfs_labeled_edges(self.D))
        forward=[(u,v) for (u,v,d) in edges if d['dir']=='forward']
        assert_in(forward, [
            [(0, 0), (0, 1), (2, 2), (2, 3)],
            [(1, 1), (1, 0), (2, 2), (2, 3)],
            [(0, 0), (0, 1), (3, 3), (3, 2)],
            [(1, 1), (1, 0), (3, 3), (3, 2)]])

    def test_dfs_tree_isolates(self):
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        T=nx.dfs_tree(G,source=1)
        assert_equal(sorted(T.nodes()),[1])
        assert_equal(sorted(T.edges()),[])
        T=nx.dfs_tree(G,source=None)
        assert_equal(sorted(T.nodes()),[1, 2])
        assert_equal(sorted(T.edges()),[])
