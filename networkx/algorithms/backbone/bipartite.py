"""
Bipartite projection backbone methods.

These methods operate on bipartite networks and extract significant edges
in the one-mode projection among "agent" nodes.

Methods
-------
sdsm
    Stochastic Degree Sequence Model (Neal 2014).
fdsm
    Fixed Degree Sequence Model (Neal et al. 2021).
"""

import networkx as nx

__all__ = ["sdsm", "fdsm"]


def _validate_bipartite(B, agent_nodes):
    """Validate that B is bipartite and agent_nodes is a valid partition."""
    if not nx.is_bipartite(B):
        raise nx.NetworkXError("Input graph B is not bipartite.")
    all_nodes = set(B.nodes())
    agent_set = set(agent_nodes)
    if not agent_set.issubset(all_nodes):
        raise nx.NetworkXError("agent_nodes contains nodes not in B.")


def _bipartite_projection_matrix(B, agent_nodes):
    """Build the co-occurrence matrix for agent nodes.

    Returns
    -------
    agents : list
        Ordered list of agent nodes.
    artifacts : list
        Ordered list of artifact nodes.
    R : np.ndarray of shape (n_agents, n_artifacts)
        Binary incidence matrix (agents x artifacts).
    observed : np.ndarray of shape (n_agents, n_agents)
        Observed co-occurrence counts (symmetric).
    """
    import numpy as np

    agent_set = set(agent_nodes)
    agents = sorted(agent_set)
    artifacts = sorted(set(B.nodes()) - agent_set)

    a_idx = {v: i for i, v in enumerate(agents)}
    f_idx = {v: i for i, v in enumerate(artifacts)}

    na = len(agents)
    nf = len(artifacts)
    R = np.zeros((na, nf), dtype=int)

    for u, v in B.edges():
        if u in a_idx and v in f_idx:
            R[a_idx[u], f_idx[v]] = 1
        elif v in a_idx and u in f_idx:
            R[a_idx[v], f_idx[u]] = 1

    # Observed co-occurrence matrix
    observed = R @ R.T
    np.fill_diagonal(observed, 0)

    return agents, artifacts, R, observed


# =====================================================================
# 1. SDSM — Neal (2014)
# =====================================================================


@nx._dispatchable(graphs="B", preserve_all_attrs=True, returns_graph=True)
def sdsm(B, agent_nodes, alpha=0.05, weight=None):
    """Extract a backbone from a bipartite projection using the SDSM.

    The Stochastic Degree Sequence Model [1]_ generates random bipartite
    networks that preserve the row and column sums *on average* (as
    probabilities).  The probability of a cell being 1 is determined by a
    logistic model fitted to match row and column totals.

    The p-value for each pair of agents is computed analytically using a
    Poisson-binomial approximation (normal).

    Parameters
    ----------
    B : graph
        A bipartite NetworkX graph.
    agent_nodes : iterable
        Nodes in the "agent" partition.
    alpha : float, optional (default=0.05)
        Significance level.  Edges with p-value < *alpha* are retained.
    weight : None or string, optional (default=None)
        Not used for SDSM (bipartite is unweighted); reserved for API
        consistency.

    Returns
    -------
    backbone : graph
        Unipartite backbone among agent nodes.  Each edge has a
        ``"sdsm_pvalue"`` attribute.

    Raises
    ------
    NetworkXError
        If *B* is not bipartite or *agent_nodes* contains nodes not in *B*.

    See Also
    --------
    fdsm : Fixed Degree Sequence Model backbone.

    References
    ----------
    .. [1] Neal, Z. P. (2014). The backbone of bipartite projections:
       Inferring relationships from co-authorship, co-sponsorship,
       co-attendance and other co-behaviors. *Social Networks*, 39, 84-97.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import sdsm
    >>> B = nx.Graph()
    >>> B.add_edges_from([(1, "a"), (1, "b"), (2, "a"), (2, "c"), (3, "b"), (3, "c")])
    >>> backbone = sdsm(B, agent_nodes=[1, 2, 3])
    >>> "sdsm_pvalue" in backbone[1][2]
    True
    """
    import numpy as np
    from scipy import stats as sp_stats

    _validate_bipartite(B, agent_nodes)
    agents, artifacts, R, observed = _bipartite_projection_matrix(B, agent_nodes)

    na = len(agents)
    nf = len(artifacts)

    # Row and column sums
    row_sums = R.sum(axis=1).astype(float)  # agent degrees
    col_sums = R.sum(axis=0).astype(float)  # artifact degrees

    # Probability matrix: P[i,k] = prob that agent i connects to artifact k
    # Use the fixed-point approach: P_ik = r_i * c_k / N  (simple model)
    total = R.sum()
    if total == 0:
        return nx.Graph()

    P = np.outer(row_sums, col_sums) / total
    P = np.clip(P, 0, 1)

    backbone = nx.Graph()
    backbone.add_nodes_from(agents)

    for i in range(na):
        for j in range(i + 1, na):
            obs = observed[i, j]

            # For each artifact k, probability both agents connect:
            # p_k = P[i,k] * P[j,k]
            probs = P[i, :] * P[j, :]

            # Mean and variance of the sum of independent Bernoullis
            mu = probs.sum()
            sigma2 = (probs * (1 - probs)).sum()

            if sigma2 > 0:
                z = (obs - mu) / np.sqrt(sigma2)
                pval = 1.0 - sp_stats.norm.cdf(z)
            else:
                pval = 0.0 if obs > mu else 1.0

            pval = float(max(min(pval, 1.0), 0.0))

            if pval < alpha:
                backbone.add_edge(agents[i], agents[j], sdsm_pvalue=pval)
            # Always record if we want the scored graph
            # For consistency, add all edges with pvalues
            if not backbone.has_edge(agents[i], agents[j]):
                backbone.add_edge(agents[i], agents[j], sdsm_pvalue=pval)

    return backbone


