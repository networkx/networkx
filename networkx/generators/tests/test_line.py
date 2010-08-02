#!/usr/bin/env python

"""line graph
----------
"""

import networkx as nx
from nose.tools import *


class TestGeneratorLine():
    def test_line(self):
        G=nx.star_graph(5)
        L=nx.line_graph(G)
        assert_true(nx.is_isomorphic(L,nx.complete_graph(5)))
        G=nx.path_graph(5)
        L=nx.line_graph(G)
        assert_true(nx.is_isomorphic(L,nx.path_graph(4)))
        G=nx.cycle_graph(5)
        L=nx.line_graph(G)
        assert_true(nx.is_isomorphic(L,G))
        G=nx.DiGraph()
        G.add_edges_from([(0,1),(0,2),(0,3)])
        L=nx.line_graph(G)
        assert_equal(L.adj, {})
        G=nx.DiGraph()
        G.add_edges_from([(0,1),(1,2),(2,3)])
        L=nx.line_graph(G)
        assert_equal(sorted(L.edges()), [((0, 1), (1, 2)), ((1, 2), (2, 3))])

