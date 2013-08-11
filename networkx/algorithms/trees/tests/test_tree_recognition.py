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
        
        self.T4 = nx.MultiGraph()

        self.T5 = nx.MultiGraph()
        self.T5.add_nodes_from(range(5))
        edges = [(i,i+1) for i in range(4)]
        self.T5.add_edges_from(edges)



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


    def test_is_tree(self):
        assert_true(nx.is_tree(self.T1))
        assert_true(nx.is_tree(self.T2))
        assert_true(nx.is_tree(self.T3))
        assert_true(nx.is_tree(self.T4))
        assert_true(nx.is_tree(self.T5))

        assert_false(nx.is_tree(self.N1))
        assert_false(nx.is_tree(self.N3))
        assert_false(nx.is_tree(self.N4))
        assert_false(nx.is_tree(self.N5))
        assert_false(nx.is_tree(self.N6))

        

