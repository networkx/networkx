#!/usr/bin/env python
import math
from nose.tools import *
import networkx

class TestEigenvectorCentrality():
        
    def test_K5(self):
        """Eigenvector centrality: K5"""
        G=networkx.complete_graph(5)
        b=networkx.eigenvector_centrality(G)
        v=math.sqrt(1/5.0)
        b_answer=dict.fromkeys(G,v)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])
        b=networkx.eigenvector_centrality_numpy(G)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_P3(self):
        """Eigenvector centrality: P3"""
        G=networkx.path_graph(3)
        b_answer={0: 0.5, 1: 0.7071, 2: 0.5}
        b=networkx.eigenvector_centrality_numpy(G)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n],places=4)


    def test_disconnected_path(self):
        """Eigenvector centrality: disconnected path"""
        G=networkx.Graph()
        G.add_path([0,1,2])
        G.add_path([3,4,5])
        b_answer={0:0.3535,1:0.5,2:0.3535,3:0.3535,4:0.5,5:0.3535}
        b=networkx.eigenvector_centrality_numpy(G)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n],places=3)

