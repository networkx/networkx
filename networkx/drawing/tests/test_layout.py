"""Unit tests for layout functions."""
import sys
from nose import SkipTest
from nose.tools import assert_equal, assert_false, assert_raises
import networkx as nx


class TestLayout(object):
    numpy = 1 # nosetests attribute, use nosetests -a 'not numpy' to skip test
    @classmethod
    def setupClass(cls):
        global numpy
        try:
            import numpy
        except ImportError:
            raise SkipTest('numpy not available.')

    def setUp(self):
        self.Gi = nx.grid_2d_graph(5, 5)
        self.Gs = nx.Graph()
        nx.add_path(self.Gs, 'abcdef')
        self.bigG = nx.grid_2d_graph(25, 25) #bigger than 500 nodes for sparse

    def test_smoke_int(self):
        G = self.Gi
        vpos = nx.random_layout(G)
        vpos = nx.circular_layout(G)
        vpos = nx.spring_layout(G)
        vpos = nx.fruchterman_reingold_layout(G)
        vpos = nx.fruchterman_reingold_layout(self.bigG)
        vpos = nx.spectral_layout(G)
        vpos = nx.spectral_layout(self.bigG)
        vpos = nx.shell_layout(G)

    def test_smoke_string(self):
        G = self.Gs
        vpos = nx.random_layout(G)
        vpos = nx.circular_layout(G)
        vpos = nx.spring_layout(G)
        vpos = nx.fruchterman_reingold_layout(G)
        vpos = nx.spectral_layout(G)
        vpos = nx.shell_layout(G)

    def test_adjacency_interface_numpy(self):
        A = nx.to_numpy_matrix(self.Gs)
        pos = nx.drawing.layout._fruchterman_reingold(A)
        assert_equal(pos.shape, (6, 2))
        pos = nx.drawing.layout._fruchterman_reingold(A, dim=3)
        assert_equal(pos.shape, (6, 3))

    def test_adjacency_interface_scipy(self):
        try:
            import scipy
        except ImportError:
            raise SkipTest('scipy not available.')
        A = nx.to_scipy_sparse_matrix(self.Gs, dtype='d')
        pos = nx.drawing.layout._sparse_fruchterman_reingold(A)
        assert_equal(pos.shape, (6, 2))
        pos = nx.drawing.layout._sparse_spectral(A)
        assert_equal(pos.shape, (6, 2))
        pos = nx.drawing.layout._sparse_fruchterman_reingold(A, dim=3)
        assert_equal(pos.shape, (6, 3))

    def test_single_nodes(self):
        G = nx.path_graph(1)
        vpos = nx.shell_layout(G)
        assert_false(vpos[0].any())
        G = nx.path_graph(3)
        vpos = nx.shell_layout(G, [[0], [1, 2]])
        assert_false(vpos[0].any())

    def test_smoke_initial_pos_fruchterman_reingold(self):
        pos = nx.circular_layout(self.Gi)
        npos = nx.fruchterman_reingold_layout(self.Gi, pos=pos)

    def test_fixed_node_fruchterman_reingold(self):
        # Dense version (numpy based)
        pos = nx.circular_layout(self.Gi)
        npos = nx.fruchterman_reingold_layout(self.Gi, pos=pos, fixed=[(0, 0)])
        assert_equal(tuple(pos[(0, 0)]), tuple(npos[(0, 0)]))
        # Sparse version (scipy based)
        pos = nx.circular_layout(self.bigG)
        npos = nx.fruchterman_reingold_layout(self.bigG, pos=pos, fixed=[(0, 0)])
        assert_equal(tuple(pos[(0, 0)]), tuple(npos[(0, 0)]))

    def test_center_parameter(self):
        G =  nx.path_graph(1)
        vpos = nx.random_layout(G, center=(1, 1))
        vpos = nx.circular_layout(G, center=(1, 1))
        assert_equal(tuple(vpos[0]), (1, 1))
        vpos = nx.spring_layout(G, center=(1, 1))
        assert_equal(tuple(vpos[0]), (1, 1))
        vpos = nx.fruchterman_reingold_layout(G, center=(1, 1))
        assert_equal(tuple(vpos[0]), (1, 1))
        vpos = nx.spectral_layout(G, center=(1, 1))
        assert_equal(tuple(vpos[0]), (1, 1))
        vpos = nx.shell_layout(G, center=(1, 1))
        assert_equal(tuple(vpos[0]), (1, 1))

    def test_center_wrong_dimensions(self):
        G =  nx.path_graph(1)
        assert_raises(ValueError, nx.random_layout, G, center=(1, 1, 1))
        assert_raises(ValueError, nx.circular_layout, G, center=(1, 1, 1))
        assert_raises(ValueError, nx.spring_layout, G, center=(1, 1, 1))
        assert_raises(ValueError, nx.fruchterman_reingold_layout, G, center=(1, 1, 1))
        assert_raises(ValueError, nx.fruchterman_reingold_layout, G, dim=3, center=(1, 1))
        assert_raises(ValueError, nx.spectral_layout, G, center=(1, 1, 1))
        assert_raises(ValueError, nx.spectral_layout, G, dim=3, center=(1, 1))
        assert_raises(ValueError, nx.shell_layout, G, center=(1, 1, 1))

    def test_empty_graph(self):
        G =  nx.empty_graph()
        vpos = nx.random_layout(G, center=(1, 1))
        assert_equal(vpos, {})
        vpos = nx.circular_layout(G, center=(1, 1))
        assert_equal(vpos, {})
        vpos = nx.spring_layout(G, center=(1, 1))
        assert_equal(vpos, {})
        vpos = nx.fruchterman_reingold_layout(G, center=(1, 1))
        assert_equal(vpos, {})
        vpos = nx.spectral_layout(G, center=(1, 1))
        assert_equal(vpos, {})
        vpos = nx.shell_layout(G, center=(1, 1))
        assert_equal(vpos, {})
