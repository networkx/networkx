from contextlib import contextmanager
from math import sqrt
import networkx as nx
from nose import SkipTest
from nose.tools import *
from random import getstate, seed, setstate

@contextmanager
def save_random_state():
    state = getstate()
    yield
    setstate(state)


def preserve_random_state(func):
    def wrapper(*args, **kwargs):
        with save_random_state():
            seed(1234567890)
            return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def check_eigenvector(A, l, x):
    nx = numpy.linalg.norm(x)
    # Check zeroness.
    assert_not_almost_equal(nx, 0)
    y = A * x
    ny = numpy.linalg.norm(y)
    # Check collinearity.
    assert_almost_equal(numpy.dot(x, y), nx * ny)
    # Check eigenvalue.
    assert_almost_equal(ny, l * nx)


class TestAlgebraicConnectivity(object):

    numpy = 1

    @classmethod
    def setupClass(cls):
        global numpy
        try:
            import numpy.linalg
            import scipy.sparse
        except ImportError:
            raise SkipTest('SciPy not available.')

    @preserve_random_state
    def test_directed(self):
        G = nx.DiGraph()
        for method in ('tracemin', 'arnoldi'):
            assert_raises(nx.NetworkXNotImplemented, nx.algebraic_connectivity,
                          G, method=method)
            assert_raises(nx.NetworkXNotImplemented, nx.fiedler_vector, G,
                          method=method)

    @preserve_random_state
    def test_null_and_singleton(self):
        G = nx.Graph()
        for method in ('tracemin', 'arnoldi'):
            assert_raises(nx.NetworkXError, nx.algebraic_connectivity, G,
                          method=method)
            assert_raises(nx.NetworkXError, nx.fiedler_vector, G,
                          method=method)
        G.add_edge(0, 0)
        for method in ('tracemin', 'arnoldi'):
            assert_raises(nx.NetworkXError, nx.algebraic_connectivity, G,
                          method=method)
            assert_raises(nx.NetworkXError, nx.fiedler_vector, G,
                          method=method)

    @preserve_random_state
    def test_disconnected(self):
        G = nx.Graph()
        G.add_nodes_from(range(2))
        for method in ('tracemin', 'arnoldi'):
            assert_raises(nx.NetworkXError, nx.algebraic_connectivity, G,
                          method=method)
            assert_raises(nx.NetworkXError, nx.fiedler_vector, G,
                          method=method)
        G.add_edge(0, 1, weight=0)
        for method in ('tracemin', 'arnoldi'):
            assert_raises(nx.NetworkXError, nx.algebraic_connectivity, G,
                          method=method)
            assert_raises(nx.NetworkXError, nx.fiedler_vector, G,
                          method=method)

    @preserve_random_state
    def test_unrecognized_method(self):
        G = nx.path_graph(4)
        assert_raises(nx.NetworkXError, nx.algebraic_connectivity, G,
                      method='unknown')
        assert_raises(nx.NetworkXError, nx.fiedler_vector, G, method='unknown')

    @preserve_random_state
    def test_two_nodes(self):
        G = nx.Graph()
        G.add_edge(0, 1, weight=1)
        for method in ('tracemin', 'arnoldi'):
            assert_almost_equal(nx.algebraic_connectivity(
                G, tol=1e-12, method=method), 2)
            A = nx.laplacian_matrix(G)
            x = nx.fiedler_vector(G, tol=1e-12, method=method)
            check_eigenvector(A, 2, x)
        G = nx.MultiGraph()
        G.add_edge(0, 0, spam=1e8)
        G.add_edge(0, 1, spam=1)
        G.add_edge(0, 1, spam=2)
        for method in ('tracemin', 'arnoldi'):
            assert_almost_equal(nx.algebraic_connectivity(
                G, weight='spam', tol=1e-12, method=method), 6)
            A = nx.laplacian_matrix(G, weight='spam')
            x = nx.fiedler_vector(G, weight='spam', tol=1e-12, method=method)
            check_eigenvector(A, 6, x)

    @preserve_random_state
    def test_path(self):
        G = nx.path_graph(8)
        sigma = 2 - sqrt(2 + sqrt(2))
        for method in ('tracemin', 'arnoldi'):
            assert_almost_equal(nx.algebraic_connectivity(
                G, tol=1e-12, method=method), sigma)
            A = nx.laplacian_matrix(G)
            x = nx.fiedler_vector(G, tol=1e-12, method=method)
            check_eigenvector(A, sigma, x)

    @preserve_random_state
    def test_cycle(self):
        G = nx.cycle_graph(8)
        sigma = 2 - sqrt(2)
        for method in ('tracemin', 'arnoldi'):
            assert_almost_equal(nx.algebraic_connectivity(
                G, tol=1e-12, method=method), sigma)
            A = nx.laplacian_matrix(G)
            x = nx.fiedler_vector(G, tol=1e-12, method=method)
            check_eigenvector(A, sigma, x)

    @preserve_random_state
    def test_buckminsterfullerene(self):
        G = nx.Graph(
            [(1, 10), (1, 41), (1, 59), (2, 12), (2, 42), (2, 60), (3, 6),
             (3, 43), (3, 57), (4, 8), (4, 44), (4, 58), (5, 13), (5, 56),
             (5, 57), (6, 10), (6, 31), (7, 14), (7, 56), (7, 58), (8, 12),
             (8, 32), (9, 23), (9, 53), (9, 59), (10, 15), (11, 24), (11, 53),
             (11, 60), (12, 16), (13, 14), (13, 25), (14, 26), (15, 27),
             (15, 49), (16, 28), (16, 50), (17, 18), (17, 19), (17, 54),
             (18, 20), (18, 55), (19, 23), (19, 41), (20, 24), (20, 42),
             (21, 31), (21, 33), (21, 57), (22, 32), (22, 34), (22, 58),
             (23, 24), (25, 35), (25, 43), (26, 36), (26, 44), (27, 51),
             (27, 59), (28, 52), (28, 60), (29, 33), (29, 34), (29, 56),
             (30, 51), (30, 52), (30, 53), (31, 47), (32, 48), (33, 45),
             (34, 46), (35, 36), (35, 37), (36, 38), (37, 39), (37, 49),
             (38, 40), (38, 50), (39, 40), (39, 51), (40, 52), (41, 47),
             (42, 48), (43, 49), (44, 50), (45, 46), (45, 54), (46, 55),
             (47, 54), (48, 55)])
        sigma = 0.24340174613993243
        for method in ('tracemin_pcg', 'tracemin_chol', 'arnoldi'):
            try:
                assert_almost_equal(nx.algebraic_connectivity(
                    G, tol=1e-12, method=method), sigma)
                A = nx.laplacian_matrix(G)
                x = nx.fiedler_vector(G, tol=1e-12, method=method)
                check_eigenvector(A, sigma, x)
            except nx.NetworkXError as e:
                if e.args != ('Cholesky solver unavailable.',):
                    raise
