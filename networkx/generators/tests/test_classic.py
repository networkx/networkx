"""
====================
Generators - Classic
====================

Unit tests for various classic graph generators in generators/classic.py
"""
import itertools
import typing
from contextlib import nullcontext as does_not_raise

import pytest

import networkx as nx
from networkx.algorithms.isomorphism.isomorph import graph_could_be_isomorphic
from networkx.utils import edges_equal, nodes_equal

is_isomorphic = graph_could_be_isomorphic


class TestGeneratorClassic:
    def test_balanced_tree(self):
        # balanced_tree(r,h) is a tree with (r**(h+1)-1)/(r-1) edges
        for r, h in [(2, 2), (3, 3), (6, 2)]:
            t = nx.balanced_tree(r, h)
            order = t.order()
            assert order == (r ** (h + 1) - 1) / (r - 1)
            assert nx.is_connected(t)
            assert t.size() == order - 1
            dh = nx.degree_histogram(t)
            assert dh[0] == 0  # no nodes of 0
            assert dh[1] == r**h  # nodes of degree 1 are leaves
            assert dh[r] == 1  # root is degree r
            assert dh[r + 1] == order - r**h - 1  # everyone else is degree r+1
            assert len(dh) == r + 2

    def test_balanced_tree_star(self):
        # balanced_tree(r,1) is the r-star
        t = nx.balanced_tree(r=2, h=1)
        assert is_isomorphic(t, nx.star_graph(2))
        t = nx.balanced_tree(r=5, h=1)
        assert is_isomorphic(t, nx.star_graph(5))
        t = nx.balanced_tree(r=10, h=1)
        assert is_isomorphic(t, nx.star_graph(10))

    def test_balanced_tree_path(self):
        """Tests that the balanced tree with branching factor one is the
        path graph.

        """
        # A tree of height four has five levels.
        T = nx.balanced_tree(1, 4)
        P = nx.path_graph(5)
        assert is_isomorphic(T, P)

    def test_full_rary_tree(self):
        r = 2
        n = 9
        t = nx.full_rary_tree(r, n)
        assert t.order() == n
        assert nx.is_connected(t)
        dh = nx.degree_histogram(t)
        assert dh[0] == 0  # no nodes of 0
        assert dh[1] == 5  # nodes of degree 1 are leaves
        assert dh[r] == 1  # root is degree r
        assert dh[r + 1] == 9 - 5 - 1  # everyone else is degree r+1
        assert len(dh) == r + 2

    def test_full_rary_tree_balanced(self):
        t = nx.full_rary_tree(2, 15)
        th = nx.balanced_tree(2, 3)
        assert is_isomorphic(t, th)

    def test_full_rary_tree_path(self):
        t = nx.full_rary_tree(1, 10)
        assert is_isomorphic(t, nx.path_graph(10))

    def test_full_rary_tree_empty(self):
        t = nx.full_rary_tree(0, 10)
        assert is_isomorphic(t, nx.empty_graph(10))
        t = nx.full_rary_tree(3, 0)
        assert is_isomorphic(t, nx.empty_graph(0))

    def test_full_rary_tree_3_20(self):
        t = nx.full_rary_tree(3, 20)
        assert t.order() == 20

    @pytest.mark.parametrize("m1", range(2, 10))
    @pytest.mark.parametrize("m2", range(10))
    def test_barbell_graph_n_nodes_edges(self, m1, m2):
        # number of nodes = 2*m1 + m2 (2 m1-complete graphs + m2-path)
        # number of edges = 2*(nx.number_of_edges(m1-complete graph)) + m2 + 1
        b = nx.barbell_graph(m1, m2)
        assert nx.number_of_nodes(b) == 2 * m1 + m2
        assert nx.number_of_edges(b) == m1 * (m1 - 1) + m2 + 1

    @pytest.mark.parametrize(
        "m1,m2,expectation",
        [
            (-1, -1, pytest.raises(nx.NetworkXError)),  # m1 < 2
            (-1, 0, pytest.raises(nx.NetworkXError)),  # m1 < 2
            (-1, 1, pytest.raises(nx.NetworkXError)),  # m1 < 2
            (0, -1, pytest.raises(nx.NetworkXError)),  # m1 < 2
            (0, 0, pytest.raises(nx.NetworkXError)),  # m1 < 2
            (0, 1, pytest.raises(nx.NetworkXError)),  # m1 < 2
            (1, -1, pytest.raises(nx.NetworkXError)),  # m1 < 2
            (1, 0, pytest.raises(nx.NetworkXError)),  # m1 < 2
            (1, 1, pytest.raises(nx.NetworkXError)),  # m1 < 2
            (2, -1, pytest.raises(nx.NetworkXError)),  # m2 < 0
            (2, 0, does_not_raise()),  # ok
            (2, 1, does_not_raise()),  # ok
        ],
    )
    def test_barbell_graph_m1_m2_exceptions(self, m1, m2, expectation):
        with expectation:
            nx.barbell_graph(m1, m2)

    @pytest.mark.parametrize(
        "create_using,expectation",
        [
            (nx.Graph, does_not_raise()),  # ok
            (nx.DiGraph, pytest.raises(nx.NetworkXError)),  # directed
            (nx.MultiGraph, does_not_raise()),  # ok
            (nx.MultiDiGraph, pytest.raises(nx.NetworkXError)),  # directed
        ],
    )
    def test_barbell_graph_create_using_exceptions(self, create_using, expectation):
        with expectation:
            nx.barbell_graph(5, 2, create_using=create_using)

    @pytest.mark.parametrize("m2", (0, 5))
    def test_barbell_graph(self, m2):
        # nx.barbell_graph(2, m) = nx.path_graph(m + 4)
        b = nx.barbell_graph(2, m2)
        assert is_isomorphic(b, nx.path_graph(m2 + 4))

    @pytest.mark.parametrize("m1", (2, 5))
    @pytest.mark.parametrize("m2", (0, 5))
    def test_barbell_graph_multigraph(self, m1, m2):
        b = nx.barbell_graph(m1, m2)
        mb = nx.barbell_graph(m1, m2, create_using=nx.MultiGraph())
        assert edges_equal(mb.edges(), b.edges())

    def test_binomial_tree(self):
        graphs = (None, nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)
        for create_using in graphs:
            for n in range(4):
                b = nx.binomial_tree(n, create_using)
                assert nx.number_of_nodes(b) == 2**n
                assert nx.number_of_edges(b) == (2**n - 1)

    def test_complete_graph(self):
        # complete_graph(m) is a connected graph with
        # m nodes and  m*(m+1)/2 edges
        for m in [0, 1, 3, 5]:
            g = nx.complete_graph(m)
            assert nx.number_of_nodes(g) == m
            assert nx.number_of_edges(g) == m * (m - 1) // 2

        mg = nx.complete_graph(m, create_using=nx.MultiGraph)
        assert edges_equal(mg.edges(), g.edges())

        g = nx.complete_graph("abc")
        assert nodes_equal(g.nodes(), ["a", "b", "c"])
        assert g.size() == 3

        # creates a self-loop... should it? <backward compatible says yes>
        g = nx.complete_graph("abcb")
        assert nodes_equal(g.nodes(), ["a", "b", "c"])
        assert g.size() == 4

        g = nx.complete_graph("abcb", create_using=nx.MultiGraph)
        assert nodes_equal(g.nodes(), ["a", "b", "c"])
        assert g.size() == 6

    def test_complete_digraph(self):
        # complete_graph(m) is a connected graph with
        # m nodes and  m*(m+1)/2 edges
        for m in [0, 1, 3, 5]:
            g = nx.complete_graph(m, create_using=nx.DiGraph)
            assert nx.number_of_nodes(g) == m
            assert nx.number_of_edges(g) == m * (m - 1)

        g = nx.complete_graph("abc", create_using=nx.DiGraph)
        assert len(g) == 3
        assert g.size() == 6
        assert g.is_directed()

    def test_circular_ladder_graph(self):
        G = nx.circular_ladder_graph(5)
        pytest.raises(
            nx.NetworkXError, nx.circular_ladder_graph, 5, create_using=nx.DiGraph
        )
        mG = nx.circular_ladder_graph(5, create_using=nx.MultiGraph)
        assert edges_equal(mG.edges(), G.edges())

    def test_circulant_graph(self):
        # Ci_n(1) is the cycle graph for all n
        Ci6_1 = nx.circulant_graph(6, [1])
        C6 = nx.cycle_graph(6)
        assert edges_equal(Ci6_1.edges(), C6.edges())

        # Ci_n(1, 2, ..., n div 2) is the complete graph for all n
        Ci7 = nx.circulant_graph(7, [1, 2, 3])
        K7 = nx.complete_graph(7)
        assert edges_equal(Ci7.edges(), K7.edges())

        # Ci_6(1, 3) is K_3,3 i.e. the utility graph
        Ci6_1_3 = nx.circulant_graph(6, [1, 3])
        K3_3 = nx.complete_bipartite_graph(3, 3)
        assert is_isomorphic(Ci6_1_3, K3_3)

    def test_cycle_graph(self):
        G = nx.cycle_graph(4)
        assert edges_equal(G.edges(), [(0, 1), (0, 3), (1, 2), (2, 3)])
        mG = nx.cycle_graph(4, create_using=nx.MultiGraph)
        assert edges_equal(mG.edges(), [(0, 1), (0, 3), (1, 2), (2, 3)])
        G = nx.cycle_graph(4, create_using=nx.DiGraph)
        assert not G.has_edge(2, 1)
        assert G.has_edge(1, 2)
        assert G.is_directed()

        G = nx.cycle_graph("abc")
        assert len(G) == 3
        assert G.size() == 3
        G = nx.cycle_graph("abcb")
        assert len(G) == 3
        assert G.size() == 2
        g = nx.cycle_graph("abc", nx.DiGraph)
        assert len(g) == 3
        assert g.size() == 3
        assert g.is_directed()
        g = nx.cycle_graph("abcb", nx.DiGraph)
        assert len(g) == 3
        assert g.size() == 4

    def test_dorogovtsev_goltsev_mendes_graph(self):
        G = nx.dorogovtsev_goltsev_mendes_graph(0)
        assert edges_equal(G.edges(), [(0, 1)])
        assert nodes_equal(list(G), [0, 1])
        G = nx.dorogovtsev_goltsev_mendes_graph(1)
        assert edges_equal(G.edges(), [(0, 1), (0, 2), (1, 2)])
        assert nx.average_clustering(G) == 1.0
        assert sorted(nx.triangles(G).values()) == [1, 1, 1]
        G = nx.dorogovtsev_goltsev_mendes_graph(10)
        assert nx.number_of_nodes(G) == 29526
        assert nx.number_of_edges(G) == 59049
        assert G.degree(0) == 1024
        assert G.degree(1) == 1024
        assert G.degree(2) == 1024

        pytest.raises(
            nx.NetworkXError,
            nx.dorogovtsev_goltsev_mendes_graph,
            7,
            create_using=nx.DiGraph,
        )
        pytest.raises(
            nx.NetworkXError,
            nx.dorogovtsev_goltsev_mendes_graph,
            7,
            create_using=nx.MultiGraph,
        )

    def test_create_using(self):
        G = nx.empty_graph()
        assert isinstance(G, nx.Graph)
        pytest.raises(TypeError, nx.empty_graph, create_using=0.0)
        pytest.raises(TypeError, nx.empty_graph, create_using="Graph")

        G = nx.empty_graph(create_using=nx.MultiGraph)
        assert isinstance(G, nx.MultiGraph)
        G = nx.empty_graph(create_using=nx.DiGraph)
        assert isinstance(G, nx.DiGraph)

        G = nx.empty_graph(create_using=nx.DiGraph, default=nx.MultiGraph)
        assert isinstance(G, nx.DiGraph)
        G = nx.empty_graph(create_using=None, default=nx.MultiGraph)
        assert isinstance(G, nx.MultiGraph)
        G = nx.empty_graph(default=nx.MultiGraph)
        assert isinstance(G, nx.MultiGraph)

        G = nx.path_graph(5)
        H = nx.empty_graph(create_using=G)
        assert not H.is_multigraph()
        assert not H.is_directed()
        assert len(H) == 0
        assert G is H

        H = nx.empty_graph(create_using=nx.MultiGraph())
        assert H.is_multigraph()
        assert not H.is_directed()
        assert G is not H

        # test for subclasses that also use typing.Protocol. See gh-6243
        class Mixin(typing.Protocol):
            pass

        class MyGraph(Mixin, nx.DiGraph):
            pass

        G = nx.empty_graph(create_using=MyGraph)

    def test_empty_graph(self):
        G = nx.empty_graph()
        assert nx.number_of_nodes(G) == 0
        G = nx.empty_graph(42)
        assert nx.number_of_nodes(G) == 42
        assert nx.number_of_edges(G) == 0

        G = nx.empty_graph("abc")
        assert len(G) == 3
        assert G.size() == 0

        # create empty digraph
        G = nx.empty_graph(42, create_using=nx.DiGraph(name="duh"))
        assert nx.number_of_nodes(G) == 42
        assert nx.number_of_edges(G) == 0
        assert isinstance(G, nx.DiGraph)

        # create empty multigraph
        G = nx.empty_graph(42, create_using=nx.MultiGraph(name="duh"))
        assert nx.number_of_nodes(G) == 42
        assert nx.number_of_edges(G) == 0
        assert isinstance(G, nx.MultiGraph)

        # create empty graph from another
        pete = nx.petersen_graph()
        G = nx.empty_graph(42, create_using=pete)
        assert nx.number_of_nodes(G) == 42
        assert nx.number_of_edges(G) == 0
        assert isinstance(G, nx.Graph)

    def test_ladder_graph(self):
        for i, G in [
            (0, nx.empty_graph(0)),
            (1, nx.path_graph(2)),
            (2, nx.hypercube_graph(2)),
            (10, nx.grid_graph([2, 10])),
        ]:
            assert is_isomorphic(nx.ladder_graph(i), G)

        pytest.raises(nx.NetworkXError, nx.ladder_graph, 2, create_using=nx.DiGraph)

        g = nx.ladder_graph(2)
        mg = nx.ladder_graph(2, create_using=nx.MultiGraph)
        assert edges_equal(mg.edges(), g.edges())

    @pytest.mark.parametrize(("m", "n"), [(3, 5), (4, 10), (3, 20)])
    def test_lollipop_graph_right_sizes(self, m, n):
        G = nx.lollipop_graph(m, n)
        assert nx.number_of_nodes(G) == m + n
        assert nx.number_of_edges(G) == m * (m - 1) / 2 + n

    @pytest.mark.parametrize(("m", "n"), [("ab", ""), ("abc", "defg")])
    def test_lollipop_graph_size_node_sequence(self, m, n):
        G = nx.lollipop_graph(m, n)
        assert nx.number_of_nodes(G) == len(m) + len(n)
        assert nx.number_of_edges(G) == len(m) * (len(m) - 1) / 2 + len(n)

    @pytest.mark.parametrize(
        ("m", "n", "expectation"),
        [
            (-1, -1, pytest.raises(nx.NetworkXError)),  # m < 2
            (-1, 0, pytest.raises(nx.NetworkXError)),  # m < 2
            (-1, "", pytest.raises(nx.NetworkXError)),  # m < 2
            (-1, 1, pytest.raises(nx.NetworkXError)),  # m < 2
            (-1, "a", pytest.raises(nx.NetworkXError)),  # m < 2
            (0, -1, pytest.raises(nx.NetworkXError)),  # m < 2
            (0, 0, pytest.raises(nx.NetworkXError)),  # m < 2
            (0, "", pytest.raises(nx.NetworkXError)),  # m < 2
            (0, 1, pytest.raises(nx.NetworkXError)),  # m < 2
            (0, "a", pytest.raises(nx.NetworkXError)),  # m < 2
            ("", -1, pytest.raises(nx.NetworkXError)),  # m < 2
            ("", 0, pytest.raises(nx.NetworkXError)),  # m < 2
            ("", "", pytest.raises(nx.NetworkXError)),  # m < 2
            ("", 1, pytest.raises(nx.NetworkXError)),  # m < 2
            ("", "a", pytest.raises(nx.NetworkXError)),  # m < 2
            (1, -1, pytest.raises(nx.NetworkXError)),  # m < 2
            (1, 0, pytest.raises(nx.NetworkXError)),  # m < 2
            (1, "", pytest.raises(nx.NetworkXError)),  # m < 2
            (1, 1, pytest.raises(nx.NetworkXError)),  # m < 2
            (1, "a", pytest.raises(nx.NetworkXError)),  # m < 2
            ("a", -1, pytest.raises(nx.NetworkXError)),  # m < 2
            ("a", 0, pytest.raises(nx.NetworkXError)),  # m < 2
            ("a", "", pytest.raises(nx.NetworkXError)),  # m < 2
            ("a", 1, pytest.raises(nx.NetworkXError)),  # m < 2
            ("a", "a", pytest.raises(nx.NetworkXError)),  # m < 2
            ("a", "b", pytest.raises(nx.NetworkXError)),  # m < 2
            (2, -1, pytest.raises(nx.NetworkXError)),  # n < 0
            (2, 0, does_not_raise()),  # ok
            (2, "", does_not_raise()),  # ok
            (2, 1, does_not_raise()),  # ok
            (2, "a", does_not_raise()),  # ok
            (2, "ab", does_not_raise()),  # ok
            (2, "aa", pytest.raises(nx.NetworkXError)),  # duplicate node
            ("ab", -1, pytest.raises(nx.NetworkXError)),  # n < 0
            ("ab", 0, does_not_raise()),  # ok
            ("ab", "", does_not_raise()),  # ok
            ("ab", 1, does_not_raise()),  # ok
            ("ab", "c", does_not_raise()),  # ok
            ("ab", "a", pytest.raises(nx.NetworkXError)),  # duplicate node
            ("aa", "b", pytest.raises(nx.NetworkXError)),  # duplicate node
            ("aa", "bb", pytest.raises(nx.NetworkXError)),  # duplicate node
        ],
    )
    def test_lollipop_graph_exceptions_m_n(self, m, n, expectation):
        with expectation:
            nx.lollipop_graph(m, n)

    @pytest.mark.parametrize(
        ("create_using", "expectation"),
        [
            (nx.Graph, does_not_raise()),  # ok
            (nx.Graph([(0, 1)]), does_not_raise()),  # ok
            (nx.DiGraph, pytest.raises(nx.NetworkXError)),  # directed
            (nx.DiGraph([(0, 1)]), pytest.raises(nx.NetworkXError)),  # directed
            (nx.MultiGraph, does_not_raise()),  # ok
            (nx.MultiGraph([(0, 1)]), does_not_raise()),  # ok
            (nx.MultiDiGraph, pytest.raises(nx.NetworkXError)),  # directed
            (nx.MultiDiGraph([(0, 1)]), pytest.raises(nx.NetworkXError)),  # directed
        ],
    )
    def test_lollipop_graph_exceptions_create_using(self, create_using, expectation):
        with expectation:
            nx.lollipop_graph(2, 20, create_using=create_using)

    @pytest.mark.parametrize("m", [2, "ab"])
    @pytest.mark.parametrize("n", range(20))
    def test_lollipop_graph_same_as_path_when_m1_is_2(self, m, n):
        G = nx.lollipop_graph(m, n)
        assert is_isomorphic(G, nx.path_graph(n + 2))

    @pytest.mark.parametrize("m", range(2, 6))
    @pytest.mark.parametrize("n", [0, 5, 10, 20])
    @pytest.mark.parametrize("create_using", [nx.MultiGraph, nx.MultiGraph([(0, 1)])])
    def test_lollipop_graph_for_multigraph(self, m, n, create_using):
        G = nx.lollipop_graph(m, n)
        MG = nx.lollipop_graph(m, n, create_using=create_using)
        assert edges_equal(MG.edges(), G.edges())

    @pytest.mark.parametrize(
        ("m", "n"),
        [(4, "abc"), ("abcd", 3), ([1, 2, 3, 4], "abc"), ("abcd", [1, 2, 3])],
    )
    def test_lollipop_graph_mixing_input_types(self, m, n):
        expected = nx.compose(nx.complete_graph(4), nx.path_graph(range(100, 103)))
        expected.add_edge(0, 100)  # Connect complete graph and path graph
        assert is_isomorphic(nx.lollipop_graph(m, n), expected)

    def test_lollipop_graph_non_builtin_ints(self):
        np = pytest.importorskip("numpy")
        G = nx.lollipop_graph(np.int32(4), np.int64(3))
        expected = nx.compose(nx.complete_graph(4), nx.path_graph(range(100, 103)))
        expected.add_edge(0, 100)  # Connect complete graph and path graph
        assert is_isomorphic(G, expected)

    def test_null_graph(self):
        assert nx.number_of_nodes(nx.null_graph()) == 0

    def test_path_graph(self):
        p = nx.path_graph(0)
        assert is_isomorphic(p, nx.null_graph())

        p = nx.path_graph(1)
        assert is_isomorphic(p, nx.empty_graph(1))

        p = nx.path_graph(10)
        assert nx.is_connected(p)
        assert sorted(d for n, d in p.degree()) == [1, 1, 2, 2, 2, 2, 2, 2, 2, 2]
        assert p.order() - 1 == p.size()

        dp = nx.path_graph(3, create_using=nx.DiGraph)
        assert dp.has_edge(0, 1)
        assert not dp.has_edge(1, 0)

        mp = nx.path_graph(10, create_using=nx.MultiGraph)
        assert edges_equal(mp.edges(), p.edges())

        G = nx.path_graph("abc")
        assert len(G) == 3
        assert G.size() == 2
        G = nx.path_graph("abcb")
        assert len(G) == 3
        assert G.size() == 2
        g = nx.path_graph("abc", nx.DiGraph)
        assert len(g) == 3
        assert g.size() == 2
        assert g.is_directed()
        g = nx.path_graph("abcb", nx.DiGraph)
        assert len(g) == 3
        assert g.size() == 3

        G = nx.path_graph((1, 2, 3, 2, 4))
        assert G.has_edge(2, 4)

    def test_star_graph(self):
        assert is_isomorphic(nx.star_graph(""), nx.empty_graph(0))
        assert is_isomorphic(nx.star_graph([]), nx.empty_graph(0))
        assert is_isomorphic(nx.star_graph(0), nx.empty_graph(1))
        assert is_isomorphic(nx.star_graph(1), nx.path_graph(2))
        assert is_isomorphic(nx.star_graph(2), nx.path_graph(3))
        assert is_isomorphic(nx.star_graph(5), nx.complete_bipartite_graph(1, 5))

        s = nx.star_graph(10)
        assert sorted(d for n, d in s.degree()) == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10]

        pytest.raises(nx.NetworkXError, nx.star_graph, 10, create_using=nx.DiGraph)

        ms = nx.star_graph(10, create_using=nx.MultiGraph)
        assert edges_equal(ms.edges(), s.edges())

        G = nx.star_graph("abc")
        assert len(G) == 3
        assert G.size() == 2

        G = nx.star_graph("abcb")
        assert len(G) == 3
        assert G.size() == 2
        G = nx.star_graph("abcb", create_using=nx.MultiGraph)
        assert len(G) == 3
        assert G.size() == 3

        G = nx.star_graph("abcdefg")
        assert len(G) == 7
        assert G.size() == 6

    def test_non_int_integers_for_star_graph(self):
        np = pytest.importorskip("numpy")
        G = nx.star_graph(np.int32(3))
        assert len(G) == 4
        assert G.size() == 3

    @pytest.mark.parametrize(("m", "n"), [(3, 0), (3, 5), (4, 10), (3, 20)])
    def test_tadpole_graph_right_sizes(self, m, n):
        G = nx.tadpole_graph(m, n)
        assert nx.number_of_nodes(G) == m + n
        assert nx.number_of_edges(G) == m + n - (m == 2)

    @pytest.mark.parametrize(("m", "n"), [("ab", ""), ("ab", "c"), ("abc", "defg")])
    def test_tadpole_graph_size_node_sequences(self, m, n):
        G = nx.tadpole_graph(m, n)
        assert nx.number_of_nodes(G) == len(m) + len(n)
        assert nx.number_of_edges(G) == len(m) + len(n) - (len(m) == 2)

    def test_tadpole_graph_exceptions(self):
        # Raise NetworkXError if m<2
        pytest.raises(nx.NetworkXError, nx.tadpole_graph, -1, 3)
        pytest.raises(nx.NetworkXError, nx.tadpole_graph, 0, 3)
        pytest.raises(nx.NetworkXError, nx.tadpole_graph, 1, 3)

        # Raise NetworkXError if n<0
        pytest.raises(nx.NetworkXError, nx.tadpole_graph, 5, -2)

        # Raise NetworkXError for digraphs
        with pytest.raises(nx.NetworkXError):
            nx.tadpole_graph(2, 20, create_using=nx.DiGraph)
        with pytest.raises(nx.NetworkXError):
            nx.tadpole_graph(2, 20, create_using=nx.MultiDiGraph)

    @pytest.mark.parametrize(("m", "n"), [(2, 0), (2, 5), (2, 10), ("ab", 20)])
    def test_tadpole_graph_same_as_path_when_m_is_2(self, m, n):
        G = nx.tadpole_graph(m, n)
        assert is_isomorphic(G, nx.path_graph(n + 2))

    @pytest.mark.parametrize("m", [4, 7])
    def test_tadpole_graph_same_as_cycle_when_m2_is_0(self, m):
        G = nx.tadpole_graph(m, 0)
        assert is_isomorphic(G, nx.cycle_graph(m))

    def test_tadpole_graph_for_multigraph(self):
        G = nx.tadpole_graph(5, 20)
        MG = nx.tadpole_graph(5, 20, create_using=nx.MultiGraph)
        assert edges_equal(MG.edges(), G.edges())

    @pytest.mark.parametrize(
        ("m", "n"),
        [(4, "abc"), ("abcd", 3), ([1, 2, 3, 4], "abc"), ("abcd", [1, 2, 3])],
    )
    def test_tadpole_graph_mixing_input_types(self, m, n):
        expected = nx.compose(nx.cycle_graph(4), nx.path_graph(range(100, 103)))
        expected.add_edge(0, 100)  # Connect cycle and path
        assert is_isomorphic(nx.tadpole_graph(m, n), expected)

    def test_tadpole_graph_non_builtin_integers(self):
        np = pytest.importorskip("numpy")
        G = nx.tadpole_graph(np.int32(4), np.int64(3))
        expected = nx.compose(nx.cycle_graph(4), nx.path_graph(range(100, 103)))
        expected.add_edge(0, 100)  # Connect cycle and path
        assert is_isomorphic(G, expected)

    def test_trivial_graph(self):
        assert nx.number_of_nodes(nx.trivial_graph()) == 1

    @pytest.mark.parametrize("n", (10, 20))
    @pytest.mark.parametrize("r", (1, 10))
    def test_turan_graph(self, n, r):
        G = nx.turan_graph(n, r)
        s = n % r
        assert (
            nx.number_of_edges(G)
            == (r - 1) * (n**2 - s**2) // (2 * r) + s * (s - 1) / 2
        )
        assert is_isomorphic(
            G,
            nx.complete_multipartite_graph(
                *((n % r) * [(n // r) + 1] + (r - (n % r)) * [n // r])
            ),
        )

    @pytest.mark.parametrize("r", [2, 3, 4, 5, 6, 10, 12, 15, 20, 30])
    def test_turan_graph_r_divides_n_strongly_regular(self, r):
        G = nx.turan_graph(60, r)
        assert nx.is_strongly_regular(G)

    @pytest.mark.parametrize(
        ("n", "r", "expectation"),
        [
            (-1, 1, pytest.raises(nx.NetworkXError)),  # n < 1
            (-1, 0, pytest.raises(nx.NetworkXError)),  # n < 1
            (-1, 1, pytest.raises(nx.NetworkXError)),  # n < 1
            (0, -1, pytest.raises(nx.NetworkXError)),  # n < 1
            (0, 0, pytest.raises(nx.NetworkXError)),  # n < 1
            (0, 1, pytest.raises(nx.NetworkXError)),  # n < 1
            (1, -1, pytest.raises(nx.NetworkXError)),  # r < 1
            (1, 0, pytest.raises(nx.NetworkXError)),  # r < 1
            (1, 1, does_not_raise()),  # ok
            (1, 2, pytest.raises(nx.NetworkXError)),  # r > n
            (2, 1, does_not_raise()),  # ok
            (2, 2, does_not_raise()),  # ok
            (2, 3, pytest.raises(nx.NetworkXError)),  # r > n
        ],
    )
    def test_turan_graph_exceptions(self, n, r, expectation):
        with expectation:
            nx.turan_graph(n, r)

    def test_wheel_graph(self):
        for n, G in [
            ("", nx.null_graph()),
            (0, nx.null_graph()),
            (1, nx.empty_graph(1)),
            (2, nx.path_graph(2)),
            (3, nx.complete_graph(3)),
            (4, nx.complete_graph(4)),
        ]:
            g = nx.wheel_graph(n)
            assert is_isomorphic(g, G)

        g = nx.wheel_graph(10)
        assert sorted(d for n, d in g.degree()) == [3, 3, 3, 3, 3, 3, 3, 3, 3, 9]

        pytest.raises(nx.NetworkXError, nx.wheel_graph, 10, create_using=nx.DiGraph)

        mg = nx.wheel_graph(10, create_using=nx.MultiGraph())
        assert edges_equal(mg.edges(), g.edges())

        G = nx.wheel_graph("abc")
        assert len(G) == 3
        assert G.size() == 3

        G = nx.wheel_graph("abcb")
        assert len(G) == 3
        assert G.size() == 4
        G = nx.wheel_graph("abcb", nx.MultiGraph)
        assert len(G) == 3
        assert G.size() == 6

    def test_non_int_integers_for_wheel_graph(self):
        np = pytest.importorskip("numpy")
        G = nx.wheel_graph(np.int32(3))
        assert len(G) == 3
        assert G.size() == 3

    def test_complete_0_partite_graph(self):
        """Tests that the complete 0-partite graph is the null graph."""
        G = nx.complete_multipartite_graph()
        H = nx.null_graph()
        assert nodes_equal(G, H)
        assert edges_equal(G.edges(), H.edges())

    @pytest.mark.parametrize("n", (0, 3))
    def test_complete_1_partite_graph(self, n):
        """Tests that the complete 1-partite graph is the empty graph."""
        G = nx.complete_multipartite_graph(n)
        H = nx.empty_graph(n)
        assert nodes_equal(G, H)
        assert edges_equal(G.edges(), H.edges())

    @pytest.mark.parametrize("m", (0, 5))
    @pytest.mark.parametrize("n", (0, 5))
    def test_complete_2_partite_graph(self, m, n):
        """Tests that the complete 2-partite graph is the complete bipartite
        graph.
        """
        G = nx.complete_multipartite_graph(m, n)
        H = nx.complete_bipartite_graph(m, n)
        assert nodes_equal(G, H)
        assert edges_equal(G.edges(), H.edges())

    @pytest.mark.parametrize("n", (0, 1, 5))
    def test_complete_2_partite_graph_star_graph(self, n):
        """Tests that the complete 2-partite graph with sizes 1 and n
        is the star graph on n + 1 nodes.
        """
        G = nx.complete_multipartite_graph(1, n)
        H = nx.star_graph(n)
        assert nodes_equal(G, H)
        assert edges_equal(G.edges(), H.edges())

    def test_complete_multipartite_graph(self):
        """Tests for generating the complete multipartite graph."""
        G = nx.complete_multipartite_graph(2, 3, 4)
        blocks = [(0, 1), (2, 3, 4), (5, 6, 7, 8)]
        # Within each block, no two vertices should be adjacent.
        for block in blocks:
            for u, v in itertools.combinations_with_replacement(block, 2):
                assert v not in G[u]
                assert G.nodes[u] == G.nodes[v]
        # Across blocks, all vertices should be adjacent.
        for block1, block2 in itertools.combinations(blocks, 2):
            for u, v in itertools.product(block1, block2):
                assert v in G[u]
                assert G.nodes[u] != G.nodes[v]

    @pytest.mark.parametrize(
        "subsets",
        itertools.chain.from_iterable(
            itertools.permutations(range(-2, 2), length) for length in range(3, 5)
        ),
    )
    def test_complete_multipartite_graph_negative_nodes(self, subsets):
        """Test that the complete multipartite graph raises an error when given negative inputs."""
        with pytest.raises(nx.NetworkXError, match="Negative number of nodes"):
            nx.complete_multipartite_graph(*subsets)

    @pytest.mark.parametrize(
        "subsets",
        itertools.chain.from_iterable(
            itertools.permutations([0, 1, "", "a"], length) for length in range(3, 5)
        ),
    )
    def test_complete_multipartite_graph_mixing_inputs_exceptions(self, subsets):
        """Tests that the complete multipartite graph raises an error when mixing inputs."""
        with pytest.raises(
            nx.NetworkXError, match="Arguments must be all ints or all iterables"
        ):
            nx.complete_multipartite_graph(*subsets)

    def test_kneser_graph(self):
        # the petersen graph is a special case of the kneser graph when n=5 and k=2
        assert is_isomorphic(nx.kneser_graph(5, 2), nx.petersen_graph())

        # when k is 1, the kneser graph returns a complete graph with n vertices
        for i in range(1, 7):
            assert is_isomorphic(nx.kneser_graph(i, 1), nx.complete_graph(i))

        # the kneser graph of n and n-1 is the empty graph with n vertices
        for j in range(3, 7):
            assert is_isomorphic(nx.kneser_graph(j, j - 1), nx.empty_graph(j))

        # in general the number of edges of the kneser graph is equal to
        # (n choose k) times (n-k choose k) divided by 2
        assert nx.number_of_edges(nx.kneser_graph(8, 3)) == 280

    @pytest.mark.parametrize(
        "n,k,expectation",
        [
            (-1, -1, pytest.raises(nx.NetworkXError)),  # n <= 0
            (-1, 0, pytest.raises(nx.NetworkXError)),  # n <= 0
            (-1, 1, pytest.raises(nx.NetworkXError)),  # n <= 0
            (0, -1, pytest.raises(nx.NetworkXError)),  # n <= 0
            (0, 0, pytest.raises(nx.NetworkXError)),  # n <= 0
            (0, 1, pytest.raises(nx.NetworkXError)),  # n <= 0
            (1, -1, pytest.raises(nx.NetworkXError)),  # k <= 0
            (1, 0, pytest.raises(nx.NetworkXError)),  # k <= 0
            (1, 1, does_not_raise()),  # ok
            (1, 2, pytest.raises(nx.NetworkXError)),  # k > n
        ],
    )
    def test_kneser_graph_raises(self, n, k, expectation):
        with expectation:
            nx.kneser_graph(n, k)
