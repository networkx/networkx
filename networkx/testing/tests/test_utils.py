from nose.tools import *
import networkx as nx
from networkx.testing import *

# thanks to numpy for this (numpy/testing/test_utils.py)
class _GenericTest(object):
    def _test_equal(self, a, b):
        self._assert_func(a, b)

    def _test_not_equal(self, a, b):
        try:
            self._assert_func(a, b)
            passed = True
        except AssertionError:
            pass
        else:
            raise AssertionError("a and b are found equal but are not")


class TestEdgesEqual(_GenericTest):
    def setUp(self):
        self._assert_func = assert_edges_equal

    def test_edges_equal(self):
        e1 = [(1,2),(5,4)]
        e2 = [(4,5),(1,2)]
        self._test_equal(e1,e2)

    def test_edges_not_equal(self):
        e1 = [(1,2),(5,4)]
        e2 = [(4,5),(1,3)]
        self._test_not_equal(e1,e2)

    def test_edges_with_data_equal(self):
        G = nx.MultiGraph()
        G.add_path([0,1,2],weight=1)
        H = nx.MultiGraph()
        H.add_path([0,1,2],weight=1)
        self._test_equal(G.edges(data=True, keys=True),
                         H.edges(data=True, keys=True))

    def test_edges_with_data_not_equal(self):
        G = nx.MultiGraph()
        G.add_path([0,1,2],weight=1)
        H = nx.MultiGraph()
        H.add_path([0,1,2],weight=2)
        self._test_not_equal(G.edges(data=True, keys=True),
                             H.edges(data=True, keys=True))
