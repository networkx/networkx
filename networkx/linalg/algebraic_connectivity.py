# -*- coding: utf-8 -*-
"""
Algebraic connectivity and Fiedler vectors of undirected graphs.
"""

__author__ = """ysitu <ysitu@users.noreply.github.com>"""
# Copyright (C) 2014 ysitu <ysitu@users.noreply.github.com>
# All rights reserved.
# BSD license.

from functools import partial
import networkx as nx
from networkx.utils import not_implemented_for
from random import normalvariate
from re import compile

try:
    from numpy import (array, asmatrix, asarray, dot, matrix, ndarray, reshape,
                       zeros)
    from numpy.linalg import norm
    from scipy.linalg import eigh, solve
    from scipy.sparse import csc_matrix
    from scipy.sparse.linalg import eigsh
    __all__ = ['algebraic_connectivity', 'fiedler_vector', 'spectral_ordering']
except ImportError:
    __all__ = []

_tracemin_method = compile('^tracemin(?:_(.*))?$')


class _PCGSolver(object):
    """Jacobi-preconditioned conjugate gradient method.
    """

    def __init__(self, A, tol):
        self._A = A
        self._M = 1. / A.diagonal()
        self._tol = tol

    def solve(self, b):
        A = self._A
        M = self._M
        tol = self._tol * norm(b, 1)
        # Initialize.
        x = zeros(b.shape)
        r = b.copy()
        z = M * r
        rz = dot(r, z)
        p = z
        # Iterate.
        while True:
            Ap = A * p
            alpha = rz / dot(p, Ap)
            x += alpha * p
            r -= alpha * Ap
            if norm(r, 1) < tol:
                return x
            z = M * r
            beta = dot(r, z)
            beta, rz = beta / rz, beta
            p = z + beta * p


class _CholeskySolver(object):
    """Cholesky factorization.
    """

    def __init__(self, A):
        if not self._cholesky:
            raise nx.NetworkXError('Cholesky solver unavailable.')
        # Convert A to CSC to suppress SparseEfficiencyWarning.
        A = csc_matrix(A, dtype=float, copy=True)
        # Force A to be nonsingular. Since A is the Laplacian matrix of a
        # connected graph, its rank deficiency is one, and thus one diagonal
        # element needs to modified. Changing to infinity forces a zero in the
        # corresponding element in the solution.
        i = A.diagonal().argmin()
        A[i, i] = float('inf')
        self._chol = self._cholesky(A)

    def solve(self, b):
        return self._chol(b)

    try:
        from scikits.sparse.cholmod import cholesky
        _cholesky = cholesky
    except ImportError:
        _cholesky = None


class _LUSolver(object):
    """LU factorization.
    """

    def __init__(self, A):
        if not self._splu:
            raise nx.NetworkXError('LU solver unavailable.')
        # Convert A to CSC to suppress SparseEfficiencyWarning.
        A = csc_matrix(A, dtype=float, copy=True)
        # Force A to be nonsingular. Since A is the Laplacian matrix of a
        # connected graph, its rank deficiency is one, and thus one diagonal
        # element needs to modified. Changing to infinity forces a zero in the
        # corresponding element in the solution.
        i = A.diagonal().argmin()
        A[i, i] = float('inf')
        self._LU = self._splu(A)

    def solve(self, b):
        return self._LU.solve(b)

    try:
        from scipy.sparse.linalg import splu
        _splu = partial(splu, permc_spec='MMD_AT_PLUS_A', diag_pivot_thresh=0.,
                        options={'Equil': True, 'SymmetricMode': True})
    except ImportError:
        _splu = None


def _preprocess_graph(G, weight):
    """Compute edge weights and eliminate zero-weight edges.
    """
    if G.is_directed():
        H = nx.MultiGraph()
        H.add_nodes_from(G)
        H.add_weighted_edges_from(((u, v, abs(e.get(weight, 1.)))
                                   for u, v, e in G.edges_iter(data=True)
                                   if u != v), weight=weight)
        G = H
    if not G.is_multigraph():
        edges = ((u, v, abs(e.get(weight, 1.)))
                 for u, v, e in G.edges_iter(data=True) if u != v)
    else:
        edges = ((u, v, sum(abs(e.get(weight, 1.)) for e in G[u][v].values()))
                 for u, v in G.edges_iter() if u != v)
    H = nx.Graph()
    H.add_nodes_from(G)
    H.add_weighted_edges_from((u, v, e) for u, v, e in edges if e != 0)
    return H


