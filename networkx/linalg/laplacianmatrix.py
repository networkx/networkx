"""Laplacian matrix of graphs.
"""
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = [
    "laplacian_matrix",
    "normalized_laplacian_matrix",
    "directed_laplacian_matrix",
    "directed_combinatorial_laplacian_matrix",
]


@not_implemented_for("directed")
def laplacian_matrix(G, nodelist=None, weight="weight"):
    """Returns the Laplacian matrix of G.

    The graph Laplacian is the matrix L = D - A, where
    A is the adjacency matrix and D is the diagonal matrix of node degrees.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    L : SciPy sparse matrix
      The Laplacian matrix of G.

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges weights are summed.

    See Also
    --------
    to_numpy_array
    normalized_laplacian_matrix
    laplacian_spectrum
    """
    import scipy as sp
    import scipy.sparse  # call as sp.sparse

    if nodelist is None:
        nodelist = list(G)
    A = nx.to_scipy_sparse_array(G, nodelist=nodelist, weight=weight, format="csr")
    n, m = A.shape
    # TODO: rm csr_array wrapper when spdiags can produce arrays
    D = sp.sparse.csr_array(sp.sparse.spdiags(A.sum(axis=1), 0, m, n, format="csr"))
    import warnings

    warnings.warn(
        "laplacian_matrix will return a scipy.sparse array instead of a matrix in Networkx 3.0.",
        FutureWarning,
        stacklevel=2,
    )
    # TODO: rm sp.sparse.csr_matrix in version 3.0
    return sp.sparse.csr_matrix(D - A)


@not_implemented_for("directed")
def normalized_laplacian_matrix(G, nodelist=None, weight="weight"):
    r"""Returns the normalized Laplacian matrix of G.

    The normalized graph Laplacian is the matrix

    .. math::

        N = D^{-1/2} L D^{-1/2}

    where `L` is the graph Laplacian and `D` is the diagonal matrix of
    node degrees.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    N : Scipy sparse matrix
      The normalized Laplacian matrix of G.

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges weights are summed.
    See to_numpy_array for other options.

    If the Graph contains selfloops, D is defined as diag(sum(A,1)), where A is
    the adjacency matrix [2]_.

    See Also
    --------
    laplacian_matrix
    normalized_laplacian_spectrum

    References
    ----------
    .. [1] Fan Chung-Graham, Spectral Graph Theory,
       CBMS Regional Conference Series in Mathematics, Number 92, 1997.
    .. [2] Steve Butler, Interlacing For Weighted Graphs Using The Normalized
       Laplacian, Electronic Journal of Linear Algebra, Volume 16, pp. 90-98,
       March 2007.
    """
    import numpy as np
    import scipy as sp
    import scipy.sparse  # call as sp.sparse

    if nodelist is None:
        nodelist = list(G)
    A = nx.to_scipy_sparse_array(G, nodelist=nodelist, weight=weight, format="csr")
    n, m = A.shape
    diags = A.sum(axis=1)
    # TODO: rm csr_array wrapper when spdiags can produce arrays
    D = sp.sparse.csr_array(sp.sparse.spdiags(diags, 0, m, n, format="csr"))
    L = D - A
    with sp.errstate(divide="ignore"):
        diags_sqrt = 1.0 / np.sqrt(diags)
    diags_sqrt[np.isinf(diags_sqrt)] = 0
    # TODO: rm csr_array wrapper when spdiags can produce arrays
    DH = sp.sparse.csr_array(sp.sparse.spdiags(diags_sqrt, 0, m, n, format="csr"))
    import warnings

    warnings.warn(
        "normalized_laplacian_matrix will return a scipy.sparse array instead of a matrix in Networkx 3.0.",
        FutureWarning,
        stacklevel=2,
    )
    # TODO: rm csr_matrix wrapper for NX 3.0
    return sp.sparse.csr_matrix(DH @ (L @ DH))


