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
    G = nx.cograph(n)
    assert_equal(len(list(G.nodes())), 2 ^ n)
