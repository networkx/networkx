#!/usr/bin/env python
from nose.tools import *
import networkx
from networkx import betweenness_centrality_subset,\
     edge_betweenness_centrality_subset

class TestSubsetBetweennessCentrality:
        
    def test_K5(self):
        """Betweenness centrality: K5"""
        G=networkx.complete_graph(5)
        b=betweenness_centrality_subset(G,
                                        sources=[0],
                                        targets=[1,3],
                                        weight=None)
        b_answer={0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_P5_directed(self):
        """Betweenness centrality: P5 directed"""
        G=networkx.DiGraph()
        G.add_path(list(range(5)))
        b_answer={0:0,1:1,2:1,3:0,4:0,5:0}
        b=betweenness_centrality_subset(G,
                                        sources=[0],
                                        targets=[3],
                                        weight=None)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_P5(self):
        """Betweenness centrality: P5"""
        G=networkx.Graph()
        G.add_path(list(range(5)))
        b_answer={0:0,1:0.5,2:0.5,3:0,4:0,5:0}
        b=betweenness_centrality_subset(G,
                                        sources=[0],
                                        targets=[3],
                                        weight=None)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_P5_multiple_target(self):
        """Betweenness centrality: P5 multiple target"""
        G=networkx.Graph()
        G.add_path(list(range(5)))
        b_answer={0:0,1:1,2:1,3:0.5,4:0,5:0}
        b=betweenness_centrality_subset(G,
                                        sources=[0],
                                        targets=[3,4],
                                        weight=None)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_box(self):
        """Betweenness centrality: box"""
        G=networkx.Graph()
        G.add_edge(0,1)
        G.add_edge(0,2)
        G.add_edge(1,3)
        G.add_edge(2,3)
        b_answer={0:0,1:0.25,2:0.25,3:0}
        b=betweenness_centrality_subset(G,
                                        sources=[0],
                                        targets=[3],
                                        weight=None)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_box_and_path(self):
        """Betweenness centrality: box and path"""
        G=networkx.Graph()
        G.add_edge(0,1)
        G.add_edge(0,2)
        G.add_edge(1,3)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        b_answer={0:0,1:0.5,2:0.5,3:0.5,4:0,5:0}
        b=betweenness_centrality_subset(G,
                                        sources=[0],
                                        targets=[3,4],
                                        weight=None)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])


    def test_box_and_path2(self):
        """Betweenness centrality: box and path multiple target"""
        G=networkx.Graph()
        G.add_edge(0,1)
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(1,20)
        G.add_edge(20,3)
        G.add_edge(3,4)
        b_answer={0:0,1:1.0,2:0.5,20:0.5,3:0.5,4:0}
        b=betweenness_centrality_subset(G,
                                        sources=[0],
                                        targets=[3,4])
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])


class TestBetweennessCentralitySources:
    def test_K5(self):
        """Betweenness centrality: K5"""
        G=networkx.complete_graph(5)
        b=networkx.betweenness_centrality_source(G,
                                                 weight=None,
                                                 normalized=False)
        b_answer={0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_P3(self):
        """Betweenness centrality: P3"""
        G=networkx.path_graph(3)
        b_answer={0: 0.0, 1: 1.0, 2: 0.0}
        b=networkx.betweenness_centrality_source(G,
                                                 weight=None,
                                                 normalized=True)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    


class TestEdgeSubsetBetweennessCentrality:
    
    def test_K5(self):
        """Edge betweenness centrality: K5"""
        G=networkx.complete_graph(5)
        b=edge_betweenness_centrality_subset(G,
                                             sources=[0],
                                             targets=[1,3],
                                             weight=None)
        b_answer=dict.fromkeys(G.edges(),0)
        b_answer[(0,3)]=0.5
        b_answer[(0,1)]=0.5
        for n in sorted(G.edges()):
            print(n,b[n])
            assert_almost_equal(b[n],b_answer[n])

    def test_P5_directed(self):
        """Edge betweenness centrality: P5 directed"""
        G=networkx.DiGraph()
        G.add_path(list(range(5)))
        b_answer=dict.fromkeys(G.edges(),0)
        b_answer[(0,1)]=1
        b_answer[(1,2)]=1
        b_answer[(2,3)]=1
        b=edge_betweenness_centrality_subset(G,
                                             sources=[0],
                                             targets=[3],
                                             weight=None)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

    def test_P5(self):
        """Edge betweenness centrality: P5"""
        G=networkx.Graph()
        G.add_path(list(range(5)))
        b_answer=dict.fromkeys(G.edges(),0)
        b_answer[(0,1)]=0.5
        b_answer[(1,2)]=0.5
        b_answer[(2,3)]=0.5
        b=edge_betweenness_centrality_subset(G,
                                             sources=[0],
                                             targets=[3],
                                             weight=None)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

    def test_P5_multiple_target(self):
        """Edge betweenness centrality: P5 multiple target"""
        G=networkx.Graph()
        G.add_path(list(range(5)))
        b_answer=dict.fromkeys(G.edges(),0)
        b_answer[(0,1)]=1
        b_answer[(1,2)]=1
        b_answer[(2,3)]=1
        b_answer[(3,4)]=0.5
        b=edge_betweenness_centrality_subset(G,
                                             sources=[0],
                                             targets=[3,4],
                                             weight=None)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

    def test_box(self):
        """Edge etweenness centrality: box"""
        G=networkx.Graph()
        G.add_edge(0,1)
        G.add_edge(0,2)
        G.add_edge(1,3)
        G.add_edge(2,3)
        b_answer=dict.fromkeys(G.edges(),0)

        b_answer[(0,1)]=0.25
        b_answer[(0,2)]=0.25
        b_answer[(1,3)]=0.25
        b_answer[(2,3)]=0.25
        b=edge_betweenness_centrality_subset(G,
                                             sources=[0],
                                             targets=[3],
                                             weight=None)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

    def test_box_and_path(self):
        """Edge etweenness centrality: box and path"""
        G=networkx.Graph()
        G.add_edge(0,1)
        G.add_edge(0,2)
        G.add_edge(1,3)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        b_answer=dict.fromkeys(G.edges(),0)
        b_answer[(0,1)]=1.0/2
        b_answer[(0,2)]=1.0/2
        b_answer[(1,3)]=1.0/2
        b_answer[(2,3)]=1.0/2
        b_answer[(3,4)]=1.0/2
        b=edge_betweenness_centrality_subset(G,
                                             sources=[0],
                                             targets=[3,4],
                                             weight=None)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])


    def test_box_and_path2(self):
        """Edge betweenness centrality: box and path multiple target"""
        G=networkx.Graph()
        G.add_edge(0,1)
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(1,20)
        G.add_edge(20,3)
        G.add_edge(3,4)
        b_answer=dict.fromkeys(G.edges(),0)
        b_answer[(0,1)]=1.0
        b_answer[(1,20)]=1.0/2
        b_answer[(3,20)]=1.0/2
        b_answer[(1,2)]=1.0/2
        b_answer[(2,3)]=1.0/2
        b_answer[(3,4)]=1.0/2
        b=edge_betweenness_centrality_subset(G,
                                             sources=[0],
                                             targets=[3,4],
                                             weight=None)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])


