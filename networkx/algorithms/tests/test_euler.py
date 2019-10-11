from unittest import TestCase
import collections

import pytest

import networkx as nx


class TestIsEulerian(TestCase):
    def test_is_eulerian(self):
        assert nx.is_eulerian(nx.complete_graph(5))
        assert nx.is_eulerian(nx.complete_graph(7))
        assert nx.is_eulerian(nx.hypercube_graph(4))
        assert nx.is_eulerian(nx.hypercube_graph(6))

        assert not nx.is_eulerian(nx.complete_graph(4))
        assert not nx.is_eulerian(nx.complete_graph(6))
        assert not nx.is_eulerian(nx.hypercube_graph(3))
        assert not nx.is_eulerian(nx.hypercube_graph(5))

        assert not nx.is_eulerian(nx.petersen_graph())
        assert not nx.is_eulerian(nx.path_graph(4))

    def test_is_eulerian2(self):
        # not connected
        G = nx.Graph()
        G.add_nodes_from([1, 2, 3])
        assert not nx.is_eulerian(G)
        # not strongly connected
        G = nx.DiGraph()
        G.add_nodes_from([1, 2, 3])
        assert not nx.is_eulerian(G)
        G = nx.MultiDiGraph()
        G.add_edge(1, 2)
        G.add_edge(2, 3)
        G.add_edge(2, 3)
        G.add_edge(3, 1)
        assert not nx.is_eulerian(G)


class TestEulerianCircuit(TestCase):
    def test_eulerian_circuit_cycle(self):
        G = nx.cycle_graph(4)

        edges = list(nx.eulerian_circuit(G, source=0))
        nodes = [u for u, v in edges]
        assert nodes == [0, 3, 2, 1]
        assert edges == [(0, 3), (3, 2), (2, 1), (1, 0)]

        edges = list(nx.eulerian_circuit(G, source=1))
        nodes = [u for u, v in edges]
        assert nodes == [1, 2, 3, 0]
        assert edges == [(1, 2), (2, 3), (3, 0), (0, 1)]

        G = nx.complete_graph(3)

        edges = list(nx.eulerian_circuit(G, source=0))
        nodes = [u for u, v in edges]
        assert nodes == [0, 2, 1]
        assert edges == [(0, 2), (2, 1), (1, 0)]

        edges = list(nx.eulerian_circuit(G, source=1))
        nodes = [u for u, v in edges]
        assert nodes == [1, 2, 0]
        assert edges == [(1, 2), (2, 0), (0, 1)]

    def test_eulerian_circuit_digraph(self):
        G = nx.DiGraph()
        nx.add_cycle(G, [0, 1, 2, 3])

        edges = list(nx.eulerian_circuit(G, source=0))
        nodes = [u for u, v in edges]
        assert nodes == [0, 1, 2, 3]
        assert edges == [(0, 1), (1, 2), (2, 3), (3, 0)]

        edges = list(nx.eulerian_circuit(G, source=1))
        nodes = [u for u, v in edges]
        assert nodes == [1, 2, 3, 0]
        assert edges == [(1, 2), (2, 3), (3, 0), (0, 1)]

    def test_multigraph(self):
        G = nx.MultiGraph()
        nx.add_cycle(G, [0, 1, 2, 3])
        G.add_edge(1, 2)
        G.add_edge(1, 2)
        edges = list(nx.eulerian_circuit(G, source=0))
        nodes = [u for u, v in edges]
        assert nodes == [0, 3, 2, 1, 2, 1]
        assert edges == [(0, 3), (3, 2), (2, 1), (1, 2), (2, 1), (1, 0)]

    def test_multigraph_with_keys(self):
        G = nx.MultiGraph()
        nx.add_cycle(G, [0, 1, 2, 3])
        G.add_edge(1, 2)
        G.add_edge(1, 2)
        edges = list(nx.eulerian_circuit(G, source=0, keys=True))
        nodes = [u for u, v, k in edges]
        assert nodes == [0, 3, 2, 1, 2, 1]
        assert edges[:2] == [(0, 3, 0), (3, 2, 0)]
        assert collections.Counter(edges[2:5]) == collections.Counter([(2, 1, 0), (1, 2, 1), (2, 1, 2)])
        assert edges[5:] == [(1, 0, 0)]

    def test_not_eulerian(self):
        with pytest.raises(nx.NetworkXError):
            f = list(nx.eulerian_circuit(nx.complete_graph(4)))


