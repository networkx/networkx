# test_mycielski.py - unit tests for the mycielski module
#
# Copyright 2010, 2011, 2012, 2013, 2014, 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.

"""Unit tests for the :mod:`networkx.generators.mycielski` module."""

import networkx as nx


class TestMycielski(object):

    def test_construction(self):
        G = nx.path_graph(2)
        M = nx.mycielskian(G)
        assert nx.is_isomorphic(M, nx.cycle_graph(5))

    def test_size(self):
        G = nx.path_graph(2)
        M = nx.mycielskian(G, 2)
        assert len(M) == 11
        assert M.size() == 20

    def test_mycielski_graph_generator(self):
        G = nx.mycielski_graph(1)
        assert nx.is_isomorphic(G, nx.empty_graph(1))
        G = nx.mycielski_graph(2)
        assert nx.is_isomorphic(G, nx.path_graph(2))
        G = nx.mycielski_graph(3)
        assert nx.is_isomorphic(G, nx.cycle_graph(5))
        G = nx.mycielski_graph(4)
        assert nx.is_isomorphic(G, nx.mycielskian(nx.cycle_graph(5)))
