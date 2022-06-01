import pytest
import networkx as nx

from networkx.algorithms import find_cycle
from networkx.algorithms import minimum_cycle_basis
from networkx.algorithms.traversal.edgedfs import FORWARD, REVERSE


class TestCycles:
    @classmethod
    def setup_class(cls):
        G = nx.Graph()
        nx.add_cycle(G, [0, 1, 2, 3])
        nx.add_cycle(G, [0, 3, 4, 5])
        nx.add_cycle(G, [0, 1, 6, 7, 8])
        G.add_edge(8, 9)
        cls.G = G

    def is_cyclic_permutation(self, a, b):
        n = len(a)
        if len(b) != n:
            return False
        l = a + a
        return any(l[i : i + n] == b for i in range(n))

    def test_cycle_basis(self):
        cy = nx.cycle_basis(self.G)
        sort_cy = sorted(sorted(c) for c in cy)
        assert_equal(sort_cy, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5]])

    def test_cycle_basis_alternate_root(self):
        cy = nx.cycle_basis(self.G, 1)
        sort_cy = sorted(sorted(c) for c in cy)
        assert_equal(sort_cy, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5]])

        cy = nx.cycle_basis(self.G, 9)
        sort_cy = sorted(sorted(c) for c in cy)
        assert_equal(sort_cy, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5]])

    def test_cycle_basis_disconnected(self):
        """Tests for cycle basis on disconnected graphs."""
        nx.add_cycle(self.G, "ABC")
        cy = nx.cycle_basis(self.G, 9)
        sort_cy = sorted(sorted(c) for c in cy[:-1]) + [sorted(cy[-1])]
        assert_equal(
            sort_cy, [[0, 1, 2, 3], [0, 1, 6, 7, 8], [0, 3, 4, 5], ["A", "B", "C"]]
        )

    def test_cycle_basis_undirected_multigraph(self):
        """Tests for cycle basis on undirected multigraphs."""
        edges = [(1, 2), (1, 2), (1, 2), (3, 1), (3, 2)]
        G = nx.MultiGraph(edges)
        Z = nx.cycle_basis(G, 3)
        assert_equal(Z, [[1, 2], [1, 2], [1, 2, 3]])

    def test_cycle_basis_undirected_multigraph_data(self):
        """Tests for cycle basis on undirected multigraphs with keys and data."""
        edges = [
            (1, 2, {"val": 10}),
            (1, 2, {"val": 10}),
            (1, 2, {"val": 1}),
            (1, 3, {"val": 0}),
            (3, 2, {"val": 0}),
        ]
        G = nx.MultiGraph(edges)
        Z = nx.cycle_basis(G, 3)
        assert_equal(Z, [[1, 2], [1, 2], [1, 2, 3]])

    def test_cycle_basis2(self):
        with pytest.raises(nx.NetworkXNotImplemented):
            G = nx.DiGraph()
            cy = nx.cycle_basis(G, 0)

    def test_simple_cycles(self):
        edges = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
        G = nx.DiGraph(edges)
        cc = sorted(nx.simple_cycles(G))
        ca = [[0], [0, 1, 2], [0, 2], [1, 2], [2]]
        assert len(cc) == len(ca)
        for c in cc:
            assert any(self.is_cyclic_permutation(c, rc) for rc in ca)

    def test_simple_cycles_graph(self):
        with pytest.raises(nx.NetworkXNotImplemented):
            G = nx.Graph()
            c = sorted(nx.simple_cycles(G))

    def test_unorderable_nodes(self):
        """Tests that computing simple cycles does not depend on
        nodes being orderable.

        For a similar issue with the longest path function for directed
        acyclic graphs, see issue #1989.

        """
        # TODO In Python 3, instances of the `object` class are
        # unorderable by default, so we wouldn't need to define our own
        # class here, we could just instantiate an instance of the
        # `object` class. However, we still support Python 2; when
        # support for Python 2 is dropped, this test can be simplified
        # by replacing `Unorderable()` by `object()`.
        class Unorderable(object):
            def __le__(self):
                raise NotImplemented

            def __ge__(self):
                raise NotImplemented

        # Create the directed path graph on four nodes, with nodes
        # represented as (unorderable) Python objects.
        nodes = [Unorderable() for n in range(4)]
        G = nx.DiGraph()
        nx.add_cycle(G, nodes)
        cycles = list(nx.simple_cycles(G))
        assert_equal(len(cycles), 1)
        assert_true(self.is_cyclic_permutation(cycles[0], nodes))

    def test_disjoint_cycles(self):
        nodes = [1, 2, 3]
        G = nx.DiGraph()
        nx.add_cycle(G, [1, 2, 3])
        c = sorted(nx.simple_cycles(G))
        assert len(c) == 1
        assert self.is_cyclic_permutation(c[0], [1, 2, 3])
        nx.add_cycle(G, [10, 20, 30])
        cc = sorted(nx.simple_cycles(G))
        assert len(cc) == 2
        ca = [[1, 2, 3], [10, 20, 30]]
        for c in cc:
            assert any(self.is_cyclic_permutation(c, rc) for rc in ca)

    def test_empty_graph(self):
        G = nx.DiGraph()
        assert list(nx.simple_cycles(G)) == []

    def test_complete_directed_graphs(self):
        # see table 2 in Johnson's paper
        ncircuits = [1, 5, 20, 84, 409, 2365, 16064]
        for n, c in zip(range(2, 9), ncircuits):
            G = nx.DiGraph(nx.complete_graph(n))
            assert len(list(nx.simple_cycles(G))) == c

    def worst_case_graph(self, k):
        # see figure 1 in Johnson's paper
        # this graph has exactly 3k simple cycles
        G = nx.DiGraph()
        for n in range(2, k + 2):
            G.add_edge(1, n)
            G.add_edge(n, k + 2)
        G.add_edge(2 * k + 1, 1)
        for n in range(k + 2, 2 * k + 2):
            G.add_edge(n, 2 * k + 2)
            G.add_edge(n, n + 1)
        G.add_edge(2 * k + 3, k + 2)
        for n in range(2 * k + 3, 3 * k + 3):
            G.add_edge(2 * k + 2, n)
            G.add_edge(n, 3 * k + 3)
        G.add_edge(3 * k + 3, 2 * k + 2)
        return G

    def test_worst_case_graph(self):
        # see figure 1 in Johnson's paper
        for k in range(3, 10):
            G = self.worst_case_graph(k)
            l = len(list(nx.simple_cycles(G)))
            assert l == 3 * k

    def test_recursive_simple_and_not(self):
        for k in range(2, 10):
            G = self.worst_case_graph(k)
            cc = sorted(nx.simple_cycles(G))
            rcc = sorted(nx.recursive_simple_cycles(G))
            assert len(cc) == len(rcc)
            for c in cc:
                assert any(self.is_cyclic_permutation(c, r) for r in rcc)
            for rc in rcc:
                assert any(self.is_cyclic_permutation(rc, c) for c in cc)

    def test_simple_graph_with_reported_bug(self):
        G = nx.DiGraph()
        edges = [
            (0, 2),
            (0, 3),
            (1, 0),
            (1, 3),
            (2, 1),
            (2, 4),
            (3, 2),
            (3, 4),
            (4, 0),
            (4, 1),
            (4, 5),
            (5, 0),
            (5, 1),
            (5, 2),
            (5, 3),
        ]
        G.add_edges_from(edges)
        cc = sorted(nx.simple_cycles(G))
        assert len(cc) == 26
        rcc = sorted(nx.recursive_simple_cycles(G))
        assert len(cc) == len(rcc)
        for c in cc:
            assert any(self.is_cyclic_permutation(c, rc) for rc in rcc)
        for rc in rcc:
            assert any(self.is_cyclic_permutation(rc, c) for c in cc)


