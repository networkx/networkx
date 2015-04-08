from nose import SkipTest

import networkx as nx
from networkx.generators.degree_seq import havel_hakimi_graph


class TestModularity(object):
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

        # Graph with selfloops
        self.Gsl = self.G.copy()
        for node in self.Gsl.nodes():
            self.Gsl.add_edge(node, node)

    def test_modularity(self):
        "Modularity matrix"
        B = numpy.matrix([[-1.125,  0.25 ,  0.25 ,  0.625,  0.   ],
                         [ 0.25 , -0.5  ,  0.5  , -0.25 ,  0.   ],
                         [ 0.25 ,  0.5  , -0.5  , -0.25 ,  0.   ],
                         [ 0.625, -0.25 , -0.25 , -0.125,  0.   ],
                         [ 0.   ,  0.   ,  0.   ,  0.   ,  0.   ]])

        permutation = [4, 0, 1, 2, 3]
        assert_equal(nx.modularity_matrix(self.G), B)
        assert_equal(nx.modularity_matrix(self.G, nodelist=permutation),
                     B[numpy.ix_(permutation, permutation)])
