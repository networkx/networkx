#!/usr/bin/env python
from nose.tools import *
import networkx as nx


class TestTreeRecognition(object):
    def setUp(self):

        self.T1 = nx.Graph()

        self.T2 = nx.Graph()
        self.T2.add_node(1)

        self.T3 = nx.Graph()
        self.T3.add_nodes_from(range(5))
        edges = [(i,i+1) for i in range(4)]
        self.T3.add_edges_from(edges)

        self.T5 = nx.MultiGraph()
        self.T5.add_nodes_from(range(5))
        edges = [(i,i+1) for i in range(4)]
        self.T5.add_edges_from(edges)

        self.T6 = nx.Graph()
        self.T6.add_nodes_from([6,7])
        self.T6.add_edge(6,7)

        self.F1 = nx.compose(self.T6,self.T3)



        self.N1 = nx.DiGraph()

        self.N3 = nx.MultiDiGraph()

        self.N4 = nx.Graph()
        self.N4.add_node(1)
        self.N4.add_edge(1,1)

        self.N5 = nx.Graph()
        self.N5.add_nodes_from(range(5))

        self.N6 = nx.Graph()
        self.N6.add_nodes_from(range(3))
        self.N6.add_edges_from([(0,1),(1,2),(2,0)])

        self.NF1 = nx.compose(self.T6,self.N6)


    @raises(nx.NetworkXPointlessConcept)
    def test_null(self):
        nx.is_tree(nx.Graph())

    @raises(nx.NetworkXPointlessConcept)
    def test_null(self):
        nx.is_tree(nx.MultiGraph())


    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        assert_false(nx.is_tree(self.N1))

    @raises(nx.NetworkXNotImplemented)
    def test_multidigraph(self):
        assert_false(nx.is_tree(self.N3))

    @raises(nx.NetworkXNotImplemented)
    def test_digraph_forest(self):
        assert_false(nx.is_forest(self.N1))

    @raises(nx.NetworkXNotImplemented)
    def test_multidigraph_forest(self):
        assert_false(nx.is_forest(self.N3))

    def test_is_tree(self):
        assert_true(nx.is_tree(self.T2))
        assert_true(nx.is_tree(self.T3))
        assert_true(nx.is_tree(self.T5))

    def test_is_not_tree(self):
        assert_false(nx.is_tree(self.N4))
        assert_false(nx.is_tree(self.N5))
        assert_false(nx.is_tree(self.N6))

    def test_is_forest(self):
        assert_true(nx.is_forest(self.T2))
        assert_true(nx.is_forest(self.T3))
        assert_true(nx.is_forest(self.T5))
        assert_true(nx.is_forest(self.F1))
        assert_true(nx.is_forest(self.N5))

    def test_is_not_forest(self):
        assert_false(nx.is_forest(self.N4))
        assert_false(nx.is_forest(self.N6))
        assert_false(nx.is_forest(self.NF1))

        

        