###############################################################################
# Code based on
# https://bitbucket.org/bedwards/networkx-community/src/370bd69fc02f/networkx/algorithms/community/


@not_implemented_for("undirected")
@not_implemented_for("multigraph")
def directed_laplacian_matrix(
    G, nodelist=None, weight="weight", walk_type=None, alpha=0.95
):
    r"""Returns the directed Laplacian matrix of G.

    The graph directed Laplacian is the matrix

    .. math::

        L = I - (\Phi^{1/2} P \Phi^{-1/2} + \Phi^{-1/2} P^T \Phi^{1/2} ) / 2

    where `I` is the identity matrix, `P` is the transition matrix of the
    graph, and `\Phi` a matrix with the Perron vector of `P` in the diagonal and
    zeros elsewhere.

    Depending on the value of walk_type, `P` can be the transition matrix
    induced by a random walk, a lazy random walk, or a random walk with
    teleportation (PageRank).

    Parameters
    ----------
    G : DiGraph
       A NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    walk_type : string or None, optional (default=None)
       If None, `P` is selected depending on the properties of the
       graph. Otherwise is one of 'random', 'lazy', or 'pagerank'

    alpha : real
       (1 - alpha) is the teleportation probability used with pagerank

    Returns
    -------
    L : NumPy matrix
      Normalized Laplacian of G.

    Notes
    -----
    Only implemented for DiGraphs

    See Also
    --------
    laplacian_matrix

    References
    ----------
    .. [1] Fan Chung (2005).
       Laplacians and the Cheeger inequality for directed graphs.
       Annals of Combinatorics, 9(1), 2005
    """
    import numpy as np
    import scipy as sp
    import scipy.sparse  # call as sp.sparse
    import scipy.sparse.linalg  # call as sp.sparse.linalg

    # NOTE: P has type ndarray if walk_type=="pagerank", else csr_array
    P = _transition_matrix(
        G, nodelist=nodelist, weight=weight, walk_type=walk_type, alpha=alpha
    )

    n, m = P.shape

    evals, evecs = sp.sparse.linalg.eigs(P.T, k=1)
    v = evecs.flatten().real
    p = v / v.sum()
    sqrtp = np.sqrt(p)
    Q = (
        # TODO: rm csr_array wrapper when spdiags creates arrays
        sp.sparse.csr_array(sp.sparse.spdiags(sqrtp, 0, n, n))
        @ P
        # TODO: rm csr_array wrapper when spdiags creates arrays
        @ sp.sparse.csr_array(sp.sparse.spdiags(1.0 / sqrtp, 0, n, n))
    )
    # NOTE: This could be sparsified for the non-pagerank cases
    I = np.identity(len(G))

    import warnings

    warnings.warn(
        "directed_laplacian_matrix will return a numpy array instead of a matrix in NetworkX 3.0",
        FutureWarning,
        stacklevel=2,
    )
    # TODO: rm np.asmatrix for networkx 3.0
    return np.asmatrix(I - (Q + Q.T) / 2.0)


