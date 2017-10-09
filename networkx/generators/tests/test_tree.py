# test_tree.py - unit tests for the networkx.generators.tree module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.generators.tree` module."""
from nose.tools import assert_true

import networkx as nx


def test_random_tree():
    """Tests that a random tree is in fact a tree."""
    T = nx.random_tree(10, seed=1234)
    assert_true(nx.is_tree(T))
