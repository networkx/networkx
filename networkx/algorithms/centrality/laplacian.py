"""
Laplacian centrality measures.
"""
import networkx as nx

__all__ = ["laplacian_centrality"]


def laplacian_centrality(
    G, normalized=True, nodelist=None, weight="weight", walk_type=None, alpha=0.95
):
    r"""Compute the Laplacian centrality for nodes in the graph `G`.

    The Laplacian Centrality of a node `i` is measured by the drop in the Laplacian Energy
    after deleting node `i` from the graph. The Laplacian Energy is the sum of the squared
    eigenvalues of a graph's Laplacian matrix.

    .. math::

        C_L(u_i,G) = \frac{(\Delta E)_i}{E_L (G)} = \frac{E_L (G)-E_L (G_i)}{E_L (G)}

        E_L (G) = \sum_{i=0}^n \lambda_i^2

    Where $E_L (G)$ is the Laplacian energy of graph `G`,
    E_L (G_i) is the Laplacian energy of graph `G` after deleting node `i`
    and $\lambda_i$ are the eigenvalues of `G`'s Laplacian matrix.
    This formula shows the normalized value. Without normalization,
    the numerator on the right side is returned.

    Parameters
    ----------

    G : graph
        A networkx graph

    normalized : bool (default = True)
        If True the centrality score is scaled so the sum over all nodes is 1.
        If False the centrality score for each node is the drop in Laplacian
        energy when that node is removed.

    nodelist : list, optional (default = None)
        The rows and columns are ordered according to the nodes in nodelist. If nodelist is None, then the ordering is produced by G.nodes().

    weight: string or None, optional (default=`weight`)
        Optional parameter for the Laplacian matrix calculation. The edge data key used to compute each value in the matrix. If None, then each edge has weight 1.

    walk_type : string or None, optional (default=None)
        Optional parameter for the Laplacian matrix calculation. If None, P is selected depending on the properties of the graph. Otherwise is one of `random`, `lazy`, or `pagerank`.

    alpha : real (default = 0.95)
        Optional parameter for the Laplacian matrix calculation. (1 - alpha) is the teleportation probability used with pagerank.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with Laplacian centrality as the value.

    Examples
    --------
    >>> G = nx.Graph()
    >>> edges = [(0, 1, 4), (0, 2, 2), (2, 1, 1), (1, 3, 2), (1, 4, 2), (4, 5, 1)]
    >>> G.add_weighted_edges_from(edges)
    >>> sorted((v, f"{c:0.2f}") for v, c in laplacian_centrality(G).items())
    [(0, '0.70'), (1, '0.90'), (2, '0.28'), (3, '0.22'), (4, '0.26'), (5, '0.04')]

    Notes
    -----
    The algorithm is implemented based on [1] with an extension to directed graphs
    using the `nx.directed_laplacian_matrix` function.

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
    import numpy as np
    import scipy as sp
    import scipy.linalg  # call as sp.linalg
    import scipy.sparse  # call as sp.sparse

    def eigh_f(A):
        return sp.linalg.eigh(A.toarray(), eigvals_only=True)

    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            "cannot compute centrality for the null graph"
        )

    if nodelist != None:
        nodeset = set(G.nbunch_iter(nodelist))
        if len(nodeset) != len(nodelist):
            raise nx.NetworkXError(
                "nodelist contains duplicate nodes or nodes not in G"
            )
        full_nodelist = nodelist + [n for n in G if n not in nodeset]
    else:
        full_nodelist = set(G.nbunch_iter(nodelist))

    if G.is_directed():
        lap_matrix = sp.sparse.csr_matrix(
            nx.directed_laplacian_matrix(G, full_nodelist, weight, walk_type, alpha)
        )
        eigh = eigh_f(lap_matrix)

    else:
        lap_matrix = nx.laplacian_matrix(G, full_nodelist, weight)
        eigh = eigh_f(lap_matrix)

    if normalized:
        sum_of_full = np.power(eigh, 2).sum()
    else:
        sum_of_full = 1

    laplace_centralities_dict = {}
    for i, node in enumerate(full_nodelist):

        new_diag = lap_matrix.diagonal() - abs(lap_matrix.getcol(i).toarray().flatten())

        # remove row and col i from lap_matrix
        all_but_i = list(np.arange(lap_matrix.shape[0]))
        all_but_i.remove(i)
        A_2 = lap_matrix[all_but_i, :]
        A_2 = A_2[:, all_but_i]

        A_2.setdiag(np.r_[new_diag[:i], new_diag[i + 1 :]])

        sum_of_eigen_values_2 = np.power(eigh_f(A_2), 2).sum()

        if normalized:
            l_cent = 1 - (sum_of_eigen_values_2 / sum_of_full)
        else:
            l_cent = sum_of_full - sum_of_eigen_values_2

        laplace_centralities_dict[node] = l_cent

    return laplace_centralities_dict
