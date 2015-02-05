#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestDistanceRegular:

    def test_is_distance_regular(self):
        assert_true(nx.is_distance_regular(nx.icosahedral_graph()))
        assert_true(nx.is_distance_regular(nx.petersen_graph()))
        assert_true(nx.is_distance_regular(nx.cubical_graph()))
        assert_true(nx.is_distance_regular(nx.complete_bipartite_graph(3,3)))
        assert_true(nx.is_distance_regular(nx.tetrahedral_graph()))
        assert_true(nx.is_distance_regular(nx.dodecahedral_graph()))
        assert_true(nx.is_distance_regular(nx.pappus_graph()))
        assert_true(nx.is_distance_regular(nx.heawood_graph()))
        assert_true(nx.is_distance_regular(nx.cycle_graph(3)))
        # no distance regular
        assert_false(nx.is_distance_regular(nx.path_graph(4)))

    def test_not_connected(self):
        G=nx.cycle_graph(4)
        G.add_cycle([5,6,7])
        assert_false(nx.is_distance_regular(G))


    def test_global_parameters(self):
        b,c=nx.intersection_array(nx.cycle_graph(5))
        g=nx.global_parameters(b,c)
        assert_equal(list(g),[(0, 0, 2), (1, 0, 1), (1, 1, 0)])
        b,c=nx.intersection_array(nx.cycle_graph(3))
        g=nx.global_parameters(b,c)
        assert_equal(list(g),[(0, 0, 2), (1, 1, 0)])


    def test_intersection_array(self):
        b,c=nx.intersection_array(nx.cycle_graph(5))
        assert_equal(b,[2, 1])
        assert_equal(c,[1, 1])
        b,c=nx.intersection_array(nx.dodecahedral_graph())
        assert_equal(b,[3, 2, 1, 1, 1])
        assert_equal(c,[1, 1, 1, 2, 3])
        b,c=nx.intersection_array(nx.icosahedral_graph())
        assert_equal(b,[5, 2, 1])
        assert_equal(c,[1, 2, 5])
