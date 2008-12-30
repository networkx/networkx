#!/usr/bin/env python
from nose.tools import *
import networkx

class TestBipartite:

    def test_project(self):
        G=networkx.path_graph(4)
        P=networkx.project(G,[1,3]) 
        assert_equal(sorted(P.nodes()),[1,3])
        assert_equal(sorted(P.edges()),[(1,3)])

    def test_is_bipartite(self):
        G=networkx.path_graph(4)
        assert_equal(networkx.is_bipartite(G),True)

    def test_bipartite_color(self):
        G=networkx.path_graph(4)
        c=networkx.bipartite_color(G)
        assert_equal(c,{0: 1, 1: 0, 2: 1, 3: 0})

    def test_bipartite_sets(self):
        G=networkx.path_graph(4)
        X,Y=networkx.bipartite_sets(G)
        assert_equal(X,set([0,2]))
        assert_equal(Y,set([1,3]))