@not_implemented_for("undirected")
@not_implemented_for("multigraph")
def directed_combinatorial_laplacian_matrix(
    G, nodelist=None, weight="weight", walk_type=None, alpha=0.95
):
    r"""Return the directed combinatorial Laplacian matrix of G.

    The graph directed combinatorial Laplacian is the matrix

    .. math::

        L = \Phi - (\Phi P + P^T \Phi) / 2

    where `P` is the transition matrix of the graph and `\Phi` a matrix
    with the Perron vector of `P` in the diagonal and zeros elsewhere.

    Depending on the value of walk_type, `P` can be the transition matrix
    induced by a random walk, a lazy random walk, or a random walk with
    teleportation (PageRank).

    Parameters
    ----------
    G : DiGraph
       A NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    walk_type : string or None, optional (default=None)
       If None, `P` is selected depending on the properties of the
       graph. Otherwise is one of 'random', 'lazy', or 'pagerank'

    alpha : real
       (1 - alpha) is the teleportation probability used with pagerank

    Returns
    -------
    L : NumPy matrix
      Combinatorial Laplacian of G.

    Notes
    -----
    Only implemented for DiGraphs

    See Also
    --------
    laplacian_matrix

    References
    ----------
    .. [1] Fan Chung (2005).
       Laplacians and the Cheeger inequality for directed graphs.
       Annals of Combinatorics, 9(1), 2005
    """
    import scipy as sp
    import scipy.sparse  # call as sp.sparse
    import scipy.sparse.linalg  # call as sp.sparse.linalg

    P = _transition_matrix(
        G, nodelist=nodelist, weight=weight, walk_type=walk_type, alpha=alpha
    )

    n, m = P.shape

    evals, evecs = sp.sparse.linalg.eigs(P.T, k=1)
    v = evecs.flatten().real
    p = v / v.sum()
    # NOTE: could be improved by not densifying
    # TODO: Rm csr_array wrapper when spdiags array creation becomes available
    Phi = sp.sparse.csr_array(sp.sparse.spdiags(p, 0, n, n)).toarray()

    import warnings

    warnings.warn(
        "directed_combinatorial_laplacian_matrix will return a numpy array instead of a matrix in NetworkX 3.0",
        FutureWarning,
        stacklevel=2,
    )
    # TODO: Rm np.asmatrix for networkx 3.0
    import numpy as np

    return np.asmatrix(Phi - (Phi @ P + P.T @ Phi) / 2.0)


def _transition_matrix(G, nodelist=None, weight="weight", walk_type=None, alpha=0.95):
    """Returns the transition matrix of G.

    This is a row stochastic giving the transition probabilities while
    performing a random walk on the graph. Depending on the value of walk_type,
    P can be the transition matrix induced by a random walk, a lazy random walk,
    or a random walk with teleportation (PageRank).

    Parameters
    ----------
    G : DiGraph
       A NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    walk_type : string or None, optional (default=None)
       If None, `P` is selected depending on the properties of the
       graph. Otherwise is one of 'random', 'lazy', or 'pagerank'

    alpha : real
       (1 - alpha) is the teleportation probability used with pagerank

    Returns
    -------
    P : numpy.ndarray
      transition matrix of G.

    Raises
    ------
    NetworkXError
        If walk_type not specified or alpha not in valid range
    """
    import numpy as np
    import scipy as sp
    import scipy.sparse  # call as sp.sparse

    if walk_type is None:
        if nx.is_strongly_connected(G):
            if nx.is_aperiodic(G):
                walk_type = "random"
            else:
                walk_type = "lazy"
        else:
            walk_type = "pagerank"

    A = nx.to_scipy_sparse_array(G, nodelist=nodelist, weight=weight, dtype=float)
    n, m = A.shape
    if walk_type in ["random", "lazy"]:
        # TODO: Rm csr_array wrapper when spdiags array creation becomes available
        DI = sp.sparse.csr_array(sp.sparse.spdiags(1.0 / A.sum(axis=1), 0, n, n))
        if walk_type == "random":
            P = DI @ A
        else:
            # TODO: Rm csr_array wrapper when identity array creation becomes available
            I = sp.sparse.csr_array(sp.sparse.identity(n))
            P = (I + DI @ A) / 2.0

    elif walk_type == "pagerank":
        if not (0 < alpha < 1):
            raise nx.NetworkXError("alpha must be between 0 and 1")
        # this is using a dense representation. NOTE: This should be sparsified!
        A = A.toarray()
        # add constant to dangling nodes' row
        A[A.sum(axis=1) == 0, :] = 1 / n
        # normalize
        A = A / A.sum(axis=1)[np.newaxis, :].T
        P = alpha * A + (1 - alpha) / n
    else:
        raise nx.NetworkXError("walk_type must be random, lazy, or pagerank")

    return P
