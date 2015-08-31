"""
    Unit tests for matplotlib drawing functions.
"""

import os

from nose import SkipTest

import networkx as nx

class TestPylab(object):
    @classmethod
    def setupClass(cls):
        global plt
        try:
            import matplotlib as mpl
            mpl.use('PS',warn=False)
            import matplotlib.pyplot as plt
            plt.rcParams['text.usetex'] = False
        except ImportError:
            raise SkipTest('matplotlib not available.')
        except RuntimeError:
            raise SkipTest('matplotlib not available.')

    def setUp(self):
        self.G=nx.barbell_graph(5,10)


    def test_draw(self):
        try:
            N=self.G
            nx.draw_spring(N)
            plt.savefig("test.ps")
            nx.draw_random(N)
            plt.savefig("test.ps")
            nx.draw_circular(N)
            plt.savefig("test.ps")
            nx.draw_spectral(N)
            plt.savefig("test.ps")
            nx.draw_spring(N.to_directed())
            plt.savefig("test.ps")
        finally:
            try:
                os.unlink('test.ps')
            except OSError:
                pass