def _tracemin_fiedler(L, tol, solver=None):
    """Compute the Fiedler vector of L using the TRACEMIN-Fiedler algorithm.
    """
    n = L.shape[0]
    q = 2

    Lnorm = abs(L).sum(axis=0).flatten().max()

    def project(X):
        """Make X orthogonal to the nullspace of L.
        """
        X = asarray(X)
        for j in range(q):
            X[:, j] -= sum(X[:, j]) / n

    def gram_schmidt(X):
        """Return an orthonormalized copy of X.
        """
        V = asarray(X.copy())
        for j in range(q):
            for k in range(j):
                V[:, j] -= dot(V[:, k], V[:, j]) * V[:, k]
            V[:, j] /= norm(V[:, j])
        return asmatrix(V)

    if solver is None or solver == 'pcg':
        solver = _PCGSolver(L, tol / 10)
    elif solver == 'chol':
        solver = _CholeskySolver(L)
    elif solver == 'lu':
        solver = _LUSolver(L)
    else:
        raise nx.NetworkXError('unknown solver.')

    # Randomly initialize eigenvectors.
    X = asmatrix(reshape([normalvariate(0, 1) for i in range(n * q)], (n, q),
                         order='F'))
    project(X)
    W = asmatrix(ndarray((n, q), order='F'))

    first = True
    while True:
        V = gram_schmidt(X)
        # Compute interation matrix H.
        H = V.transpose() * L * V
        sigma, Y = eigh(H, overwrite_a=True)
        # Test for convergence.
        if not first:
            r = L * X[:, 0] - sigma[0] * X[:, 0]
            if norm(r, 1) < tol * Lnorm:
                break
        else:
            first = False
        # Compute Ritz vectors.
        X = V * Y
        # Solve saddle point problem using the Schur complement.
        for j in range(q):
            asarray(W)[:, j] = solver.solve(asarray(X)[:, j])
        project(W)
        S = X.transpose() * W  # Schur complement
        N = solve(S, X.transpose() * X, overwrite_a=True, overwrite_b=True)
        X = W * N

    return sigma, asarray(X)


@not_implemented_for('directed')
def algebraic_connectivity(G, weight='weight', tol=1e-8, method='tracemin'):
    """Return the algebraic connectivity of an undirected graph.

    The algebraic connectivity of a connected undirected graph is the second
    smallest eigenvalue of its Laplacian matrix.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    weight : string or None
        The data key used to determine the weight of each edge. If None, then
        each edge has unit weight. Default value: None.

    tol : float
        Tolerance of eigenvalue computation. Default value: 1e-8.

    method : string
        Method of eigenvalue computation. It should be either 'tracemin'
        (TraceMIN) or 'arnoldi' (Arnoldi iteration). Default value: 'tracemin'.

    Returns
    -------
    algebraic_connectivity : float
        Algebraic connectivity.

    Raises
    ------
    NetworkXNotImplemented :
        If G is directed.

    NetworkXError :
        If G has less than two nodes.

    Notes
    -----
    Edge weights are interpreted by their absolute values. For MultiGraph's,
    weights of parallel edges are summed. Zero-weighted edges are ignored.

    See Also
    --------
    laplacian_matrix
    """
    if len(G) < 2:
        raise nx.NetworkXError('graph has less than two nodes.')
    G = _preprocess_graph(G, weight)
    if not nx.is_connected(G):
        return 0.

    L = nx.laplacian_matrix(G)
    if len(G) == 2:
        return 2. * L[0, 0]

    match = _tracemin_method.match(method)
    if match:
        sigma, X = _tracemin_fiedler(L, tol, match.group(1))
        return sigma[0]
    elif method == 'arnoldi':
        L = csc_matrix(L, dtype=float)
        sigma = eigsh(L, 2, which='SM', tol=tol, return_eigenvectors=False)
        return sigma[0]
    else:
        raise nx.NetworkXError(
            "method should be either 'tracemin' or 'arnoldi'.")


