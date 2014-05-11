from nose.tools import *

import networkx as nx
from networkx.exception import *
import networkx.algorithms.link_prediction as lp


class TestResourceAllocationIndex():
    def setUp(self):
        self.func = lp.resource_allocation_index
        def test_func(G, u, v, expected):
            tol = 1e-7
            result = self.func(G, u, v)
            assert_true(abs(result - expected) < tol)
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        self.test(G, 0, 1, 0.75)

    def test_P3(self):
        G = nx.path_graph(3)
        self.test(G, 0, 2, 0.5)

    def test_S4(self):
        G = nx.star_graph(4)
        self.test(G, 1, 2, 0.25)

    @raises(NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, 0, 2)

    @raises(NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, 0, 2)

    @raises(NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, 0, 2)

    def test_custom1(self):
        """Case of no common neighbors."""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, 0, 1, 0)

    def test_custom2(self):
        """Case of equal nodes."""
        G = nx.complete_graph(4)
        self.test(G, 0, 0, 1)


class TestJaccardCoefficient():
    def setUp(self):
        self.func = lp.jaccard_coefficient
        def test_func(G, u, v, expected):
            tol = 1e-7
            result = self.func(G, u, v)
            assert_true(abs(result - expected) < tol)
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        self.test(G, 0, 1, 0.6)

    def test_P4(self):
        G = nx.path_graph(4)
        self.test(G, 0, 2, 0.5)

    @raises(NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, 0, 2)

    @raises(NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, 0, 2)

    @raises(NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, 0, 2)

    @raises(NetworkXError)
    def test_nonexistent_node1(self):
        G = nx.complete_graph(5)
        self.func(G, 'A', 0)

    @raises(NetworkXError)
    def test_nonexistent_node2(self):
        G = nx.complete_graph(5)
        self.func(G, 0, 'A')

    def test_no_common_neighbor(self):
        G = nx.Graph()
        G.add_edges_from([(0, 1), (2, 3)])
        self.test(G, 0, 2, 0)

    def test_isolated_nodes(self):
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, 0, 1, 0)


class TestCNSoundarajanHopcroft():
    def setUp(self):
        self.func = lp.cn_soundarajan_hopcroft
        def test_func(G, u, v, expected):
            result = self.func(G, u, v)
            assert_equal(result, expected)
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 1
        self.test(G, 0, 1, 5)

    def test_P3(self):
        G = nx.path_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 0
        self.test(G, 0, 2, 1)

    def test_S4(self):
        G = nx.star_graph(4)
        G.node[0]['community'] = 1
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, 1, 2, 2)

    @raises(NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 2)

    @raises(NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 2)

    @raises(NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 2)

    def test_custom1(self):
        """Case of no common neighbors."""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        self.test(G, 0, 1, 0)

    def test_custom2(self):
        """Case of equal nodes."""
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.test(G, 0, 0, 4)

    def test_custom3(self):
        """Case of different community."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 1
        self.test(G, 0, 3, 2)

    @raises(NetworkXAlgorithmError)
    def test_custom4(self):
        """Case of no community information."""
        G = nx.complete_graph(5)
        self.func(G, 0, 1)

    @raises(NetworkXAlgorithmError)
    def test_custom5(self):
        """Case of insufficient community information."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[3]['community'] = 0
        self.func(G, 0, 3)

    def test_custom6(self):
        """Case of sufficient community information."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, 1, 4, 4)


class TestRAIndexSoundarajanHopcroft():
    def setUp(self):
        self.func = lp.ra_index_soundarajan_hopcroft
        def test_func(G, u, v, expected):
            tol = 1e-7
            result = self.func(G, u, v)
            assert_true(abs(result - expected) < tol)
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 1
        self.test(G, 0, 1, 0.5)

    def test_P3(self):
        G = nx.path_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 0
        self.test(G, 0, 2, 0)

    def test_S4(self):
        G = nx.star_graph(4)
        G.node[0]['community'] = 1
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, 1, 2, 0.25)

    @raises(NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 2)

    @raises(NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 2)

    @raises(NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 2)

    def test_custom1(self):
        """Case of no common neighbors."""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        self.test(G, 0, 1, 0)

    def test_custom2(self):
        """Case of equal nodes."""
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.test(G, 0, 0, 1)

    def test_custom3(self):
        """Case of different community."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 1
        self.test(G, 0, 3, 0)

    @raises(NetworkXAlgorithmError)
    def test_custom4(self):
        """Case of no community information."""
        G = nx.complete_graph(5)
        self.func(G, 0, 1)

    @raises(NetworkXAlgorithmError)
    def test_custom5(self):
        """Case of insufficient community information."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[3]['community'] = 0
        self.func(G, 0, 3)

    def test_custom6(self):
        """Case of sufficient community information."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, 1, 4, 1)


class TestWithinInterCluster():
    def setUp(self):
        self.delta = 0.001
        self.func = lp.within_inter_cluster
        def test_func(G, u, v, expected):
            tol = 1e-7
            result = self.func(G, u, v, self.delta)
            assert_true(abs(result - expected) < tol)
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 1
        self.test(G, 0, 1, 2 / (1 + self.delta))

    def test_P3(self):
        G = nx.path_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 0
        self.test(G, 0, 2, 0)

    def test_S4(self):
        G = nx.star_graph(4)
        G.node[0]['community'] = 1
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, 1, 2, 1 / self.delta)

    @raises(NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 2, self.delta)

    @raises(NetworkXNotImplemented)
    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 2, self.delta)

    @raises(NetworkXNotImplemented)
    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 2, self.delta)

    def test_custom1(self):
        """Case of no common neighbors."""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        self.test(G, 0, 1, 0)

    def test_custom2(self):
        """Case of equal nodes."""
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.test(G, 0, 0, 2 / self.delta)

    def test_custom3(self):
        """Case of different community."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 1
        self.test(G, 0, 3, 0)

    def test_custom4(self):
        """Case of no inter-cluster neighbor."""
        G = nx.complete_graph(4)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        self.test(G, 0, 3, 2 / self.delta)

    @raises(NetworkXAlgorithmError)
    def test_custom5(self):
        """Case of no community information."""
        G = nx.complete_graph(5)
        self.func(G, 0, 1)

    @raises(NetworkXAlgorithmError)
    def test_custom6(self):
        """Case of insufficient community information."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[3]['community'] = 0
        self.func(G, 0, 3)

    def test_custom7(self):
        """Case of sufficient community information."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, 1, 4, 2 / self.delta)

    @raises(NetworkXAlgorithmError)
    def test_custom8(self):
        """Case of delta equals zero."""
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 1, 0)

    @raises(NetworkXAlgorithmError)
    def test_custom9(self):
        """Case of delta less than zero."""
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 1, -0.5)
