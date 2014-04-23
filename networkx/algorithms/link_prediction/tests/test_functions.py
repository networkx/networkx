from nose.tools import *
import networkx as nx
from networkx.exception import *
import networkx.algorithms.link_prediction.functions as lpfunc


class TestCommonNeighbors():
    def setUp(self):
        self.func = lpfunc.common_neighbors
        def test_func(G, node1, node2, expected):
            result = self.func(G, node1, node2)
            assert result == expected
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        self.test(G, 0, 1, 3)

    def test_P3(self):
        G = nx.path_graph(3)
        self.test(G, 0, 2, 1)

    def test_S4(self):
        G = nx.star_graph(4)
        self.test(G, 0, 0, 4)

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

    def test_custom(self):
        """Case of no common neighbors"""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, 0, 1, 0)


class TestResourceAllocationIndex():
    def setUp(self):
        self.func = lpfunc.resource_allocation_index
        def test_func(G, node1, node2, expected):
            tol = 1e-7
            result = self.func(G, node1, node2)
            assert abs(result - expected) < tol
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        self.test(G, 0, 1, 0.75)

    def test_P3(self):
        G = nx.path_graph(3)
        self.test(G, 0, 2, 0.5)

    def test_S4(self):
        G = nx.star_graph(4)
        self.test(G, 0, 0, 4)

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

    def test_custom(self):
        """Case of no common neighbors"""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, 0, 1, 0)


class TestCNSoundarajanHopcroft():
    def setUp(self):
        self.func = lpfunc.cn_soundarajan_hopcroft
        def test_func(G, node1, node2, expected):
            result = self.func(G, node1, node2)
            assert result == expected
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
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, 0, 0, 6)

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
        """Case of no common neighbors"""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        self.test(G, 0, 1, 0)

    def test_custom2(self):
        """Case of different community"""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 1
        self.test(G, 0, 3, 2)

    @raises(NetworkXAlgorithmError)
    def test_custom3(self):
        """Case of no community information"""
        G = nx.complete_graph(5)
        self.func(G, 0, 1)


class TestRAIndexSoundarajanHopcroft():
    def setUp(self):
        self.func = lpfunc.ra_index_soundarajan_hopcroft
        def test_func(G, node1, node2, expected):
            tol = 1e-7
            result = self.func(G, node1, node2)
            assert abs(result - expected) < tol
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
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, 0, 0, 2)

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
        """Case of no common neighbors"""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        self.test(G, 0, 1, 0)

    def test_custom2(self):
        """Case of different community"""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 1
        self.test(G, 0, 3, 0)

    @raises(NetworkXAlgorithmError)
    def test_custom3(self):
        """Case of no community information"""
        G = nx.complete_graph(5)
        self.func(G, 0, 1)


class TestWithinInterCluster():
    def setUp(self):
        self.delta = 0.001
        self.func = lpfunc.within_inter_cluster
        def test_func(G, node1, node2, expected):
            tol = 1e-7
            result = self.func(G, node1, node2, self.delta)
            assert abs(result - expected) < tol
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
        G.node[0]['community'] = 0
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        self.test(G, 0, 0, 2 / (2 + self.delta))

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
        """Case of no common neighbors"""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        self.test(G, 0, 1, 0)

    def test_custom2(self):
        """Case of different community"""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)])
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 1
        self.test(G, 0, 3, 0)

    def test_custom3(self):
        """Case of no inter-cluster neighbor"""
        G = nx.complete_graph(4)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        self.test(G, 0, 3, 2 / self.delta)

    @raises(NetworkXAlgorithmError)
    def test_custom4(self):
        """Case of no community information"""
        G = nx.complete_graph(5)
        self.func(G, 0, 1)

    @raises(NetworkXAlgorithmError)
    def test_custom5(self):
        """Case of delta equals zero"""
        G = nx.complete_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        self.func(G, 0, 1, 0)
