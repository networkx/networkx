from itertools import combinations

from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_in
from nose.tools import assert_raises
from nose.tools import assert_true
from nose.tools import ok_

import networkx as nx
from networkx.testing.utils import assert_edges_equal
from networkx.utils import consume


class TestDagLongestPath(object):
    """Unit tests for computing the longest path in a directed acyclic
    graph.

    """

    def test_unweighted1(self):
        edges = [(1, 2), (2, 3), (2, 4), (3, 5), (5, 6), (3, 7)]
        G = nx.DiGraph(edges)
        assert_equal(nx.dag_longest_path(G), [1, 2, 3, 5, 6])

    def test_unweighted2(self):
        edges = [(1, 2), (2, 3), (3, 4), (4, 5), (1, 3), (1, 5), (3, 5)]
        G = nx.DiGraph(edges)
        assert_equal(nx.dag_longest_path(G), [1, 2, 3, 4, 5])

    def test_weighted(self):
        G = nx.DiGraph()
        edges = [(1, 2, -5), (2, 3, 1), (3, 4, 1), (4, 5, 0), (3, 5, 4),
                 (1, 6, 2)]
        G.add_weighted_edges_from(edges)
        assert_equal(nx.dag_longest_path(G), [2, 3, 5])

    def test_undirected_not_implemented(self):
        G = nx.Graph()
        assert_raises(nx.NetworkXNotImplemented, nx.dag_longest_path, G)

    def test_unorderable_nodes(self):
        """Tests that computing the longest path does not depend on
        nodes being orderable.

        For more information, see issue #1989.

        """
        # TODO In Python 3, instances of the `object` class are
        # unorderable by default, so we wouldn't need to define our own
        # class here, we could just instantiate an instance of the
        # `object` class. However, we still support Python 2; when
        # support for Python 2 is dropped, this test can be simplified
        # by replacing `Unorderable()` by `object()`.
        class Unorderable(object):
            def __lt__(self, other):
                error_msg = "< not supported between instances of " \
                  "{} and {}".format(type(self).__name__, type(other).__name__)
                raise TypeError(error_msg)

        # Create the directed path graph on four nodes in a diamond shape,
        # with nodes represented as (unorderable) Python objects.
        nodes = [Unorderable() for n in range(4)]
        G = nx.DiGraph()
        G.add_edge(nodes[0], nodes[1])
        G.add_edge(nodes[0], nodes[2])
        G.add_edge(nodes[2], nodes[3])
        G.add_edge(nodes[1], nodes[3])

        # this will raise NotImplementedError when nodes need to be ordered
        nx.dag_longest_path(G)


class TestDagLongestPathLength(object):
    """Unit tests for computing the length of a longest path in a
    directed acyclic graph.

    """

    def test_unweighted(self):
        edges = [(1, 2), (2, 3), (2, 4), (3, 5), (5, 6), (5, 7)]
        G = nx.DiGraph(edges)
        assert_equal(nx.dag_longest_path_length(G), 4)

        edges = [(1, 2), (2, 3), (3, 4), (4, 5), (1, 3), (1, 5), (3, 5)]
        G = nx.DiGraph(edges)
        assert_equal(nx.dag_longest_path_length(G), 4)

        # test degenerate graphs
        G = nx.DiGraph()
        G.add_node(1)
        assert_equal(nx.dag_longest_path_length(G), 0)

    def test_undirected_not_implemented(self):
        G = nx.Graph()
        assert_raises(nx.NetworkXNotImplemented, nx.dag_longest_path_length, G)

    def test_weighted(self):
        edges = [(1, 2, -5), (2, 3, 1), (3, 4, 1), (4, 5, 0), (3, 5, 4),
                 (1, 6, 2)]
        G = nx.DiGraph()
        G.add_weighted_edges_from(edges)
        assert_equal(nx.dag_longest_path_length(G), 5)



