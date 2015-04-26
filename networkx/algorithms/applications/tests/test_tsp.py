from nose.tools import *
import networkx as nx


def _setUp(self):
    self.unsymmetric = nx.DiGraph()
    self.unsymmetric.add_weighted_edges_from({('A', 'B', 3),
                                              ('A', 'C', 17), ('A', 'D', 14), ('B', 'A', 3),
                                              ('B', 'C', 12), ('B', 'D', 16), ('C', 'A', 13),
                                              ('C', 'B', 12), ('C', 'D', 4), ('D', 'A', 14),
                                              ('D', 'B', 15), ('D', 'C', 2)})
    self.unweightedUG = nx.complete_graph(5, nx.Graph())
    self.unweightedDG = nx.complete_graph(5, nx.DiGraph())
    self.notCompletedUG = nx.Graph()
    self.notCompletedUG.add_weighted_edges_from({(0, 1, 1), (1, 2, 3)})
    self.notCompletedDG = nx.DiGraph()
    self.notCompletedDG.add_weighted_edges_from({(0, 1, 1), (1, 2, 3)})
    self.unsymmetricSelfLoops = nx.DiGraph()
    self.unsymmetricSelfLoops.add_weighted_edges_from({('A', 'B', 3),
                                                       ('A', 'C', 17), ('A', 'D', 14), ('B', 'A', 3),
                                                       ('B', 'C', 12), ('B', 'D', 16), ('C', 'A', 13),
                                                       ('C', 'B', 12), ('C', 'D', 4), ('D', 'A', 14),
                                                       ('D', 'B', 15), ('D', 'C', 2), ('A', 'A', 2),
                                                       ('B', 'B', 13), ('C', 'C', 2), ('D', 'D', 3)})


def validate_solution(comp, cost, exp_comp, exp_cost):
    assert_equal(comp, exp_comp)
    assert_equal(cost, exp_cost)


class TestGreedyTSP:

    setUp = _setUp

    def test_greedy(self):
        output = nx.greedy_tsp(self.unsymmetric, 'D')
        validate_solution(output[0], output[1], [('D', 'C'), ('C', 'B'), ('B', 'A')], 17.0)
        output2 = nx.greedy_tsp(self.unsymmetricSelfLoops, 'D')
        validate_solution(output2[0], output2[1], [('D', 'C'), ('C', 'B'), ('B', 'A')], 17.0)

    def test_not_completed_graph(self):
        assert_raises(nx.NetworkXError, nx.greedy_tsp, self.notCompletedUG, 0)
        assert_raises(nx.NetworkXError, nx.greedy_tsp, self.notCompletedDG, 0)

    def test_not_weighted_graph(self):
        assert_raises(nx.NetworkXError, nx.greedy_tsp, self.unweightedUG, 0)
        assert_raises(nx.NetworkXError, nx.greedy_tsp, self.unweightedDG, 0)
