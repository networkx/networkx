import pytest
import networkx as nx
import networkx.algorithms.approximation as nxapp


@classmethod
def _setup_class(cls):
    cls.DG = nx.DiGraph()
    cls.DG.add_weighted_edges_from(
        {
            ("A", "B", 3),
            ("A", "C", 17),
            ("A", "D", 14),
            ("B", "A", 3),
            ("B", "C", 12),
            ("B", "D", 16),
            ("C", "A", 13),
            ("C", "B", 12),
            ("C", "D", 4),
            ("D", "A", 14),
            ("D", "B", 15),
            ("D", "C", 2),
        }
    )
    cls.DG2 = nx.DiGraph()
    cls.DG2.add_weighted_edges_from(
        {
            ("A", "B", 3),
            ("A", "C", 17),
            ("A", "D", 14),
            ("B", "A", 30),
            ("B", "C", 2),
            ("B", "D", 16),
            ("C", "A", 33),
            ("C", "B", 32),
            ("C", "D", 34),
            ("D", "A", 14),
            ("D", "B", 15),
            ("D", "C", 2),
        }
    )
    cls.unweightedUG = nx.complete_graph(5, nx.Graph())
    cls.unweightedDG = nx.complete_graph(5, nx.DiGraph())
    cls.incompleteUG = nx.Graph()
    cls.incompleteUG.add_weighted_edges_from({(0, 1, 1), (1, 2, 3)})
    cls.incompleteDG = nx.DiGraph()
    cls.incompleteDG.add_weighted_edges_from({(0, 1, 1), (1, 2, 3)})
    cls.UG = nx.Graph()
    cls.UG.add_weighted_edges_from(
        {
            ("A", "B", 3),
            ("A", "C", 17),
            ("A", "D", 14),
            ("B", "C", 12),
            ("B", "D", 16),
            ("C", "D", 4),
        }
    )
    cls.UG2 = nx.Graph()
    cls.UG2.add_weighted_edges_from(
        {
            ("A", "B", 1),
            ("A", "C", 15),
            ("A", "D", 5),
            ("B", "C", 16),
            ("B", "D", 8),
            ("C", "D", 3),
        }
    )


def validate_solution(soln, cost, exp_soln, exp_cost):
    assert soln == exp_soln
    assert cost == exp_cost


def validate_symmetric_solution(soln, cost, exp_soln, exp_cost):
    assert soln == exp_soln or soln == exp_soln[::-1]
    assert cost == exp_cost


class TestGreedyTSP:
    setup_class = _setup_class

    def test_greedy(self):
        output = nxapp.greedy_tsp(self.DG, "D")
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 31.0)

        output = nxapp.greedy_tsp(self.DG2, "D")
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 78.0)

        output = nxapp.greedy_tsp(self.UG, "D")
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 33.0)

        output = nxapp.greedy_tsp(self.UG2, "D")
        validate_solution(output[0], output[1], ["D", "C", "A", "B", "D"], 27.0)

    def test_not_complete_graph(self):
        pytest.raises(nx.NetworkXError, nxapp.greedy_tsp, self.incompleteUG, 0)
        pytest.raises(nx.NetworkXError, nxapp.greedy_tsp, self.incompleteDG, 0)

    def test_not_weighted_graph(self):
        pytest.raises(nx.NetworkXError, nxapp.greedy_tsp, self.unweightedUG, 0)
        pytest.raises(nx.NetworkXError, nxapp.greedy_tsp, self.unweightedDG, 0)

    def test_two_nodes(self):
        G = nx.Graph()
        G.add_weighted_edges_from({(1, 2, 1)})
        cycle, cost = nxapp.greedy_tsp(G, 1)
        validate_solution(cycle, cost, [1, 2, 1], 2)


