from nose import SkipTest
from nose.tools import raises

import networkx as nx

class TestConnectivityPairs(object):
    numpy=1 # nosetests attribute, use nosetests -a 'not numpy' to skip test
    @classmethod
    def setupClass(cls):
        global itertools
        import itertools
        global numpy
        global assert_equal
        global assert_almost_equal

        try:
            import numpy
            from numpy.testing import assert_equal,assert_almost_equal
        except ImportError:
             raise SkipTest('NumPy not available.')

    def test_all_pairs_connectivity(self, nodelist=[0,1,2,3]):
        G = nx.Graph()
        nodes = [0,1,2,3]
        G.add_path(nodes)
        A = numpy.zeros((4,4), dtype=int)
        for u,v in itertools.combinations(nodes,2):
            A[u][v] = nx.node_connectivity(G,u,v)
            A[v][u] = nx.node_connectivity(G,u,v)
        C = nx.all_pairs_node_connectivity_matrix(G)
        assert_equal(A,C)

    def test_all_pairs_connectivity_directed(self):
        G = nx.DiGraph()
        nodes = [0,1,2,3]
        G.add_path(nodes)
        A = numpy.zeros((4,4), dtype=int)
        for u,v in itertools.combinations(nodes,2):
            A[u][v] = nx.node_connectivity(G,u,v)
        C = nx.all_pairs_node_connectivity_matrix(G)
        assert_equal(A,C)


    @raises(nx.NetworkXError)
    def test_all_pairs_connectivity_empty(self):
        C = nx.all_pairs_node_connectivity_matrix(nx.Graph())

    @raises(nx.NetworkXError)
    def test_all_pairs_connectivity_nodelist(self):
        G = nx.path_graph(4)
        C = nx.all_pairs_node_connectivity_matrix(G, nodelist=[1,2,3,1])
