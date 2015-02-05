#!/usr/bin/env python

"""Generators - Directed Graphs
----------------------------
"""

from nose.tools import *
from networkx import *
from networkx.generators.directed import *

class TestGeneratorsDirected():
    def test_smoke_test_random_graphs(self):
        G=gn_graph(100)
        G=gnr_graph(100,0.5)
        G=gnc_graph(100)
        G=scale_free_graph(100)

    def test_create_using_keyword_arguments(self):
        assert_raises(networkx.exception.NetworkXError,
                      gn_graph, 100, create_using=Graph())
        assert_raises(networkx.exception.NetworkXError,
                      gnr_graph, 100, 0.5, create_using=Graph())
        assert_raises(networkx.exception.NetworkXError,
                      gnc_graph, 100, create_using=Graph())
        assert_raises(networkx.exception.NetworkXError,
                      scale_free_graph, 100, create_using=Graph())
        G=gn_graph(100,seed=1)
        MG=gn_graph(100,create_using=MultiDiGraph(),seed=1)
        assert_equal(G.edges(), MG.edges())
        G=gnr_graph(100,0.5,seed=1)
        MG=gnr_graph(100,0.5,create_using=MultiDiGraph(),seed=1)
        assert_equal(G.edges(), MG.edges())
        G=gnc_graph(100,seed=1)
        MG=gnc_graph(100,create_using=MultiDiGraph(),seed=1)
        assert_equal(G.edges(), MG.edges())

