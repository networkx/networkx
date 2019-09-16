# test_maximum_disjoint_paths.py - unit tests for the approximation.maximum_disjoint_paths module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.approximation.maximum_disjoint_paths`
module.

"""

from nose.tools import assert_equal
from nose.tools import raises
import random

import networkx as nx

class TestMaximumDisjointPaths(object):
    """Unit tests for the
    :func:`~networkx.algorithms.approximation.maximum_disjoint_paths` function.

    """

    def test_trivial(self):
        G = nx.complete_graph(2)
        paths, satisfied, unsatisfied = nx.maximum_disjoint_paths(G, [(0, 1)])
        assert_equal(paths, [[(0, 1)]])
        assert_equal(satisfied, [(0, 1)])
        assert_equal(unsatisfied, [])
