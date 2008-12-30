#!/usr/bin/env python
from nose.tools import *
import networkx

class TestBetweennessCentrality:

    def setUp(self):

        G=networkx.Graph();
        G.add_edge(0,1,3)
        G.add_edge(0,2,2)
        G.add_edge(0,3,6)
        G.add_edge(0,4,4)
        G.add_edge(1,3,5)
        G.add_edge(1,5,5)
        G.add_edge(2,4,1)
        G.add_edge(3,4,2)
        G.add_edge(3,5,1)
        G.add_edge(4,5,4)
        self.G=G
        self.exact_weighted={0: 4.0, 1: 0.0, 2: 8.0, 3: 6.0, 4: 8.0, 5: 0.0}


    def test_brandes_betweenness(self):
        b=networkx.betweenness_centrality(self.G,weighted_edges=True,
                                          normalized=False)
        for n in sorted(self.G):
            assert_equal(b[n],self.exact_weighted[n])


    def test_load(self):
        b=networkx.load_centrality(self.G,weighted_edges=True,
                                   normalized=False)
        for n in sorted(self.G):
            assert_equal(b[n],self.exact_weighted[n])


