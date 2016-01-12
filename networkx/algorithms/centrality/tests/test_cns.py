# test_cns.py - unit tests for the centrality.cns module
#
# Copyright 2009 "dheerajrav".
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.centrality.cns` module.

"""
from nose.tools import assert_almost_equal

import networkx as nx


def test_cns_disconnected():
    # This graph is the disjoint union of two triangles.
    G = nx.Graph()
    G.add_path([0, 1, 2, 0])
    G.add_path([3, 4, 5, 3])
    cns = nx.cns_centrality(G)
    for v in cns.values():
        assert_almost_equal(v, 1.5)


def test_cns_connected():
    G = nx.complete_graph(3)
    cns = nx.cns_centrality(G)
    for v in cns.values():
        assert_almost_equal(v, 1)
