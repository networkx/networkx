import networkx as nx
from networkx import tensor_product, cartesian_product, lexicographic_product, strong_product
from nose.tools import assert_raises, assert_true, assert_equal, raises
from networkx.testing.utils import assert_graphs_equal


@raises(nx.NetworkXError)
def test_tensor_product_raises():
    P = tensor_product(nx.DiGraph(), nx.Graph())


def test_tensor_product_null():
    null = nx.null_graph()
    empty10 = nx.empty_graph(10)
    K3 = nx.complete_graph(3)
    K10 = nx.complete_graph(10)
    P3 = nx.path_graph(3)
    P10 = nx.path_graph(10)
    # null graph
    G = tensor_product(null, null)
    assert_true(nx.is_isomorphic(G, null))
    # null_graph X anything = null_graph and v.v.
    G = tensor_product(null, empty10)
    assert_true(nx.is_isomorphic(G, null))
    G = tensor_product(null, K3)
    assert_true(nx.is_isomorphic(G, null))
    G = tensor_product(null, K10)
    assert_true(nx.is_isomorphic(G, null))
    G = tensor_product(null, P3)
    assert_true(nx.is_isomorphic(G, null))
    G = tensor_product(null, P10)
    assert_true(nx.is_isomorphic(G, null))
    G = tensor_product(empty10, null)
    assert_true(nx.is_isomorphic(G, null))
    G = tensor_product(K3, null)
    assert_true(nx.is_isomorphic(G, null))
    G = tensor_product(K10, null)
    assert_true(nx.is_isomorphic(G, null))
    G = tensor_product(P3, null)
    assert_true(nx.is_isomorphic(G, null))
    G = tensor_product(P10, null)
    assert_true(nx.is_isomorphic(G, null))


