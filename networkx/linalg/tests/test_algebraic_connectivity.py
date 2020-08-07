from math import sqrt

import pytest

numpy = pytest.importorskip("numpy")
numpy.linalg = pytest.importorskip("numpy.linalg")
scipy = pytest.importorskip("scipy")
scipy.sparse = pytest.importorskip("scipy.sparse")


import networkx as nx
from networkx.testing import almost_equal

try:
    from scikits.sparse.cholmod import cholesky

    _cholesky = cholesky
except ImportError:
    _cholesky = None

if _cholesky is None:
    methods = ("tracemin_pcg", "tracemin_lu", "lanczos", "lobpcg")
else:
    methods = ("tracemin_pcg", "tracemin_chol", "tracemin_lu", "lanczos", "lobpcg")


def check_eigenvector(A, l, x):
    nx = numpy.linalg.norm(x)
    # Check zeroness.
    assert not almost_equal(nx, 0)
    y = A * x
    ny = numpy.linalg.norm(y)
    # Check collinearity.
    assert almost_equal(numpy.dot(x, y), nx * ny)
    # Check eigenvalue.
    assert almost_equal(ny, l * nx)


class TestAlgebraicConnectivity:
    @pytest.mark.parametrize("method", methods)
    def test_directed(self, method):
        G = nx.DiGraph()
        pytest.raises(
            nx.NetworkXNotImplemented, nx.algebraic_connectivity, G, method=method
        )
        pytest.raises(nx.NetworkXNotImplemented, nx.fiedler_vector, G, method=method)

    @pytest.mark.parametrize("method", methods)
    def test_null_and_singleton(self, method):
        G = nx.Graph()
        pytest.raises(nx.NetworkXError, nx.algebraic_connectivity, G, method=method)
        pytest.raises(nx.NetworkXError, nx.fiedler_vector, G, method=method)
        G.add_edge(0, 0)
        pytest.raises(nx.NetworkXError, nx.algebraic_connectivity, G, method=method)
        pytest.raises(nx.NetworkXError, nx.fiedler_vector, G, method=method)

    @pytest.mark.parametrize("method", methods)
    def test_disconnected(self, method):
        G = nx.Graph()
        G.add_nodes_from(range(2))
        assert nx.algebraic_connectivity(G) == 0
        pytest.raises(nx.NetworkXError, nx.fiedler_vector, G, method=method)
        G.add_edge(0, 1, weight=0)
        assert nx.algebraic_connectivity(G) == 0
        pytest.raises(nx.NetworkXError, nx.fiedler_vector, G, method=method)

    def test_unrecognized_method(self):
        G = nx.path_graph(4)
        pytest.raises(nx.NetworkXError, nx.algebraic_connectivity, G, method="unknown")
        pytest.raises(nx.NetworkXError, nx.fiedler_vector, G, method="unknown")

    @pytest.mark.parametrize("method", methods)
    def test_two_nodes(self, method):
        G = nx.Graph()
        G.add_edge(0, 1, weight=1)
        A = nx.laplacian_matrix(G)
        assert almost_equal(nx.algebraic_connectivity(G, tol=1e-12, method=method), 2)
        x = nx.fiedler_vector(G, tol=1e-12, method=method)
        check_eigenvector(A, 2, x)

    @pytest.mark.parametrize("method", methods)
    def test_two_nodes_multigraph(self, method):
        G = nx.MultiGraph()
        G.add_edge(0, 0, spam=1e8)
        G.add_edge(0, 1, spam=1)
        G.add_edge(0, 1, spam=-2)
        A = -3 * nx.laplacian_matrix(G, weight="spam")
        assert almost_equal(
            nx.algebraic_connectivity(G, weight="spam", tol=1e-12, method=method), 6
        )
        x = nx.fiedler_vector(G, weight="spam", tol=1e-12, method=method)
        check_eigenvector(A, 6, x)

    def test_abbreviation_of_method(self):
        G = nx.path_graph(8)
        A = nx.laplacian_matrix(G)
        sigma = 2 - sqrt(2 + sqrt(2))
        ac = nx.algebraic_connectivity(G, tol=1e-12, method="tracemin")
        assert almost_equal(ac, sigma)
        x = nx.fiedler_vector(G, tol=1e-12, method="tracemin")
        check_eigenvector(A, sigma, x)

    @pytest.mark.parametrize("method", methods)
    def test_path(self, method):
        G = nx.path_graph(8)
        A = nx.laplacian_matrix(G)
        sigma = 2 - sqrt(2 + sqrt(2))
        ac = nx.algebraic_connectivity(G, tol=1e-12, method=method)
        assert almost_equal(ac, sigma)
        x = nx.fiedler_vector(G, tol=1e-12, method=method)
        check_eigenvector(A, sigma, x)

    @pytest.mark.parametrize("method", methods)
    def test_problematic_graph_issue_2381(self, method):
        G = nx.path_graph(4)
        G.add_edges_from([(4, 2), (5, 1)])
        A = nx.laplacian_matrix(G)
        sigma = 0.438447187191
        ac = nx.algebraic_connectivity(G, tol=1e-12, method=method)
        assert almost_equal(ac, sigma)
        x = nx.fiedler_vector(G, tol=1e-12, method=method)
        check_eigenvector(A, sigma, x)

    @pytest.mark.parametrize("method", methods)
    def test_cycle(self, method):
        G = nx.cycle_graph(8)
        A = nx.laplacian_matrix(G)
        sigma = 2 - sqrt(2)
        ac = nx.algebraic_connectivity(G, tol=1e-12, method=method)
        assert almost_equal(ac, sigma)
        x = nx.fiedler_vector(G, tol=1e-12, method=method)
        check_eigenvector(A, sigma, x)

    @pytest.mark.parametrize("method", methods)
    def test_seed_argument(self, method):
        G = nx.cycle_graph(8)
        A = nx.laplacian_matrix(G)
        sigma = 2 - sqrt(2)
        ac = nx.algebraic_connectivity(G, tol=1e-12, method=method, seed=1)
        assert almost_equal(ac, sigma)
        x = nx.fiedler_vector(G, tol=1e-12, method=method, seed=1)
        check_eigenvector(A, sigma, x)

    @pytest.mark.parametrize(
        ("normalized", "sigma", "laplacian_fn"),
        (
            (False, 0.2434017461399311, nx.laplacian_matrix),
            (True, 0.08113391537997749, nx.normalized_laplacian_matrix),
        ),
    )
    @pytest.mark.parametrize("method", methods)
    def test_buckminsterfullerene(self, normalized, sigma, laplacian_fn, method):
        G = nx.Graph(
            [
                (1, 10),
                (1, 41),
                (1, 59),
                (2, 12),
                (2, 42),
                (2, 60),
                (3, 6),
                (3, 43),
                (3, 57),
                (4, 8),
                (4, 44),
                (4, 58),
                (5, 13),
                (5, 56),
                (5, 57),
                (6, 10),
                (6, 31),
                (7, 14),
                (7, 56),
                (7, 58),
                (8, 12),
                (8, 32),
                (9, 23),
                (9, 53),
                (9, 59),
                (10, 15),
                (11, 24),
                (11, 53),
                (11, 60),
                (12, 16),
                (13, 14),
                (13, 25),
                (14, 26),
                (15, 27),
                (15, 49),
                (16, 28),
                (16, 50),
                (17, 18),
                (17, 19),
                (17, 54),
                (18, 20),
                (18, 55),
                (19, 23),
                (19, 41),
                (20, 24),
                (20, 42),
                (21, 31),
                (21, 33),
                (21, 57),
                (22, 32),
                (22, 34),
                (22, 58),
                (23, 24),
                (25, 35),
                (25, 43),
                (26, 36),
                (26, 44),
                (27, 51),
                (27, 59),
                (28, 52),
                (28, 60),
                (29, 33),
                (29, 34),
                (29, 56),
                (30, 51),
                (30, 52),
                (30, 53),
                (31, 47),
                (32, 48),
                (33, 45),
                (34, 46),
                (35, 36),
                (35, 37),
                (36, 38),
                (37, 39),
                (37, 49),
                (38, 40),
                (38, 50),
                (39, 40),
                (39, 51),
                (40, 52),
                (41, 47),
                (42, 48),
                (43, 49),
                (44, 50),
                (45, 46),
                (45, 54),
                (46, 55),
                (47, 54),
                (48, 55),
            ]
        )
        A = laplacian_fn(G)
        try:
            assert almost_equal(
                nx.algebraic_connectivity(
                    G, normalized=normalized, tol=1e-12, method=method
                ),
                sigma,
            )
            x = nx.fiedler_vector(G, normalized=normalized, tol=1e-12, method=method)
            check_eigenvector(A, sigma, x)
        except nx.NetworkXError as e:
            if e.args not in (
                ("Cholesky solver unavailable.",),
                ("LU solver unavailable.",),
            ):
                raise


