from nose.tools import *
import networkx as nx
from networkx.testing import *

# thanks to numpy for this GenericTest class (numpy/testing/test_utils.py)
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


class TestNodesEqual(_GenericTest):
    def setUp(self):
        self._assert_func = assert_nodes_equal

    def test_nodes_equal(self):
        a = [1,2,5,4]
        b = [4,5,1,2]
        self._test_equal(a,b)

    def test_nodes_not_equal(self):
        a = [1,2,5,4]
        b = [4,5,1,3]
        self._test_not_equal(a,b)

    def test_nodes_with_data_equal(self):
        G = nx.Graph()
        G.add_nodes_from([1,2,3],color='red')
        H = nx.Graph()
        H.add_nodes_from([1,2,3],color='red')
        self._test_equal(G.nodes(data=True), H.nodes(data=True))

    def test_edges_with_data_not_equal(self):
        G = nx.Graph()
        G.add_nodes_from([1,2,3],color='red')
        H = nx.Graph()
        H.add_nodes_from([1,2,3],color='blue')
        self._test_not_equal(G.nodes(data=True), H.nodes(data=True))


class TestEdgesEqual(_GenericTest):
    def setUp(self):
        self._assert_func = assert_edges_equal

    def test_edges_equal(self):
        a = [(1,2),(5,4)]
        b = [(4,5),(1,2)]
        self._test_equal(a,b)

    def test_edges_not_equal(self):
        a = [(1,2),(5,4)]
        b = [(4,5),(1,3)]
        self._test_not_equal(a,b)

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

class TestGraphsEqual(_GenericTest):
    def setUp(self):
        self._assert_func = assert_graphs_equal

    def test_graphs_equal(self):
        G = nx.path_graph(4)
        H = nx.Graph()
        H.add_path(range(4))
        H.name='path_graph(4)'
        self._test_equal(G,H)

    def test_digraphs_equal(self):
        G = nx.path_graph(4, create_using=nx.DiGraph())
        H = nx.DiGraph()
        H.add_path(range(4))
        H.name='path_graph(4)'
        self._test_equal(G,H)

    def test_multigraphs_equal(self):
        G = nx.path_graph(4, create_using=nx.MultiGraph())
        H = nx.MultiGraph()
        H.add_path(range(4))
        H.name='path_graph(4)'
        self._test_equal(G,H)

    def test_multigraphs_equal(self):
        G = nx.path_graph(4, create_using=nx.MultiDiGraph())
        H = nx.MultiDiGraph()
        H.add_path(range(4))
        H.name='path_graph(4)'
        self._test_equal(G,H)

    def test_graphs_not_equal(self):
        G = nx.path_graph(4)
        H = nx.Graph()
        H.add_cycle(range(4))
        self._test_not_equal(G,H)

    def test_graphs_not_equal2(self):
        G = nx.path_graph(4)
        H = nx.Graph()
        H.add_path(range(3))
        H.name='path_graph(4)'
        self._test_not_equal(G,H)

    def test_graphs_not_equal3(self):
        G = nx.path_graph(4)
        H = nx.Graph()
        H.add_path(range(4))
        H.name='path_graph(foo)'
        self._test_not_equal(G,H)
