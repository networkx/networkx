"""
Adjacency matrix and incidence matrix of graphs.
"""

import networkx as nx

__all__ = ["incidence_matrix", "adjacency_matrix", "normalized_adjacency_matrix"]


@nx._dispatchable(edge_attrs="weight")
def incidence_matrix(
    G, nodelist=None, edgelist=None, oriented=False, weight=None, *, dtype=None
):
    """Returns incidence matrix of G.

    The incidence matrix assigns each row to a node and each column to an edge.
    For a standard incidence matrix a 1 appears wherever a row's node is
    incident on the column's edge.  For an oriented incidence matrix each
    edge is assigned an orientation (arbitrarily for undirected and aligning to
    direction for directed).  A -1 appears for the source (tail) of an edge and
    1 for the destination (head) of the edge.  The elements are zero otherwise.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    nodelist : list, optional   (default= all nodes in G)
       The rows are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    edgelist : list, optional (default= all edges in G)
       The columns are ordered according to the edges in edgelist.
       If edgelist is None, then the ordering is produced by G.edges().

    oriented: bool, optional (default=False)
       If True, matrix elements are +1 or -1 for the head or tail node
       respectively of each edge.  If False, +1 occurs at both nodes.

    weight : string or None, optional (default=None)
       The edge data key used to provide each value in the matrix.
       If None, then each edge has weight 1.  Edge weights, if used,
       should be positive so that the orientation can provide the sign.

    dtype : a NumPy dtype or None (default=None)
        The dtype of the output sparse array. This type should be a compatible
        type of the weight argument, eg. if weight would return a float this
        argument should also be a float.
        If None, then the default for SciPy is used.

    Returns
    -------
    A : SciPy sparse array
      The incidence matrix of G.

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges in edgelist should be
    (u,v,key) 3-tuples.

    "Networks are the best discrete model for so many problems in
    applied mathematics" [1]_.

    References
    ----------
    .. [1] Gil Strang, Network applications: A = incidence matrix,
       http://videolectures.net/mit18085f07_strang_lec03/
    """
    import scipy as sp

    if nodelist is None:
        nodelist = list(G)
    if edgelist is None:
        if G.is_multigraph():
            edgelist = list(G.edges(keys=True))
        else:
            edgelist = list(G.edges())
    A = sp.sparse.lil_array((len(nodelist), len(edgelist)), dtype=dtype)
    node_index = {node: i for i, node in enumerate(nodelist)}
    for ei, e in enumerate(edgelist):
        (u, v) = e[:2]
        if u == v:
            continue  # self loops give zero column
        try:
            ui = node_index[u]
            vi = node_index[v]
        except KeyError as err:
            raise nx.NetworkXError(
                f"node {u} or {v} in edgelist but not in nodelist"
            ) from err
        if weight is None:
            wt = 1
        else:
            if G.is_multigraph():
                ekey = e[2]
                wt = G[u][v][ekey].get(weight, 1)
            else:
                wt = G[u][v].get(weight, 1)
        if oriented:
            A[ui, ei] = -wt
            A[vi, ei] = wt
        else:
            A[ui, ei] = wt
            A[vi, ei] = wt
    return A.asformat("csc")