class TestSpectralOrdering:
    _graphs = (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)

    @pytest.mark.parametrize("graph", _graphs)
    def test_nullgraph(self, graph):
        G = graph()
        pytest.raises(nx.NetworkXError, nx.spectral_ordering, G)

    @pytest.mark.parametrize("graph", _graphs)
    def test_singleton(self, graph):
        G = graph()
        G.add_node("x")
        assert nx.spectral_ordering(G) == ["x"]
        G.add_edge("x", "x", weight=33)
        G.add_edge("x", "x", weight=33)
        assert nx.spectral_ordering(G) == ["x"]

    def test_unrecognized_method(self):
        G = nx.path_graph(4)
        pytest.raises(nx.NetworkXError, nx.spectral_ordering, G, method="unknown")

    @pytest.mark.parametrize("method", methods)
    def test_three_nodes(self, method):
        G = nx.Graph()
        G.add_weighted_edges_from([(1, 2, 1), (1, 3, 2), (2, 3, 1)], weight="spam")
        order = nx.spectral_ordering(G, weight="spam", method=method)
        assert set(order) == set(G)
        assert {1, 3} in (set(order[:-1]), set(order[1:]))

    @pytest.mark.parametrize("method", methods)
    def test_three_nodes_multigraph(self, method):
        G = nx.MultiDiGraph()
        G.add_weighted_edges_from([(1, 2, 1), (1, 3, 2), (2, 3, 1), (2, 3, 2)])
        order = nx.spectral_ordering(G, method=method)
        assert set(order) == set(G)
        assert {2, 3} in (set(order[:-1]), set(order[1:]))

    @pytest.mark.parametrize("method", methods)
    def test_path(self, method):
        # based on setup_class numpy is installed if we get here
        from numpy.random import shuffle

        path = list(range(10))
        shuffle(path)
        G = nx.Graph()
        nx.add_path(G, path)
        order = nx.spectral_ordering(G, method=method)
        assert order in [path, list(reversed(path))]

    @pytest.mark.parametrize("method", methods)
    def test_seed_argument(self, method):
        # based on setup_class numpy is installed if we get here
        from numpy.random import shuffle

        path = list(range(10))
        shuffle(path)
        G = nx.Graph()
        nx.add_path(G, path)
        order = nx.spectral_ordering(G, method=method, seed=1)
        assert order in [path, list(reversed(path))]

    @pytest.mark.parametrize("method", methods)
    def test_disconnected(self, method):
        G = nx.Graph()
        nx.add_path(G, range(0, 10, 2))
        nx.add_path(G, range(1, 10, 2))
        order = nx.spectral_ordering(G, method=method)
        assert set(order) == set(G)
        seqs = [
            list(range(0, 10, 2)),
            list(range(8, -1, -2)),
            list(range(1, 10, 2)),
            list(range(9, -1, -2)),
        ]
        assert order[:5] in seqs
        assert order[5:] in seqs

    @pytest.mark.parametrize(
        ("normalized", "expected_order"),
        (
            (False, [[1, 2, 0, 3, 4, 5, 6, 9, 7, 8], [8, 7, 9, 6, 5, 4, 3, 0, 2, 1]]),
            (True, [[1, 2, 3, 0, 4, 5, 9, 6, 7, 8], [8, 7, 6, 9, 5, 4, 0, 3, 2, 1]]),
        ),
    )
    @pytest.mark.parametrize("method", methods)
    def test_cycle(self, normalized, expected_order, method):
        path = list(range(10))
        G = nx.Graph()
        nx.add_path(G, path, weight=5)
        G.add_edge(path[-1], path[0], weight=1)
        A = nx.laplacian_matrix(G).todense()
        try:
            order = nx.spectral_ordering(G, normalized=normalized, method=method)
        except nx.NetworkXError as e:
            if e.args not in (
                ("Cholesky solver unavailable.",),
                ("LU solver unavailable.",),
            ):
                raise
        else:
            assert order in expected_order
