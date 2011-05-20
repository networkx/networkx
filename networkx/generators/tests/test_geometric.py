#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestGeneratorsGeometric():
    def test_random_geometric_graph(self):
        G=nx.random_geometric_graph(50,0.25)
        assert_equal(len(G),50)

    def test_geographical_threshold_graph(self):
        G=nx.geographical_threshold_graph(50,100)
        assert_equal(len(G),50)

    def test_waxman_graph(self):
        G=nx.waxman_graph(50,0.5,0.1)
        assert_equal(len(G),50)
        G=nx.waxman_graph(50,0.5,0.1,L=1)
        assert_equal(len(G),50)
