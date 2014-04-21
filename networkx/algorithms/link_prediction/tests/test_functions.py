from nose.tools import *
import networkx as nx
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