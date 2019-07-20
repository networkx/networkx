#!/usr/bin/env python
import networkx as nx

from nose.tools import *
from nose import SkipTest
from nose.plugins.attrib import attr


@attr('numpy')
def test_non_randomness():
    try:
        import numpy.testing as npt
    except ImportError:
        raise SkipTest('numpy not available.')
    G = nx.karate_club_graph()
    npt.assert_almost_equal(nx.non_randomness(G, 2)[0], 11.7, decimal=2)
    npt.assert_almost_equal(nx.non_randomness(G)[0],
                            7.21, decimal=2)  # infers 3 communities