# These tests might fail with hash randomization since they depend on
# edge_dfs. For more information, see the comments in:
#    networkx/algorithms/traversal/tests/test_edgedfs.py
class TestFindCycle:
    @classmethod
    def setup_class(cls):
        cls.nodes = [0, 1, 2, 3]
        cls.edges = [(-1, 0), (0, 1), (1, 0), (1, 0), (2, 1), (3, 1)]

    def test_graph_nocycle(self):
        G = nx.Graph(self.edges)
        pytest.raises(nx.exception.NetworkXNoCycle, find_cycle, G, self.nodes)

    def test_graph_cycle(self):
        G = nx.Graph(self.edges)
        G.add_edge(2, 0)
        x = list(find_cycle(G, self.nodes))
        x_ = [(0, 1), (1, 2), (2, 0)]
        assert x == x_

    def test_graph_orientation_none(self):
        G = nx.Graph(self.edges)
        G.add_edge(2, 0)
        x = list(find_cycle(G, self.nodes, orientation=None))
        x_ = [(0, 1), (1, 2), (2, 0)]
        assert x == x_

    def test_graph_orientation_original(self):
        G = nx.Graph(self.edges)
        G.add_edge(2, 0)
        x = list(find_cycle(G, self.nodes, orientation="original"))
        x_ = [(0, 1, FORWARD), (1, 2, FORWARD), (2, 0, FORWARD)]
        assert x == x_

    def test_digraph(self):
        G = nx.DiGraph(self.edges)
        x = list(find_cycle(G, self.nodes))
        x_ = [(0, 1), (1, 0)]
        assert x == x_

    def test_digraph_orientation_none(self):
        G = nx.DiGraph(self.edges)
        x = list(find_cycle(G, self.nodes, orientation=None))
        x_ = [(0, 1), (1, 0)]
        assert x == x_

    def test_digraph_orientation_original(self):
        G = nx.DiGraph(self.edges)
        x = list(find_cycle(G, self.nodes, orientation="original"))
        x_ = [(0, 1, FORWARD), (1, 0, FORWARD)]
        assert x == x_

    def test_multigraph(self):
        G = nx.MultiGraph(self.edges)
        x = list(find_cycle(G, self.nodes))
        x_ = [(0, 1, 0), (1, 0, 1)]  # or (1, 0, 2)
        # Hash randomization...could be any edge.
        assert x[0] == x_[0]
        assert x[1][:2] == x_[1][:2]

    def test_multidigraph(self):
        G = nx.MultiDiGraph(self.edges)
        x = list(find_cycle(G, self.nodes))
        x_ = [(0, 1, 0), (1, 0, 0)]  # (1, 0, 1)
        assert x[0] == x_[0]
        assert x[1][:2] == x_[1][:2]

    def test_digraph_ignore(self):
        G = nx.DiGraph(self.edges)
        x = list(find_cycle(G, self.nodes, orientation="ignore"))
        x_ = [(0, 1, FORWARD), (1, 0, FORWARD)]
        assert x == x_

    def test_digraph_reverse(self):
        G = nx.DiGraph(self.edges)
        x = list(find_cycle(G, self.nodes, orientation="reverse"))
        x_ = [(1, 0, REVERSE), (0, 1, REVERSE)]
        assert x == x_

    def test_multidigraph_ignore(self):
        G = nx.MultiDiGraph(self.edges)
        x = list(find_cycle(G, self.nodes, orientation="ignore"))
        x_ = [(0, 1, 0, FORWARD), (1, 0, 0, FORWARD)]  # or (1, 0, 1, 1)
        assert x[0] == x_[0]
        assert x[1][:2] == x_[1][:2]
        assert x[1][3] == x_[1][3]

    def test_multidigraph_ignore2(self):
        # Loop traversed an edge while ignoring its orientation.
        G = nx.MultiDiGraph([(0, 1), (1, 2), (1, 2)])
        x = list(find_cycle(G, [0, 1, 2], orientation="ignore"))
        x_ = [(1, 2, 0, FORWARD), (1, 2, 1, REVERSE)]
        assert x == x_

    def test_multidigraph_original(self):
        # Node 2 doesn't need to be searched again from visited from 4.
        # The goal here is to cover the case when 2 to be researched from 4,
        # when 4 is visited from the first time (so we must make sure that 4
        # is not visited from 2, and hence, we respect the edge orientation).
        G = nx.MultiDiGraph([(0, 1), (1, 2), (2, 3), (4, 2)])
        pytest.raises(
            nx.exception.NetworkXNoCycle,
            find_cycle,
            G,
            [0, 1, 2, 3, 4],
            orientation="original",
        )

    def test_dag(self):
        G = nx.DiGraph([(0, 1), (0, 2), (1, 2)])
        pytest.raises(
            nx.exception.NetworkXNoCycle, find_cycle, G, orientation="original"
        )
        x = list(find_cycle(G, orientation="ignore"))
        assert x == [(0, 1, FORWARD), (1, 2, FORWARD), (0, 2, REVERSE)]

    def test_prev_explored(self):
        # https://github.com/networkx/networkx/issues/2323

        G = nx.DiGraph()
        G.add_edges_from([(1, 0), (2, 0), (1, 2), (2, 1)])
        pytest.raises(nx.NetworkXNoCycle, find_cycle, G, source=0)
        x = list(nx.find_cycle(G, 1))
        x_ = [(1, 2), (2, 1)]
        assert x == x_

        x = list(nx.find_cycle(G, 2))
        x_ = [(2, 1), (1, 2)]
        assert x == x_

        x = list(nx.find_cycle(G))
        x_ = [(1, 2), (2, 1)]
        assert x == x_

    def test_no_cycle(self):
        # https://github.com/networkx/networkx/issues/2439

        G = nx.DiGraph()
        G.add_edges_from([(1, 2), (2, 0), (3, 1), (3, 2)])
        pytest.raises(nx.NetworkXNoCycle, find_cycle, G, source=0)
        pytest.raises(nx.NetworkXNoCycle, find_cycle, G)


