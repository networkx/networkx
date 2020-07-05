"""Unit tests for the :mod:`networkx.algorithms.tournament` module."""
from itertools import combinations


from networkx import DiGraph
from networkx.algorithms.tournament import is_reachable
from networkx.algorithms.tournament import is_strongly_connected
from networkx.algorithms.tournament import is_tournament
from networkx.algorithms.tournament import random_tournament
from networkx.algorithms.tournament import hamiltonian_path


class TestIsTournament:
    """Unit tests for the :func:`networkx.tournament.is_tournament`
    function.

    """

    def test_is_tournament(self):
        G = DiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (1, 3), (0, 2)])
        assert is_tournament(G)

    def test_self_loops(self):
        """A tournament must have no self-loops."""
        G = DiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (1, 3), (0, 2)])
        G.add_edge(0, 0)
        assert not is_tournament(G)

    def test_missing_edges(self):
        """A tournament must not have any pair of nodes without at least
        one edge joining the pair.

        """
        G = DiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (1, 3)])
        assert not is_tournament(G)

    def test_bidirectional_edges(self):
        """A tournament must not have any pair of nodes with greater
        than one edge joining the pair.

        """
        G = DiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (1, 3), (0, 2)])
        G.add_edge(1, 0)
        assert not is_tournament(G)


class TestRandomTournament:
    """Unit tests for the :func:`networkx.tournament.random_tournament`
    function.

    """
    def test_graph_is_tournament(self):
        for n in range(10):
            G = random_tournament(5)
            assert is_tournament(G)

    def test_graph_is_tournament_seed(self):
        for n in range(10):
            G = random_tournament(5, seed=1)
            assert is_tournament(G)


class TestHamiltonianPath:
    """Unit tests for the :func:`networkx.tournament.hamiltonian_path`
    function.

    """

    def test_path_is_hamiltonian(self):
        G = DiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (1, 3), (0, 2)])
        path = hamiltonian_path(G)
        assert len(path) == 4
        assert all(v in G[u] for u, v in zip(path, path[1:]))

    def test_hamiltonian_cycle(self):
        """Tests that :func:`networkx.tournament.hamiltonian_path`
        returns a Hamiltonian cycle when provided a strongly connected
        tournament.

        """
        G = DiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (1, 3), (0, 2)])
        path = hamiltonian_path(G)
        assert len(path) == 4
        assert all(v in G[u] for u, v in zip(path, path[1:]))
        assert path[0] in G[path[-1]]


class TestReachability:
    """Unit tests for the :func:`networkx.tournament.is_reachable`
    function.

    """

    def test_reachable_pair(self):
        """Tests for a reachable pair of nodes."""
        G = DiGraph([(0, 1), (1, 2), (2, 0)])
        assert is_reachable(G, 0, 2)

    def test_same_node_is_reachable(self):
        """Tests that a node is always reachable from itself."""
        # G is an arbitrary tournament on ten nodes.
        G = DiGraph(sorted(p) for p in combinations(range(10), 2))
        assert all(is_reachable(G, v, v) for v in G)

    def test_unreachable_pair(self):
        """Tests for an unreachable pair of nodes."""
        G = DiGraph([(0, 1), (0, 2), (1, 2)])
        assert not is_reachable(G, 1, 0)


class TestStronglyConnected:
    """Unit tests for the
    :func:`networkx.tournament.is_strongly_connected` function.

    """

    def test_is_strongly_connected(self):
        """Tests for a strongly connected tournament."""
        G = DiGraph([(0, 1), (1, 2), (2, 0)])
        assert is_strongly_connected(G)

    def test_not_strongly_connected(self):
        """Tests for a tournament that is not strongly connected."""
        G = DiGraph([(0, 1), (0, 2), (1, 2)])
        assert not is_strongly_connected(G)
