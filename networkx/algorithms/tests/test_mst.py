#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestMST:

    def setUp(self):
    # example from Wikipedia: http://en.wikipedia.org/wiki/Kruskal's_algorithm
        G=nx.Graph() 
        edgelist = [(0,3,[('weight',5)]),
                    (0,1,[('weight',7)]),
                    (1,3,[('weight',9)]),
                    (1,2,[('weight',8)]),
                    (1,4,[('weight',7)]),
                    (3,4,[('weight',15)]),
                    (3,5,[('weight',6)]),
                    (2,4,[('weight',5)]),
                    (4,5,[('weight',8)]),
                    (4,6,[('weight',9)]),
                    (5,6,[('weight',11)])]
                     

        G.add_edges_from(edgelist)
        self.G=G
        tree_edgelist =  [(0,1,{'weight':7}),
                          (0,3,{'weight':5}),
                          (3,5,{'weight':6}),
                          (1,4,{'weight':7}),
                          (4,2,{'weight':5}),
                          (4,6,{'weight':9})]
        self.tree_edgelist=sorted((sorted((u, v))[0], sorted((u, v))[1], d)
                                  for u,v,d in tree_edgelist)

    def test_mst(self):
        T=nx.minimum_spanning_tree(self.G)
        assert_equal(T.edges(data=True),self.tree_edgelist)

    def test_mst_edges(self):
        edgelist=sorted(nx.minimum_spanning_edges(self.G))
        assert_equal(edgelist,self.tree_edgelist)

    def test_mst_disconnected(self):
        G=nx.Graph()
        G.add_path([1,2])
        G.add_path([10,20])
        T=nx.minimum_spanning_tree(G)
        assert_equal(sorted(T.edges()),[(1, 2), (20, 10)])
        assert_equal(sorted(T.nodes()),[1, 2, 10, 20])

    def test_mst_isolate(self):
        G=nx.Graph()
        G.add_nodes_from([1,2])
        T=nx.minimum_spanning_tree(G)
        assert_equal(sorted(T.nodes()),[1, 2])
        assert_equal(sorted(T.edges()),[])

        
