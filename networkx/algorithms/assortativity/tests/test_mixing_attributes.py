#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest

import networkx
import networkx.algorithms.mixing as mixing


class TestAttributeMixing(object):
    
    def setUp(self):
        G=networkx.Graph() 
        G.add_nodes_from([0,1],fish='one')
        G.add_nodes_from([2,3],fish='two')
        G.add_nodes_from([4],fish='red')
        G.add_nodes_from([5],fish='blue')
        G.add_edges_from([(0,1),(2,3),(0,4),(2,5)])
        self.G=G

        D=networkx.DiGraph() 
        D.add_nodes_from([0,1],fish='one')
        D.add_nodes_from([2,3],fish='two')
        D.add_nodes_from([4],fish='red')
        D.add_nodes_from([5],fish='blue')
        D.add_edges_from([(0,1),(2,3),(0,4),(2,5)])
        self.D=D

        M=networkx.MultiGraph() 
        M.add_nodes_from([0,1],fish='one')
        M.add_nodes_from([2,3],fish='two')
        M.add_nodes_from([4],fish='red')
        M.add_nodes_from([5],fish='blue')
        M.add_edges_from([(0,1),(0,1),(2,3)])
        self.M=M

        S=networkx.Graph()
        S.add_nodes_from([0,1],fish='one')
        S.add_nodes_from([2,3],fish='two')
        S.add_nodes_from([4],fish='red')
        S.add_nodes_from([5],fish='blue')
        S.add_edge(0,0)
        S.add_edge(2,2)
        self.S=S

    def test_node_attribute_xy_undirected(self):
        attrxy=sorted(mixing.node_attribute_xy(self.G,'fish'))
        attrxy_result=sorted([('one','one'),
                              ('one','one'),
                              ('two','two'),
                              ('two','two'),
                              ('one','red'),
                              ('red','one'),
                              ('blue','two'),
                              ('two','blue')
                              ])
        assert_equal(attrxy,attrxy_result)

    def test_node_attribute_xy_directed(self):
        attrxy=sorted(mixing.node_attribute_xy(self.D,'fish'))
        attrxy_result=sorted([('one','one'),
                              ('two','two'),
                              ('one','red'),
                              ('two','blue')
                              ])
        assert_equal(attrxy,attrxy_result)

    def test_node_attribute_xy_multigraph(self):
        attrxy=sorted(mixing.node_attribute_xy(self.M,'fish'))
        attrxy_result=[('one','one'),
                       ('one','one'),
                       ('one','one'),
                       ('one','one'),
                       ('two','two'),
                       ('two','two')
                       ]
        assert_equal(attrxy,attrxy_result)

    def test_node_attribute_xy_selfloop(self):
        attrxy=sorted(mixing.node_attribute_xy(self.S,'fish'))
        attrxy_result=[('one','one'),
                       ('two','two')
                       ]
        assert_equal(attrxy,attrxy_result)

    def test_attribute_mixing_dict_undirected(self):
        d=mixing.attribute_mixing_dict(self.G,'fish')
        d_result={'one':{'one':2,'red':1},
                  'two':{'two':2,'blue':1},
                  'red':{'one':1},
                  'blue':{'two':1}
                  }
        assert_equal(d,d_result)

    def test_attribute_mixing_dict_directed(self):
        d=mixing.attribute_mixing_dict(self.D,'fish')
        d_result={'one':{'one':1,'red':1},
                  'two':{'two':1,'blue':1},
                  'red':{},
                  'blue':{}
                  }
        assert_equal(d,d_result)


    def test_attribute_mixing_dict_multigraph(self):
        d=mixing.attribute_mixing_dict(self.M,'fish')
        d_result={'one':{'one':4},
                  'two':{'two':2},
                  }
        assert_equal(d,d_result)



class TestAttributeMixingMatrix(TestAttributeMixing):
    @classmethod
    def setupClass(cls):
        global np
        global npt
        try:
            import numpy as np
            import numpy.testing as npt

        except ImportError:
             raise SkipTest('NumPy not available.')

    def test_attribute_mixing_matrix_undirected(self):
        mapping={'one':0,'two':1,'red':2,'blue':3}
        a_result=np.array([[2,0,1,0],
                           [0,2,0,1],
                           [1,0,0,0],
                           [0,1,0,0]]
                          )
        a=mixing.attribute_mixing_matrix(self.G,'fish',
                                         mapping=mapping,
                                         normalized=False)
        npt.assert_equal(a,a_result)
        a=mixing.attribute_mixing_matrix(self.G,'fish',
                                         mapping=mapping)
        npt.assert_equal(a,a_result/float(a_result.sum()))

    def test_attribute_mixing_matrix_directed(self):
        mapping={'one':0,'two':1,'red':2,'blue':3}
        a_result=np.array([[1,0,1,0],
                           [0,1,0,1],
                           [0,0,0,0],
                           [0,0,0,0]]
                          )
        a=mixing.attribute_mixing_matrix(self.D,'fish',
                                         mapping=mapping,
                                         normalized=False)
        npt.assert_equal(a,a_result)
        a=mixing.attribute_mixing_matrix(self.D,'fish',
                                         mapping=mapping)
        npt.assert_equal(a,a_result/float(a_result.sum()))

    def test_attribute_mixing_matrix_multigraph(self):
        mapping={'one':0,'two':1,'red':2,'blue':3}
        a_result=np.array([[4,0,0,0],
                           [0,2,0,0],
                           [0,0,0,0],
                           [0,0,0,0]]
                          )
        a=mixing.attribute_mixing_matrix(self.M,'fish',
                                         mapping=mapping,
                                         normalized=False)
        npt.assert_equal(a,a_result)
        a=mixing.attribute_mixing_matrix(self.M,'fish',
                                         mapping=mapping)
        npt.assert_equal(a,a_result/float(a_result.sum()))


    def test_attribute_assortativity_undirected(self):
        r=mixing.attribute_assortativity(self.G,'fish')
        assert_equal(r,6.0/22.0)

    def test_attribute_assortativity_directed(self):
        r=mixing.attribute_assortativity(self.D,'fish')
        assert_equal(r,1.0/3.0)

    def test_attribute_assortativity_multigraph(self):
        r=mixing.attribute_assortativity(self.M,'fish')
        assert_equal(r,1.0)

    def test_attribute_assortativity_coefficient(self):
        # from "Mixing patterns in networks"
        a=np.array([[0.258,0.016,0.035,0.013],
                    [0.012,0.157,0.058,0.019],
                    [0.013,0.023,0.306,0.035],
                    [0.005,0.007,0.024,0.016]])
        r=mixing.attribute_assortativity_coefficient(a)
        npt.assert_almost_equal(r,0.623,decimal=3)

    def test_attribute_assortativity_coefficient(self):
        a=np.array([[0.18,0.02,0.01,0.03],
                    [0.02,0.20,0.03,0.02],
                    [0.01,0.03,0.16,0.01],
                    [0.03,0.02,0.01,0.22]])

        r=mixing.attribute_assortativity_coefficient(a)
        npt.assert_almost_equal(r,0.68,decmial=2)

    def test_attribute_assortativity_coefficient(self):
        a=np.array([[50,50,0],[50,50,0],[0,0,2]])
        r=mixing.attribute_assortativity_coefficient(a)
        npt.assert_almost_equal(r,0.029,decimal=3)