def test_tensor_product_size():
    P5 = nx.path_graph(5)
    K3 = nx.complete_graph(3)
    K5 = nx.complete_graph(5)

    G = tensor_product(P5, K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = tensor_product(K3, K5)
    assert_equal(nx.number_of_nodes(G), 3 * 5)


def test_tensor_product_combinations():
    # basic smoke test, more realistic tests would be usefule
    P5 = nx.path_graph(5)
    K3 = nx.complete_graph(3)
    G = tensor_product(P5, K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = tensor_product(P5, nx.MultiGraph(K3))
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = tensor_product(nx.MultiGraph(P5), K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = tensor_product(nx.MultiGraph(P5), nx.MultiGraph(K3))
    assert_equal(nx.number_of_nodes(G), 5 * 3)

    G = tensor_product(nx.DiGraph(P5), nx.DiGraph(K3))
    assert_equal(nx.number_of_nodes(G), 5 * 3)


def test_tensor_product_classic_result():
    K2 = nx.complete_graph(2)
    G = nx.petersen_graph()
    G = tensor_product(G, K2)
    assert_true(nx.is_isomorphic(G, nx.desargues_graph()))

    G = nx.cycle_graph(5)
    G = tensor_product(G, K2)
    assert_true(nx.is_isomorphic(G, nx.cycle_graph(10)))

    G = nx.tetrahedral_graph()
    G = tensor_product(G, K2)
    assert_true(nx.is_isomorphic(G, nx.cubical_graph()))


def test_tensor_product_random():
    G = nx.erdos_renyi_graph(10, 2 / 10.)
    H = nx.erdos_renyi_graph(10, 2 / 10.)
    GH = tensor_product(G, H)

    for (u_G, u_H) in GH.nodes():
        for (v_G, v_H) in GH.nodes():
            if H.has_edge(u_H, v_H) and G.has_edge(u_G, v_G):
                assert_true(GH.has_edge((u_G, u_H), (v_G, v_H)))
            else:
                assert_true(not GH.has_edge((u_G, u_H), (v_G, v_H)))


def test_cartesian_product_multigraph():
    G = nx.MultiGraph()
    G.add_edge(1, 2, key=0)
    G.add_edge(1, 2, key=1)
    H = nx.MultiGraph()
    H.add_edge(3, 4, key=0)
    H.add_edge(3, 4, key=1)
    GH = cartesian_product(G, H)
    assert_equal(set(GH), {(1, 3), (2, 3), (2, 4), (1, 4)})
    assert_equal({(frozenset([u, v]), k) for u, v, k in GH.edges(keys=True)},
                 {(frozenset([u, v]), k) for u, v, k in
                  [((1, 3), (2, 3), 0), ((1, 3), (2, 3), 1),
                   ((1, 3), (1, 4), 0), ((1, 3), (1, 4), 1),
                   ((2, 3), (2, 4), 0), ((2, 3), (2, 4), 1),
                   ((2, 4), (1, 4), 0), ((2, 4), (1, 4), 1)]})


@raises(nx.NetworkXError)
def test_cartesian_product_raises():
    P = cartesian_product(nx.DiGraph(), nx.Graph())


def test_cartesian_product_null():
    null = nx.null_graph()
    empty10 = nx.empty_graph(10)
    K3 = nx.complete_graph(3)
    K10 = nx.complete_graph(10)
    P3 = nx.path_graph(3)
    P10 = nx.path_graph(10)
    # null graph
    G = cartesian_product(null, null)
    assert_true(nx.is_isomorphic(G, null))
    # null_graph X anything = null_graph and v.v.
    G = cartesian_product(null, empty10)
    assert_true(nx.is_isomorphic(G, null))
    G = cartesian_product(null, K3)
    assert_true(nx.is_isomorphic(G, null))
    G = cartesian_product(null, K10)
    assert_true(nx.is_isomorphic(G, null))
    G = cartesian_product(null, P3)
    assert_true(nx.is_isomorphic(G, null))
    G = cartesian_product(null, P10)
    assert_true(nx.is_isomorphic(G, null))
    G = cartesian_product(empty10, null)
    assert_true(nx.is_isomorphic(G, null))
    G = cartesian_product(K3, null)
    assert_true(nx.is_isomorphic(G, null))
    G = cartesian_product(K10, null)
    assert_true(nx.is_isomorphic(G, null))
    G = cartesian_product(P3, null)
    assert_true(nx.is_isomorphic(G, null))
    G = cartesian_product(P10, null)
    assert_true(nx.is_isomorphic(G, null))


def test_cartesian_product_size():
    # order(GXH)=order(G)*order(H)
    K5 = nx.complete_graph(5)
    P5 = nx.path_graph(5)
    K3 = nx.complete_graph(3)
    G = cartesian_product(P5, K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    assert_equal(nx.number_of_edges(G),
                 nx.number_of_edges(P5) * nx.number_of_nodes(K3) +
                 nx.number_of_edges(K3) * nx.number_of_nodes(P5))
    G = cartesian_product(K3, K5)
    assert_equal(nx.number_of_nodes(G), 3 * 5)
    assert_equal(nx.number_of_edges(G),
                 nx.number_of_edges(K5) * nx.number_of_nodes(K3) +
                 nx.number_of_edges(K3) * nx.number_of_nodes(K5))


def test_cartesian_product_classic():
    # test some classic product graphs
    P2 = nx.path_graph(2)
    P3 = nx.path_graph(3)
    # cube = 2-path X 2-path
    G = cartesian_product(P2, P2)
    G = cartesian_product(P2, G)
    assert_true(nx.is_isomorphic(G, nx.cubical_graph()))

    # 3x3 grid
    G = cartesian_product(P3, P3)
    assert_true(nx.is_isomorphic(G, nx.grid_2d_graph(3, 3)))


def test_cartesian_product_random():
    G = nx.erdos_renyi_graph(10, 2 / 10.)
    H = nx.erdos_renyi_graph(10, 2 / 10.)
    GH = cartesian_product(G, H)

    for (u_G, u_H) in GH.nodes():
        for (v_G, v_H) in GH.nodes():
            if (u_G == v_G and H.has_edge(u_H, v_H)) or \
               (u_H == v_H and G.has_edge(u_G, v_G)):
                assert_true(GH.has_edge((u_G, u_H), (v_G, v_H)))
            else:
                assert_true(not GH.has_edge((u_G, u_H), (v_G, v_H)))


@raises(nx.NetworkXError)
def test_lexicographic_product_raises():
    P = lexicographic_product(nx.DiGraph(), nx.Graph())


def test_lexicographic_product_null():
    null = nx.null_graph()
    empty10 = nx.empty_graph(10)
    K3 = nx.complete_graph(3)
    K10 = nx.complete_graph(10)
    P3 = nx.path_graph(3)
    P10 = nx.path_graph(10)
    # null graph
    G = lexicographic_product(null, null)
    assert_true(nx.is_isomorphic(G, null))
    # null_graph X anything = null_graph and v.v.
    G = lexicographic_product(null, empty10)
    assert_true(nx.is_isomorphic(G, null))
    G = lexicographic_product(null, K3)
    assert_true(nx.is_isomorphic(G, null))
    G = lexicographic_product(null, K10)
    assert_true(nx.is_isomorphic(G, null))
    G = lexicographic_product(null, P3)
    assert_true(nx.is_isomorphic(G, null))
    G = lexicographic_product(null, P10)
    assert_true(nx.is_isomorphic(G, null))
    G = lexicographic_product(empty10, null)
    assert_true(nx.is_isomorphic(G, null))
    G = lexicographic_product(K3, null)
    assert_true(nx.is_isomorphic(G, null))
    G = lexicographic_product(K10, null)
    assert_true(nx.is_isomorphic(G, null))
    G = lexicographic_product(P3, null)
    assert_true(nx.is_isomorphic(G, null))
    G = lexicographic_product(P10, null)
    assert_true(nx.is_isomorphic(G, null))


def test_lexicographic_product_size():
    K5 = nx.complete_graph(5)
    P5 = nx.path_graph(5)
    K3 = nx.complete_graph(3)
    G = lexicographic_product(P5, K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = lexicographic_product(K3, K5)
    assert_equal(nx.number_of_nodes(G), 3 * 5)


def test_lexicographic_product_combinations():
    P5 = nx.path_graph(5)
    K3 = nx.complete_graph(3)
    G = lexicographic_product(P5, K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = lexicographic_product(nx.MultiGraph(P5), K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = lexicographic_product(P5, nx.MultiGraph(K3))
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = lexicographic_product(nx.MultiGraph(P5), nx.MultiGraph(K3))
    assert_equal(nx.number_of_nodes(G), 5 * 3)

    # No classic easily found classic results for lexicographic product


def test_lexicographic_product_random():
    G = nx.erdos_renyi_graph(10, 2 / 10.)
    H = nx.erdos_renyi_graph(10, 2 / 10.)
    GH = lexicographic_product(G, H)

    for (u_G, u_H) in GH.nodes():
        for (v_G, v_H) in GH.nodes():
            if G.has_edge(u_G, v_G) or (u_G == v_G and H.has_edge(u_H, v_H)):
                assert_true(GH.has_edge((u_G, u_H), (v_G, v_H)))
            else:
                assert_true(not GH.has_edge((u_G, u_H), (v_G, v_H)))


@raises(nx.NetworkXError)
def test_strong_product_raises():
    P = strong_product(nx.DiGraph(), nx.Graph())


def test_strong_product_null():
    null = nx.null_graph()
    empty10 = nx.empty_graph(10)
    K3 = nx.complete_graph(3)
    K10 = nx.complete_graph(10)
    P3 = nx.path_graph(3)
    P10 = nx.path_graph(10)
    # null graph
    G = strong_product(null, null)
    assert_true(nx.is_isomorphic(G, null))
    # null_graph X anything = null_graph and v.v.
    G = strong_product(null, empty10)
    assert_true(nx.is_isomorphic(G, null))
    G = strong_product(null, K3)
    assert_true(nx.is_isomorphic(G, null))
    G = strong_product(null, K10)
    assert_true(nx.is_isomorphic(G, null))
    G = strong_product(null, P3)
    assert_true(nx.is_isomorphic(G, null))
    G = strong_product(null, P10)
    assert_true(nx.is_isomorphic(G, null))
    G = strong_product(empty10, null)
    assert_true(nx.is_isomorphic(G, null))
    G = strong_product(K3, null)
    assert_true(nx.is_isomorphic(G, null))
    G = strong_product(K10, null)
    assert_true(nx.is_isomorphic(G, null))
    G = strong_product(P3, null)
    assert_true(nx.is_isomorphic(G, null))
    G = strong_product(P10, null)
    assert_true(nx.is_isomorphic(G, null))


def test_strong_product_size():
    K5 = nx.complete_graph(5)
    P5 = nx.path_graph(5)
    K3 = nx.complete_graph(3)
    G = strong_product(P5, K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = strong_product(K3, K5)
    assert_equal(nx.number_of_nodes(G), 3 * 5)


def test_strong_product_combinations():
    P5 = nx.path_graph(5)
    K3 = nx.complete_graph(3)
    G = strong_product(P5, K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = strong_product(nx.MultiGraph(P5), K3)
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = strong_product(P5, nx.MultiGraph(K3))
    assert_equal(nx.number_of_nodes(G), 5 * 3)
    G = strong_product(nx.MultiGraph(P5), nx.MultiGraph(K3))
    assert_equal(nx.number_of_nodes(G), 5 * 3)

    # No classic easily found classic results for strong product

def test_strong_product_random():
    G = nx.erdos_renyi_graph(10, 2 / 10.)
    H = nx.erdos_renyi_graph(10, 2 / 10.)
    GH = strong_product(G, H)

    for (u_G, u_H) in GH.nodes():
        for (v_G, v_H) in GH.nodes():
            if (u_G == v_G and H.has_edge(u_H, v_H)) or \
               (u_H == v_H and G.has_edge(u_G, v_G)) or \
               (G.has_edge(u_G, v_G) and H.has_edge(u_H, v_H)):
                assert_true(GH.has_edge((u_G, u_H), (v_G, v_H)))
            else:
                assert_true(not GH.has_edge((u_G, u_H), (v_G, v_H)))


@raises(nx.NetworkXNotImplemented)
def test_graph_power_raises():
    nx.power(nx.MultiDiGraph(), 2)


def test_graph_power():
    # wikipedia example for graph power
    G = nx.cycle_graph(7)
    G.add_edge(6, 7)
    G.add_edge(7, 8)
    G.add_edge(8, 9)
    G.add_edge(9, 2)
    H = nx.power(G, 2)
    assert_equal(list(H.edges()), [(0, 1), (0, 2), (0, 5), (0, 6), (0, 7), (1, 9),
                             (1, 2), (1, 3), (1, 6), (2, 3), (2, 4), (2, 8),
                             (2, 9), (3, 4), (3, 5), (3, 9), (4, 5), (4, 6),
                             (5, 6), (5, 7), (6, 7), (6, 8), (7, 8), (7, 9),
                             (8, 9)])
    assert_raises(ValueError, nx.power, G, -1)


class TestWalkPower(object):
    """Unit tests for the
    :func:`~networkx.algorithms.operators.product.walk_power` function.

    """

    def test_multidigraph(self):
        """Tests for getting the second walk power of a multidigraph."""
        # Create a directed multigraph with four nodes and five edges,
        # including one pair of parallel edges.
        G = nx.MultiDiGraph()
        G.add_nodes_from(range(4))
        G.add_edges_from([(0, 1), (0, 3), (0, 3), (1, 3), (3, 2)])
        # After squaring, we expect to get the following directed
        # multigraph; this can be verified with pen and paper.
        expected = nx.MultiDiGraph()
        expected.add_nodes_from(range(4))
        expected.add_edges_from([(0, 2), (0, 2), (0, 3), (1, 2)], weight=1)
        # Compare the expected graph with the computed one.
        actual = nx.walk_power(G, 2)
        assert_graphs_equal(expected, actual)

    def test_cube(self):
        """Tests for getting the third walk power of a multigraph."""
        # Test a higher power.
        G = nx.MultiGraph(nx.path_graph(3))
        actual = nx.walk_power(G, 3, parallel_edges=True,
                               create_using=nx.MultiGraph())
        expected = nx.MultiGraph()
        expected.add_edges_from([(0, 1), (0, 1), (1, 2), (1, 2)], weight=1)
        assert_graphs_equal(expected, actual)

    @raises(ValueError)
    def test_negative_exponent(self):
        """Tests that an attempt to raise a graph to a negative power
        raises an exception.

        """
        nx.walk_power(nx.Graph(), -1)

    def test_parallel_edges_directed(self):
        """Tests for computing the power of a graph using a directed
        multigraph, but forcing the "logical" (Boolean) graph power
        instead of the power with multiple edges.

        """
        # Create a directed multigraph with four nodes and five edges,
        # including one pair of parallel edges.
        G = nx.MultiDiGraph()
        G.add_nodes_from(range(4))
        G.add_edges_from([(0, 1), (0, 3), (0, 3), (1, 3), (3, 2)])
        # After squaring, we expect to get the following directed
        # multigraph; this can be verified with pen and paper.
        expected = nx.MultiDiGraph()
        expected.add_nodes_from(range(4))
        expected.add_weighted_edges_from([(0, 2, 2), (0, 3, 1), (1, 2, 1)])
        # Compare the expected graph with the computed one.
        actual = nx.walk_power(G, 2, parallel_edges=False)
        assert_graphs_equal(expected, actual)

    def test_parallel_edges_undirected(self):
        """Tests for computing the power of a graph using an undirected
        multigraph, but forcing the "logical" (Boolean) graph power
        instead of the power with multiple edges.

        """
        G = nx.cycle_graph(4)
        expected = nx.MultiGraph()
        edges = [(0, 0, 2), (0, 2, 2), (1, 1, 2), (1, 3, 2), (2, 2, 2),
                 (3, 3, 2)]
        expected.add_weighted_edges_from(edges)
        actual = nx.walk_power(G, 2, parallel_edges=False)
        assert_graphs_equal(expected, actual)

    def test_create_using(self):
        """Tests for computing the power of a graph while specifying the
        type of output graph.

        """
        # There are many possibilities: two possible values for
        # `parallel_edges`, four possible graph types for the input
        # graph, and four possible graph types for the output graph
        # (that is, the value of `create_using`).
        G = nx.cycle_graph(4)
        def check(parallel_edges, create_using, expected):
            actual = nx.walk_power(G, 2, parallel_edges, create_using)
            assert_graphs_equal(expected, actual)

        # Parallel edges can't be created in an instance of
        # :class:`Graph`, so there should only be one edge joining each
        # pair of adjacent vertices.
        parallel = True
        create_using = nx.Graph()
        expected = nx.Graph()
        edges = [(0, 0, 2), (0, 2, 2), (1, 1, 2), (1, 3, 2), (2, 2, 2),
                 (3, 3, 2)]
        expected.add_weighted_edges_from(edges)
        check(parallel, create_using, expected)

        # Parallel edges can't be created in an instance of
        # :class:`DiGraph`, but complementary edges can.
        parallel = True
        create_using = nx.DiGraph()
        expected = nx.DiGraph()
        edges = [(0, 0, 2), (0, 2, 2), (1, 1, 2), (1, 3, 2), (2, 0, 2),
                 (2, 2, 2), (3, 1, 2), (3, 3, 2)]
        expected.add_weighted_edges_from(edges)
        check(parallel, create_using, expected)

        # Create parallel edges in an undirected multigraph.
        parallel = True
        create_using = nx.MultiGraph()
        expected = nx.MultiGraph()
        edges = [(0, 0), (0, 2), (1, 1), (1, 3), (2, 2), (3, 3)]
        # We expect each of these edges to appear twice.
        expected.add_edges_from(edges, weight=1)
        expected.add_edges_from(edges, weight=1)
        check(parallel, create_using, expected)

        # Create parallel edges in a directed multigraph.
        parallel = True
        create_using = nx.MultiDiGraph()
        expected = nx.MultiDiGraph()
        # We expect each vertex to have two self-loops.
        for u in range(4):
            expected.add_edge(u, u, weight=1)
            expected.add_edge(u, u, weight=1)
        # For each pair of vertices at distance two, there are two paths
        # joining the pair in either direction.
        for u, v in [(0, 2), (1, 3)]:
            expected.add_edge(u, v, weight=1)
            expected.add_edge(u, v, weight=1)
            expected.add_edge(v, u, weight=1)
            expected.add_edge(v, u, weight=1)
        check(parallel, create_using, expected)

        # Since parallel edges can't be created in a simple graph
        # anyway, this should be the same as the ``parallel = True``
        # case above.
        parallel = False
        create_using = nx.Graph()
        expected = nx.walk_power(G, 2, parallel_edges=True,
                                 create_using=create_using)
        check(parallel, create_using, expected)

        # Since parallel edges can't be created in a simple graph
        # anyway, this should be the same as the ``parallel = True``
        # case from above.
        parallel = False
        create_using = nx.DiGraph()
        expected = nx.walk_power(G, 2, parallel_edges=True,
                                 create_using=create_using)
        check(parallel, create_using, expected)

        # Since we will not be creating parallel edges in the resulting
        # graph, we expect that there will be at most one edge joining
        # any pair of vertices.
        parallel = False
        create_using = nx.MultiGraph()
        expected = nx.MultiGraph()
        edges = [(0, 0, 2), (0, 2, 2), (1, 1, 2), (1, 3, 2), (2, 2, 2),
                 (3, 3, 2)]
        expected.add_weighted_edges_from(edges)
        check(parallel, create_using, expected)

        # Again, there will be at most one edge joining any pair of
        # vertices, but now the complementary edges appear as well.
        parallel = False
        create_using = nx.MultiDiGraph()
        expected = nx.MultiDiGraph()
        edges = [(0, 0, 2), (0, 2, 2), (2, 0, 2), (1, 1, 2), (1, 3, 2),
                 (3, 1, 2), (2, 2, 2), (3, 3, 2)]
        expected.add_weighted_edges_from(edges)
        check(parallel, create_using, expected)