@not_implemented_for('directed')
def fiedler_vector(G, weight='weight', tol=1e-8, method='tracemin'):
    """Return the Fiedler vector of a connected undirected graph.

    The Fiedler vector of a connected undirected graph is the eigenvector
    corresponding to the second smallest eigenvalue of the Laplacian matrix of
    of the graph.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    weight : string or None
        The data key used to determine the weight of each edge. If None, then
        each edge has unit weight. Default value: None.

    tol : float
        Tolerance of relative residual in eigenvalue computation. Default
        value: 1e-8.

    method : string
        Method of eigenvalue computation. It should be either 'tracemin'
        (TraceMIN) or 'arnoldi' (Arnoldi iteration). Default value: 'tracemin'.

    Returns
    -------
    fiedler_vector : NumPy array of floats.
        Fiedler vector.

    Raises
    ------
    NetworkXNotImplemented :
        If G is directed.

    NetworkXError :
        If G has less than two nodes or is not connected.

    Notes
    -----
    Edge weights are interpreted by their absolute values. For MultiGraph's,
    weights of parallel edges are summed. Zero-weighted edges are ignored.

    See Also
    --------
    laplacian_matrix
    """
    if len(G) < 2:
        raise nx.NetworkXError('graph has less than two nodes.')
    G = _preprocess_graph(G, weight)
    if not nx.is_connected(G):
        raise nx.NetworkXError('graph is not connected.')

    L = nx.laplacian_matrix(G)
    if len(G) == 2:
        return array([1., -1.])

    match = _tracemin_method.match(method)
    if match:
        sigma, X = _tracemin_fiedler(L, tol, match.group(1))
        return array(X[:, 0])
    elif method == 'arnoldi':
        L = csc_matrix(L, dtype=float)
        sigma, X = eigsh(L, 2, which='SM', tol=tol)
        return array(X[:, 1])
    else:
        raise nx.NetworkXError(
            "method should be either 'tracemin' or 'arnoldi'.")


def spectral_ordering(G, weight='weight', tol=1e-8, method='tracemin'):
    """Compute the spectral_ordering of a graph.

    The spectral ordering of a graph is an ordering of its nodes where nodes
    in the same weakly connected components appear contiguous and ordered by
    their corresponding elements in the Fiedler vector of the component.

    Parameters
    ----------
    G : NetworkX graph
        A graph.

    weight : string or None
        The data key used to determine the weight of each edge. If None, then
        each edge has unit weight. Default value: None.

    tol : float
        Tolerance of relative residual in eigenvalue computation. Default
        value: 1e-8.

    method : string
        Method of eigenvalue computation. It should be either 'tracemin'
        (TraceMIN) or 'arnoldi' (Arnoldi iteration). Default value: 'tracemin'.

    Returns
    -------
    spectral_ordering : NumPy array of floats.
        Spectral ordering of nodes.

    Raises
    ------
    NetworkXError :
        If G is empty.

    Notes
    -----
    Edge weights are interpreted by their absolute values. For MultiGraph's,
    weights of parallel edges are summed. Zero-weighted edges are ignored.

    See Also
    --------
    laplacian_matrix
    """
    if len(G) == 0:
        raise nx.NetworkXError('graph is empty.')
    G = _preprocess_graph(G, weight)

    match = _tracemin_method.match(method)
    if match:
        method = match.group(1)
        def find_fiedler(L):
            sigma, X = _tracemin_fiedler(L, tol, method)
            return array(X[:, 0])
    elif method == 'arnoldi':
        def find_fiedler(L):
            L = csc_matrix(L, dtype=float)
            sigma, X = eigsh(L, 2, which='SM', tol=tol)
            return array(X[:, 1])
    else:
        raise nx.NetworkXError(
            "method should be either 'tracemin' or 'arnoldi'.")

    order = []
    for component in nx.connected_components(G):
        size = len(component)
        if size > 2:
            L = nx.laplacian_matrix(G, component)
            fiedler = find_fiedler(L)
            order.extend(
                u for x, c, u in sorted(zip(fiedler, range(size), component)))
        else:
            order.extend(component)

    return order


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
        import scipy.sparse
    except ImportError:
        raise SkipTest('SciPy not available.')