class TestSimulatedAnnealingTSP:
    setup_class = _setup_class

    def test_simulated_annealing(self):
        output = nxapp.simulated_annealing_tsp(self.DG, "D")
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 31.0)

        output = nxapp.simulated_annealing_tsp(self.DG2, "D")
        validate_solution(output[0], output[1], ["D", "A", "B", "C", "D"], 53.0)
        output = nxapp.simulated_annealing_tsp(self.DG2, "D", move="1-0")
        validate_solution(output[0], output[1], ["D", "A", "B", "C", "D"], 53.0)
        output = nxapp.simulated_annealing_tsp(self.UG2, "D")
        validate_symmetric_solution(
            output[0], output[1], ["D", "C", "B", "A", "D"], 25.0
        )
        output = nxapp.simulated_annealing_tsp(self.UG2, "D", move="1-0")
        validate_symmetric_solution(
            output[0], output[1], ["D", "C", "B", "A", "D"], 25.0
        )

        initial_sol = ["D", "B", "A", "C", "D"]
        output = nxapp.simulated_annealing_tsp(self.DG, "D", cycle=initial_sol)
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 31.0)
        initial_sol = ["D", "A", "C", "B", "D"]
        output = nxapp.simulated_annealing_tsp(
            self.DG, "D", move="1-0", cycle=initial_sol
        )
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 31.0)

        output = nxapp.simulated_annealing_tsp(self.UG, "D")
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 33.0)

    def test_not_complete_graph(self):
        pytest.raises(
            nx.NetworkXError,
            nxapp.simulated_annealing_tsp,
            self.incompleteUG,
            0,
            cycle=[],
        )
        pytest.raises(
            nx.NetworkXError,
            nxapp.simulated_annealing_tsp,
            self.incompleteDG,
            0,
            cycle=[],
        )

    def test_not_weighted_graph(self):
        pytest.raises(
            nx.NetworkXError,
            nxapp.simulated_annealing_tsp,
            self.unweightedUG,
            0,
            cycle=[],
        )
        pytest.raises(
            nx.NetworkXError,
            nxapp.simulated_annealing_tsp,
            self.unweightedDG,
            0,
            cycle=[],
        )

    def test_simulated_annealing_fails(self):
        output = nxapp.simulated_annealing_tsp(
            self.DG2, "D", move="1-0", alpha=1, iterations=1, tolerance=1
        )
        assert output[1] > 53.0

        initial_sol = ["D", "A", "B", "C", "D"]
        output = nxapp.simulated_annealing_tsp(
            self.DG,
            "D",
            move="1-0",
            alpha=1,
            iterations=1,
            tolerance=1,
            cycle=initial_sol,
        )
        assert output[1] > 31.0

    def test_two_nodes(self):
        G = nx.Graph()
        G.add_weighted_edges_from({(1, 2, 1)})
        cycle, cost = nxapp.simulated_annealing_tsp(G, 1)
        validate_solution(cycle, cost, [1, 2, 1], 2)
        cycle, cost = nxapp.simulated_annealing_tsp(G, 1, cycle=[1, 2, 1])
        validate_solution(cycle, cost, [1, 2, 1], 2)


class TestThresholdAcceptingTSP:
    setup_class = _setup_class

    def test_threshold_accepting(self):
        output = nxapp.threshold_accepting_tsp(self.DG, "D")
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 31.0)

        output = nxapp.threshold_accepting_tsp(self.DG2, "D")
        validate_solution(output[0], output[1], ["D", "A", "B", "C", "D"], 53.0)
        output = nxapp.threshold_accepting_tsp(self.DG2, "D", move="1-0")
        validate_solution(output[0], output[1], ["D", "A", "B", "C", "D"], 53.0)
        output = nxapp.threshold_accepting_tsp(self.UG2, "D")
        validate_symmetric_solution(
            output[0], output[1], ["D", "C", "B", "A", "D"], 25.0
        )
        output = nxapp.threshold_accepting_tsp(self.UG2, "D", move="1-0")
        validate_symmetric_solution(
            output[0], output[1], ["D", "C", "B", "A", "D"], 25.0
        )

        initial_sol = ["D", "B", "A", "C", "D"]
        output = nxapp.threshold_accepting_tsp(self.DG, "D", cycle=initial_sol)
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 31.0)
        initial_sol = ["D", "A", "C", "B", "D"]
        output = nxapp.threshold_accepting_tsp(
            self.DG, "D", move="1-0", cycle=initial_sol
        )
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 31.0)

        output = nxapp.threshold_accepting_tsp(self.UG, "D")
        validate_solution(output[0], output[1], ["D", "C", "B", "A", "D"], 33.0)

    def test_not_completed_graph(self):
        pytest.raises(
            nx.NetworkXError,
            nxapp.threshold_accepting_tsp,
            self.incompleteUG,
            0,
            cycle=[],
        )
        pytest.raises(
            nx.NetworkXError,
            nxapp.threshold_accepting_tsp,
            self.incompleteDG,
            0,
            cycle=[],
        )

    def test_not_weighted_graph(self):
        pytest.raises(
            nx.NetworkXError,
            nxapp.threshold_accepting_tsp,
            self.unweightedUG,
            0,
            cycle=[],
        )
        pytest.raises(
            nx.NetworkXError,
            nxapp.threshold_accepting_tsp,
            self.unweightedDG,
            0,
            cycle=[],
        )

    def test_two_nodes(self):
        G = nx.Graph()
        G.add_weighted_edges_from({(1, 2, 1)})
        cycle, cost = nxapp.threshold_accepting_tsp(G, 1)
        validate_solution(cycle, cost, [1, 2, 1], 2)
        cycle, cost = nxapp.threshold_accepting_tsp(G, 1, cycle=[1, 2, 1])
        validate_solution(cycle, cost, [1, 2, 1], 2)
