"""Unit tests for layout functions."""
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
        G = self.Gs
        vpos = nx.random_layout(G)
        vpos = nx.circular_layout(G)
        vpos = nx.spring_layout(G)
        vpos = nx.fruchterman_reingold_layout(G)
        vpos = nx.spectral_layout(G)
        vpos = nx.shell_layout(G)

    def test_empty_graph(self):
        G=nx.Graph()
        vpos = nx.random_layout(G)
        vpos = nx.circular_layout(G)
        vpos = nx.spring_layout(G)
        vpos = nx.fruchterman_reingold_layout(G)
        vpos = nx.shell_layout(G)
        vpos = nx.spectral_layout(G)
        # center arg
        vpos = nx.random_layout(G, scale=2, center=(4,5))
        vpos = nx.circular_layout(G, scale=2, center=(4,5))
        vpos = nx.spring_layout(G, scale=2, center=(4,5))
        vpos = nx.shell_layout(G, scale=2, center=(4,5))
        vpos = nx.spectral_layout(G, scale=2, center=(4,5))

    def test_single_node(self):
        G = nx.Graph()
        G.add_node(0)
        vpos = nx.random_layout(G)
        vpos = nx.circular_layout(G)
        vpos = nx.spring_layout(G)
        vpos = nx.fruchterman_reingold_layout(G)
        vpos = nx.shell_layout(G)
        vpos = nx.spectral_layout(G)
        # center arg
        vpos = nx.random_layout(G, scale=2, center=(4,5))
        vpos = nx.circular_layout(G, scale=2, center=(4,5))
        vpos = nx.spring_layout(G, scale=2, center=(4,5))
        vpos = nx.shell_layout(G, scale=2, center=(4,5))
        vpos = nx.spectral_layout(G, scale=2, center=(4,5))

    def check_scale_and_center(self, pos, scale, center):
        center = numpy.array(center)
        low = center - 0.5 * scale
        hi = center + 0.5 * scale
        vpos = numpy.array(list(pos.values()))
        length = vpos.max(0) - vpos.min(0)
        assert (length <= scale).all()
        assert (vpos >= low).all()
        assert (vpos <= hi).all()

    def test_scale_and_center_arg(self):
        G = nx.complete_graph(9)
        G.add_node(9)
        vpos = nx.random_layout(G, scale=2, center=(4,5))
        self.check_scale_and_center(vpos, scale=2, center=(4,5))
        vpos = nx.spring_layout(G, scale=2, center=(4,5))
        self.check_scale_and_center(vpos, scale=2, center=(4,5))
        vpos = nx.spectral_layout(G, scale=2, center=(4,5))
        self.check_scale_and_center(vpos, scale=2, center=(4,5))
        # circular can have twice as big length
        vpos = nx.circular_layout(G, scale=2, center=(4,5))
        self.check_scale_and_center(vpos, scale=2*2, center=(4,5))
        vpos = nx.shell_layout(G, scale=2, center=(4,5))
        self.check_scale_and_center(vpos, scale=2*2, center=(4,5))

        # check default center and scale
        vpos = nx.random_layout(G)
        self.check_scale_and_center(vpos, scale=1, center=(0.5,0.5))
        vpos = nx.spring_layout(G)
        self.check_scale_and_center(vpos, scale=1, center=(0.5,0.5))
        vpos = nx.spectral_layout(G)
        self.check_scale_and_center(vpos, scale=1, center=(0.5,0.5))
        vpos = nx.circular_layout(G)
        self.check_scale_and_center(vpos, scale=2, center=(0,0))
        vpos = nx.shell_layout(G)
        self.check_scale_and_center(vpos, scale=2, center=(0,0))

    def test_shell_layout(self):
        G = nx.complete_graph(9)
        shells=[[0], [1,2,3,5], [4,6,7,8]]
        vpos = nx.shell_layout(G, nlist=shells)
        vpos = nx.shell_layout(G, nlist=shells, scale=2, center=(3,4))
        shells=[[0,1,2,3,5], [4,6,7,8]]
        vpos = nx.shell_layout(G, nlist=shells)
        vpos = nx.shell_layout(G, nlist=shells, scale=2, center=(3,4))

    def test_spring_args(self):
        G = nx.complete_graph(9)
        vpos = nx.spring_layout(G, dim=3)
        assert_equal(vpos[0].shape, (3,))
        vpos = nx.spring_layout(G, fixed=[0,1], pos={1:(0,0), 2:(1,1)})
        vpos = nx.spring_layout(G, k=2, fixed=[0,1], pos={1:(0,0), 2:(1,1)})
        vpos = nx.spring_layout(G, scale=3, center=(2,5))
        vpos = nx.spring_layout(G, scale=3)
        vpos = nx.spring_layout(G, center=(2,5))

    def test_spectral_for_small_graphs(self):
        G = nx.Graph()
        vpos = nx.spectral_layout(G)
        vpos = nx.spectral_layout(G, center=(2,3))
        G.add_node(0)
        vpos = nx.spectral_layout(G)
        vpos = nx.spectral_layout(G, center=(2,3))
        G.add_node(1)
        vpos = nx.spectral_layout(G)
        vpos = nx.spectral_layout(G, center=(2,3))
        # 3 nodes should allow eigensolvers to work
        G.add_node(2)
        vpos = nx.spectral_layout(G)
        vpos = nx.spectral_layout(G, center=(2,3))

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

        A=nx.to_scipy_sparse_matrix(self.Gs,dtype='d')
        pos=nx.drawing.layout._sparse_fruchterman_reingold(A)
        pos=nx.drawing.layout._sparse_spectral(A)

        pos=nx.drawing.layout._sparse_fruchterman_reingold(A,dim=3)
        assert_equal(pos.shape,(6,3))
