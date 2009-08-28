"""
    Unit tests for matplotlib drawing functions.
"""

import os, sys
import tempfile

from nose import SkipTest
from nose.tools import assert_true

import networkx as nx

class TestPylab(object):
    @classmethod
    def setupClass(cls):
        global pylab
        try:
            import pylab
        except ImportError:
            raise SkipTest('matplotlib not available.')

    def setUp(self):
        self.G=nx.barbell_graph(5,10)


    def test_draw(self):
#         hold(False)
        N=self.G
        nx.draw_spring(N)
        savefig("test.png")
        draw_random(N)
        savefig("test.ps")
        draw_circular(N)
        savefig("test.png")
        draw_spectral(N)
        savefig("test.png")

