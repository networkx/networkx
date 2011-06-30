#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx
import networkx.algorithms.mixing as mixing


class TestDegreeMixing(object):
    
    def setUp(self):
        self.P4=networkx.path_graph(4)
        self.D=networkx.DiGraph() 
        self.D.add_edges_from([(0, 2), (0, 3), (1, 3), (2, 3)])
        self.M=networkx.MultiGraph() 
        self.M.add_path(list(range(4)))
        self.M.add_edge(0,1)
        self.S=networkx.Graph()
        self.S.add_edges_from([(0,0),(1,1)])


    def test_node_degree_xy_undirected(self):
        xy=sorted(mixing.node_degree_xy(self.P4))
        xy_result=sorted([(1,2),
                          (2,1),
                          (2,2),
                          (2,2),
                          (1,2),
                          (2,1)])
        assert_equal(xy,xy_result)

    def test_node_degree_xy_directed(self):
        xy=sorted(mixing.node_degree_xy(self.D))
        xy_result=sorted([(2,1),
                          (2,3),
                          (1,3),
                          (1,3)])
        assert_equal(xy,xy_result)

    def test_node_degree_xy_multigraph(self):
        xy=sorted(mixing.node_degree_xy(self.M))
        xy_result=sorted([(2,3),
                          (2,3),
                          (3,2),
                          (3,2),
                          (2,3),
                          (3,2),
                          (1,2),
                          (2,1)])
        assert_equal(xy,xy_result)


    def test_node_degree_xy_selfloop(self):
        xy=sorted(mixing.node_degree_xy(self.S))
        xy_result=sorted([(2,2),
                          (2,2)])
        assert_equal(xy,xy_result)


    def test_degree_mixing_dict_undirected(self):
        d=mixing.degree_mixing_dict(self.P4)
        d_result={1:{2:2},
                  2:{1:2,2:2},
                  }
        assert_equal(d,d_result)

    def test_degree_mixing_dict_directed(self):
        d=mixing.degree_mixing_dict(self.D)
        print(d)
        d_result={1:{3:2},
                  2:{1:1,3:1},
                  3:{}
                  }
        assert_equal(d,d_result)

    def test_degree_mixing_dict_multigraph(self):
        d=mixing.degree_mixing_dict(self.M)
        d_result={1:{2:1},
                  2:{1:1,3:3},
                  3:{2:3}
                  }
        assert_equal(d,d_result)


class TestDegreeMixingMatrix(object):

    @classmethod
    def setupClass(cls):
        global np
        global npt
        try:
            import numpy as np
            import numpy.testing as npt

        except ImportError:
             raise SkipTest('NumPy not available.')
    
    def setUp(self):
        self.P4=networkx.path_graph(4)
        self.D=networkx.DiGraph() 
        self.D.add_edges_from([(0, 2), (0, 3), (1, 3), (2, 3)])
        self.M=networkx.MultiGraph() 
        self.M.add_path(list(range(4)))
        self.M.add_edge(0,1)
        self.S=networkx.Graph()
        self.S.add_edges_from([(0,0),(1,1)])



    def test_degree_mixing_matrix_undirected(self):
        a_result=np.array([[0,0,0],
                           [0,0,2],
                           [0,2,2]]
                          )
        a=mixing.degree_mixing_matrix(self.P4,normalized=False)
        npt.assert_equal(a,a_result)
        a=mixing.degree_mixing_matrix(self.P4)
        npt.assert_equal(a,a_result/float(a_result.sum()))

    def test_degree_mixing_matrix_directed(self):
        a_result=np.array([[0,0,0,0],
                           [0,0,0,2],
                           [0,1,0,1],
                           [0,0,0,0]]
                          )
        a=mixing.degree_mixing_matrix(self.D,normalized=False)
        npt.assert_equal(a,a_result)
        a=mixing.degree_mixing_matrix(self.D)
        npt.assert_equal(a,a_result/float(a_result.sum()))

    def test_degree_mixing_matrix_multigraph(self):
        a_result=np.array([[0,0,0,0],
                           [0,0,1,0],
                           [0,1,0,3],
                           [0,0,3,0]]
                          )
        a=mixing.degree_mixing_matrix(self.M,normalized=False)
        npt.assert_equal(a,a_result)
        a=mixing.degree_mixing_matrix(self.M)
        npt.assert_equal(a,a_result/float(a_result.sum()))


    def test_degree_mixing_matrix_selfloop(self):
        a_result=np.array([[0,0,0],
                           [0,0,0],
                           [0,0,2]]
                          )
        a=mixing.degree_mixing_matrix(self.S,normalized=False)
        npt.assert_equal(a,a_result)
        a=mixing.degree_mixing_matrix(self.S)
        npt.assert_equal(a,a_result/float(a_result.sum()))


    def test_degree_assortativity_undirected(self):
        r=mixing.degree_assortativity(self.P4)
        npt.assert_almost_equal(r,-1.0/2,decimal=4)

    def test_degree_assortativity_directed(self):
        r=mixing.degree_assortativity(self.D)
        npt.assert_almost_equal(r,-0.57735,decimal=4)

    def test_degree_assortativity_multigraph(self):
        r=mixing.degree_assortativity(self.M)
        npt.assert_almost_equal(r,-1.0/7.0,decimal=4)



class TestDegreeMixingMatrixPearsonr(object):
    @classmethod
    def setupClass(cls):
        global np
        global npt
        try:
            import numpy as np
            import numpy.testing as npt
        except ImportError:
             raise SkipTest('NumPy not available.')
        try:
            import scipy
            import scipy.stats
        except ImportError:
             raise SkipTest('SciPy not available.')

    def setUp(self):
        self.P4=networkx.path_graph(4)
        self.D=networkx.DiGraph() 
        self.D.add_edges_from([(0, 2), (0, 3), (1, 3), (2, 3)])
        self.M=networkx.MultiGraph() 
        self.M.add_path(list(range(4)))
        self.M.add_edge(0,1)
        self.S=networkx.Graph()
        self.S.add_edges_from([(0,0),(1,1)])

    def test_degree_assortativity_undirected(self):
        r=mixing.degree_pearsonr(self.P4)
        npt.assert_almost_equal(r,-1.0/2,decimal=4)

    def test_degree_assortativity_directed(self):
        r=mixing.degree_pearsonr(self.D)
        npt.assert_almost_equal(r,-0.57735,decimal=4)

    def test_degree_assortativity_multigraph(self):
        r=mixing.degree_pearsonr(self.M)
        npt.assert_almost_equal(r,-1.0/7.0,decimal=4)