@nx._dispatchable(edge_attrs="weight")
def adjacency_matrix(G, nodelist=None, dtype=None, weight="weight", *, format="csr"):
    """Returns adjacency matrix of `G`.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered according to the nodes in `nodelist`.
       If ``nodelist=None`` (the default), then the ordering is produced by
       ``G.nodes()``.

    dtype : NumPy data-type, optional
        The desired data-type for the array.
        If `None`, then the NumPy default is used.

    weight : string or None, optional (default='weight')
       The edge data key used to provide each value in the matrix.
       If None, then each edge has weight 1.

    format : str in {'bsr', 'csr', 'csc', 'coo', 'lil', 'dia', 'dok', 'dense'}
       The type of the array to be returned (default 'csr'). For 'dense',
       a `numpy.ndarray` is returned instead of a SciPy sparse array.

    Returns
    -------
    A : SciPy sparse array or numpy ndarray
      Adjacency matrix representation of G.

    Notes
    -----
    For directed graphs, entry ``i, j`` corresponds to an edge from ``i`` to ``j``.

    If you want a pure Python adjacency matrix representation try
    :func:`~networkx.convert.to_dict_of_dicts` which will return a
    dictionary-of-dictionaries format that can be addressed as a
    sparse matrix.

    For multigraphs with parallel edges the weights are summed.
    See :func:`networkx.convert_matrix.to_numpy_array` for other options.

    The convention used for self-loop edges in graphs is to assign the
    diagonal matrix entry value to the edge weight attribute
    (or the number 1 if the edge has no weight attribute).  If the
    alternate convention of doubling the edge weight is desired the
    resulting SciPy sparse array can be modified as follows::

        >>> G = nx.Graph([(1, 1)])
        >>> A = nx.adjacency_matrix(G)
        >>> A.toarray()
        array([[1]])
        >>> A.setdiag(A.diagonal() * 2)
        >>> A.toarray()
        array([[2]])

    See Also
    --------
    to_numpy_array
    to_scipy_sparse_array
    to_dict_of_dicts
    adjacency_spectrum
    """
    return nx.to_scipy_sparse_array(
        G, nodelist=nodelist, dtype=dtype, weight=weight, format=format
    )


@nx._dispatchable(edge_attrs="weight")
def normalized_adjacency_matrix(G, nodelist=None, weight="weight"):
    r"""Returns the normalized adjacency matrix of `G`.

    The normalized adjacency matrix is the matrix

    .. math::

        N = D^{-1/2} A D^{-1/2}

    where `A` is the adjacency matrix of `G` and `D` is the diagonal matrix of
    node degrees [1]_. The eigenvalues of `N` lie in the interval `[-1, 1]`.
    It is related to the normalized Laplacian `\mathcal{L}` by
    `N = I - \mathcal{L}` for graphs without isolated nodes.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered according to the nodes in `nodelist`.
       If ``nodelist=None`` (the default), then the ordering is produced by
       ``G.nodes()``.

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    N : SciPy sparse array
      The normalized adjacency matrix of `G`.

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edge weights are summed.
    See :func:`to_numpy_array` for other options.

    `D` is the diagonal matrix of the row sums of the adjacency matrix, i.e.
    the out-degree for directed graphs. To use the in-degree instead, use
    ``G.reverse(copy=False)``. Following the convention of
    `normalized_laplacian_matrix`, an isolated node (zero degree) produces a
    zero row and column rather than a division by zero.

    For an unnormalized output, use `adjacency_matrix`.

    Examples
    --------
    >>> import numpy as np
    >>> G = nx.path_graph(4)
    >>> print(nx.normalized_adjacency_matrix(G).toarray())
    [[0.         0.70710678 0.         0.        ]
     [0.70710678 0.         0.5        0.        ]
     [0.         0.5        0.         0.70710678]
     [0.         0.         0.70710678 0.        ]]

    The normalized adjacency and normalized Laplacian matrices satisfy
    `N = I - \mathcal{L}`:

    >>> N = nx.normalized_adjacency_matrix(G).toarray()
    >>> L = nx.normalized_laplacian_matrix(G).toarray()
    >>> np.allclose(N, np.eye(len(G)) - L)
    True

    See Also
    --------
    adjacency_matrix
    normalized_adjacency_spectrum
    normalized_laplacian_matrix

    References
    ----------
    .. [1] Fan Chung-Graham, Spectral Graph Theory,
       CBMS Regional Conference Series in Mathematics, Number 92, 1997.
    """
    import numpy as np
    import scipy as sp

    if nodelist is None:
        nodelist = list(G)
    A = nx.to_scipy_sparse_array(G, nodelist=nodelist, weight=weight, format="csr")
    n, _ = A.shape
    diags = A.sum(axis=1)
    with np.errstate(divide="ignore"):
        diags_sqrt = 1.0 / np.sqrt(diags)
    diags_sqrt[np.isinf(diags_sqrt)] = 0
    DH = sp.sparse.dia_array((diags_sqrt, 0), shape=(n, n)).tocsr()
    return DH @ (A @ DH)
