#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestIsomorph:

    def setUp(self):
        self.G1=nx.Graph()
        self.G2=nx.Graph()
        self.G3=nx.Graph()
        self.G4=nx.Graph()
        self.G1.add_edges_from([ [1,2],[1,3],[1,5],[2,3] ])
        self.G2.add_edges_from([ [10,20],[20,30],[10,30],[10,50] ])
        self.G3.add_edges_from([ [1,2],[1,3],[1,5],[2,5] ])
        self.G4.add_edges_from([ [1,2],[1,3],[1,5],[2,4] ])

    def test_could_be_isomorphic(self):
       assert_true(nx.could_be_isomorphic(self.G1,self.G2))
       assert_true(nx.could_be_isomorphic(self.G1,self.G3))
       assert_false(nx.could_be_isomorphic(self.G1,self.G4))
       assert_true(nx.could_be_isomorphic(self.G3,self.G2))

    def test_fast_could_be_isomorphic(self):
        assert_true(nx.fast_could_be_isomorphic(self.G3,self.G2))

    def test_faster_could_be_isomorphic(self):
        assert_true(nx.faster_could_be_isomorphic(self.G3,self.G2))

    def test_is_isomorphic(self):
        assert_true(nx.is_isomorphic(self.G1,self.G2))
        assert_false(nx.is_isomorphic(self.G1,self.G4))
