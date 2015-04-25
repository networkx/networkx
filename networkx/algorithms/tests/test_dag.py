#!/usr/bin/env python
from itertools import combinations
from nose.tools import *
from networkx.testing.utils import assert_edges_equal
import networkx as nx


class TestDAG:

    def setUp(self):
        pass

    def test_topological_sort1(self):
        DG = nx.DiGraph()
        DG.add_edges_from([(1, 2), (1, 3), (2, 3)])
        assert_equal(nx.topological_sort(DG), [1, 2, 3])
        assert_equal(nx.topological_sort_recursive(DG), [1, 2, 3])

        DG.add_edge(3, 2)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort, DG)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort_recursive, DG)

        DG.remove_edge(2, 3)
        assert_equal(nx.topological_sort(DG), [1, 3, 2])
        assert_equal(nx.topological_sort_recursive(DG), [1, 3, 2])

    def test_reverse_topological_sort1(self):
        DG = nx.DiGraph()
        DG.add_edges_from([(1, 2), (1, 3), (2, 3)])
        assert_equal(nx.topological_sort(DG, reverse=True), [3, 2, 1])
        assert_equal(
            nx.topological_sort_recursive(DG, reverse=True), [3, 2, 1])

        DG.add_edge(3, 2)
        assert_raises(nx.NetworkXUnfeasible,
                      nx.topological_sort, DG, reverse=True)
        assert_raises(nx.NetworkXUnfeasible,
                      nx.topological_sort_recursive, DG, reverse=True)

        DG.remove_edge(2, 3)
        assert_equal(nx.topological_sort(DG, reverse=True), [2, 3, 1])
        assert_equal(
            nx.topological_sort_recursive(DG, reverse=True), [2, 3, 1])

    def test_is_directed_acyclic_graph(self):
        G = nx.generators.complete_graph(2)
        assert_false(nx.is_directed_acyclic_graph(G))
        assert_false(nx.is_directed_acyclic_graph(G.to_directed()))
        assert_false(nx.is_directed_acyclic_graph(nx.Graph([(3, 4), (4, 5)])))
        assert_true(nx.is_directed_acyclic_graph(nx.DiGraph([(3, 4), (4, 5)])))

    def test_topological_sort2(self):
        DG = nx.DiGraph({1: [2], 2: [3], 3: [4],
                         4: [5], 5: [1], 11: [12],
                         12: [13], 13: [14], 14: [15]})
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort, DG)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort_recursive, DG)

        assert_false(nx.is_directed_acyclic_graph(DG))

        DG.remove_edge(1, 2)
        assert_equal(nx.topological_sort_recursive(DG),
                     [11, 12, 13, 14, 15, 2, 3, 4, 5, 1])
        assert_equal(nx.topological_sort(DG),
                     [11, 12, 13, 14, 15, 2, 3, 4, 5, 1])
        assert_true(nx.is_directed_acyclic_graph(DG))

    def test_topological_sort3(self):
        DG = nx.DiGraph()
        DG.add_edges_from([(1, i) for i in range(2, 5)])
        DG.add_edges_from([(2, i) for i in range(5, 9)])
        DG.add_edges_from([(6, i) for i in range(9, 12)])
        DG.add_edges_from([(4, i) for i in range(12, 15)])

        def validate(order):
            ok_(isinstance(order, list))
            assert_equal(set(order), set(DG))
            for u, v in combinations(order, 2):
                assert_false(nx.has_path(DG, v, u))
        validate(nx.topological_sort_recursive(DG))
        validate(nx.topological_sort(DG))

        DG.add_edge(14, 1)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort, DG)
        assert_raises(nx.NetworkXUnfeasible, nx.topological_sort_recursive, DG)

    def test_topological_sort4(self):
        G = nx.Graph()
        G.add_edge(1, 2)
        assert_raises(nx.NetworkXError, nx.topological_sort, G)
        assert_raises(nx.NetworkXError, nx.topological_sort_recursive, G)

    def test_topological_sort5(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        assert_equal(nx.topological_sort_recursive(G), [0, 1])
        assert_equal(nx.topological_sort(G), [0, 1])

    def test_nbunch_argument(self):
        G = nx.DiGraph()
        G.add_edges_from([(1, 2), (2, 3), (1, 4), (1, 5), (2, 6)])
        assert_equal(nx.topological_sort(G), [1, 2, 3, 6, 4, 5])
        assert_equal(nx.topological_sort_recursive(G), [1, 5, 4, 2, 6, 3])
        assert_equal(nx.topological_sort(G, [1]), [1, 2, 3, 6, 4, 5])
        assert_equal(nx.topological_sort_recursive(G, [1]), [1, 5, 4, 2, 6, 3])
        assert_equal(nx.topological_sort(G, [5]), [5])
        assert_equal(nx.topological_sort_recursive(G, [5]), [5])

    def test_ancestors(self):
        G = nx.DiGraph()
        ancestors = nx.algorithms.dag.ancestors
        G.add_edges_from([
            (1, 2), (1, 3), (4, 2), (4, 3), (4, 5), (2, 6), (5, 6)])
        assert_equal(ancestors(G, 6), set([1, 2, 4, 5]))
        assert_equal(ancestors(G, 3), set([1, 4]))
        assert_equal(ancestors(G, 1), set())
        assert_raises(nx.NetworkXError, ancestors, G, 8)

    def test_descendants(self):
        G = nx.DiGraph()
        descendants = nx.algorithms.dag.descendants
        G.add_edges_from([
            (1, 2), (1, 3), (4, 2), (4, 3), (4, 5), (2, 6), (5, 6)])
        assert_equal(descendants(G, 1), set([2, 3, 6]))
        assert_equal(descendants(G, 4), set([2, 3, 5, 6]))
        assert_equal(descendants(G, 3), set())
        assert_raises(nx.NetworkXError, descendants, G, 8)

    def test_transitive_closure(self):
        G = nx.DiGraph([(1, 2), (2, 3), (3, 4)])
        transitive_closure = nx.algorithms.dag.transitive_closure
        solution = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
        assert_edges_equal(transitive_closure(G).edges(), solution)
        G = nx.DiGraph([(1, 2), (2, 3), (2, 4)])
        solution = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]
        assert_edges_equal(transitive_closure(G).edges(), solution)
        G = nx.Graph([(1, 2), (2, 3), (3, 4)])
        assert_raises(nx.NetworkXNotImplemented, transitive_closure, G)

    def _check_antichains(self, solution, result):
        sol = [frozenset(a) for a in solution]
        res = [frozenset(a) for a in result]
        assert_true(set(sol) == set(res))

    def test_antichains(self):
        antichains = nx.algorithms.dag.antichains
        G = nx.DiGraph([(1, 2), (2, 3), (3, 4)])
        solution = [[], [4], [3], [2], [1]]
        self._check_antichains(list(antichains(G)), solution)
        G = nx.DiGraph([(1, 2), (2, 3), (2, 4), (3, 5), (5, 6), (5, 7)])
        solution = [[], [4], [7], [7, 4], [6], [6, 4], [6, 7], [6, 7, 4],
                    [5], [5, 4], [3], [3, 4], [2], [1]]
        self._check_antichains(list(antichains(G)), solution)
        G = nx.DiGraph([(1, 2), (1, 3), (3, 4), (3, 5), (5, 6)])
        solution = [[], [6], [5], [4], [4, 6], [4, 5], [3], [2], [2, 6],
                    [2, 5], [2, 4], [2, 4, 6], [2, 4, 5], [2, 3], [1]]
        self._check_antichains(list(antichains(G)), solution)
        G = nx.DiGraph({0: [1, 2], 1: [4], 2: [3], 3: [4]})
        solution = [[], [4], [3], [2], [1], [1, 3], [1, 2], [0]]
        self._check_antichains(list(antichains(G)), solution)
        G = nx.DiGraph()
        self._check_antichains(list(antichains(G)), [[]])
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2])
        solution = [[], [0], [1], [1, 0], [2], [2, 0], [2, 1], [2, 1, 0]]
        self._check_antichains(list(antichains(G)), solution)
        f = lambda x: list(antichains(x))
        G = nx.Graph([(1, 2), (2, 3), (3, 4)])
        assert_raises(nx.NetworkXNotImplemented, f, G)
        G = nx.DiGraph([(1, 2), (2, 3), (3, 1)])
        assert_raises(nx.NetworkXUnfeasible, f, G)

    def test_dag_longest_path(self):
        longest_path = nx.algorithms.dag.dag_longest_path
        G = nx.DiGraph([(1, 2), (2, 3), (2, 4), (3, 5), (5, 6), (5, 7)])
        assert_equal(longest_path(G), [1, 2, 3, 5, 6])
        G = nx.DiGraph(
            [(1, 2), (2, 3), (3, 4), (4, 5), (1, 3), (1, 5), (3, 5)])
        assert_equal(longest_path(G), [1, 2, 3, 4, 5])
        G = nx.Graph()
        assert_raises(nx.NetworkXNotImplemented, longest_path, G)

    def test_dag_longest_path_length(self):
        longest_path_length = nx.algorithms.dag.dag_longest_path_length
        G = nx.DiGraph([(1, 2), (2, 3), (2, 4), (3, 5), (5, 6), (5, 7)])
        assert_equal(longest_path_length(G), 4)
        G = nx.DiGraph(
            [(1, 2), (2, 3), (3, 4), (4, 5), (1, 3), (1, 5), (3, 5)])
        assert_equal(longest_path_length(G), 4)
        G = nx.Graph()
        assert_raises(nx.NetworkXNotImplemented, longest_path_length, G)