class TestDAG:

    def setUp(self):
        pass

    def test_topological_sort1(self):
        DG = nx.DiGraph([(1, 2), (1, 3), (2, 3)])

        for algorithm in [nx.topological_sort,
                          nx.lexicographical_topological_sort]:
            assert_equal(tuple(algorithm(DG)), (1, 2, 3))

        DG.add_edge(3, 2)

        for algorithm in [nx.topological_sort,
                          nx.lexicographical_topological_sort]:
            assert_raises(nx.NetworkXUnfeasible, consume, algorithm(DG))

        DG.remove_edge(2, 3)

        for algorithm in [nx.topological_sort,
                          nx.lexicographical_topological_sort]:
            assert_equal(tuple(algorithm(DG)), (1, 3, 2))

        DG.remove_edge(3, 2)

        assert_in(tuple(nx.topological_sort(DG)), {(1, 2, 3), (1, 3, 2)})
        assert_equal(tuple(nx.lexicographical_topological_sort(DG)), (1, 2, 3))

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
        assert_raises(nx.NetworkXUnfeasible, consume, nx.topological_sort(DG))

        assert_false(nx.is_directed_acyclic_graph(DG))

        DG.remove_edge(1, 2)
        consume(nx.topological_sort(DG))
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
        validate(list(nx.topological_sort(DG)))

        DG.add_edge(14, 1)
        assert_raises(nx.NetworkXUnfeasible, consume, nx.topological_sort(DG))

    def test_topological_sort4(self):
        G = nx.Graph()
        G.add_edge(1, 2)
        # Only directed graphs can be topologically sorted.
        assert_raises(nx.NetworkXError, consume, nx.topological_sort(G))

    def test_topological_sort5(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        assert_equal(list(nx.topological_sort(G)), [0, 1])

    def test_topological_sort6(self):
        for algorithm in [nx.topological_sort,
                          nx.lexicographical_topological_sort]:
            def runtime_error():
                DG = nx.DiGraph([(1, 2), (2, 3), (3, 4)])
                first = True
                for x in algorithm(DG):
                    if first:
                        first = False
                        DG.add_edge(5 - x, 5)

            def unfeasible_error():
                DG = nx.DiGraph([(1, 2), (2, 3), (3, 4)])
                first = True
                for x in algorithm(DG):
                    if first:
                        first = False
                        DG.remove_node(4)

            def runtime_error2():
                DG = nx.DiGraph([(1, 2), (2, 3), (3, 4)])
                first = True
                for x in algorithm(DG):
                    if first:
                        first = False
                        DG.remove_node(2)

            assert_raises(RuntimeError, runtime_error)
            assert_raises(RuntimeError, runtime_error2)
            assert_raises(nx.NetworkXUnfeasible, unfeasible_error)

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

    def test_transitive_reduction(self):
        G = nx.DiGraph([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])
        transitive_reduction = nx.algorithms.dag.transitive_reduction
        solution = [(1, 2), (2, 3), (3, 4)]
        assert_edges_equal(transitive_reduction(G).edges(), solution)
        G = nx.DiGraph([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4)])
        transitive_reduction = nx.algorithms.dag.transitive_reduction
        solution = [(1, 2), (2, 3), (2, 4)]
        assert_edges_equal(transitive_reduction(G).edges(), solution)        
        G = nx.Graph([(1, 2), (2, 3), (3, 4)])
        assert_raises(nx.NetworkXNotImplemented, transitive_reduction, G)

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

    def test_lexicographical_topological_sort(self):
        G = nx.DiGraph([(1,2), (2,3), (1,4), (1,5), (2,6)])
        assert_equal(list(nx.lexicographical_topological_sort(G)),
                     [1, 2, 3, 4, 5, 6])
        assert_equal(list(nx.lexicographical_topological_sort(
            G, key=lambda x: x)),
                     [1, 2, 3, 4, 5, 6])
        assert_equal(list(nx.lexicographical_topological_sort(
            G, key=lambda x: -x)),
                     [1, 5, 4, 2, 6, 3])


def test_is_aperiodic_cycle():
    G = nx.DiGraph()
    nx.add_cycle(G, [1, 2, 3, 4])
    assert_false(nx.is_aperiodic(G))


def test_is_aperiodic_cycle2():
    G = nx.DiGraph()
    nx.add_cycle(G, [1, 2, 3, 4])
    nx.add_cycle(G, [3, 4, 5, 6, 7])
    assert_true(nx.is_aperiodic(G))


def test_is_aperiodic_cycle3():
    G = nx.DiGraph()
    nx.add_cycle(G, [1, 2, 3, 4])
    nx.add_cycle(G, [3, 4, 5, 6])
    assert_false(nx.is_aperiodic(G))


def test_is_aperiodic_cycle4():
    G = nx.DiGraph()
    nx.add_cycle(G, [1, 2, 3, 4])
    G.add_edge(1, 3)
    assert_true(nx.is_aperiodic(G))


def test_is_aperiodic_selfloop():
    G = nx.DiGraph()
    nx.add_cycle(G, [1, 2, 3, 4])
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
    nx.add_cycle(G, [1, 2, 3, 4])
    nx.add_cycle(G, [5, 6, 7, 8])
    assert_false(nx.is_aperiodic(G))
    G.add_edge(1, 3)
    G.add_edge(5, 7)
    assert_true(nx.is_aperiodic(G))


def test_is_aperiodic_disconnected2():
    G = nx.DiGraph()
    nx.add_cycle(G, [0, 1, 2])
    G.add_edge(3, 3)
    assert_false(nx.is_aperiodic(G))
