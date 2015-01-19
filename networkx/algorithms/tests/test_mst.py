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
        assert_equal(sorted(map(sorted,T.edges())),[[1, 2], [10, 20]])
        assert_equal(sorted(T.nodes()),[1, 2, 10, 20])

    def test_mst_isolate(self):
        G=nx.Graph()
        G.add_nodes_from([1,2])
        T=nx.minimum_spanning_tree(G)
        assert_equal(sorted(T.nodes()),[1, 2])
        assert_equal(sorted(T.edges()),[])

    def test_mst_attributes(self):
        G=nx.Graph()
        G.add_edge(1,2,weight=1,color='red',distance=7)
        G.add_edge(2,3,weight=1,color='green',distance=2)
        G.add_edge(1,3,weight=10,color='blue',distance=1)
        G.add_node(13,color='purple')
        G.graph['foo']='bar'
        T=nx.minimum_spanning_tree(G)
        assert_equal(T.graph,G.graph)
        assert_equal(T.node[13],G.node[13])
        assert_equal(T.edge[1][2],G.edge[1][2])

    def test_mst_edges_specify_weight(self):
        G=nx.Graph()
        G.add_edge(1,2,weight=1,color='red',distance=7)
        G.add_edge(1,3,weight=30,color='blue',distance=1)
        G.add_edge(2,3,weight=1,color='green',distance=1)
        G.add_node(13,color='purple')
        G.graph['foo']='bar'
        T=nx.minimum_spanning_tree(G)
        assert_equal(sorted(T.nodes()),[1,2,3,13])
        assert_equal(sorted(T.edges()),[(1,2),(2,3)])
        T=nx.minimum_spanning_tree(G,weight='distance')
        assert_equal(sorted(T.edges()),[(1,3),(2,3)])
        assert_equal(sorted(T.nodes()),[1,2,3,13])

    def test_prim_mst(self):
        T=nx.prim_mst(self.G)
        assert_equal(T.edges(data=True),self.tree_edgelist)

    def test_prim_mst_edges(self):
        edgelist=sorted(nx.prim_mst_edges(self.G))
        edgelist=sorted((sorted((u, v))[0], sorted((u, v))[1], d)
                                  for u,v,d in edgelist)
        assert_equal(edgelist,self.tree_edgelist)

    def test_prim_mst_disconnected(self):
        G=nx.Graph()
        G.add_path([1,2])
        G.add_path([10,20])
        T=nx.prim_mst(G)
        assert_equal(sorted(map(sorted,T.edges())),[[1, 2], [10, 20]])
        assert_equal(sorted(T.nodes()),[1, 2, 10, 20])

    def test_prim_mst_isolate(self):
        G=nx.Graph()
        G.add_nodes_from([1,2])
        T=nx.prim_mst(G)
        assert_equal(sorted(T.nodes()),[1, 2])
        assert_equal(sorted(T.edges()),[])

    def test_prim_mst_attributes(self):
        G=nx.Graph()
        G.add_edge(1,2,weight=1,color='red',distance=7)
        G.add_edge(2,3,weight=1,color='green',distance=2)
        G.add_edge(1,3,weight=10,color='blue',distance=1)
        G.add_node(13,color='purple')
        G.graph['foo']='bar'
        T=nx.prim_mst(G)
        assert_equal(T.graph,G.graph)
        assert_equal(T.node[13],G.node[13])
        assert_equal(T.edge[1][2],G.edge[1][2])

    def test_prim_mst_edges_specify_weight(self):
        G=nx.Graph()
        G.add_edge(1,2,weight=1,color='red',distance=7)
        G.add_edge(1,3,weight=30,color='blue',distance=1)
        G.add_edge(2,3,weight=1,color='green',distance=1)
        G.add_node(13,color='purple')
        G.graph['foo']='bar'
        T=nx.prim_mst(G)
        assert_equal(sorted(T.nodes()),[1,2,3,13])
        assert_equal(sorted(T.edges()),[(1,2),(2,3)])
        T=nx.prim_mst(G,weight='distance')
        assert_equal(sorted(T.edges()),[(1,3),(2,3)])
        assert_equal(sorted(T.nodes()),[1,2,3,13])

