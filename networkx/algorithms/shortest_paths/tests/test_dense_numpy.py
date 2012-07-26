#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx as nx

class TestFloydNumpy(object):
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

    def test_cycle_numpy(self):
        dist = nx.floyd_warshall_numpy(nx.cycle_graph(7))
        assert_equal(dist[0,3],3)
        assert_equal(dist[0,4],3)

    def test_weighted_numpy(self):
        XG3=nx.Graph()
        XG3.add_weighted_edges_from([ [0,1,2],[1,2,12],[2,3,1],
                                      [3,4,5],[4,5,1],[5,0,10] ])
        dist = nx.floyd_warshall_numpy(XG3)
        assert_equal(dist[0,3],15)

    def test_weighted_numpy(self):
        XG4=nx.Graph()
        XG4.add_weighted_edges_from([ [0,1,2],[1,2,2],[2,3,1],
                                      [3,4,1],[4,5,1],[5,6,1],
                                      [6,7,1],[7,0,1] ])
        dist = nx.floyd_warshall_numpy(XG4)
        assert_equal(dist[0,2],4)

    def test_weight_parameter_numpy(self):
        XG4 = nx.Graph()
        XG4.add_edges_from([ (0, 1, {'heavy': 2}), (1, 2, {'heavy': 2}),
                             (2, 3, {'heavy': 1}), (3, 4, {'heavy': 1}),
                             (4, 5, {'heavy': 1}), (5, 6, {'heavy': 1}),
                             (6, 7, {'heavy': 1}), (7, 0, {'heavy': 1}) ])
        dist = nx.floyd_warshall_numpy(XG4, weight='heavy')
        assert_equal(dist[0, 2], 4)

    def test_directed_cycle_numpy(self):
        G = nx.DiGraph()
        G.add_cycle([0,1,2,3])
        pred,dist = nx.floyd_warshall_predecessor_and_distance(G)
        D = nx.utils.dict_to_numpy_array(dist)
        assert_equal(nx.floyd_warshall_numpy(G),D)
