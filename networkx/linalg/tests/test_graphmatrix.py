from nose import SkipTest

import networkx as nx
from networkx.generators.degree_seq import havel_hakimi_graph

class TestGraphMatrix(object):
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
        self.OI=numpy.array([[-1, -1, -1, 0],
                            [1, 0, 0, -1],
                            [0, 1, 0, 1],
                            [0, 0, 1, 0],
                            [0, 0, 0, 0]])
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
        self.MGOI=numpy.array([[-1, -1, -1, -1, 0],
                            [1, 1, 0, 0, -1],
                            [0, 0, 1, 0, 1],
                            [0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0]])

    def test_incidence_matrix(self):
        "Conversion to incidence matrix"
        assert_equal(nx.incidence_matrix(self.G,oriented=True),self.OI)
        assert_equal(nx.incidence_matrix(self.G),numpy.abs(self.OI))
        assert_equal(nx.incidence_matrix(self.MG,oriented=True),self.OI)
        assert_equal(nx.incidence_matrix(self.MG),numpy.abs(self.OI))
        assert_equal(nx.incidence_matrix(self.MG2,oriented=True),self.MGOI)
        assert_equal(nx.incidence_matrix(self.MG2),numpy.abs(self.MGOI))
        assert_equal(nx.incidence_matrix(self.WG,oriented=True),self.OI)
        assert_equal(nx.incidence_matrix(self.WG),numpy.abs(self.OI))
        assert_equal(nx.incidence_matrix(self.WG,oriented=True,
                                         weight='weight'),0.5*self.OI)
        assert_equal(nx.incidence_matrix(self.WG,weight='weight'),
                     numpy.abs(0.5*self.OI))
        assert_equal(nx.incidence_matrix(self.WG,oriented=True,weight='other'),
                     0.3*self.OI)
        WMG=nx.MultiGraph(self.WG)
        WMG.add_edge(0,1,attr_dict={'weight':0.5,'other':0.3})
        assert_equal(nx.incidence_matrix(WMG,weight='weight'),
                     numpy.abs(0.5*self.MGOI))
        assert_equal(nx.incidence_matrix(WMG,weight='weight',oriented=True),
                     0.5*self.MGOI)
        assert_equal(nx.incidence_matrix(WMG,weight='other',oriented=True),
                     0.3*self.MGOI)

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

