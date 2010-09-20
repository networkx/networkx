#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from networkx import convert_node_labels_to_integers as cnlti

class TestBoundary:

    def setUp(self):
        self.null=nx.null_graph()
        self.P10=cnlti(nx.path_graph(10),first_label=1)
        self.K10=cnlti(nx.complete_graph(10),first_label=1)

    def test_null_node_boundary(self):
        """null graph has empty node boundaries"""
        null=self.null
        assert_equal(nx.node_boundary(null,[]),[])
        assert_equal(nx.node_boundary(null,[],[]),[])
        assert_equal(nx.node_boundary(null,[1,2,3]),[])
        assert_equal(nx.node_boundary(null,[1,2,3],[4,5,6]),[])
        assert_equal(nx.node_boundary(null,[1,2,3],[3,4,5]),[])

    def test_null_edge_boundary(self):
        """null graph has empty edge boundaries"""
        null=self.null
        assert_equal(nx.edge_boundary(null,[]),[])
        assert_equal(nx.edge_boundary(null,[],[]),[])
        assert_equal(nx.edge_boundary(null,[1,2,3]),[])
        assert_equal(nx.edge_boundary(null,[1,2,3],[4,5,6]),[])
        assert_equal(nx.edge_boundary(null,[1,2,3],[3,4,5]),[])

    def test_path_node_boundary(self):
        """Check node boundaries in path graph."""
        P10=self.P10
        assert_equal(nx.node_boundary(P10,[]),[])
        assert_equal(nx.node_boundary(P10,[],[]),[])
        assert_equal(nx.node_boundary(P10,[1,2,3]),[4])
        assert_equal(sorted(nx.node_boundary(P10,[4,5,6])),[3, 7])
        assert_equal(sorted(nx.node_boundary(P10,[3,4,5,6,7])),[2, 8])
        assert_equal(nx.node_boundary(P10,[8,9,10]),[7])
        assert_equal(sorted(nx.node_boundary(P10,[4,5,6],[9,10])),[])

    def test_path_edge_boundary(self):
        """Check edge boundaries in path graph."""
        P10=self.P10

        assert_equal(nx.edge_boundary(P10,[]),[])
        assert_equal(nx.edge_boundary(P10,[],[]),[])
        assert_equal(nx.edge_boundary(P10,[1,2,3]),[(3, 4)])
        assert_equal(sorted(nx.edge_boundary(P10,[4,5,6])),[(4, 3), (6, 7)])
        assert_equal(sorted(nx.edge_boundary(P10,[3,4,5,6,7])),[(3, 2), (7, 8)])
        assert_equal(nx.edge_boundary(P10,[8,9,10]),[(8, 7)])
        assert_equal(sorted(nx.edge_boundary(P10,[4,5,6],[9,10])),[])
        assert_equal(nx.edge_boundary(P10,[1,2,3],[3,4,5]) ,[(2, 3), (3, 4)])


    def test_k10_node_boundary(self):
        """Check node boundaries in K10"""
        K10=self.K10

        assert_equal(nx.node_boundary(K10,[]),[])
        assert_equal(nx.node_boundary(K10,[],[]),[])
        assert_equal(sorted(nx.node_boundary(K10,[1,2,3])),
                     [4, 5, 6, 7, 8, 9, 10])
        assert_equal(sorted(nx.node_boundary(K10,[4,5,6])),
                     [1, 2, 3, 7, 8, 9, 10])
        assert_equal(sorted(nx.node_boundary(K10,[3,4,5,6,7])),
                            [1, 2, 8, 9, 10])
        assert_equal(nx.node_boundary(K10,[4,5,6],[]),[])
        assert_equal(nx.node_boundary(K10,K10),[])
        assert_equal(nx.node_boundary(K10,[1,2,3],[3,4,5]),[4, 5])

    def test_k10_edge_boundary(self):
        """Check edge boundaries in K10"""
        K10=self.K10

        assert_equal(nx.edge_boundary(K10,[]),[])
        assert_equal(nx.edge_boundary(K10,[],[]),[])
        assert_equal(len(nx.edge_boundary(K10,[1,2,3])),21)
        assert_equal(len(nx.edge_boundary(K10,[4,5,6,7])),24)
        assert_equal(len(nx.edge_boundary(K10,[3,4,5,6,7])),25)
        assert_equal(len(nx.edge_boundary(K10,[8,9,10])),21)
        assert_equal(sorted(nx.edge_boundary(K10,[4,5,6],[9,10])),
                     [(4, 9), (4, 10), (5, 9), (5, 10), (6, 9), (6, 10)])
        assert_equal(nx.edge_boundary(K10,[1,2,3],[3,4,5]),
                     [(1, 3), (1, 4), (1, 5), (2, 3), (2, 4), 
                      (2, 5), (3, 4), (3, 5)])


    def test_petersen(self):
        """Check boundaries in the petersen graph

        cheeger(G,k)=min(|bdy(S)|/|S| for |S|=k, 0<k<=|V(G)|/2)
        """
        from random import sample
        P=nx.petersen_graph()
        def cheeger(G,k):
            return min([float(len(nx.node_boundary(G,sample(G.nodes(),k))))/k 
                        for n in range(100)])

        assert_almost_equals(cheeger(P,1),3.00,places=2)
        assert_almost_equals(cheeger(P,2),2.00,places=2)
        assert_almost_equals(cheeger(P,3),1.67,places=2)
        assert_almost_equals(cheeger(P,4),1.00,places=2)
        assert_almost_equals(cheeger(P,5),0.80,places=2)
