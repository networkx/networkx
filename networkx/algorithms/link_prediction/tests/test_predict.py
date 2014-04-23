from nose.tools import *
import networkx as nx
import networkx.algorithms.link_prediction.predict as pred
from networkx.exception import *


class TestPredictCommonNeighbors():
    def setUp(self):
        def test_func(G, expected):
            result = list(pred.predict_common_neighbors(G))
            assert len(result) == len(expected)
            for (u, v, p) in expected:
                assert (u, v, p) in result or (v, u, p) in result
        self.test = test_func

    def test_P4(self):
        G = nx.path_graph(4)
        expected = [(0, 2, 1), (0, 3, 0), (1, 3, 1)]
        self.test(G, expected)

    def test_S4(self):
        G = nx.star_graph(4)
        expected = [
            (1, 2, 1), (1, 3, 1), (1, 4, 1), (2, 3, 1), (2, 4, 1), (3, 4, 1)
        ]
        self.test(G, expected)


class TestPredictResourceAllocationIndex():
    def setUp(self):
        def test_func(G, expected):
            result = list(pred.predict_resource_allocation_index(G))
            assert len(result) == len(expected)
            for (u, v, p) in expected:
                assert (u, v, p) in result or (v, u, p) in result
        self.test = test_func

    def test_P4(self):
        G = nx.path_graph(4)
        expected = [(0, 2, 0.5), (0, 3, 0), (1, 3, 0.5)]
        self.test(G, expected)

    def test_S4(self):
        G = nx.star_graph(4)
        expected = [
            (1, 2, 0.25), (1, 3, 0.25), (1, 4, 0.25), (2, 3, 0.25),
            (2, 4, 0.25), (3, 4, 0.25)
        ]
        self.test(G, expected)


class TestPredictCNSoundarajanHopcroft():
    def setUp(self):
        def test_func(G, expected):
            result = list(pred.predict_cn_soundarajan_hopcroft(G))
            assert len(result) == len(expected)
            for (u, v, p) in expected:
                assert (u, v, p) in result or (v, u, p) in result
        self.test = test_func

    def test_P4(self):
        G = nx.path_graph(4)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        expected = [(0, 2, 2), (0, 3, 0), (1, 3, 2)]
        self.test(G, expected)

    def test_S4(self):
        G = nx.star_graph(4)
        G.node[0]['community'] = 1
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        expected = [
            (1, 2, 2), (1, 3, 1), (1, 4, 1), (2, 3, 1), (2, 4, 1), (3, 4, 1)
        ]
        self.test(G, expected)


class TestPredictRAIndexSoundarajanHopcroft():
    def setUp(self):
        def test_func(G, expected):
            result = list(pred.predict_ra_index_soundarajan_hopcroft(G))
            assert len(result) == len(expected)
            for (u, v, p) in expected:
                assert (u, v, p) in result or (v, u, p) in result
        self.test = test_func

    def test_P4(self):
        G = nx.path_graph(4)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        expected = [(0, 2, 0.5), (0, 3, 0), (1, 3, 0.5)]
        self.test(G, expected)

    def test_S4(self):
        G = nx.star_graph(4)
        G.node[0]['community'] = 1
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        expected = [
            (1, 2, 0.25), (1, 3, 0), (1, 4, 0), (2, 3, 0), (2, 4, 0), (3, 4, 0)
        ]
        self.test(G, expected)


class TestPredictWithinInterCluster():
    def setUp(self):
        def test_func(G, delta, expected):
            result = list(pred.predict_within_inter_cluster(G, delta))
            assert len(result) == len(expected)
            for (u, v, p) in expected:
                assert (u, v, p) in result or (v, u, p) in result
        self.test = test_func

    def test_P4(self):
        G = nx.path_graph(4)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        G.node[3]['community'] = 0
        delta = 0.001
        expected = [(0, 2, 1 / delta), (0, 3, 0), (1, 3, 1 / delta)]
        self.test(G, delta, expected)

    def test_S4(self):
        G = nx.star_graph(4)
        G.node[0]['community'] = 1
        G.node[1]['community'] = 1
        G.node[2]['community'] = 1
        G.node[3]['community'] = 0
        G.node[4]['community'] = 0
        delta = 0.001
        expected = [
            (1, 2, 1 / delta), (1, 3, 0), (1, 4, 0), (2, 3, 0), (2, 4, 0),
            (3, 4, 0)
        ]
        self.test(G, delta, expected)

    @raises(NetworkXAlgorithmError)
    def test_custom1(self):
        """Case of delta equals zero"""
        G = nx.star_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        pred.predict_within_inter_cluster(G, 0)

    @raises(NetworkXAlgorithmError)
    def test_custom2(self):
        """Case of delta less than zero"""
        G = nx.star_graph(3)
        G.node[0]['community'] = 0
        G.node[1]['community'] = 0
        G.node[2]['community'] = 0
        pred.predict_within_inter_cluster(G, -1.2)
