#!/usr/bin/env python
from nose.tools import assert_raises, assert_true

import networkx as nx
from networkx.generators.line import line_graph, inverse_line_graph

class TestLineGraph():
    def test_invalid_line_graphs(self):
        # a claw is not a line graph
        K13 = nx.complete_bipartite_graph(1, 3)
        assert_raises(nx.NetworkXError, inverse_line_graph, K13)
        # neither is "K5 minus an edge":
        K5me = nx.complete_graph(5)
        K5me.remove_edge(0,1)
        assert_raises(nx.NetworkXError, inverse_line_graph, K5me)

    def test_valid_line_graphs(self):
        # the line graph of a star is a complete graph
        S4 = nx.star_graph(4)
        L = line_graph(S4)
        K4 = nx.complete_graph(4)

        assert_true(nx.is_isomorphic(L, K4))

        L_ = inverse_line_graph(K4)
        assert_true(nx.is_isomorphic(L_, S4))