def test_is_aperiodic_cycle():
    G = nx.DiGraph()
    G.add_cycle([1, 2, 3, 4])
    assert_false(nx.is_aperiodic(G))


def test_is_aperiodic_cycle2():
    G = nx.DiGraph()
    G.add_cycle([1, 2, 3, 4])
    G.add_cycle([3, 4, 5, 6, 7])
    assert_true(nx.is_aperiodic(G))


def test_is_aperiodic_cycle3():
    G = nx.DiGraph()
    G.add_cycle([1, 2, 3, 4])
    G.add_cycle([3, 4, 5, 6])
    assert_false(nx.is_aperiodic(G))


def test_is_aperiodic_cycle4():
    G = nx.DiGraph()
    G.add_cycle([1, 2, 3, 4])
    G.add_edge(1, 3)
    assert_true(nx.is_aperiodic(G))


def test_is_aperiodic_selfloop():
    G = nx.DiGraph()
    G.add_cycle([1, 2, 3, 4])
    G.add_edge(1, 1)
    assert_true(nx.is_aperiodic(G))


def test_is_aperiodic_raise():
    G = nx.Graph()
    assert_raises(nx.NetworkXError,
                  nx.is_aperiodic,
                  G)


def test_is_aperiodic_bipartite():
    # Bipartite graph
    G = nx.DiGraph(nx.davis_southern_women_graph())
    assert_false(nx.is_aperiodic(G))


def test_is_aperiodic_rary_tree():
    G = nx.full_rary_tree(3, 27, create_using=nx.DiGraph())
    assert_false(nx.is_aperiodic(G))


def test_is_aperiodic_disconnected():
    # disconnected graph
    G = nx.DiGraph()
    G.add_cycle([1, 2, 3, 4])
    G.add_cycle([5, 6, 7, 8])
    assert_false(nx.is_aperiodic(G))
    G.add_edge(1, 3)
    G.add_edge(5, 7)
    assert_true(nx.is_aperiodic(G))


def test_is_aperiodic_disconnected2():
    G = nx.DiGraph()
    G.add_cycle([0, 1, 2])
    G.add_edge(3, 3)
    assert_false(nx.is_aperiodic(G))
