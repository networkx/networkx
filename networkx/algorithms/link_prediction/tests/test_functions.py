from nose.tools import *
import networkx as nx
from networkx.exception import *
import networkx.algorithms.link_prediction as lp


class TestCommonNeighbors():
    def setUp(self):
        self.K5 = nx.complete_graph(5)
        self.P3 = nx.path_graph(3)
        self.S4 = nx.star_graph(4)
        def test_func(G, node1, node2, expected):
            result = lp.functions.common_neighbors(G, node1, node2)
            assert result == expected
        self.test = test_func

    def test_K5(self):
        self.test(self.K5, 0, 1, 3)

    def test_P3(self):
        self.test(self.P3, 0, 2, 1)

    def test_S4(self):
        self.test(self.S4, 0, 0, 4)

    def test_custom(self):
        """Case of no common neighbors"""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, 0, 1, 0)


class TestResourceAllocationIndex():
    def setUp(self):
        self.K5 = nx.complete_graph(5)
        self.P3 = nx.path_graph(3)
        self.S4 = nx.star_graph(4)
        def test_func(G, node1, node2, expected):
            tol = 1e-7
            result = lp.functions.resource_allocation_index(G, node1, node2)
            assert abs(result - expected) < tol
        self.test = test_func

    def test_K5(self):
        self.test(self.K5, 0, 1, 0.75)

    def test_P3(self):
        self.test(self.P3, 0, 2, 0.5)

    def test_S4(self):
        self.test(self.S4, 0, 0, 4)

    def test_custom(self):
        """Case of no common neighbors"""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, 0, 1, 0)


class TestCNSoundarajanHopcroft():
    def setUp(self):
        self.K5 = nx.complete_graph(5)
        self.K5.node[0]['community'] = 0
        self.K5.node[1]['community'] = 0
        self.K5.node[2]['community'] = 0
        self.K5.node[3]['community'] = 0
        self.K5.node[4]['community'] = 1

        self.P3 = nx.path_graph(3)
        self.P3.node[0]['community'] = 0
        self.P3.node[1]['community'] = 1
        self.P3.node[2]['community'] = 0

        self.S4 = nx.star_graph(4)
        self.S4.node[0]['community'] = 0
        self.S4.node[1]['community'] = 1
        self.S4.node[2]['community'] = 1
        self.S4.node[3]['community'] = 0
        self.S4.node[4]['community'] = 0

        def test_func(G, node1, node2, expected):
            f = lp.functions.cn_soundarajan_hopcroft
            result = f(G, node1, node2)
            assert result == expected
        self.test = test_func

    def test_K5(self):
        self.test(self.K5, 0, 1, 5)

    def test_P3(self):
        self.test(self.P3, 0, 2, 1)

    def test_S4(self):
        self.test(self.S4, 0, 0, 6)

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
        self.test(G, 0, 1, 3)


class TestRAIndexSoundarajanHopcroft():
    def setUp(self):
        self.K5 = nx.complete_graph(5)
        self.K5.node[0]['community'] = 0
        self.K5.node[1]['community'] = 0
        self.K5.node[2]['community'] = 0
        self.K5.node[3]['community'] = 0
        self.K5.node[4]['community'] = 1

        self.P3 = nx.path_graph(3)
        self.P3.node[0]['community'] = 0
        self.P3.node[1]['community'] = 1
        self.P3.node[2]['community'] = 0

        self.S4 = nx.star_graph(4)
        self.S4.node[0]['community'] = 0
        self.S4.node[1]['community'] = 1
        self.S4.node[2]['community'] = 1
        self.S4.node[3]['community'] = 0
        self.S4.node[4]['community'] = 0

        def test_func(G, node1, node2, expected):
            tol = 1e-7
            f = lp.functions.ra_index_soundarajan_hopcroft
            result = f(G, node1, node2)
            assert abs(result - expected) < tol
        self.test = test_func

    def test_K5(self):
        self.test(self.K5, 0, 1, 0.5)

    def test_P3(self):
        self.test(self.P3, 0, 2, 0)

    def test_S4(self):
        self.test(self.S4, 0, 0, 2)

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
        self.test(G, 0, 1, 3)