def assert_basis_equal(a, b):
    assert sorted(a) == sorted(b)


class TestMinimumCycles:
    @classmethod
    def setup_class(cls):
        T = nx.Graph()
        nx.add_cycle(T, [1, 2, 3, 4], weight=1)
        T.add_edge(2, 4, weight=5)
        cls.diamond_graph = T

    def test_unweighted_diamond(self):
        mcb = minimum_cycle_basis(self.diamond_graph)
        assert_basis_equal([sorted(c) for c in mcb], [[1, 2, 4], [2, 3, 4]])

    def test_weighted_diamond(self):
        mcb = minimum_cycle_basis(self.diamond_graph, weight="weight")
        assert_basis_equal([sorted(c) for c in mcb], [[1, 2, 4], [1, 2, 3, 4]])

    def test_dimensionality(self):
        # checks |MCB|=|E|-|V|+|NC|
        ntrial = 10
        for _ in range(ntrial):
            rg = nx.erdos_renyi_graph(10, 0.3)
            nnodes = rg.number_of_nodes()
            nedges = rg.number_of_edges()
            ncomp = nx.number_connected_components(rg)

            dim_mcb = len(minimum_cycle_basis(rg))
            assert dim_mcb == nedges - nnodes + ncomp

    def test_complete_graph(self):
        cg = nx.complete_graph(5)
        mcb = minimum_cycle_basis(cg)
        assert all([len(cycle) == 3 for cycle in mcb])

    def test_tree_graph(self):
        tg = nx.balanced_tree(3, 3)
        assert not minimum_cycle_basis(tg)


