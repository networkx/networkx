#!/usr/bin/env python

"""ego graph
---------
"""

from nose.tools import assert_true, assert_equal
import networkx as nx

class TestGeneratorEgo():
    def test_ego(self):
        G=nx.star_graph(3)
        H=nx.ego_graph(G,0)
        assert_true(nx.is_isomorphic(G,H))
        G.add_edge(1,11)
        G.add_edge(2,22)
        G.add_edge(3,33)
        H=nx.ego_graph(G,0)
        assert_true(nx.is_isomorphic(nx.star_graph(3),H))
        G=nx.path_graph(3)
        H=nx.ego_graph(G,0)
        assert_equal(H.edges(), [(0, 1)])

