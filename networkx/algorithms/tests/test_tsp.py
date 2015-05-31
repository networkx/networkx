from nose.tools import *
import networkx as nx


def _setUp(self):
    self.DG = nx.DiGraph()
    self.DG.add_weighted_edges_from({('A', 'B', 3),
                                     ('A', 'C', 17), ('A', 'D', 14), ('B', 'A', 3),
                                     ('B', 'C', 12), ('B', 'D', 16), ('C', 'A', 13),
                                     ('C', 'B', 12), ('C', 'D', 4), ('D', 'A', 14),
                                     ('D', 'B', 15), ('D', 'C', 2)})
    self.DG2 = nx.DiGraph()
    self.DG2.add_weighted_edges_from({('A', 'B', 3),
                                      ('A', 'C', 17), ('A', 'D', 14), ('B', 'A', 30),
                                      ('B', 'C', 2), ('B', 'D', 16), ('C', 'A', 33),
                                      ('C', 'B', 32), ('C', 'D', 34), ('D', 'A', 14),
                                      ('D', 'B', 15), ('D', 'C', 2)})
    self.unweightedUG = nx.complete_graph(5, nx.Graph())
    self.unweightedDG = nx.complete_graph(5, nx.DiGraph())
    self.notCompletedUG = nx.Graph()
    self.notCompletedUG.add_weighted_edges_from({(0, 1, 1), (1, 2, 3)})
    self.notCompletedDG = nx.DiGraph()
    self.notCompletedDG.add_weighted_edges_from({(0, 1, 1), (1, 2, 3)})
    self.UG = nx.Graph()
    self.UG.add_weighted_edges_from({('A', 'B', 3),
                                     ('A', 'C', 17), ('A', 'D', 14),
                                     ('B', 'C', 12), ('B', 'D', 16),
                                     ('C', 'D', 4)})
    self.UG2 = nx.Graph()
    self.UG2.add_weighted_edges_from({('A', 'B', 1),
                                      ('A', 'C', 15), ('A', 'D', 5),
                                      ('B', 'C', 16), ('B', 'D', 8),
                                      ('C', 'D', 3)})


def validate_solution(comp, cost, exp_comp, exp_cost):
    assert_equal(comp, exp_comp)
    assert_equal(cost, exp_cost)


def validate_symmetric_solution(comp, cost, exp_comp, exp_cost):
    assert_true(comp == exp_comp or comp == exp_comp[::-1])
    assert_equal(cost, exp_cost)


class TestGreedyTSP:
    setUp = _setUp

    def test_greedy(self):
        output = nx.greedy_tsp(self.DG, 'D')
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 31.0)

        output = nx.greedy_tsp(self.DG2, 'D')
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 78.0)

        output = nx.greedy_tsp(self.UG, 'D')
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 33.0)

        output = nx.greedy_tsp(self.UG2, 'D')
        validate_solution(output[0], output[1], ['D', 'C', 'A', 'B', 'D'], 27.0)

    def test_not_completed_graph(self):
        assert_raises(nx.NetworkXError, nx.greedy_tsp,
                      self.notCompletedUG, 0)
        assert_raises(nx.NetworkXError, nx.greedy_tsp,
                      self.notCompletedDG, 0)

    def test_not_weighted_graph(self):
        assert_raises(nx.NetworkXError, nx.greedy_tsp,
                      self.unweightedUG, 0)
        assert_raises(nx.NetworkXError, nx.greedy_tsp,
                      self.unweightedDG, 0)

    def test_two_nodes(self):
        G = nx.Graph()
        G.add_weighted_edges_from({(1, 2, 1)})
        cycle, cost = nx.greedy_tsp(G, 1)
        validate_solution(cycle, cost, [1, 2, 1], 2)


