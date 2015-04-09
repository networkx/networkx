#!/usr/bin/env python
"""
====================
Generators - Non Isomorphic Trees
====================

Unit tests for WROM algorithm generator in generators/nonisomorphic_trees.py
"""
from nose.tools import *
from networkx import *


class TestGeneratorNonIsomorphicTrees():

    def test_number_of_nonisomorphic_trees(self):
        # http://oeis.org/A000055
        assert_equal(nx.number_of_nonisomorphic_trees(2), 1)
        assert_equal(nx.number_of_nonisomorphic_trees(3), 1)
        assert_equal(nx.number_of_nonisomorphic_trees(4), 2)
        assert_equal(nx.number_of_nonisomorphic_trees(5), 3)
        assert_equal(nx.number_of_nonisomorphic_trees(6), 6)
        assert_equal(nx.number_of_nonisomorphic_trees(7), 11)
        assert_equal(nx.number_of_nonisomorphic_trees(8), 23)

    def test_nonisomorphic_trees(self):
        f = lambda x: list(nx.nonisomorphic_trees(x))
        assert_equal(f(3)[0].edges(), [(0, 1), (0, 2)])
        assert_equal(f(4)[0].edges(), [(0, 1), (0, 3), (1, 2)])
        assert_equal(f(4)[1].edges(), [(0, 1), (0, 2), (0, 3)])
