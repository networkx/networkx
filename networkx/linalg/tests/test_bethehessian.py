import pytest
numpy = pytest.importorskip('numpy')
npt = pytest.importorskip('numpy.testing')
scipy = pytest.importorskip('scipy')

import networkx as nx
from networkx.generators.degree_seq import havel_hakimi_graph


class TestBetheHessian(object):

    @classmethod
    def setup_class(cls):
        deg = [3, 2, 2, 1, 0]
        cls.G = havel_hakimi_graph(deg)
        cls.P = nx.path_graph(3)

    def test_bethe_hessian(self):
        "Bethe Hessian matrix"
        H = numpy.array([[4, -2,  0],
                         [-2,  5, -2],
                         [0, -2,  4]])
        permutation = [2, 0, 1]
        # Bethe Hessian gives expected form
        npt.assert_equal(nx.bethe_hessian_matrix(self.P, r=2).todense(), H)
        # nodelist is correctly implemented
        npt.assert_equal(nx.bethe_hessian_matrix(self.P, r=2, nodelist=permutation).todense(),
                         H[numpy.ix_(permutation, permutation)])
        # Equal to Laplacian matrix when r=1
        npt.assert_equal(nx.bethe_hessian_matrix(self.G, r=1).todense(),
                         nx.laplacian_matrix(self.G).todense())
        # Correct default for the regularizer r
        npt.assert_equal(nx.bethe_hessian_matrix(self.G).todense(),
                         nx.bethe_hessian_matrix(self.G, r=1.25).todense())
