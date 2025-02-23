# -*- coding: utf-8 -*-

import networkx as nx
from nose.tools import assert_equal, assert_raises
import os

class TestGeneralizedFlow:
    def test_simple_digraph(self):
        G = nx.DiGraph()
        G.add_node('a', demand = -5)
        G.add_node('d', demand = 5)
        G.add_edge('a', 'b', weight = 3, capacity = 4, multiplier = 1)
        G.add_edge('a', 'c', weight = 6, capacity = 10, multiplier = 1)
        G.add_edge('b', 'd', weight = 1, capacity = 9, multiplier = 1)
        G.add_edge('c', 'd', weight = 2, capacity = 5, multiplier = 1)
        flowCost, H = nx.network_simplex_generalized(G)
        soln = {'a': {'b': 4, 'c': 1},
                'b': {'d': 4},
                'c': {'d': 1},
                'd': {}}

        assert_equal(flowCost, 24)
        assert_equal(H, soln)

