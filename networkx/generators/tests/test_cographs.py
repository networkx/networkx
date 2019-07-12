# -*- encoding: utf-8 -*-
# test_cographs.py - unit tests for cograph generators
#
# Copyright 2010-2019 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.generators.cographs` module.

"""

import networkx as nx
from nose.tools import *


def test_random_cograph():
    n = 3
    G = nx.random_cograph(n)

    assert_equal(len(G), 2 ** n)

    #Every connected subgraph of G has diameter <= 2
    if nx.is_connected(G):
        assert_true(nx.diameter(G) <= 2)
    else:
        components = nx.connected_components(G)
        for component in components:
            assert_true(nx.diameter(G.subgraph(component)) <= 2)
