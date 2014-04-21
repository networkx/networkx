from nose.tools import *
import networkx as nx
import networkx.algorithms.link_prediction as lp


class TestPredictCommonNeighbors():
    def setUp(self):
        self.P4 = nx.path_graph(4)
        self.S4 = nx.star_graph(4)
        def test_func(G, expected):
            result = lp.predict.predict_common_neighbors(G)
            for (u, v) in expected:
                assert (u, v) in result or (v, u) in result
                if (u, v) in result:
                    assert result[u, v] == expected[u, v]
                else:
                    assert result[v, u] == expected[v, u]
        self.test = test_func

    def test_P4(self):
        expected = {(0, 2): 1, (0, 3): 0, (1, 3): 1}
        self.test(self.P4, expected)

    def test_S4(self):
        expected = {
            (1, 2): 1, (1, 3): 1, (1, 4): 1, (2, 3): 1, (2, 4): 1,
            (3, 4): 1
        }
        self.test(self.S4, expected)


class TestPredictResourceAllocationIndex():
    def setUp(self):
        self.P4 = nx.path_graph(4)
        self.S4 = nx.star_graph(4)
        def test_func(G, expected):
            tol = 1e-7
            result = lp.predict.predict_resource_allocation_index(G)
            for (u, v) in expected:
                assert (u, v) in result or (v, u) in result
                if (u, v) in result:
                    assert abs(result[u, v] - expected[u, v]) < tol
                else:
                    assert abs(result[v, u] - expected[v, u]) < tol
        self.test = test_func

    def test_P4(self):
        expected = {(0, 2): 0.5, (0, 3): 0, (1, 3): 0.5}
        self.test(self.P4, expected)

    def test_S4(self):
        expected = {
            (1, 2): 0.25, (1, 3): 0.25, (1, 4): 0.25, (2, 3): 0.25,
            (2, 4): 0.25, (3, 4): 0.25
        }
        self.test(self.S4, expected)