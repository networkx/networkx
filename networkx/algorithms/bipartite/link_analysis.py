import itertools

import networkx as nx

__all__ = ["birank"]


@nx._dispatchable(edge_attrs="weight")
def birank(
    G,
    nodes,
    alpha=None,
    beta=None,
    top_personalization={},
    bottom_personalization={},
    max_iter=100,
    tol=1.0e-6,
    weight="weight",
):
    r"""Compute the BiRank score for nodes in a bipartite network.

    Given the bipartite sets $U$ and $P$, the BiRank algorithm seeks to satisfy the following
    recursive relationships between the scores of nodes $j \in P$ and $i \in U$:

    .. math::

       p_j = \alpha \sum_{i \in U} \frac{w_{ij}}{\sqrt{d_i}\sqrt{d_j}} u_i + (1 - \alpha) p_j^0

       u_i = \beta \sum_{j \in P} \frac{w_{ij}}{\sqrt{d_i}\sqrt{d_j}} p_j + (1 - \beta) u_i^0

    where

    * $p_j$ and $u_i$ are the BiRank scores of nodes $j \in P$ and $i \in U$.
    * $w_{ij}$ is the weight of the edge between nodes $i \in U$ and $j \in P$ (With a value of 0 if no edge exists).
    * $d_i$ and $d_j$ are the weighted degrees of nodes $i \in U$ and $j \in P$, respectively.
    * $p_j^0$ and $u_i^0$ are personalization values that can encode a priori weights for the nodes $j \in P$ and $i \in U$, respectively. Akin to the query vector used by PageRank.
    * $\alpha$ and $\beta$ are damping hyperparameters applying to nodes in $P$ and $U$ respectively. They have values in the interval $[0, 1]$ and are analogous to those used by PageRank.

    Below are two use cases for this algorithm.

    1. Personalized Recommendation System
        Given a bipartite graph representing users
        and items, BiRank can be used as a collaborative filtering algorithm
        to recommend items to users. Previous ratings are encoded as edge weights,
        and the specific ratings of an individual user on a set of items is used as
        the personalization vector over items. See the example below for an implementation of
        this on a toy dataset provided in [1]_.

    2. Popularity Prediction
        Given a bipartite graph representing user interactions with items,
        e.g. commits to a GitHub repository, BiRank can be used to predict the popularity of a given
        item. Edge weights should encode the strength of the interaction signal. This could be a raw
        count, or weighted by a time decay function like that specified in Eq. (15) of [1]_. The
        personalization vectors can be used to encode existing popularity signals, for example, the
        monthly download count of a repository's package.

    Parameters
    ----------
    G : graph
       A bipartite network

    nodes : list or container
      Container with all nodes belonging to the first bipartite node set ('top'). The nodes
      in this set use the hyperparameter `alpha`, and the personalization
      dictionary `top_personalization`. The nodes in the second bipartite node set ('bottom') are
      automatically determined by taking the complement of 'top' with respect to the graph `G`.

    alpha : float, optional (default=0.80 if top_personalization is not empty, 1 otherwise)
      Damping factor for the 'top' nodes. Must be in the interval $[0, 1]$.

    beta : float, optional (default=0.80 if bottom_personalization is not empty, 1 otherwise)
      Damping factor for the 'bottom' nodes. Must be in the interval $[0, 1]$.

    top_personalization : dict, optional (default={})
      Dictionary keyed by nodes in 'top' with the personalization value as the value. Unspecified
      nodes will be assigned a personalization value of 0.

    bottom_personalization : dict, optional (default={})
      Dictionary keyed by nodes in 'bottom' with the personalization value as the value. Unspecified
      nodes will be assigned a personalization value of 0.

    max_iter : int, optional (default=100)
      Maximum number of iterations in power method eigenvalue solver.

    tol : float, optional (default=1.0e-6)
      Error tolerance used to check convergence in power method solver. The iteration will stop
      after a tolerance of both ``len(top) * tol`` and ``len(bottom) * tol`` is
      reached for nodes in 'top' and 'bottom' respectively.

    weight : string or None, optional (default='weight')
      Edge data key to use as weight.

    Returns
    -------
    birank : dictionary
       Dictionary keyed by node with the BiRank score as the value.

    Raises
    ------
    NetworkXAlgorithmError
        If the parameters `alpha` or `beta` are not in the interval [0, 1],
        or if either of the bipartite sets are empty.

    PowerIterationFailedConvergence
        If the algorithm fails to converge to the specified tolerance
        within the specified number of iterations of the power iteration
        method.

    See Also
    --------
    :func:`~networkx.algorithms.link_analysis.pagerank_alg.pagerank`
    :func:`~networkx.algorithms.link_analysis.hits_alg.hits`
    :func:`~networkx.algorithms.bipartite.centrality.betweenness_centrality`
    :func:`~networkx.algorithms.bipartite.basic.sets`
    :func:`~networkx.algorithms.bipartite.basic.is_bipartite`

    Notes
    -----
    The nodes input parameter must contain all nodes in one bipartite
    node set, but the dictionary returned contains all nodes from both
    bipartite node sets. See :mod:`bipartite documentation
    <networkx.algorithms.bipartite>` for further details on how
    bipartite graphs are handled in NetworkX.

    References
    ----------
    .. [1] Xiangnan He, Ming Gao, Min-Yen Kan, and Dingxian Wang. 2017.
    BiRank: Towards Ranking on Bipartite Graphs. IEEE Trans. on Knowl.
    and Data Eng. 29, 1 (January 2017), 57–71.
    https://arxiv.org/pdf/1708.04396

    """
    import numpy as np
    import scipy as sp

    # Initialize the sets of top and bottom nodes
    top = set(nodes)
    bottom = set(G) - top
    top_count = len(top)
    bottom_count = len(bottom)

    if top_count == 0 or bottom_count == 0:
        raise nx.NetworkXAlgorithmError(
            "The BiRank algorithm requires a bipartite graph with at least one node in each set."
        )

    # Set default values for alpha and beta if not provided
    if alpha is None:
        alpha = 0.8 if top_personalization else 1
    if beta is None:
        beta = 0.8 if bottom_personalization else 1

    if alpha < 0 or alpha > 1:
        raise nx.NetworkXAlgorithmError("alpha must be in the interval [0, 1]")
    if beta < 0 or beta > 1:
        raise nx.NetworkXAlgorithmError("beta must be in the interval [0, 1]")

    # Initialize query vectors
    p0 = np.array([top_personalization.get(n, 0) for n in top], dtype=float)
    u0 = np.array([bottom_personalization.get(n, 0) for n in bottom], dtype=float)

    # Construct weight biadjacency matrix `S`
    W = nx.bipartite.biadjacency_matrix(G, bottom, top, weight=weight, dtype=float)
    D_p = sp.sparse.dia_array(
        ([1.0 / np.sqrt(W.sum(axis=0))], [0]), shape=(top_count, top_count), dtype=float
    )
    D_u = sp.sparse.dia_array(
        ([1.0 / np.sqrt(W.sum(axis=1))], [0]),
        shape=(bottom_count, bottom_count),
        dtype=float,
    )
    S = D_u @ W @ D_p

    # Initialize birank vectors for iteration
    p = np.ones(top_count, dtype=float) / top_count
    u = np.ones(bottom_count, dtype=float) / bottom_count

    # Iterate until convergence
    for _ in range(max_iter):
        p_last = p
        u_last = u
        p = alpha * (S.T @ u) + (1 - alpha) * p0
        u = beta * (S @ p) + (1 - beta) * u0
        err_p = np.absolute(p - p_last).sum()
        err_u = np.absolute(u - u_last).sum()
        if err_p < top_count * tol and err_u < bottom_count * tol:
            return dict(
                zip(itertools.chain(top, bottom), map(float, itertools.chain(p, u)))
            )

    # If we reach this point, we have not converged
    raise nx.PowerIterationFailedConvergence(max_iter)
