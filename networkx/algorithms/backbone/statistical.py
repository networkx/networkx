"""
Statistical backbone extraction methods.

These methods evaluate edge significance using hypothesis testing against
a null model. Each method computes a p-value (or score) for every edge,
which can then be filtered using functions in ``backbone.filters``.

Methods
-------
disparity_filter
    Serrano et al. (2009) — uniform distribution null model.
noise_corrected_filter
    Coscia & Neffke (2017) — Bayesian binomial framework.
marginal_likelihood_filter
    Dianati (2016) — binomial null considering both endpoints.
ecm_filter
    Gemmetto et al. (2017) — enhanced configuration model.
lans_filter
    Foti et al. (2011) — nonparametric, empirical CDF-based.
"""

import math

import networkx as nx

__all__ = [
    "disparity_filter",
    "noise_corrected_filter",
    "marginal_likelihood_filter",
    "ecm_filter",
    "lans_filter",
]


# =====================================================================
# Helper: validate positive weights
# =====================================================================


def _validate_weights(G, weight):
    """Check that all edges have a positive weight attribute."""
    for u, v, data in G.edges(data=True):
        w = data.get(weight)
        if w is None or w <= 0:
            raise nx.NetworkXError(
                f"Edge ({u}, {v}) has non-positive or missing weight."
            )


# =====================================================================
# 1. Disparity filter — Serrano et al. (2009)
# =====================================================================


@nx._dispatchable(edge_attrs="weight", preserve_all_attrs=True, returns_graph=True)
def disparity_filter(G, weight="weight"):
    r"""Compute disparity filter p-values for each edge.

    The disparity filter [1]_ tests whether an edge's weight is
    statistically significant compared to a null model where each node's
    total strength is uniformly distributed across its edges.

    For each node *u* with degree *k_u* and strength *s_u*, the normalised
    weight of edge (u, v) is ``p_uv = w_uv / s_u``.  Under the null the
    probability of observing a normalised weight >= p_uv is::

        alpha_uv = 1 - (k_u - 1) * (1 - p_uv) ** (k_u - 2)

    For an undirected edge the p-value is the *minimum* of the values
    computed from each endpoint.  For a directed edge the p-value is
    computed from the source node only (out-strength, out-degree).

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    weight : string, optional (default="weight")
        Edge attribute key for weights.  All weights must be positive.

    Returns
    -------
    H : graph
        A copy of *G* (same type) with ``"disparity_pvalue"`` added as an
        edge attribute.

    Raises
    ------
    NetworkXError
        If any edge has a non-positive or missing weight.

    See Also
    --------
    noise_corrected_filter : Bayesian binomial significance scores.
    marginal_likelihood_filter : Binomial null considering both endpoints.
    ecm_filter : Enhanced configuration model p-values.
    lans_filter : Nonparametric, empirical CDF-based p-values.

    Notes
    -----
    The algorithm runs in $O(m)$ time where $m$ is the number of edges,
    since each edge is visited a constant number of times.  Degree-one
    nodes always produce a p-value of 1.0.

    References
    ----------
    .. [1] Serrano, M. A., Boguna, M., & Vespignani, A. (2009).
       Extracting the multiscale backbone of complex weighted networks.
       *PNAS*, 106(16), 6483-6488.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import disparity_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 2.0)])
    >>> H = disparity_filter(G)
    >>> "disparity_pvalue" in H[0][1]
    True
    """
    H = G.copy()
    _validate_weights(H, weight)

    if G.is_directed():
        strength = dict(G.out_degree(weight=weight))
        degree = dict(G.out_degree())
    else:
        strength = dict(G.degree(weight=weight))
        degree = dict(G.degree())

    for u, v, data in H.edges(data=True):
        w = data[weight]
        if G.is_directed():
            pval = _disparity_node_pvalue(w, strength[u], degree[u])
        else:
            pval_u = _disparity_node_pvalue(w, strength[u], degree[u])
            pval_v = _disparity_node_pvalue(w, strength[v], degree[v])
            pval = min(pval_u, pval_v)
        data["disparity_pvalue"] = pval

    return H


def _disparity_node_pvalue(w, s, k):
    """Disparity p-value from one node's perspective."""
    if k <= 1:
        return 1.0
    p = min(w / s, 1.0)
    try:
        alpha = 1.0 - (k - 1) * (1.0 - p) ** (k - 2)
    except (OverflowError, ValueError):
        alpha = 0.0
    return max(alpha, 0.0)


