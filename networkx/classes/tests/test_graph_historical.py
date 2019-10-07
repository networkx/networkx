#!/usr/bin/env python
"""Original NetworkX graph tests"""
from nose.tools import *
import networkx
import networkx as nx

from .historical_tests import HistoricalTests


class TestGraphHistorical(HistoricalTests):

    @classmethod
    def setup_class(cls):
        HistoricalTests.setup_class()
        cls.G = nx.Graph
