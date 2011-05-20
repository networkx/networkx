from nose import SkipTest

import networkx as nx
from networkx.generators.degree_seq import havel_hakimi_graph

class TestSpectrum(object):
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
        self.P=nx.path_graph(3)
        self.A=numpy.array([[0, 1, 1, 1, 0],
                            [1, 0, 1, 0, 0],
                            [1, 1, 0, 0, 0],
                            [1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]])
        self.WG=nx.Graph( (u,v,{'weight':0.5,'other':0.3})
                for (u,v) in self.G.edges_iter() )
        self.WG.add_node(4)
        self.WA=numpy.array([[0 , 0.5, 0.5, 0.5, 0],
                            [0.5, 0  , 0.5, 0  , 0],
                            [0.5, 0.5, 0  , 0  , 0],
                            [0.5, 0  , 0  , 0  , 0],
                            [0  , 0  , 0  , 0  , 0]])
        self.MG=nx.MultiGraph(self.G)
        self.MG2=self.MG.copy()
        self.MG2.add_edge(0,1)
        self.MG2A=numpy.array([[0, 2, 1, 1, 0],
                            [2, 0, 1, 0, 0],
                            [1, 1, 0, 0, 0],
                            [1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0]])

    def test_adjacency_matrix(self):
        "Conversion to adjacency matrix"
        assert_equal(nx.adj_matrix(self.G),self.A)
        assert_equal(nx.adj_matrix(self.MG),self.A)
        assert_equal(nx.adj_matrix(self.MG2),self.MG2A)
        assert_equal(nx.adj_matrix(self.G,nodelist=[0,1]),self.A[:2,:2])
        assert_equal(nx.adj_matrix(self.WG),self.WA)
        assert_equal(nx.adj_matrix(self.WG,weight=None),self.A)
        assert_equal(nx.adj_matrix(self.MG2,weight=None),self.MG2A)
        assert_equal(nx.adj_matrix(self.WG,weight='other'),0.6*self.WA)

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

    def test_laplacian_spectrum(self):
        "Laplacian eigenvalues"
        evals=numpy.array([0, 0, 1, 3, 4])
        e=sorted(nx.laplacian_spectrum(self.G))
        assert_almost_equal(e,evals)
        e=sorted(nx.laplacian_spectrum(self.WG,weight=None))
        assert_almost_equal(e,evals)
        e=sorted(nx.laplacian_spectrum(self.WG))
        assert_almost_equal(e,0.5*evals)
        e=sorted(nx.laplacian_spectrum(self.WG,weight='other'))
        assert_almost_equal(e,0.3*evals)

    def test_adjacency_spectrum(self):
        "Adjacency eigenvalues"
        evals=numpy.array([-numpy.sqrt(2), 0, numpy.sqrt(2)])
        e=sorted(nx.adjacency_spectrum(self.P))
        assert_almost_equal(e,evals)

