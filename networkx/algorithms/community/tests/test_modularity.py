# test_modularity.py - unit tests for the community.modularity module
#
# Copyright 2011 Ben Edwards <bedwards@cs.unm.edu>.
# Copyright 2011 Aric Hagberg <hagberg@lanl.gov>.
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.community.modularity`
module.

"""
from __future__ import division

from nose.tools import assert_almost_equal

import networkx as nx


def test_modularity():
    G = nx.barbell_graph(3, 0)
    C = [{0, 1, 4}, {2, 3, 5}]
    assert_almost_equal(-16 / (14 ** 2), nx.modularity(G, C))
    C = [{0, 1, 2}, {3, 4, 5}]
    assert_almost_equal((35 * 2) / (14 ** 2), nx.modularity(G, C))
