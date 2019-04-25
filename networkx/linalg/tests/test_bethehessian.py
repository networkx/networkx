
from nose import SkipTest

import networkx as nx
from networkx.generators.degree_seq import havel_hakimi_graph


class TestBetheHessian(object):
    numpy = 1  # nosetests attribute, use nosetests -a 'not numpy' to skip test

    @classmethod
    def setupClass(cls):
        global numpy
        global scipy
        global assert_equal
        global assert_almost_equal
        try:
            import numpy
            import scipy
            from numpy.testing import assert_equal, assert_almost_equal
        except ImportError:
            raise SkipTest('SciPy not available.')

    def setUp(self):
        deg = [3, 2, 2, 1, 0]
        self.G = havel_hakimi_graph(deg)
        self.P = nx.path_graph(3)

    def test_bethe_hessian(self):
        "Bethe Hessian matrix"
        H = numpy.array([[ 4, -2,  0],
                          [-2,  5, -2],
                          [ 0, -2,  4]])
        permutation = [2, 0, 1]
        # Bethe Hessian gives expected form
        assert_equal(nx.bethe_hessian_matrix(self.P, r=2).todense(), H)
        # nodelist is correctly implemented
        assert_equal(nx.bethe_hessian_matrix(self.P, r=2, nodelist=permutation).todense(),
                     H[numpy.ix_(permutation, permutation)])
        # Equal to Laplacian matrix when r=1
        assert_equal(nx.bethe_hessian_matrix(self.G, r=1).todense(),
                     nx.laplacian_matrix(self.G).todense())
        # Correct default for the regularizer r
        assert_equal(nx.bethe_hessian_matrix(self.G).todense(),
                     nx.bethe_hessian_matrix(self.G, r=1.25).todense())