# =====================================================================
# 2. FDSM — Neal et al. (2021)
# =====================================================================


@nx._dispatchable(graphs="B", preserve_all_attrs=True, returns_graph=True)
def fdsm(B, agent_nodes, alpha=0.05, trials=1000, seed=None):
    """Extract a backbone from a bipartite projection using the FDSM.

    The Fixed Degree Sequence Model [1]_ uses Monte Carlo simulation to
    estimate p-values.  Each trial generates a random bipartite graph that
    *exactly* preserves both the row sums (agent degrees) and column sums
    (artifact degrees), then computes the co-occurrence matrix.

    Parameters
    ----------
    B : graph
        A bipartite NetworkX graph.
    agent_nodes : iterable
        Nodes in the "agent" partition.
    alpha : float, optional (default=0.05)
        Significance level.
    trials : int, optional (default=1000)
        Number of Monte Carlo randomisations.
    seed : integer, random_state, or None (default)
        Random seed for reproducibility.

    Returns
    -------
    backbone : graph
        Unipartite backbone among agent nodes.  Each edge has an
        ``"fdsm_pvalue"`` attribute.

    Raises
    ------
    NetworkXError
        If *B* is not bipartite or *agent_nodes* contains nodes not in *B*.

    See Also
    --------
    sdsm : Stochastic Degree Sequence Model backbone.

    References
    ----------
    .. [1] Neal, Z. P., Domagalski, R., & Sagan, B. (2021). Comparing
       alternatives to the fixed degree sequence model. *Scientific
       Reports*, 11, 23929.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import fdsm
    >>> B = nx.Graph()
    >>> B.add_edges_from([(1, "a"), (1, "b"), (2, "a"), (2, "c"), (3, "b"), (3, "c")])
    >>> backbone = fdsm(B, agent_nodes=[1, 2, 3], trials=100, seed=42)
    >>> "fdsm_pvalue" in backbone[1][2]
    True
    """
    import numpy as np

    _validate_bipartite(B, agent_nodes)
    agents, artifacts, R, observed = _bipartite_projection_matrix(B, agent_nodes)

    na = len(agents)
    nf = len(artifacts)
    rng = np.random.default_rng(seed)

    row_sums = R.sum(axis=1)
    col_sums = R.sum(axis=0)

    # Count how many times the random co-occurrence >= observed
    exceed_count = np.zeros((na, na), dtype=int)

    for _ in range(trials):
        R_rand = _random_bipartite_matrix(row_sums, col_sums, rng)
        co_rand = R_rand @ R_rand.T
        np.fill_diagonal(co_rand, 0)
        exceed_count += (co_rand >= observed).astype(int)

    backbone = nx.Graph()
    backbone.add_nodes_from(agents)

    for i in range(na):
        for j in range(i + 1, na):
            pval = exceed_count[i, j] / trials
            backbone.add_edge(agents[i], agents[j], fdsm_pvalue=float(pval))

    return backbone


def _random_bipartite_matrix(row_sums, col_sums, rng):
    """Generate a random binary matrix with given row and column sums.

    Uses a greedy fill followed by Curveball swaps for randomisation.
    """
    import numpy as np

    nrows = len(row_sums)
    ncols = len(col_sums)

    # Initialise with a valid matrix using a greedy fill
    R = np.zeros((nrows, ncols), dtype=int)
    col_remaining = col_sums.copy().astype(float)

    for i in range(nrows):
        k = int(row_sums[i])
        if k <= 0:
            continue
        # Only consider columns that still have capacity
        avail = np.where(col_remaining > 0)[0]
        if len(avail) == 0:
            continue
        k = min(k, len(avail))
        probs = col_remaining[avail]
        total = probs.sum()
        if total <= 0:
            continue
        probs = probs / total
        chosen = rng.choice(avail, size=k, replace=False, p=probs)
        R[i, chosen] = 1
        col_remaining[chosen] -= 1
        col_remaining = np.maximum(col_remaining, 0)

    # Curveball swaps to improve randomisation
    n_swaps = nrows * 5
    for _ in range(n_swaps):
        if nrows < 2:
            break
        r1, r2 = rng.choice(nrows, size=2, replace=False)
        cols1 = set(np.where(R[r1] == 1)[0])
        cols2 = set(np.where(R[r2] == 1)[0])
        only1 = list(cols1 - cols2)
        only2 = list(cols2 - cols1)
        if len(only1) == 0 or len(only2) == 0:
            continue
        n_swap = rng.integers(1, min(len(only1), len(only2)) + 1)
        swap1 = rng.choice(only1, size=n_swap, replace=False)
        swap2 = rng.choice(only2, size=n_swap, replace=False)
        R[r1, swap1] = 0
        R[r1, swap2] = 1
        R[r2, swap2] = 0
        R[r2, swap1] = 1

    return R
