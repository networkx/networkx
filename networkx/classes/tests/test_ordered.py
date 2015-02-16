#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest

import networkx as nx

from networkx.classes.ordered import OrderedDict

if OrderedDict is None:
    raise SkipTest('OrderedDict not available')


class SmokeTestOrdered(object):
    # Just test instantiation.
    def test_graph():
        G = nx.OrderedGraph()

    def test_digraph():
        G = nx.OrderedDiGraph()

    def test_multigraph():
        G = nx.OrderedMultiGraph()

    def test_multidigraph():
        G = nx.OrderedMultiDiGraph()

