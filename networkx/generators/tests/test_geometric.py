#!/usr/bin/env python

from nose.tools import *
from networkx import *
from networkx.generators.geometric import *

"""Generators - Geometric
======================
"""

class TestGeneratorsGeometric():
    def test_random_geometric_graph(self):
        G=random_geometric_graph(50,0.25)

