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
            import matplotlib as mpl
            mpl.use('PS',warn=False)
            import pylab
        except ImportError:
            raise SkipTest('matplotlib not available.')
        except RuntimeError:
            raise SkipTest('matplotlib not available.')

    def setUp(self):
        self.G=nx.barbell_graph(5,10)


    def test_draw(self):
#         hold(False)
        N=self.G
        nx.draw_spring(N)
        pylab.savefig("test.ps")
        nx.draw_random(N)
        pylab.savefig("test.ps")
        nx.draw_circular(N)
        pylab.savefig("test.ps")
        nx.draw_spectral(N)
        pylab.savefig("test.ps")
        os.unlink('test.ps')
