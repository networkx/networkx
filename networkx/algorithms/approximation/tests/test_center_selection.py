# test_center_selection.py - unit tests for the approximation.center_selection module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.approximation.center_selection`
module.

"""

from nose.tools import assert_equal
from nose.tools import raises
import random

import networkx as nx

class TestCenterSelection(object):
    """Unit tests for the
    :func:`~networkx.algorithms.approximation.center_selection` function.

    """

    @raises(nx.NetworkXError)
    def test_exception_complete(self):
        G = nx.complete_graph(10)
        G.remove_edge(0, 1)
        nx.center_selection(G, 2)

    @raises(nx.NetworkXError)
    def test_exception_float(self):
        G = nx.complete_graph(10)
        nx.center_selection(G, 2.5)
    
    @raises(nx.NetworkXError)
    def test_exception_big_k(self):
        G = nx.complete_graph(2)
        nx.center_selection(G, 5)

    @raises(nx.NetworkXError)
    def test_exception_negative_k(self):
        G = nx.complete_graph(2)
        nx.center_selection(G, -1)

    @raises(nx.NetworkXError)
    def test_exception_negative_weight(self):
        G = nx.complete_graph(2)
        for (u, v) in G.edges():
            G.edges[u,v]['weight'] = -10
        nx.center_selection(G, 2)

    def test_trivial1(self):
        G = nx.complete_graph(2)
        _, centers = nx.center_selection(G, 2)
        assert_equal(set(centers), set(G.nodes))
