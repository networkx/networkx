#!/usr/bin/env python
"""Original NetworkX graph tests"""
import copy
from nose.tools import *
import networkx
import networkx as nx
from networkx import convert_node_labels_to_integers as cnlti

from historical_tests import HistoricalTests

class TestGraphHistorical(HistoricalTests):

    def setUp(self):
        HistoricalTests.setUp(self)
        self.G=nx.Graph

