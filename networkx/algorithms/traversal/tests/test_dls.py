#!/usr/bin/env python
from nose.tools import *
import networkx as nx


class Testdls:

    def setUp(self):
        # a tree
        G = nx.Graph()
        G.add_path([0, 1, 2, 3, 4, 5, 6])
        G.add_path([2, 7, 8, 9, 10])
        self.G = G
        # a disconnected graph
        D = nx.Graph()
        D.add_edges_from([(0, 1), (2, 3)])
        D.add_path([2, 7, 8, 9, 10])
        self.D = D

    def dls_test_preorder_nodes(self):
        assert_equal(list(nx.dls_preorder_nodes(self.G, source=0,
        search_depth=2)), [0, 1, 2])
        assert_equal(list(nx.dls_preorder_nodes(self.D, source=1,
        search_depth=2)), ([1, 0]))

    def dls_test_postorder_nodes(self):
        assert_equal(list(nx.dls_postorder_nodes(self.G,
        source=3, search_depth=3)), [1, 7, 2, 5, 4, 3])
        assert_equal(list(nx.dls_postorder_nodes(self.D,
        source=2, search_depth=2)),
            ([3, 7, 2]))

    def dls_test_successor(self):
        assert_equal(nx.dls_successors(self.G, source=4, search_depth=3),
                     {2: [1, 7], 3: [2], 4: [3, 5], 5: [6]})
        assert_equal(nx.dls_successors(self.D, source=7, search_depth=2),
            {8: [9], 2: [3], 7: [8, 2]})

    def dls_test_predecessor(self):
        assert_equal(nx.dls_predecessors(self.G, source=0, search_depth=3),
                      {1: 0, 2: 1, 3: 2, 7: 2})
        assert_equal(nx.dls_predecessors(self.D, source=2, search_depth=3),
            {8: 7, 9: 8, 3: 2, 7: 2})

    def test_dls_tree(self):
        T = nx.dls_tree(self.G, source=3, search_depth=1)
        assert_equal(sorted(T.edges()), [(3, 2), (3, 4)])

    def test_dls_edges(self):
        edges = nx.dls_edges(self.G, source=9, search_depth=4)
        assert_equal(list(edges),
        [(9, 8), (8, 7), (7, 2), (2, 1), (2, 3), (9, 10)])

    def test_dls_labeled_edges(self):
        edges = list(nx.dls_labeled_edges(self.G, source=5, search_depth=1))
        forward = [(u, v) for (u, v, d) in edges if d['dir'] == 'forward']
        assert_equal(forward, [(5, 5), (5, 4), (5, 6)])

    def test_dls_labeled_disconnected_edges(self):
        edges = list(nx.dls_labeled_edges(self.G, source=6, search_depth=2))
        forward = [(u, v) for (u, v, d) in edges if d['dir'] == 'forward']
        assert_equal(forward, [(6, 6), (6, 5), (5, 4)])
