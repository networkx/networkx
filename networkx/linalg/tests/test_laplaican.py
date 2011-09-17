from nose import SkipTest

import networkx as nx
from networkx.generators.degree_seq import havel_hakimi_graph

class TestLaplacian(object):
    numpy=1 # nosetests attribute, use nosetests -a 'not numpy' to skip test
    @classmethod
    def setupClass(cls):
        global numpy
        global assert_equal
        global assert_almost_equal
        try:
            import numpy
            from numpy.testing import assert_equal,assert_almost_equal
        except ImportError:
             raise SkipTest('NumPy not available.')

    def setUp(self):
        deg=[3,2,2,1,0]
        self.G=havel_hakimi_graph(deg)
        self.WG=nx.Graph( (u,v,{'weight':0.5,'other':0.3})
                for (u,v) in self.G.edges_iter() )
        self.WG.add_node(4)
        self.MG=nx.MultiGraph(self.G)


    def test_laplacian(self):
        "Graph Laplacian"
        NL=numpy.array([[ 3, -1, -1, -1, 0],
                        [-1,  2, -1,  0, 0],
                        [-1, -1,  2,  0, 0],
                        [-1,  0,  0,  1, 0],
                        [ 0,  0,  0,  0, 0]])
        WL=0.5*NL
        OL=0.3*NL
        assert_equal(nx.laplacian(self.G),NL)
        assert_equal(nx.laplacian(self.MG),NL)
        assert_equal(nx.laplacian(self.G,nodelist=[0,1]),
                numpy.array([[ 1, -1],[-1, 1]]))
        assert_equal(nx.laplacian(self.WG),WL)
        assert_equal(nx.laplacian(self.WG,weight=None),NL)
        assert_equal(nx.laplacian(self.WG,weight='other'),OL)

    def test_generalized_laplacian(self):
        "Generalized Graph Laplacian"
        GL=numpy.array([[ 1.00, -0.408, -0.408, -0.577,  0.00],
                        [-0.408,  1.00, -0.50,  0.00 , 0.00], 
                        [-0.408, -0.50,  1.00,  0.00,  0.00], 
                        [-0.577,  0.00,  0.00,  1.00,  0.00],
                        [ 0.00,  0.00,  0.00,  0.00,  0.00]]) 
        assert_almost_equal(nx.generalized_laplacian(self.G),GL,decimal=3)
                       
    def test_normalized_laplacian(self):
        "Generalized Graph Laplacian"
        GL=numpy.array([[ 1.00, -0.408, -0.408, -0.577,  0.00],
                        [-0.408,  1.00, -0.50,  0.00 , 0.00], 
                        [-0.408, -0.50,  1.00,  0.00,  0.00], 
                        [-0.577,  0.00,  0.00,  1.00,  0.00],
                        [ 0.00,  0.00,  0.00,  0.00,  0.00]]) 
        assert_almost_equal(nx.normalized_laplacian(self.G),GL,decimal=3)
        assert_almost_equal(nx.normalized_laplacian(self.MG),GL,decimal=3)
        assert_almost_equal(nx.normalized_laplacian(self.WG),GL,decimal=3)
        assert_almost_equal(nx.normalized_laplacian(self.WG,weight='other'),GL,decimal=3)

