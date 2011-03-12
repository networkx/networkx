#!/usr/bin/env python

from nose.tools import *
from networkx import *
from networkx.generators.random_graphs import *


"""Generators - Random Graphs
----------------------------
"""

class TestGeneratorsRandom():
    def smoke_test_random_graph(self):
        G=gnp_random_graph(100,0.25)
        G=binomial_graph(100,0.25)
        G=erdos_renyi_graph(100,0.25)
        G=fast_gnp_random_graph(100,0.25)
        G=gnm_random_graph(100,20)
        G=dense_gnm_random_graph(100,20)

        G=watts_strogatz_graph(10,2,0.25)
        assert_equal(len(G), 10)
        assert_equal(G.number_of_edges(), 10)
        
        G=watts_strogatz_graph(10,4,0.25)
        assert_equal(len(G), 10)
        assert_equal(G.number_of_edges(), 20)

        G=newman_watts_strogatz_graph(10,2,0.0)
        assert_equal(len(G), 10)
        assert_equal(G.number_of_edges(), 10)

        G=newman_watts_strogatz_graph(10,4,0.25)
        assert_equal(len(G), 10)
        assert_true(G.number_of_edges() >= 20)

        G=barabasi_albert_graph(100,1)
        G=barabasi_albert_graph(100,3)
        assert_equal(G.number_of_edges(),(97*3))
        
        G=powerlaw_cluster_graph(100,1,1.0)
        G=powerlaw_cluster_graph(100,3,0.0)
        assert_equal(G.number_of_edges(),(97*3))
        
        G=random_regular_graph(10,20)
        
        assert_raises(networkx.exception.NetworkXError,
                      random_regular_graph, 3, 21)

        constructor=[(10,20,0.8),(20,40,0.8)]
        G=random_shell_graph(constructor)

        """This test fails sometimes because of not enough tries
        and takes too long for more tries...
        s=random_powerlaw_tree_sequence(10,gamma=3,tries=1000)
        s=random_powerlaw_tree(10,gamma=3,tries=1000)
        """

    def test_gnp(self):
        G=gnp_random_graph(10,0.1)
        assert_equal(len(G),10)

        G=gnp_random_graph(10,0.1,seed=42)
        assert_equal(len(G),10)

        G=gnp_random_graph(10,1.1)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),45)

        G=gnp_random_graph(10,1.1,directed=True)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),90)

        G=gnp_random_graph(10,-1.1)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),0)

        G=binomial_graph(10,0.1)
        assert_equal(len(G),10)

        G=erdos_renyi_graph(10,0.1)
        assert_equal(len(G),10)


    def test_fast_gnp(self):
        G=fast_gnp_random_graph(10,0.1)
        assert_equal(len(G),10)

        G=fast_gnp_random_graph(10,0.1,seed=42)
        assert_equal(len(G),10)

        G=fast_gnp_random_graph(10,1.1)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),45)

        G=fast_gnp_random_graph(10,-1.1)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),0)

        G=fast_gnp_random_graph(10,0.1,directed=True)
        assert_true(G.is_directed())
        assert_equal(len(G),10)


    def test_gnm(self):
        G=gnm_random_graph(10,3)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),3)

        G=gnm_random_graph(10,3,seed=42)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),3)

        G=gnm_random_graph(10,100)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),45)

        G=gnm_random_graph(10,100,directed=True)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),90)

        G=gnm_random_graph(10,-1.1)
        assert_equal(len(G),10)
        assert_equal(len(G.edges()),0)