class TestSimulatedAnnealingTSP:
    setUp = _setUp

    def test_simulated_annealing(self):
        output = nx.simulated_annealing_tsp(self.DG, 'D')
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 31.0)

        output = nx.simulated_annealing_tsp(self.DG2, 'D')
        validate_solution(output[0], output[1], ['D', 'A', 'B', 'C', 'D'], 53.0)
        output = nx.simulated_annealing_tsp(self.DG2, 'D', move='1-0')
        validate_solution(output[0], output[1], ['D', 'A', 'B', 'C', 'D'], 53.0)
        output = nx.simulated_annealing_tsp(self.UG2, 'D')
        validate_symmetric_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 25.0)
        output = nx.simulated_annealing_tsp(self.UG2, 'D', move='1-0')
        validate_symmetric_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 25.0)

        initial_sol = ['D', 'B', 'A', 'C', 'D']
        output = nx.simulated_annealing_tsp(self.DG, 'D', cycle=initial_sol)
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 31.0)
        initial_sol = ['D', 'A', 'C', 'B', 'D']
        output = nx.simulated_annealing_tsp(self.DG, 'D', move='1-0',
                                            cycle=initial_sol)
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 31.0)

        output = nx.simulated_annealing_tsp(self.UG, 'D')
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 33.0)

    def test_not_completed_graph(self):
        assert_raises(nx.NetworkXError, nx.simulated_annealing_tsp,
                      self.notCompletedUG, 0, cycle=[])
        assert_raises(nx.NetworkXError, nx.simulated_annealing_tsp,
                      self.notCompletedDG, 0, cycle=[])

    def test_not_weighted_graph(self):
        assert_raises(nx.NetworkXError, nx.simulated_annealing_tsp,
                      self.unweightedUG, 0, cycle=[])
        assert_raises(nx.NetworkXError, nx.simulated_annealing_tsp,
                      self.unweightedDG, 0, cycle=[])

    def test_simulated_annealing_fails(self):
        output = nx.simulated_annealing_tsp(self.DG2, 'D', move='1-0', a=1,
                                            iterations=1, tolerance=1)
        assert_true(output[1] > 53.0)

        initial_sol = ['D', 'A', 'B', 'C', 'D']
        output = nx.simulated_annealing_tsp(self.DG, 'D', move='1-0', a=1,
                                            iterations=1, tolerance=1,
                                            cycle=initial_sol)
        assert_true(output[1] > 31.0)

    def test_two_nodes(self):
        G = nx.Graph()
        G.add_weighted_edges_from({(1, 2, 1)})
        cycle, cost = nx.simulated_annealing_tsp(G, 1)
        validate_solution(cycle, cost, [1, 2, 1], 2)
        cycle, cost = nx.simulated_annealing_tsp(G, 1, cycle=[1, 2, 1])
        validate_solution(cycle, cost, [1, 2, 1], 2)

class TestThresholdAcceptingTSP:
    setUp = _setUp

    def test_threshold_accepting(self):
        output = nx.threshold_accepting_tsp(self.DG, 'D')
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 31.0)

        output = nx.threshold_accepting_tsp(self.DG2, 'D')
        validate_solution(output[0], output[1], ['D', 'A', 'B', 'C', 'D'], 53.0)
        output = nx.threshold_accepting_tsp(self.DG2, 'D', move='1-0')
        validate_solution(output[0], output[1], ['D', 'A', 'B', 'C', 'D'], 53.0)
        output = nx.threshold_accepting_tsp(self.UG2, 'D')
        validate_symmetric_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 25.0)
        output = nx.threshold_accepting_tsp(self.UG2, 'D', move='1-0')
        validate_symmetric_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 25.0)

        initial_sol = ['D', 'B', 'A', 'C', 'D']
        output = nx.threshold_accepting_tsp(self.DG, 'D', cycle=initial_sol)
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 31.0)
        initial_sol = ['D', 'A', 'C', 'B', 'D']
        output = nx.threshold_accepting_tsp(self.DG, 'D', move='1-0',
                                            cycle=initial_sol)
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 31.0)

        output = nx.threshold_accepting_tsp(self.UG, 'D')
        validate_solution(output[0], output[1], ['D', 'C', 'B', 'A', 'D'], 33.0)

    def test_not_completed_graph(self):
        assert_raises(nx.NetworkXError, nx.threshold_accepting_tsp,
                      self.notCompletedUG, 0, cycle=[])
        assert_raises(nx.NetworkXError, nx.threshold_accepting_tsp,
                      self.notCompletedDG, 0, cycle=[])

    def test_not_weighted_graph(self):
        assert_raises(nx.NetworkXError, nx.threshold_accepting_tsp,
                      self.unweightedUG, 0, cycle=[])
        assert_raises(nx.NetworkXError, nx.threshold_accepting_tsp,
                      self.unweightedDG, 0, cycle=[])

    def test_two_nodes(self):
        G = nx.Graph()
        G.add_weighted_edges_from({(1, 2, 1)})
        cycle, cost = nx.threshold_accepting_tsp(G, 1)
        validate_solution(cycle, cost, [1, 2, 1], 2)
        cycle, cost = nx.threshold_accepting_tsp(G, 1, cycle=[1, 2, 1])
        validate_solution(cycle, cost, [1, 2, 1], 2)
