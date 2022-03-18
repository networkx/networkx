"""Laplacian centrality measures."""

import networkx as nx
import numpy as np
from scipy import linalg
import scipy as sp
from scipy import sparse

__all__ = ["laplacian_centrality"]


def delete_row_csr(mat, i):
    r"""Delete specific row from a scipy csr matrix based on the index

    Parameters
    ----------
    mat : sparse matrix

    i : index of the column to drop


    Returns
    -------
    csr matrxix : sparse matrix

    """
    if not isinstance(mat, sp.sparse.csr_matrix):
        raise ValueError("works only for CSR format -- use .tocsr() first")
    n = mat.indptr[i + 1] - mat.indptr[i]
    if n > 0:
        mat.data[mat.indptr[i] : -n] = mat.data[mat.indptr[i + 1] :]
        mat.data = mat.data[:-n]
        mat.indices[mat.indptr[i] : -n] = mat.indices[mat.indptr[i + 1] :]
        mat.indices = mat.indices[:-n]
    mat.indptr[i:-1] = mat.indptr[i + 1 :]
    mat.indptr[i:] -= n
    mat.indptr = mat.indptr[:-1]
    mat._shape = (mat._shape[0] - 1, mat._shape[1])

    return mat


def delete_col_csr(mat, i):
    r"""Delete specific column from a scipy csr matrix based on the index

    Parameters
    ----------
    mat : sparse matrix

    i : index of the column to drop


    Returns
    -------
    csr matrxix : sparse matrix

    """
    idx_to_drop = np.unique(i)
    C = mat.tocoo()
    keep = ~np.in1d(C.col, idx_to_drop)
    C.data, C.row, C.col = C.data[keep], C.row[keep], C.col[keep]
    C.col -= idx_to_drop.searchsorted(C.col)  # decrement column indices
    C._shape = (C.shape[0], C.shape[1] - len(idx_to_drop))
    return C.tocsr()

    # @not_implemented_for("multigraph")


def laplacian_centrality(
    G, normalized=True, nbunch=None, directed_laplacian_matrix_args=None
):
    r"""Compute the Laplacian centrality for nodes in the graph `G`.

    The Laplacian Centrality of a node `i` is measured by the drop in the Laplacian Energy
    after deleting node `i` from the graph.

    .. math::

        C_L(u_i,G) = \frac{(\Delta E)_i}{E_L (G)} = \frac{E_L (G)-E_L (G_i)}{E_L (G)}

        E_L (G) = \sum_{i=0}^n \lambda_i^2

    Where $E_L (G)$ is the Laplacian energy of graph `G`,
    E_L (G_i) is the Laplacian energy of graph `G` after deleting node `i`
    and $\lambda_i$ are the eigenvalues of its Laplacian matrix.

    Parameters
    ----------

    G : graph
        A networkx graph

    normalized : bool (default = True)
        If False then the algorithm does't calculate Laplacian energy of entire graph `G`,
        just the Laplacian energy of the given nodes.

    nbunch : list (default = None)
        An nbunch is a single node, container of nodes or None (representing all nodes)

    b_keyword_args_dict : dictiory (default = None)


    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with Laplacian centrality as the value.

    Notes
    -----
    The algorithm is implemented based on [1] with an extension to directed graphs using nx.directed_laplacian_matrix function.

    Raises
    ------
    NetworkXPointlessConcept
        If the graph `G` is the null graph.

    References
    ----------
    .. [1] Qi, X., Fuller, E., Wu, Q., Wu, Y., and Zhang, C.-Q. (2012).
    Laplacian centrality: A new centrality measure for weighted networks.
    Information Sciences, 194:240-253.
    https://math.wvu.edu/~cqzhang/Publication-files/my-paper/INS-2012-Laplacian-W.pdf

    """

    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            "cannot compute centrality for the null graph"
        )

    if G.is_directed():
        lap_matrix = sparse.csr_matrix(
            nx.directed_laplacian_matrix(G, **directed_laplacian_matrix_args)
        )
    else:
        lap_matrix = nx.laplacian_matrix(G)

    if normalized:
        sum_of_full = np.power(
            linalg.eigh(lap_matrix.toarray(), eigvals_only=True), 2
        ).sum()
    else:
        sum_of_full = 1

    if nbunch is None:
        vs = G.nodes()
    else:
        vs = [i for i, v in enumerate(G.nodes()) if v in nbunch]

    laplace_centralities_dict = {}
    for i, v in enumerate(vs):

        new_diag = lap_matrix.diagonal() - abs(lap_matrix.getcol(i).toarray().flatten())

        A_2 = lap_matrix.copy()
        A_2 = delete_row_csr(A_2, i)
        A_2 = delete_col_csr(A_2, i)

        A_2.setdiag(np.r_[new_diag[:i], new_diag[i + 1 :]])

        sum_of_eigen_values_2 = np.power(
            linalg.eigh(A_2.toarray(), eigvals_only=True), 2
        ).sum()

        if normalized:
            l_cent = 1 - (sum_of_eigen_values_2 / sum_of_full)
        else:
            l_cent = sum_of_eigen_values_2

        laplace_centralities_dict.update({v: l_cent})

    return laplace_centralities_dict