# =====================================================================
# 2. Noise-corrected filter — Coscia & Neffke (2017)
# =====================================================================


@nx._dispatchable(edge_attrs="weight", preserve_all_attrs=True, returns_graph=True)
def noise_corrected_filter(G, weight="weight"):
    r"""Compute noise-corrected edge significance scores.

    Uses a Bayesian framework where each edge weight is modelled as the
    outcome of a binomial process [1]_.  The expected weight of edge
    (u, v) given a total network weight *W* is::

        E[w_uv] = (s_u * s_v) / W

    The score measures how many standard deviations the observed weight
    lies above the expectation (a z-score).  Higher scores indicate
    more significant edges.

    For directed graphs, out-strength of *u* and in-strength of *v*
    are used.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    weight : string, optional (default="weight")
        Edge attribute key for weights.  All weights must be positive.

    Returns
    -------
    H : graph
        A copy of *G* (same type) with ``"nc_score"`` edge attribute
        (z-score; higher means more significant).

    Raises
    ------
    NetworkXError
        If any edge has a non-positive or missing weight.

    See Also
    --------
    disparity_filter : Disparity filter p-values.
    marginal_likelihood_filter : Binomial null considering both endpoints.
    ecm_filter : Enhanced configuration model p-values.
    lans_filter : Nonparametric, empirical CDF-based p-values.

    Notes
    -----
    The z-score is computed as
    $z = (w - n \cdot p) / \sqrt{n \cdot p \cdot (1 - p)}$
    where $n = W$ and $p = s_u \cdot s_v / W^2$.

    References
    ----------
    .. [1] Coscia, M. & Neffke, F. M. (2017). Network backboning with
       noisy data. *Proc. IEEE ICDE*, 425-436.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import noise_corrected_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 2.0)])
    >>> H = noise_corrected_filter(G)
    >>> "nc_score" in H[0][1]
    True
    """
    H = G.copy()
    _validate_weights(H, weight)

    W = sum(d[weight] for _, _, d in G.edges(data=True))
    if W == 0:
        return H

    if G.is_directed():
        s_out = dict(G.out_degree(weight=weight))
        s_in = dict(G.in_degree(weight=weight))
    else:
        s_out = dict(G.degree(weight=weight))
        s_in = s_out

    for u, v, data in H.edges(data=True):
        w = data[weight]
        su = s_out[u]
        sv = s_in[v]

        p_ij = (su * sv) / (W * W)
        n = W
        expected = n * p_ij
        variance = n * p_ij * (1 - p_ij)

        if variance > 0:
            z = (w - expected) / math.sqrt(variance)
        else:
            z = 0.0

        data["nc_score"] = z

    return H


# =====================================================================
# 3. Marginal likelihood filter — Dianati (2016)
# =====================================================================


@nx._dispatchable(edge_attrs="weight", preserve_all_attrs=True, returns_graph=True)
def marginal_likelihood_filter(G, weight="weight"):
    r"""Compute marginal likelihood p-values for each edge.

    The marginal likelihood filter [1]_ considers edge weights as
    integer counts under a binomial null model that accounts for
    both endpoints' strengths.

    The p-value for edge (u, v) is::

        P(X >= w_uv)  where  X ~ Binom(s_u, s_v / (W - s_u))

    clamped to valid parameter ranges.

    Parameters
    ----------
    G : graph
        A NetworkX graph.  Integer weights are recommended.

    weight : string, optional (default="weight")
        Edge attribute key for weights.  All weights must be positive.

    Returns
    -------
    H : graph
        A copy of *G* (same type) with ``"ml_pvalue"`` edge attribute.

    Raises
    ------
    NetworkXError
        If any edge has a non-positive or missing weight.

    See Also
    --------
    disparity_filter : Disparity filter p-values.
    noise_corrected_filter : Bayesian binomial significance scores.
    ecm_filter : Enhanced configuration model p-values.
    lans_filter : Nonparametric, empirical CDF-based p-values.

    Notes
    -----
    Edge weights are rounded to the nearest integer for the binomial
    survival function computation.  The binomial parameters are
    $n = \mathrm{round}(s_u)$ and $p = \min(s_v / (W - s_u), 1)$.

    References
    ----------
    .. [1] Dianati, N. (2016). Unwinding the hairball graph: Pruning
       algorithms for weighted complex networks. *Physical Review E*,
       93, 012304.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import marginal_likelihood_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 2.0)])
    >>> H = marginal_likelihood_filter(G)
    >>> "ml_pvalue" in H[0][1]
    True
    """
    from scipy import stats as sp_stats

    H = G.copy()
    _validate_weights(H, weight)

    W = sum(d[weight] for _, _, d in G.edges(data=True))
    if W == 0:
        return H

    if G.is_directed():
        s_out = dict(G.out_degree(weight=weight))
        s_in = dict(G.in_degree(weight=weight))
    else:
        s_out = dict(G.degree(weight=weight))
        s_in = s_out

    for u, v, data in H.edges(data=True):
        w = data[weight]
        su = s_out[u]
        sv = s_in[v]

        n_param = int(round(su))
        denom = W - su
        if denom > 0 and n_param > 0:
            p_param = min(sv / denom, 1.0)
            pval = sp_stats.binom.sf(int(round(w)) - 1, n_param, p_param)
        else:
            pval = 1.0

        data["ml_pvalue"] = float(pval)

    return H


