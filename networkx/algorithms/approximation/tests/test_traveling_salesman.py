"""Unit tests for the traveling_salesman module."""
import pytest
import random
import networkx as nx
import networkx.algorithms.approximation as nx_app

pairwise = nx.utils.pairwise


def test_christofides_exception():
    G = nx.complete_graph(10)
    G.remove_edge(0, 1)
    pytest.raises(ValueError, nx_app.christofides, G)


def test_christofides_hamiltonian():
    random.seed(42)
    G = nx.complete_graph(20)
    for (u, v) in G.edges():
        G[u][v]["weight"] = random.randint(0, 10)

    H = nx.Graph()
    H.add_edges_from(pairwise(nx_app.christofides(G)))
    H.remove_edges_from(nx.find_cycle(H))
    assert len(H.edges) == 0

    tree = nx.minimum_spanning_tree(G, weight="weight")
    H = nx.Graph()
    H.add_edges_from(pairwise(nx_app.christofides(G, tree)))
    H.remove_edges_from(nx.find_cycle(H))
    assert len(H.edges) == 0


def test_christofides_selfloop():
    G = nx.complete_graph(10)
    G.add_edge(3, 3)
    pytest.raises(ValueError, nx_app.christofides, G)


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
        cycle = nx_app.greedy_tsp(self.DG, source="D")
        cost = sum(self.DG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 31.0)

        cycle = nx_app.greedy_tsp(self.DG2, source="D")
        cost = sum(self.DG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 78.0)

        cycle = nx_app.greedy_tsp(self.UG, source="D")
        cost = sum(self.UG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 33.0)

        cycle = nx_app.greedy_tsp(self.UG2, source="D")
        cost = sum(self.UG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "A", "B", "D"], 27.0)

    def test_not_complete_graph(self):
        pytest.raises(nx.NetworkXError, nx_app.greedy_tsp, self.incompleteUG)
        pytest.raises(nx.NetworkXError, nx_app.greedy_tsp, self.incompleteDG)

    def test_not_weighted_graph(self):
        pytest.raises(nx.NetworkXError, nx_app.greedy_tsp, self.unweightedUG)
        pytest.raises(nx.NetworkXError, nx_app.greedy_tsp, self.unweightedDG)

    def test_two_nodes(self):
        G = nx.Graph()
        G.add_weighted_edges_from({(1, 2, 1)})
        cycle = nx_app.greedy_tsp(G)
        cost = sum(G[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, [1, 2, 1], 2)


class TestSimulatedAnnealingTSP:
    setup_class = _setup_class

    def test_simulated_annealing(self):
        cycle = nx_app.simulated_annealing_tsp(self.DG, source="D")
        cost = sum(self.DG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 31.0)

        cycle = nx_app.simulated_annealing_tsp(self.DG2, source="D")
        cost = sum(self.DG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "A", "B", "C", "D"], 53.0)
        cycle = nx_app.simulated_annealing_tsp(self.DG2, move="1-0", source="D")
        cost = sum(self.DG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "A", "B", "C", "D"], 53.0)
        cycle = nx_app.simulated_annealing_tsp(self.UG2, source="D")
        cost = sum(self.UG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_symmetric_solution(cycle, cost, ["D", "C", "B", "A", "D"], 25.0)
        cycle = nx_app.simulated_annealing_tsp(self.UG2, move="1-0", source="D")
        cost = sum(self.UG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_symmetric_solution(cycle, cost, ["D", "C", "B", "A", "D"], 25.0)

        initial_sol = ["D", "B", "A", "C", "D"]
        cycle = nx_app.simulated_annealing_tsp(self.DG, cycle=initial_sol, source="D")
        cost = sum(self.DG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 31.0)
        initial_sol = ["D", "A", "C", "B", "D"]
        cycle = nx_app.simulated_annealing_tsp(
            self.DG, move="1-0", cycle=initial_sol, source="D"
        )
        cost = sum(self.DG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 31.0)

        cycle = nx_app.simulated_annealing_tsp(self.UG, source="D")
        cost = sum(self.UG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 33.0)

    def test_not_complete_graph(self):
        pytest.raises(
            nx.NetworkXError,
            nx_app.simulated_annealing_tsp,
            self.incompleteUG,
            source=0,
            cycle=[],
        )
        pytest.raises(
            nx.NetworkXError,
            nx_app.simulated_annealing_tsp,
            self.incompleteDG,
            source=0,
            cycle=[],
        )

    def test_not_weighted_graph(self):
        pytest.raises(
            nx.NetworkXError,
            nx_app.simulated_annealing_tsp,
            self.unweightedUG,
            source=0,
            cycle=[],
        )
        pytest.raises(
            nx.NetworkXError,
            nx_app.simulated_annealing_tsp,
            self.unweightedDG,
            source=0,
            cycle=[],
        )

    def test_simulated_annealing_fails(self):
        cycle = nx_app.simulated_annealing_tsp(
            self.DG2, source="D", move="1-0", alpha=1, iterations=1, tolerance=1
        )
        cost = sum(self.DG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        assert cost > 53.0

        initial_sol = ["D", "A", "B", "C", "D"]
        cycle = nx_app.simulated_annealing_tsp(
            self.DG,
            source="D",
            move="1-0",
            alpha=1,
            iterations=1,
            tolerance=1,
            cycle=initial_sol,
        )
        cost = sum(self.DG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        assert cost > 31.0

    def test_two_nodes(self):
        G = nx.Graph()
        G.add_weighted_edges_from({(1, 2, 1)})
        cycle = nx_app.simulated_annealing_tsp(G, source=1)
        cost = sum(G[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, [1, 2, 1], 2)
        cycle = nx_app.simulated_annealing_tsp(G, source=1, cycle=[1, 2, 1])
        cost = sum(G[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, [1, 2, 1], 2)


class TestThresholdAcceptingTSP:
    setup_class = _setup_class

    def test_threshold_accepting(self):
        cycle = nx_app.threshold_accepting_tsp(self.DG, source="D")
        cost = sum(self.DG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 31.0)

        cycle = nx_app.threshold_accepting_tsp(self.DG2, source="D")
        cost = sum(self.DG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "A", "B", "C", "D"], 53.0)
        cycle = nx_app.threshold_accepting_tsp(self.DG2, source="D", move="1-0")
        cost = sum(self.DG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "A", "B", "C", "D"], 53.0)
        cycle = nx_app.threshold_accepting_tsp(self.UG2, source="D")
        cost = sum(self.UG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_symmetric_solution(cycle, cost, ["D", "C", "B", "A", "D"], 25.0)
        cycle = nx_app.threshold_accepting_tsp(self.UG2, source="D", move="1-0")
        cost = sum(self.UG2[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_symmetric_solution(cycle, cost, ["D", "C", "B", "A", "D"], 25.0)

        initial_sol = ["D", "B", "A", "C", "D"]
        cycle = nx_app.threshold_accepting_tsp(self.DG, source="D", cycle=initial_sol)
        cost = sum(self.DG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 31.0)
        initial_sol = ["D", "A", "C", "B", "D"]
        cycle = nx_app.threshold_accepting_tsp(
            self.DG, source="D", move="1-0", cycle=initial_sol
        )
        cost = sum(self.DG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 31.0)

        cycle = nx_app.threshold_accepting_tsp(self.UG, source="D")
        cost = sum(self.UG[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, ["D", "C", "B", "A", "D"], 33.0)

    def test_not_completed_graph(self):
        pytest.raises(
            nx.NetworkXError,
            nx_app.threshold_accepting_tsp,
            self.incompleteUG,
            source=0,
            cycle=[],
        )
        pytest.raises(
            nx.NetworkXError,
            nx_app.threshold_accepting_tsp,
            self.incompleteDG,
            source=0,
            cycle=[],
        )

    def test_not_weighted_graph(self):
        pytest.raises(
            nx.NetworkXError,
            nx_app.threshold_accepting_tsp,
            self.unweightedUG,
            source=0,
            cycle=[],
        )
        pytest.raises(
            nx.NetworkXError,
            nx_app.threshold_accepting_tsp,
            self.unweightedDG,
            source=0,
            cycle=[],
        )

    def test_two_nodes(self):
        G = nx.Graph()
        G.add_weighted_edges_from({(1, 2, 1)})
        cycle = nx_app.threshold_accepting_tsp(G, source=1)
        cost = sum(G[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, [1, 2, 1], 2)
        cycle = nx_app.threshold_accepting_tsp(G, source=1, cycle=[1, 2, 1])
        cost = sum(G[n][nbr]["weight"] for n, nbr in pairwise(cycle))
        validate_solution(cycle, cost, [1, 2, 1], 2)


def test_TSP_unweighted():
    G = nx.cycle_graph(9)
    path = nx_app.traveling_salesman_problem(G, [3, 6], cycle=False)
    assert path in ([3, 4, 5, 6], [6, 5, 4, 3])

    cycle = nx_app.traveling_salesman_problem(G, [3, 6])
    assert cycle in ([3, 4, 5, 6, 5, 4, 3], [6, 5, 4, 3, 4, 5, 6])


def test_TSP_weighted():
    G = nx.cycle_graph(9)
    G[0][1]["weight"] = 2
    G[1][2]["weight"] = 2
    G[2][3]["weight"] = 2
    G[3][4]["weight"] = 4
    G[4][5]["weight"] = 5
    G[5][6]["weight"] = 4
    G[6][7]["weight"] = 2
    G[7][8]["weight"] = 2
    G[8][0]["weight"] = 2
    tsp = nx_app.traveling_salesman_problem
    path = tsp(G, [3, 6], weight="weight", cycle=False)
    assert path in ([3, 2, 1, 0, 8, 7, 6], [6, 7, 8, 0, 1, 2, 3])

    cycle = tsp(G, [3, 6], weight="weight")
    expected = (
        [3, 2, 1, 0, 8, 7, 6, 7, 8, 0, 1, 2, 3],
        [6, 7, 8, 0, 1, 2, 3, 2, 1, 0, 8, 7, 6],
    )
    assert cycle in expected

    cycle_christofides = tsp(G, [3, 6], weight="weight", method=nx_app.christofides)
    assert cycle == cycle_christofides
    cycle_greedy = tsp(G, [3, 6], weight="weight", method=nx_app.greedy_tsp)
    assert cycle == cycle_greedy
    cycle_SA = tsp(G, [3, 6], weight="weight", method=nx_app.simulated_annealing_tsp)
    assert cycle == cycle_SA
    cycle_TA = tsp(G, [3, 6], weight="weight", method=nx_app.threshold_accepting_tsp)
    assert cycle == cycle_TA
