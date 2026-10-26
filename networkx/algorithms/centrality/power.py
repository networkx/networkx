"""Bonacich power centrality."""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["power_centrality"]


@not_implemented_for("multigraph")
@nx._dispatch(edge_attrs="weight")
def power_centrality(G, beta=0.1, normalized=False, weight=None):
    r"""Compute the Bonacich power centrality for the graph G.

    Bonacich power centrality computes the centrality of a node based on the
    centrality of its neighbors. It is a generalization of eigenvector centrality,
    motivated by the observation that power does not equal centrality in exchange
    networks - power comes from being connected to those who are powerless [1]_.
    The Bonacich power centrality for node $i$ is:

    .. math::

        c_i(\alpha, \beta) = \alpha (\mathbf{I} - \beta \mathbf{A})^{-1} \mathbf{A}
            \mathbf{1},

    where $\mathbf{A}$ is the graph adjacency matrix, $\alpha$ is a scaling parameter,
    $\beta$ is a decay rate, and $\mathbf{1}$ is a column vector of ones.

    Following [1]_, if `normalized = False`, this algorithm sets $\alpha$ such that
    $\sum_i c_i(\alpha, \beta)^2$ equals to the number of nodes in the network. This
    allows $c_i(\alpha, \beta) = 1$ to be used as a reference value for the "middle"
    of the centrality range.

    $\beta$ reflects the degree to which $i$'s power is a function of those to whom
    $i$ is connected. The magnitude of $\beta$ controls the influence of distant nodes
    on $i$'s power, with larger magnitudes indicating slower rates of decay. When
    $\beta > 0$, a node becomes more powerful as its neighbors becomes more powerful
    (as occurs in cooperative relations). When $\beta < 0$, a node becomes powerful
    only when their neighbors become weaker (as occurs in competitive or antagonistic
    relations). When $\beta = 1 / \kappa$ ($\kappa$ is the largest eigenvalue of
    $\mathbf{A}$), this measure is equivalent to eigenvector centrality [3]_.

    Parameters
    ----------
    G : graph
      A NetworkX graph

    beta : scalar, optional (default=0.1)
      The decay rate $\beta$, can be negative.

    normalized : bool, optional (default=False)
      If True, the centrality scores are normalized such that they sum to 1.

    weight : None or string, optional (default=None)
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.
      In this measure the weight is interpreted as the connection strength.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with Bonacich power centrality as the value.

    Raises
    ------
    numpy.linalg.LinAlgError :
       If $\mathbf{I} - \beta \mathbf{A}$ is singular

    Examples
    --------
    >>> G = nx.star_graph(3)
    >>> centrality = nx.power_centrality(G)
    >>> for n, c in sorted(centrality.items()):
    ...     print(f"{n} {c:.2f}")
    0 1.65
    1 0.65
    2 0.65
    3 0.65

    See Also
    --------
    katz_centrality
    katz_centrality_numpy
    eigenvector_centrality_numpy
    eigenvector_centrality
    :func:`~networkx.algorithms.link_analysis.pagerank_alg.pagerank`
    :func:`~networkx.algorithms.link_analysis.hits_alg.hits`

    Notes
    -----
    This algorithm is implemented with reference to the R igraph implementation [2]_.

    One interesting feature of this centrality measure is its relative instability to
    changes in the magnitude of $\beta$ (particularly in the negative case). If your
    theory motivates use of this measure, you should be very careful to choose $\beta$
    on a non-ad-hoc basis. For more information, see [3]_.

    This algorithm may fail if $\mathbf{I} - \beta \mathbf{A}$ is singular.

    References
    ----------
    .. [1] Phillip Bonacich:
       "Power and Centrality: A Family of Measures."
       American Journal of Sociology, 92, 1170-1182.
       https://www.jstor.org/stable/pdf/2780000.pdf
    .. [2] "Find Bonacich Power Centrality Scores of Network Positions."
       https://igraph.org/r/html/1.2.6/power_centrality.html
    .. [3] Simon Rodan:
       "Choosing the ‘β’ parameter when using the Bonacich power measure."
       Journal of Social Structure 12.1 (2011): 1-23.
       https://intapi.sciendo.com/pdf/10.21307/joss-2019-032
    """
    import numpy as np

    if len(G) == 0:
        return {}

    A = nx.adjacency_matrix(G, weight=weight).todense()
    n = A.shape[0]
    I = np.identity(n)

    centrality = np.linalg.solve(I - beta * A, np.matmul(A, np.ones(n)))

    if normalized:
        centrality = centrality / sum(centrality)
    else:
        centrality = centrality * np.sqrt(n / sum(centrality**2))

    return dict(zip(G.nodes, centrality))
