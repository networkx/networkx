"""
    Unit tests for layout functions.
"""

import sys

from nose import SkipTest
from nose.tools import assert_equal

import networkx as nx

class TestLayout(object):
    numpy=1 # nosetests attribute, use nosetests -a 'not numpy' to skip test
    @classmethod
    def setupClass(cls):
        global numpy
        try:
            import numpy
        except ImportError:
            raise SkipTest('numpy not available.')
        if sys.version_info[0] > 2:
            raise SkipTest('Drawing not implemented for Python 3.x')


    def setUp(self):
        self.Gi=nx.grid_2d_graph(5,5)
        self.Gs=nx.Graph()
        self.Gs.add_path('abcdef')
        self.bigG=nx.grid_2d_graph(25,25) #bigger than 500 nodes for sparse

    def test_smoke_int(self):
        G=self.Gi
        vpos=nx.random_layout(G)
        vpos=nx.circular_layout(G)
        vpos=nx.spring_layout(G)
        vpos=nx.fruchterman_reingold_layout(G)
        vpos=nx.spectral_layout(G)
        vpos=nx.spectral_layout(self.bigG)
        vpos=nx.shell_layout(G)

    def test_smoke_string(self):
        G=self.Gs
        vpos=nx.random_layout(G)
        vpos=nx.circular_layout(G)
        vpos=nx.spring_layout(G)
        vpos=nx.fruchterman_reingold_layout(G)
        vpos=nx.spectral_layout(G)
        vpos=nx.shell_layout(G)


    def test_adjacency_interface_numpy(self):
        A=nx.to_numpy_matrix(self.Gs)
        pos=nx.drawing.layout._fruchterman_reingold(A)
        pos=nx.drawing.layout._fruchterman_reingold(A,dim=3)
        assert_equal(pos.shape,(6,3))

    def test_adjacency_interface_scipy(self):
        try:
            import scipy
        except ImportError:
            raise SkipTest('scipy not available.')

        A=nx.to_scipy_sparse_matrix(self.Gs)
        pos=nx.drawing.layout._sparse_fruchterman_reingold(A)
        pos=nx.drawing.layout._sparse_spectral(A)

        pos=nx.drawing.layout._sparse_fruchterman_reingold(A,dim=3)
        assert_equal(pos.shape,(6,3))


