#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestDAG:

    def setUp(self):
        pass

    def test_topological_sort1(self):
        DG=nx.DiGraph()
        DG.add_edges_from([(1,2),(1,3),(2,3)])
        assert_equal(nx.topological_sort(DG),[1, 2, 3])
        assert_equal(nx.topological_sort_recursive(DG),[1, 2, 3])

        DG.add_edge(3,2)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort, DG)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort_recursive, DG)
        
        DG.remove_edge(2,3)
        assert_equal(nx.topological_sort(DG),[1, 3, 2])
        assert_equal(nx.topological_sort_recursive(DG),[1, 3, 2])

    def test_topological_sort2(self):
        DG=nx.DiGraph({1:[2],2:[3],3:[4],
                       4:[5],5:[1],11:[12],
                       12:[13],13:[14],14:[15]})
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort, DG)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort_recursive, DG)

        assert_false(nx.is_directed_acyclic_graph(DG))

        DG.remove_edge(1,2)
        assert_equal(nx.topological_sort_recursive(DG),
                     [11, 12, 13, 14, 15, 2, 3, 4, 5, 1])
        assert_equal(nx.topological_sort(DG),
                     [11, 12, 13, 14, 15, 2, 3, 4, 5, 1])
        assert_true(nx.is_directed_acyclic_graph(DG))

    def test_topological_sort3(self):
        DG=nx.DiGraph()
        DG.add_edges_from([(1,i) for i in range(2,5)])
        DG.add_edges_from([(2,i) for i in range(5,9)])
        DG.add_edges_from([(6,i) for i in range(9,12)])
        DG.add_edges_from([(4,i) for i in range(12,15)])
        assert_equal(nx.topological_sort_recursive(DG),
                     [1, 4, 14, 13, 12, 3, 2, 7, 6, 11, 10, 9, 5, 8])
        assert_equal(nx.topological_sort(DG),
                     [1, 2, 8, 5, 6, 9, 10, 11, 7, 3, 4, 12, 13, 14])

        DG.add_edge(14,1)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort, DG)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort_recursive, DG)

    def test_topological_sort4(self):
        G=nx.Graph()
        G.add_edge(1,2)
        assert_raises(nx.NetworkXError, nx.topological_sort, G)
        assert_raises(nx.NetworkXError, nx.topological_sort_recursive, G)

