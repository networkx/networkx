#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestVitality:

    def test_closeness_vitality_unweighted(self):
        G=nx.cycle_graph(3)
        v=nx.closeness_vitality(G)
        assert_equal(v,{0:4.0, 1:4.0, 2:4.0})
        assert_equal(v[0],4.0)

    def test_closeness_vitality_weighted(self):
        G=nx.Graph()
        G.add_cycle([0,1,2],weight=2)
        v=nx.closeness_vitality(G,weight='weight')
        assert_equal(v,{0:8.0, 1:8.0, 2:8.0})

    def test_closeness_vitality_unweighted_digraph(self):
        G=nx.DiGraph()
        G.add_cycle([0,1,2])
        v=nx.closeness_vitality(G)
        assert_equal(v,{0:8.0, 1:8.0, 2:8.0})

    def test_closeness_vitality_weighted_digraph(self):
        G=nx.DiGraph()
        G.add_cycle([0,1,2],weight=2)
        v=nx.closeness_vitality(G,weight='weight')
        assert_equal(v,{0:16.0, 1:16.0, 2:16.0})

    def test_closeness_vitality_weighted_multidigraph(self):
        G=nx.MultiDiGraph()
        G.add_cycle([0,1,2],weight=2)
        v=nx.closeness_vitality(G,weight='weight')
        assert_equal(v,{0:16.0, 1:16.0, 2:16.0})
