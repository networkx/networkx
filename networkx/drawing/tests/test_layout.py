"""Unit tests for layout functions."""
import sys
from nose import SkipTest
from nose.tools import assert_almost_equal, assert_equal, \
                       assert_false, assert_raises
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
        vpos = nx.kamada_kawai_layout(G)
        vpos = nx.spectral_layout(G)
        vpos = nx.spectral_layout(self.bigG)
        vpos = nx.shell_layout(G)

    def test_smoke_string(self):
        G = self.Gs
        vpos = nx.random_layout(G)
        vpos = nx.circular_layout(G)
        vpos = nx.spring_layout(G)
        vpos = nx.fruchterman_reingold_layout(G)
        vpos = nx.kamada_kawai_layout(G)
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

    def test_kamada_kawai_costfn_1d(self):
        costfn = nx.drawing.layout._kamada_kawai_costfn

        pos = numpy.array([4.0, 7.0])
        invdist = 1 / numpy.array([[0.1, 2.0], [2.0, 0.3]])

        cost, grad = costfn(pos, numpy, invdist, meanweight=0, dim=1)

        assert_almost_equal(cost, ((3 / 2.0 - 1) ** 2))
        assert_almost_equal(grad[0], -0.5)
        assert_almost_equal(grad[1], 0.5)

    def test_kamada_kawai_costfn_2d(self):
        costfn = nx.drawing.layout._kamada_kawai_costfn

        pos = numpy.array([[ 1.3, -3.2 ],
                           [ 2.7, -0.3 ],
                           [ 5.1, 2.5 ]])
        invdist = 1 / numpy.array([[ 0.1, 2.1, 1.7 ],
                                   [ 2.1, 0.2, 0.6 ],
                                   [ 1.7, 0.6, 0.3 ]])
        meanwt = 0.3

        cost, grad = costfn(pos.ravel(), numpy, invdist,
                            meanweight=meanwt, dim=2)

        expected_cost = 0.5 * meanwt * numpy.sum(numpy.sum(pos, axis=0) ** 2)
        for i in range(pos.shape[0]):
            for j in range(i+1, pos.shape[0]):
                expected_cost += (numpy.linalg.norm(pos[i] - pos[j])
                                    * invdist[i][j] - 1.0) ** 2

        assert_almost_equal(cost, expected_cost)

        dx = 1e-4
        for nd in range(pos.shape[0]):
            for dm in range(pos.shape[1]):
                idx = nd * pos.shape[1] + dm
                pos0 = pos.flatten()

                pos0[idx] += dx
                cplus = costfn(pos0, numpy, invdist,
                               meanweight=meanwt, dim=pos.shape[1])[0]

                pos0[idx] -= 2 * dx
                cminus = costfn(pos0, numpy, invdist,
                                meanweight=meanwt, dim=pos.shape[1])[0]

                assert_almost_equal(grad[idx], (cplus - cminus) / (2 * dx),
                                    places=5)