# =====================================================================
# 4. ECM filter — Gemmetto et al. (2017)
# =====================================================================


@nx._dispatchable(edge_attrs="weight", preserve_all_attrs=True, returns_graph=True)
def ecm_filter(G, weight="weight", max_iter=1000, tol=1e-6):
    r"""Compute ECM (Enhanced Configuration Model) p-values.

    The ECM [1]_ is a maximum-entropy null model for weighted networks
    that preserves the expected degree *and* strength sequence.  Lagrange
    multipliers $(x_i, y_i)$ are assigned to each node and solved
    iteratively.  The expected weight of edge (u, v) is::

        <w_uv> = (x_u * x_v * y_u * y_v) / (1 - y_u * y_v)

    The p-value is computed assuming a geometric distribution with
    parameter ``1 - y_u * y_v``.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    weight : string, optional (default="weight")
        Edge attribute key for weights.  All weights must be positive.

    max_iter : int, optional (default=1000)
        Maximum number of iterations for the fixed-point solver.

    tol : float, optional (default=1e-6)
        Convergence tolerance for the Lagrange multipliers.

    Returns
    -------
    H : graph
        A copy of *G* (same type) with ``"ecm_pvalue"`` edge attribute.

    Raises
    ------
    NetworkXError
        If any edge has a non-positive or missing weight.

    See Also
    --------
    disparity_filter : Disparity filter p-values.
    noise_corrected_filter : Bayesian binomial significance scores.
    marginal_likelihood_filter : Binomial null considering both endpoints.
    lans_filter : Nonparametric, empirical CDF-based p-values.

    Notes
    -----
    The fixed-point iteration alternately updates $x_i$ and $y_i$ for
    each node to match the observed degree and strength.  Convergence
    is declared when the maximum absolute change in both $x$ and $y$
    falls below *tol*.  The geometric distribution parameter is
    $q = y_u \cdot y_v$, and the p-value is $q^{\mathrm{round}(w)}$.

    References
    ----------
    .. [1] Gemmetto, V., Cardillo, A., & Garlaschelli, D. (2017).
       Irreducible network backbones: unbiased graph filtering via
       maximum entropy. arXiv:1706.00230.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import ecm_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 2.0)])
    >>> H = ecm_filter(G)
    >>> "ecm_pvalue" in H[0][1]
    True
    """
    import numpy as np

    H = G.copy()
    _validate_weights(H, weight)

    nodes = list(G.nodes())
    n = len(nodes)
    if n == 0:
        return H

    node_idx = {v: i for i, v in enumerate(nodes)}

    if G.is_directed():
        deg = np.array([G.out_degree(v) for v in nodes], dtype=float)
        strength = np.array(
            [G.out_degree(v, weight=weight) for v in nodes], dtype=float
        )
    else:
        deg = np.array([G.degree(v) for v in nodes], dtype=float)
        strength = np.array([G.degree(v, weight=weight) for v in nodes], dtype=float)

    # Initialise Lagrange multipliers
    deg_sum = deg.sum()
    str_sum = strength.sum()
    x = np.where(deg > 0, deg / max(deg_sum, 1), 1e-10)
    y = np.where(strength > 0, strength / max(str_sum, 1), 1e-10)
    y = np.clip(y, 1e-15, 1.0 - 1e-10)

    # Fixed-point iterations
    for _ in range(max_iter):
        x_new = np.zeros(n)
        y_new = np.zeros(n)

        for i in range(n):
            sum_x = 0.0
            sum_y = 0.0
            for j in range(n):
                if i == j:
                    continue
                yy = y[i] * y[j]
                if yy >= 1.0:
                    yy = 1.0 - 1e-15
                denom = 1.0 - yy
                xy = x[i] * x[j]
                p_ij = (xy * yy) / (denom + xy * yy)
                if denom > 0:
                    w_ij = (xy * yy) / (denom * denom + xy * yy * denom)
                else:
                    w_ij = 0
                sum_x += p_ij
                sum_y += w_ij

            x_new[i] = deg[i] / sum_x if sum_x > 0 else 1e-10
            y_new[i] = strength[i] / sum_y if sum_y > 0 else 1e-10

        y_new = np.clip(y_new, 1e-15, 1.0 - 1e-10)

        if np.max(np.abs(x_new - x)) < tol and np.max(np.abs(y_new - y)) < tol:
            x, y = x_new, y_new
            break
        x, y = x_new, y_new

    # Compute p-values using geometric distribution
    for u, v, data in H.edges(data=True):
        w = data[weight]
        i, j = node_idx[u], node_idx[v]
        yy = y[i] * y[j]
        if yy >= 1.0:
            yy = 1.0 - 1e-15

        q = yy
        if 0 < q < 1:
            pval = q ** int(round(w))
        elif q >= 1:
            pval = 0.0
        else:
            pval = 1.0

        data["ecm_pvalue"] = float(max(min(pval, 1.0), 0.0))

    return H


