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
from networkx.utils import reverse_cuthill_mckee_ordering
from re import compile

try:
    from numpy import (array, asmatrix, asarray, dot, matrix, ndarray, reshape,
                       sqrt, zeros)
    from numpy.linalg import norm
    from numpy.random import normal
    from scipy.linalg import eigh, solve
    from scipy.sparse import csc_matrix, spdiags
    from scipy.sparse.linalg import eigsh, lobpcg
    __all__ = ['algebraic_connectivity', 'fiedler_vector', 'spectral_ordering']
except ImportError:
    __all__ = []

_tracemin_method = compile('^tracemin(?:_(.*))?$')


class _PCGSolver(object):
    """Preconditioned conjugate gradient method.
    """

    def __init__(self, A, M, tol):
        self._A = A
        self._M = M or (lambda x: x)
        self._tol = tol

    def solve(self, b):
        A = self._A
        M = self._M
        tol = self._tol * norm(b, 1)
        # Initialize.
        x = zeros(b.shape)
        r = b.copy()
        z = M(r)
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
            z = M(r)
            beta = dot(r, z)
            beta, rz = beta / rz, beta
            p *= beta
            p += z


class _CholeskySolver(object):
    """Cholesky factorization.
    """

    def __init__(self, A):
        if not self._cholesky:
            raise nx.NetworkXError('Cholesky solver unavailable.')
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
        H.add_weighted_edges_from(((u, v, e.get(weight, 1.))
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


def _rcm_estimate(G, nodelist):
    """Estimate the Fiedler vector using the reverse Cuthill-McKee ordering.
    """
    G = G.subgraph(nodelist)
    order = reverse_cuthill_mckee_ordering(G)
    n = len(nodelist)
    index = dict(zip(nodelist, range(n)))
    x = ndarray(n, dtype=float)
    for i, u in enumerate(order):
        x[index[u]] = i
    x -= (n - 1) / 2.
    return x


def _tracemin_fiedler(L, X, normalized, tol, solver):
    """Compute the Fiedler vector of L using the TraceMIN-Fiedler algorithm.
    """
    n, q = X.shape

    if normalized:
        # Form the normalized Laplacian matrix and determine the eigenvector of
        # its nullspace.
        e = sqrt(L.diagonal())
        D = spdiags(1. / e, [0], n, n, format='csr')
        NL = D * L * D
        D = e.copy()
        e *= 1. / norm(e, 2)

    if not normalized:
        def project(X):
            """Make X orthogonal to the nullspace of L.
            """
            X = asarray(X)
            for j in range(q):
                X[:, j] -= sum(X[:, j]) * (1. / n)
    else:
        def project(X):
            """Make X orthogonal to the nullspace of NL.
            """
            X = asarray(X)
            for j in range(q):
                X[:, j] -= dot(X[:, j], e) * e

    def gram_schmidt(X):
        """Return an orthonormalized copy of X.
        """
        X = asarray(X)
        for j in range(q):
            for k in range(j):
                X[:, j] -= dot(X[:, k], X[:, j]) * X[:, k]
            X[:, j] *= 1. / norm(X[:, j], 2)

    if solver is None or solver == 'pcg':
        M = (1. / L.diagonal()).__mul__
        solver = _PCGSolver(L, M, tol / 10)
    elif solver == 'chol' or solver == 'lu':
        # Convert A to CSC to suppress SparseEfficiencyWarning.
        A = csc_matrix(L, dtype=float, copy=True)
        # Force A to be nonsingular. Since A is the Laplacian matrix of a
        # connected graph, its rank deficiency is one, and thus one diagonal
        # element needs to modified. Changing to infinity forces a zero in the
        # corresponding element in the solution.
        i = A.diagonal().argmin()
        A[i, i] = float('inf')
        solver = (_CholeskySolver if solver == 'chol' else _LUSolver)(A)
    else:
        raise nx.NetworkXError('unknown linear system solver.')

    if normalized:
        L = NL
    Lnorm = abs(L).sum(axis=1).flatten().max()

    # Initialize eigenvectors.
    project(X)
    W = asmatrix(ndarray((n, q), order='F'))

    first = True
    while True:
        gram_schmidt(X)
        # Compute interation matrix H.
        H = X.T * (L * X)
        sigma, Y = eigh(H, overwrite_a=True)
        # Test for convergence.
        if not first:
            x = asarray(X)[:, 0]
            if norm(L * x - sigma[0] * x, 1) < tol * Lnorm:
                break
        else:
            first = False
        # Compute Ritz vectors.
        X *= Y
        # Solve saddle point problem using the Schur complement.
        if not normalized:
            for j in range(q):
                asarray(W)[:, j] = solver.solve(asarray(X)[:, j])
        else:
            for j in range(q):
                asarray(W)[:, j] = D * solver.solve(D * asarray(X)[:, j])
        project(W)
        S = X.T * W  # Schur complement
        N = solve(S, X.T * X, overwrite_a=True, overwrite_b=True)
        X = (N.T * W.T).T  # X == N * W. Preserves Fortran storage order.

    return sigma, asarray(X)


def _get_fiedler_func(method):
    """Return a function that solves the Fiedler eigenvalue problem.
    """
    match = _tracemin_method.match(method)
    if match:
        method = match.group(1)
        def find_fiedler(L, x, normalized, tol):
            X = asmatrix(normal(size=(2, L.shape[0]))).T
            sigma, X = _tracemin_fiedler(L, X, normalized, tol, method)
            return sigma[0], X[:, 0]
    elif method == 'lanczos' or method == 'lobpcg':
        def find_fiedler(L, x, normalized, tol):
            L = csc_matrix(L, dtype=float)
            n = L.shape[0]
            if normalized:
                D = spdiags(1. / sqrt(L.diagonal()), [0], n, n, format='csc')
                L = D * L * D
            if method == 'lanczos' or n < 10:
                # Avoid LOBPCG when n < 10 due to
                # https://github.com/scipy/scipy/issues/3592
                # https://github.com/scipy/scipy/pull/3594
                sigma, X = eigsh(L, 2, which='SM', tol=tol,
                                 return_eigenvectors=True)
            else:
                X = ndarray((n, 2), dtype=float)
                X[:, 0] = 1.
                X[:, 1] = x
                M = spdiags(1. / L.diagonal(), [0], n, n)
                sigma, X = lobpcg(L, X, M=M, tol=tol, maxiter=n, largest=False)
            return sigma[1], X[:, 1]
    else:
        raise nx.NetworkXError("unknown method '%s'." % method)

    return find_fiedler


@not_implemented_for('directed')
def algebraic_connectivity(G, weight='weight', normalized=False, tol=1e-8,
                           method='tracemin'):
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

    normalized : bool
        Whether the normalized Laplacian matrix is used.

    tol : float
        Tolerance of eigenvalue computation. Default value: 1e-8.

    method : string
        Method of eigenvalue computation. It should be one of 'tracemin'
        (TraceMIN), 'lanczos' (Lanczos iteration) and 'lobpcg' (LOBPCG).
        Default value: 'tracemin'.

        The TraceMIN algorithm uses on a linear system solver. The following
        values allow specifying the solver to be used.

        =============== ========================================
        Value           Solver
        =============== ========================================
        'tracemin_pcg'  Preconditioned conjugate gradient method
        'tracemin_chol' Cholesky factorization
        'tracemin_lu'   LU factorization
        =============== ========================================

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
    if L.shape[0] == 2:
        return 2. * L[0, 0] if not normalized else 2.

    find_fiedler = _get_fiedler_func(method)
    x = None if method != 'lobpcg' else _rcm_estimate(G, G)
    return find_fiedler(L, x, normalized, tol)[0]


@not_implemented_for('directed')
def fiedler_vector(G, weight='weight', normalized=False, tol=1e-8,
                   method='tracemin'):
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

    normalized : bool
        Whether the normalized Laplacian matrix is used.

    tol : float
        Tolerance of relative residual in eigenvalue computation. Default
        value: 1e-8.

    method : string
        Method of eigenvalue computation. It should be one of 'tracemin'
        (TraceMIN), 'lanczos' (Lanczos iteration) and 'lobpcg' (LOBPCG).
        Default value: 'tracemin'.

        The TraceMIN algorithm uses on a linear system solver. The following
        values allow specifying the solver to be used.

        =============== ========================================
        Value           Solver
        =============== ========================================
        'tracemin_pcg'  Preconditioned conjugate gradient method
        'tracemin_chol' Cholesky factorization
        'tracemin_lu'   LU factorization
        =============== ========================================

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

    if len(G) == 2:
        return array([1., -1.])

    find_fiedler = _get_fiedler_func(method)
    L = nx.laplacian_matrix(G)
    x = None if method != 'lobpcg' else _rcm_estimate(G, G)
    return find_fiedler(L, x, normalized, tol)[1]


def spectral_ordering(G, weight='weight', normalized=False, tol=1e-8,
                      method='tracemin'):
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

    normalized : bool
        Whether the normalized Laplacian matrix is used.

    tol : float
        Tolerance of relative residual in eigenvalue computation. Default
        value: 1e-8.

    method : string
        Method of eigenvalue computation. It should be one of 'tracemin'
        (TraceMIN), 'lanczos' (Lanczos iteration) and 'lobpcg' (LOBPCG).
        Default value: 'tracemin'.

        The TraceMIN algorithm uses on a linear system solver. The following
        values allow specifying the solver to be used.

        =============== ========================================
        Value           Solver
        =============== ========================================
        'tracemin_pcg'  Preconditioned conjugate gradient method
        'tracemin_chol' Cholesky factorization
        'tracemin_lu'   LU factorization
        =============== ========================================

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

    find_fiedler = _get_fiedler_func(method)
    order = []
    for component in nx.connected_components(G):
        size = len(component)
        if size > 2:
            L = nx.laplacian_matrix(G, component)
            x = None if method != 'lobpcg' else _rcm_estimate(G, component)
            fiedler = find_fiedler(L, x, normalized, tol)[1]
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
