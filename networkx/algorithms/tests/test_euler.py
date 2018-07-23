from unittest import TestCase

from nose.tools import assert_equal
from nose.tools import assert_false
try:
    from nose.tools import assert_count_equal
except ImportError:
    from nose.tools import assert_items_equal as assert_count_equal
from nose.tools import assert_true
from nose.tools import raises

import networkx as nx
from networkx import is_eulerian, eulerian_circuit


class TestIsEulerian(TestCase):

    def test_is_eulerian(self):
        assert_true(is_eulerian(nx.complete_graph(5)))
        assert_true(is_eulerian(nx.complete_graph(7)))
        assert_true(is_eulerian(nx.hypercube_graph(4)))
        assert_true(is_eulerian(nx.hypercube_graph(6)))

        assert_false(is_eulerian(nx.complete_graph(4)))
        assert_false(is_eulerian(nx.complete_graph(6)))
        assert_false(is_eulerian(nx.hypercube_graph(3)))
        assert_false(is_eulerian(nx.hypercube_graph(5)))

        assert_false(is_eulerian(nx.petersen_graph()))
        assert_false(is_eulerian(nx.path_graph(4)))

    def test_is_eulerian2(self):
        # not connected
        G = nx.Graph()
        G.add_nodes_from([1, 2, 3])
        assert_false(is_eulerian(G))
        # not strongly connected
        G = nx.DiGraph()
        G.add_nodes_from([1, 2, 3])
        assert_false(is_eulerian(G))
        G = nx.MultiDiGraph()
        G.add_edge(1, 2)
        G.add_edge(2, 3)
        G.add_edge(2, 3)
        G.add_edge(3, 1)
        assert_false(is_eulerian(G))


class TestEulerianCircuit(TestCase):

    def test_eulerian_circuit_cycle(self):
        G = nx.cycle_graph(4)

        edges = list(eulerian_circuit(G, source=0))
        nodes = [u for u, v in edges]
        assert_equal(nodes, [0, 3, 2, 1])
        assert_equal(edges, [(0, 3), (3, 2), (2, 1), (1, 0)])

        edges = list(eulerian_circuit(G, source=1))
        nodes = [u for u, v in edges]
        assert_equal(nodes, [1, 2, 3, 0])
        assert_equal(edges, [(1, 2), (2, 3), (3, 0), (0, 1)])

        G = nx.complete_graph(3)

        edges = list(eulerian_circuit(G, source=0))
        nodes = [u for u, v in edges]
        assert_equal(nodes, [0, 2, 1])
        assert_equal(edges, [(0, 2), (2, 1), (1, 0)])

        edges = list(eulerian_circuit(G, source=1))
        nodes = [u for u, v in edges]
        assert_equal(nodes, [1, 2, 0])
        assert_equal(edges, [(1, 2), (2, 0), (0, 1)])

    def test_eulerian_circuit_digraph(self):
        G = nx.DiGraph()
        nx.add_cycle(G, [0, 1, 2, 3])

        edges = list(eulerian_circuit(G, source=0))
        nodes = [u for u, v in edges]
        assert_equal(nodes, [0, 1, 2, 3])
        assert_equal(edges, [(0, 1), (1, 2), (2, 3), (3, 0)])

        edges = list(eulerian_circuit(G, source=1))
        nodes = [u for u, v in edges]
        assert_equal(nodes, [1, 2, 3, 0])
        assert_equal(edges, [(1, 2), (2, 3), (3, 0), (0, 1)])

    def test_multigraph(self):
        G = nx.MultiGraph()
        nx.add_cycle(G, [0, 1, 2, 3])
        G.add_edge(1, 2)
        G.add_edge(1, 2)
        edges = list(eulerian_circuit(G, source=0))
        nodes = [u for u, v in edges]
        assert_equal(nodes, [0, 3, 2, 1, 2, 1])
        assert_equal(edges, [(0, 3), (3, 2), (2, 1), (1, 2), (2, 1), (1, 0)])

    def test_multigraph_with_keys(self):
        G = nx.MultiGraph()
        nx.add_cycle(G, [0, 1, 2, 3])
        G.add_edge(1, 2)
        G.add_edge(1, 2)
        edges = list(eulerian_circuit(G, source=0, keys=True))
        nodes = [u for u, v, k in edges]
        assert_equal(nodes, [0, 3, 2, 1, 2, 1])
        assert_equal(edges[:2], [(0, 3, 0), (3, 2, 0)])
        assert_count_equal(edges[2:5], [(2, 1, 0), (1, 2, 1), (2, 1, 2)])
        assert_equal(edges[5:], [(1, 0, 0)])

    @raises(nx.NetworkXError)
    def test_not_eulerian(self):
        f = list(eulerian_circuit(nx.complete_graph(4)))


class TestEulerize(TestCase):

    @raises(nx.NetworkXError)
    def test_disconnected(self):
        G = nx.from_edgelist([(0, 1), (2, 3)])
        nx.eulerize(G)

    @raises(nx.NetworkXPointlessConcept)
    def test_null_graph(self):
        nx.eulerize(nx.Graph())

    @raises(nx.NetworkXPointlessConcept)
    def test_null_multigraph(self):
        nx.eulerize(nx.MultiGraph())

    @raises(nx.NetworkXError)
    def test_on_empty_graph(self):
        nx.eulerize(nx.empty_graph(3))

    def test_on_eulerian(self):
        G = nx.cycle_graph(3)
        H = nx.eulerize(G)
        assert_true(nx.is_isomorphic(G, H))

    def test_on_eulerian_multigraph(self):
        G = nx.MultiGraph(nx.cycle_graph(3))
        G.add_edge(0, 1)
        H = nx.eulerize(G)
        assert_true(nx.is_eulerian(H))

    def test_on_complete_graph(self):
        G = nx.complete_graph(4)
        assert_true(nx.is_eulerian(nx.eulerize(G)))
        assert_true(nx.is_eulerian(nx.eulerize(nx.MultiGraph(G))))