# =====================================================================
# 5. LANS — Foti et al. (2011)
# =====================================================================


@nx._dispatchable(edge_attrs="weight", preserve_all_attrs=True, returns_graph=True)
def lans_filter(G, weight="weight"):
    r"""Compute LANS (Locally Adaptive Network Sparsification) p-values.

    LANS [1]_ is a nonparametric method that makes no distributional
    assumptions.  For each edge (u, v), it computes the fraction of
    edges at node *u* (and node *v*) that have weight <= w_uv --- the
    empirical CDF value.  The edge p-value is one minus the maximum
    of the two eCDF values (so lower p means more significant).

    For directed graphs, only the source node's out-edges are used.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    weight : string, optional (default="weight")
        Edge attribute key for weights.  All weights must be positive.

    Returns
    -------
    H : graph
        A copy of *G* (same type) with ``"lans_pvalue"`` edge attribute.

    Raises
    ------
    NetworkXError
        If any edge has a non-positive or missing weight.

    See Also
    --------
    disparity_filter : Disparity filter p-values.
    noise_corrected_filter : Bayesian binomial significance scores.
    marginal_likelihood_filter : Binomial null considering both endpoints.
    ecm_filter : Enhanced configuration model p-values.

    Notes
    -----
    The method is entirely nonparametric: it ranks each edge against
    the other edges incident to the same node, using a sorted-list
    binary search for $O(\log k)$ per edge-endpoint lookup.  Total
    runtime is $O(m \log k_{\max})$.

    References
    ----------
    .. [1] Foti, N. J., Hughes, J. M., & Rockmore, D. N. (2011).
       Nonparametric sparsification of complex multiscale networks.
       *PLoS ONE*, 6(2), e16431.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import lans_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 2.0)])
    >>> H = lans_filter(G)
    >>> "lans_pvalue" in H[0][1]
    True
    """
    H = G.copy()
    _validate_weights(H, weight)

    # Pre-compute sorted weight lists per node
    if G.is_directed():
        node_weights = {}
        for u in G.nodes():
            ws = sorted(d[weight] for _, _, d in G.out_edges(u, data=True))
            node_weights[u] = ws
    else:
        node_weights = {}
        for u in G.nodes():
            ws = sorted(G[u][v][weight] for v in G[u])
            node_weights[u] = ws

    for u, v, data in H.edges(data=True):
        w = data[weight]

        if G.is_directed():
            ecdf_u = _empirical_cdf(w, node_weights[u])
            pval = 1.0 - ecdf_u
        else:
            ecdf_u = _empirical_cdf(w, node_weights[u])
            ecdf_v = _empirical_cdf(w, node_weights[v])
            pval = 1.0 - max(ecdf_u, ecdf_v)

        data["lans_pvalue"] = max(pval, 0.0)

    return H


def _empirical_cdf(w, sorted_weights):
    """Compute the empirical CDF value F(w) from a sorted list."""
    n = len(sorted_weights)
    if n == 0:
        return 0.0
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_weights[mid] <= w:
            lo = mid + 1
        else:
            hi = mid
    return lo / n