class TestIsSemiEulerian(TestCase):
    def test_is_semieulerian(self):
        # Test graphs with Eulerian paths but no cycles return True.
        assert nx.is_semieulerian(nx.path_graph(4))
        G = nx.path_graph(6, create_using=nx.DiGraph)
        assert nx.is_semieulerian(G)

        # Test graphs with Eulerian cycles return False.
        assert not nx.is_semieulerian(nx.complete_graph(5))
        assert not nx.is_semieulerian(nx.complete_graph(7))
        assert not nx.is_semieulerian(nx.hypercube_graph(4))
        assert not nx.is_semieulerian(nx.hypercube_graph(6))


class TestHasEulerianPath(TestCase):
    def test_has_eulerian_path_cyclic(self):
        # Test graphs with Eulerian cycles return True.
        assert nx.has_eulerian_path(nx.complete_graph(5))
        assert nx.has_eulerian_path(nx.complete_graph(7))
        assert nx.has_eulerian_path(nx.hypercube_graph(4))
        assert nx.has_eulerian_path(nx.hypercube_graph(6))

    def test_has_eulerian_path_non_cyclic(self):
        # Test graphs with Eulerian paths but no cycles return True.
        assert nx.has_eulerian_path(nx.path_graph(4))
        G = nx.path_graph(6, create_using=nx.DiGraph)
        assert nx.has_eulerian_path(G)


class TestFindPathStart(TestCase):
    def testfind_path_start(self):
        find_path_start = nx.algorithms.euler._find_path_start
        # Test digraphs return correct starting node.
        G = nx.path_graph(6, create_using=nx.DiGraph)
        assert find_path_start(G) == 0
        edges = [(0, 1), (1, 2), (2, 0), (4, 0)]
        assert find_path_start(nx.DiGraph(edges)) == 4

        # Test graph with no Eulerian path return None.
        edges = [(0, 1), (1, 2), (2, 3), (2, 4)]
        assert find_path_start(nx.DiGraph(edges)) == None


class TestEulerianPath(TestCase):
    def test_eulerian_path(self):
        x = [(4, 0), (0, 1), (1, 2), (2, 0)]
        for e1, e2 in zip(x, nx.eulerian_path(nx.DiGraph(x))):
            assert e1 == e2


class TestEulerize(TestCase):
    def test_disconnected(self):
        with pytest.raises(nx.NetworkXError):
            G = nx.from_edgelist([(0, 1), (2, 3)])
            nx.eulerize(G)

    def test_null_graph(self):
        with pytest.raises(nx.NetworkXPointlessConcept):
            nx.eulerize(nx.Graph())

    def test_null_multigraph(self):
        with pytest.raises(nx.NetworkXPointlessConcept):
            nx.eulerize(nx.MultiGraph())

    def test_on_empty_graph(self):
        with pytest.raises(nx.NetworkXError):
            nx.eulerize(nx.empty_graph(3))

    def test_on_eulerian(self):
        G = nx.cycle_graph(3)
        H = nx.eulerize(G)
        assert nx.is_isomorphic(G, H)

    def test_on_eulerian_multigraph(self):
        G = nx.MultiGraph(nx.cycle_graph(3))
        G.add_edge(0, 1)
        H = nx.eulerize(G)
        assert nx.is_eulerian(H)

    def test_on_complete_graph(self):
        G = nx.complete_graph(4)
        assert nx.is_eulerian(nx.eulerize(G))
        assert nx.is_eulerian(nx.eulerize(nx.MultiGraph(G)))
