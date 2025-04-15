# %%

import numpy as np
import scipy as sp

import itertools

from pathlib import Path
import pandas as pd


import networkx as nx
from networkx import bipartite
from networkx.algorithms.bipartite.matrix import biadjacency_matrix

tops = [2, 5, 10]
bots = [5, 10, 15]
for i in range(len(tops)):
    G = bipartite.random_graph(tops[i], bots[i], 0.2)
    top = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
    M = bipartite.biadjacency_matrix(G, top)

path_exiobase_root_directory = Path('/Users/michaelweinold/data/IOT_2020_ixi')
df_S = pd.read_csv(
    path_exiobase_root_directory / 'satellite' / 'S.txt',
    delimiter='\t',
    skiprows=3,
    header=None
)
df_S.drop(columns=[0], inplace=True)

S = df_S.to_numpy()
sparseS = sp.sparse.csr_array(S)

GG = bipartite.from_biadjacency_matrix(sparseS)


# %%

def biadjacency_matrix_NEW(
    G, row_order, column_order=None, dtype=None, weight="weight", format="csr"
):
    r"""Returns the biadjacency matrix of the bipartite graph G.

    Let `G = (U, V, E)` be a bipartite graph with node sets
    `U = u_{1},...,u_{r}` and `V = v_{1},...,v_{s}`. The biadjacency
    matrix [1]_ is the `r` x `s` matrix `B` in which `b_{i,j} = 1`
    if, and only if, `(u_i, v_j) \in E`. If the parameter `weight` is
    not `None` and matches the name of an edge attribute, its value is
    used instead of 1.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    row_order : list of nodes
       The rows of the matrix are ordered according to the list of nodes.

    column_order : list, optional
       The columns of the matrix are ordered according to the list of nodes.
       If column_order is None, then the ordering of columns is arbitrary.

    dtype : NumPy data-type, optional
        A valid NumPy dtype used to initialize the array. If None, then the
        NumPy default is used.

    weight : string or None, optional (default='weight')
       The edge data key used to provide each value in the matrix.
       If None, then each edge has weight 1.

    format : str in {'dense', 'bsr', 'csr', 'csc', 'coo', 'lil', 'dia', 'dok'}
        The type of the matrix to be returned (default 'csr'). For
        some algorithms different implementations of sparse matrices
        can perform better.  See [2]_ for details.

    Returns
    -------
    M : SciPy sparse array
        Biadjacency matrix representation of the bipartite graph G.

    Notes
    -----
    No attempt is made to check that the input graph is bipartite.

    For directed bipartite graphs only successors are considered as neighbors.
    To obtain an adjacency matrix with ones (or weight values) for both
    predecessors and successors you have to generate two biadjacency matrices
    where the rows of one of them are the columns of the other, and then add
    one to the transpose of the other.

    See Also
    --------
    adjacency_matrix
    from_biadjacency_matrix

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Adjacency_matrix#Adjacency_matrix_of_a_bipartite_graph
    .. [2] Scipy Dev. References, "Sparse Matrices",
       https://docs.scipy.org/doc/scipy/reference/sparse.html
    """
    import scipy as sp

    nlen = len(row_order)
    if nlen == 0:
        raise nx.NetworkXError("row_order is empty list")
    if len(row_order) != len(set(row_order)):
        msg = "Ambiguous ordering: `row_order` contained duplicates."
        raise nx.NetworkXError(msg)
    if column_order is None:
        column_order = list(set(G) - set(row_order))
    mlen = len(column_order)
    if len(column_order) != len(set(column_order)):
        msg = "Ambiguous ordering: `column_order` contained duplicates."
        raise nx.NetworkXError(msg)

    row_index = dict(zip(row_order, itertools.count()))
    col_index = dict(zip(column_order, itertools.count()))

    if G.number_of_edges() == 0:
        row, col, data = [], [], []
    else:
        row, col, data = zip(
            *(
                (row_index[u], col_index[v], d.get(weight, 1))
                for u, v, d in G.edges(row_order, data=True)
                if u in row_index and v in col_index
            )
        )
    A = sp.sparse.coo_array((data, (row, col)), shape=(nlen, mlen), dtype=dtype)
    try:
        return A.asformat(format)
    except ValueError as err:
        raise nx.NetworkXError(f"Unknown sparse array format: {format}") from err


def biadjacency_matrix_OLD(
    G, row_order, column_order=None, dtype=None, weight="weight", format="csr"
):
    r"""Returns the biadjacency matrix of the bipartite graph G.

    Let `G = (U, V, E)` be a bipartite graph with node sets
    `U = u_{1},...,u_{r}` and `V = v_{1},...,v_{s}`. The biadjacency
    matrix [1]_ is the `r` x `s` matrix `B` in which `b_{i,j} = 1`
    if, and only if, `(u_i, v_j) \in E`. If the parameter `weight` is
    not `None` and matches the name of an edge attribute, its value is
    used instead of 1.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    row_order : list of nodes
       The rows of the matrix are ordered according to the list of nodes.

    column_order : list, optional
       The columns of the matrix are ordered according to the list of nodes.
       If column_order is None, then the ordering of columns is arbitrary.

    dtype : NumPy data-type, optional
        A valid NumPy dtype used to initialize the array. If None, then the
        NumPy default is used.

    weight : string or None, optional (default='weight')
       The edge data key used to provide each value in the matrix.
       If None, then each edge has weight 1.

    format : str in {'dense', 'bsr', 'csr', 'csc', 'coo', 'lil', 'dia', 'dok'}
        The type of the matrix to be returned (default 'csr'). For
        some algorithms different implementations of sparse matrices
        can perform better.  See [2]_ for details.

    Returns
    -------
    M : SciPy sparse array
        Biadjacency matrix representation of the bipartite graph G.

    Notes
    -----
    No attempt is made to check that the input graph is bipartite.

    For directed bipartite graphs only successors are considered as neighbors.
    To obtain an adjacency matrix with ones (or weight values) for both
    predecessors and successors you have to generate two biadjacency matrices
    where the rows of one of them are the columns of the other, and then add
    one to the transpose of the other.

    See Also
    --------
    adjacency_matrix
    from_biadjacency_matrix

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Adjacency_matrix#Adjacency_matrix_of_a_bipartite_graph
    .. [2] Scipy Dev. References, "Sparse Matrices",
       https://docs.scipy.org/doc/scipy/reference/sparse.html
    """
    import scipy as sp
    import numpy as np

    nlen = len(row_order)
    if nlen == 0:
        raise nx.NetworkXError("row_order is empty list")
    if len(row_order) != len(set(row_order)):
        msg = "Ambiguous ordering: `row_order` contained duplicates."
        raise nx.NetworkXError(msg)
    if column_order is None:
        column_order = list(set(G) - set(row_order))
    mlen = len(column_order)
    if len(column_order) != len(set(column_order)):
        msg = "Ambiguous ordering: `column_order` contained duplicates."
        raise nx.NetworkXError(msg)

    row_index = dict(zip(row_order, itertools.count()))
    col_index = dict(zip(column_order, itertools.count()))

    if G.number_of_edges() == 0:
        row, col, data = [], [], []
    else:
        row, col, data = zip(
            *(
                (row_index[u], col_index[v], d.get(weight, 1))
                for u, v, d in G.edges(row_order, data=True)
                if u in row_index and v in col_index
            )
        )
    A = sp.sparse.coo_array((data, (row, col)), shape=(nlen, mlen), dtype=dtype)
    try:
        return A.asformat(format)
    except ValueError as err:
        raise nx.NetworkXError(f"Unknown sparse array format: {format}") from err