class TestCycleBasisMatrix:
    @classmethod
    def setupClass(cls):
        global np
        try:
            import scipy as np
        except ImportError:
            raise SkipTest("Scipy not available.")

    def test_undirected_multigraph(self):
        # Testing undirected multigraph
        cables = [(1, 2), (1, 2), (1, 2), (3, 1), (3, 2)]
        G = nx.MultiGraph(cables)
        M = nx.cycle_basis_matrix(G)
        assert_true(
            (
                M
                == np.array([[-1, -1, -1], [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 1]])
            ).all()
        )

    def test_undirected_multigraph_data(self):
        # Testing undirected multigraph with keys and data
        cables = [
            (1, 2, {"val": 10}),
            (1, 2, {"val": 10}),
            (1, 2, {"val": 1}),
            (1, 3, {"val": 0}),
            (3, 2, {"val": 0}),
        ]
        G = nx.MultiGraph(cables)
        M = nx.cycle_basis_matrix(G)
        assert_equal(
            M, np.array([-1, -1, -1], [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 1])
        )

    def test_cycle_basis_matrix(self):
        # Testing sparse matrix
        with pytest.raises(nx.NetworkXNotImplemented):
            G = nx.Graph()
            cy = nx.cycle_basis_matrix(G, sparse=True)

    def test_cycle_basis_matrix(self):
        # Testing directed multigraph
        with pytest.raises(nx.NetworkXNotImplemented):
            cables = [(1, 2), (1, 2), (1, 2), (1, 3), (3, 2)]
            G = nx.MultiDiGraph(cables)
            M = nx.cycle_basis_matrix(G)
