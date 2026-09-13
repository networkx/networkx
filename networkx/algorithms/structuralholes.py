import math

import networkx as nx

__all__ = [
    "constraint",
    "local_constraint",
    "effective_size",
    "hierarchy",
    "structural_efficiency",
]


@nx._dispatchable(edge_attrs="weight")
def mutual_weight(G, u, v, weight=None):
    """Returns the sum of the weights of the edge from `u` to `v` and
    the edge from `v` to `u` in `G`.

    `weight` is the edge data key that represents the edge weight. If
    the specified key is `None` or is not in the edge data for an edge,
    that edge is assumed to have weight 1.

    Pre-conditions: `u` and `v` must both be in `G`.

    """
    try:
        a_uv = G[u][v].get(weight, 1)
    except KeyError:
        a_uv = 0
    try:
        a_vu = G[v][u].get(weight, 1)
    except KeyError:
        a_vu = 0
    return a_uv + a_vu


@nx._dispatchable(edge_attrs="weight")
def normalized_mutual_weight(G, u, v, norm=sum, weight=None):
    """Returns normalized mutual weight of the edges from `u` to `v`
    with respect to the mutual weights of the neighbors of `u` in `G`.

    `norm` specifies how the normalization factor is computed. It must
    be a function that takes a single argument and returns a number.
    The argument will be an iterable of mutual weights
    of pairs ``(u, w)``, where ``w`` ranges over each (in- and
    out-)neighbor of ``u``. Commons values for `normalization` are
    ``sum`` and ``max``.

    `weight` can be ``None`` or a string, if None, all edge weights
    are considered equal. Otherwise holds the name of the edge
    attribute used as weight.

    """
    scale = norm(mutual_weight(G, u, w, weight) for w in set(nx.all_neighbors(G, u)))
    return 0 if scale == 0 else mutual_weight(G, u, v, weight) / scale


@nx._dispatchable(edge_attrs="weight")
def effective_size(G, nodes=None, weight=None):
    r"""Returns the effective size of all nodes in the graph ``G``.

    The *effective size* of a node's ego network is based on the concept
    of redundancy. A person's ego network has redundancy to the extent
    that her contacts are connected to each other as well. The
    nonredundant part of a person's relationships is the effective
    size of her ego network [1]_.  Formally, the effective size of a
    node $u$, denoted $e(u)$, is defined by

    .. math::

       e(u) = \sum_{v \in N(u) \setminus \{u\}}
       \left(1 - \sum_{w \in N(v)} p_{uw} m_{vw}\right)

    where $N(u)$ is the set of neighbors of $u$ and $p_{uw}$ is the
    normalized mutual weight of the (directed or undirected) edges
    joining $u$ and $v$, for each vertex $u$ and $v$ [1]_. And $m_{vw}$
    is the mutual weight of $v$ and $w$ divided by $v$ highest mutual
    weight with any of its neighbors. The *mutual weight* of $u$ and $v$
    is the sum of the weights of edges joining them (edge weights are
    assumed to be one if the graph is unweighted).

    For the case of unweighted and undirected graphs, Borgatti proposed
    a simplified formula to compute effective size [2]_

    .. math::

       e(u) = n - \frac{2t}{n}

    where `t` is the number of ties in the ego network (not including
    ties to ego) and `n` is the number of nodes (excluding ego).

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``v``. Directed graphs are treated like
        undirected graphs when computing neighbors of ``v``.

    nodes : container, optional
        Container of nodes in the graph ``G`` to compute the effective size.
        If None, the effective size of every node is computed.

    weight : None or string, optional
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.

    Returns
    -------
    dict
        Dictionary with nodes as keys and the effective size of the node as values.

    Notes
    -----
    Isolated nodes, including nodes which only have self-loop edges, do not
    have a well-defined effective size::

        >>> G = nx.path_graph(3)
        >>> G.add_edge(4, 4)
        >>> nx.effective_size(G)
        {0: 1.0, 1: 2.0, 2: 1.0, 4: nan}

    Burt also defined the related concept of *efficiency* of a node's ego
    network, which is its effective size divided by the degree of that
    node [1]_. So you can easily compute efficiency:

    >>> G = nx.DiGraph()
    >>> G.add_edges_from([(0, 1), (0, 2), (1, 0), (2, 1)])
    >>> esize = nx.effective_size(G)
    >>> efficiency = {n: v / G.degree(n) for n, v in esize.items()}

    See also
    --------
    constraint

    References
    ----------
    .. [1] Burt, Ronald S.
           *Structural Holes: The Social Structure of Competition.*
           Cambridge: Harvard University Press, 1995.

    .. [2] Borgatti, S.
           "Structural Holes: Unpacking Burt's Redundancy Measures"
           CONNECTIONS 20(1):35-38.
           http://www.analytictech.com/connections/v20(1)/holes.htm

    """

    def redundancy(G, u, v, weight=None):
        nmw = normalized_mutual_weight
        r = sum(
            nmw(G, u, w, weight=weight) * nmw(G, v, w, norm=max, weight=weight)
            for w in set(nx.all_neighbors(G, u))
        )
        return 1 - r

    # Check if scipy is available
    try:
        # Needed for errstate
        import numpy as np

        # make sure nx.adjacency_matrix will not raise
        import scipy as sp

        has_scipy = True
    except:
        has_scipy = False

    if nodes is None and has_scipy:
        # In order to compute constraint of all nodes,
        # algorithms based on sparse matrices can be much faster

        # Obtain the adjacency matrix
        P = nx.adjacency_matrix(G, weight=weight)

        # Calculate mutual weights
        mutual_weights1 = P + P.T
        mutual_weights2 = mutual_weights1.copy()

        with np.errstate(divide="ignore"):
            # Mutual_weights1 = Normalize mutual weights by row sums
            mutual_weights1 /= mutual_weights1.sum(axis=1)[:, np.newaxis]

            # Mutual_weights2 = Normalize mutual weights by row max
            mutual_weights2 /= mutual_weights2.max(axis=1).toarray()

        # Calculate effective sizes
        r = 1 - (mutual_weights1 @ mutual_weights2.T).toarray()
        effective_size = ((mutual_weights1 > 0) * r).sum(axis=1)

        # Special treatment: isolated nodes (ignoring selfloops) marked with "nan"
        sum_mutual_weights = mutual_weights1.sum(axis=1) - mutual_weights1.diagonal()
        isolated_nodes = sum_mutual_weights == 0
        effective_size[isolated_nodes] = float("nan")
        # Use tolist() to automatically convert numpy scalars -> Python scalars
        return dict(zip(G, effective_size.tolist()))

    # Results for only requested nodes
    effective_size = {}
    if nodes is None:
        nodes = G
    # Use Borgatti's simplified formula for unweighted and undirected graphs
    if not G.is_directed() and weight is None:
        for v in nodes:
            # Effective size is not defined for isolated nodes, including nodes
            # with only self-edges
            if all(u == v for u in G[v]):
                effective_size[v] = float("nan")
                continue
            E = nx.ego_graph(G, v, center=False, undirected=True)
            effective_size[v] = len(E) - (2 * E.size()) / len(E)
    else:
        for v in nodes:
            # Effective size is not defined for isolated nodes, including nodes
            # with only self-edges
            if all(u == v for u in G[v]):
                effective_size[v] = float("nan")
                continue
            effective_size[v] = sum(
                redundancy(G, v, u, weight) for u in set(nx.all_neighbors(G, v))
            )
    return effective_size


@nx._dispatchable(edge_attrs="weight")
def constraint(G, nodes=None, weight=None):
    r"""Returns the constraint on all nodes in the graph ``G``.

    The *constraint* is a measure of the extent to which a node *v* is
    invested in those nodes that are themselves invested in the
    neighbors of *v*. Formally, the *constraint on v*, denoted `c(v)`,
    is defined by

    .. math::

       c(v) = \sum_{w \in N(v) \setminus \{v\}} \ell(v, w)

    where $N(v)$ is the subset of the neighbors of `v` that are either
    predecessors or successors of `v` and $\ell(v, w)$ is the local
    constraint on `v` with respect to `w` [1]_. For the definition of local
    constraint, see :func:`local_constraint`.

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``v``. This can be either directed or undirected.

    nodes : container, optional
        Container of nodes in the graph ``G`` to compute the constraint. If
        None, the constraint of every node is computed.

    weight : None or string, optional
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.

    Returns
    -------
    dict
        Dictionary with nodes as keys and the constraint on the node as values.

    See also
    --------
    local_constraint

    References
    ----------
    .. [1] Burt, Ronald S.
           "Structural holes and good ideas".
           American Journal of Sociology (110): 349–399.

    """

    # Check if scipy is available
    try:
        # Needed for errstate
        import numpy as np

        # make sure nx.adjacency_matrix will not raise
        import scipy as sp

        has_scipy = True
    except:
        has_scipy = False

    if nodes is None and has_scipy:
        # In order to compute constraint of all nodes,
        # algorithms based on sparse matrices can be much faster

        # Obtain the adjacency matrix
        P = nx.adjacency_matrix(G, weight=weight)

        # Calculate mutual weights
        mutual_weights = P + P.T

        # Normalize mutual weights by row sums
        sum_mutual_weights = mutual_weights.sum(axis=1)
        with np.errstate(divide="ignore"):
            mutual_weights /= sum_mutual_weights[:, np.newaxis]

        # Calculate local constraints and constraints
        local_constraints = (mutual_weights + mutual_weights @ mutual_weights) ** 2
        constraints = ((mutual_weights > 0) * local_constraints).sum(axis=1)

        # Special treatment: isolated nodes marked with "nan"
        isolated_nodes = sum_mutual_weights - 2 * mutual_weights.diagonal() == 0
        constraints[isolated_nodes] = float("nan")
        # Use tolist() to automatically convert numpy scalars -> Python scalars
        return dict(zip(G, constraints.tolist()))

    # Result for only requested nodes
    constraint = {}
    if nodes is None:
        nodes = G
    for v in nodes:
        # Constraint is not defined for isolated nodes
        if len(G[v]) == 0:
            constraint[v] = float("nan")
            continue
        constraint[v] = sum(
            local_constraint(G, v, n, weight) for n in set(nx.all_neighbors(G, v))
        )
    return constraint


@nx._dispatchable(edge_attrs="weight")
def local_constraint(G, u, v, weight=None):
    r"""Returns the local constraint on the node ``u`` with respect to
    the node ``v`` in the graph ``G``.

    Formally, the *local constraint on u with respect to v*, denoted
    $\ell(u, v)$, is defined by

    .. math::

       \ell(u, v) = \left(p_{uv} + \sum_{w \in N(v)} p_{uw} p_{wv}\right)^2,

    where $N(v)$ is the set of neighbors of $v$ and $p_{uv}$ is the
    normalized mutual weight of the (directed or undirected) edges
    joining $u$ and $v$, for each vertex $u$ and $v$ [1]_. The *mutual
    weight* of $u$ and $v$ is the sum of the weights of edges joining
    them (edge weights are assumed to be one if the graph is
    unweighted).

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``u`` and ``v``. This can be either
        directed or undirected.

    u : node
        A node in the graph ``G``.

    v : node
        A node in the graph ``G``.

    weight : None or string, optional
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.

    Returns
    -------
    float
        The constraint of the node ``v`` in the graph ``G``.

    See also
    --------
    constraint

    References
    ----------
    .. [1] Burt, Ronald S.
           "Structural holes and good ideas".
           American Journal of Sociology (110): 349–399.

    """
    nmw = normalized_mutual_weight
    direct = nmw(G, u, v, weight=weight)
    indirect = sum(
        nmw(G, u, w, weight=weight) * nmw(G, w, v, weight=weight)
        for w in set(nx.all_neighbors(G, u))
    )
    return (direct + indirect) ** 2


@nx._dispatchable(edge_attrs="weight")
def hierarchy(G, nodes=None, weight=None):
    r"""Returns the hierarchy of nodes in the graph ``G``.

    The *hierarchy* of a node measures the extent to which constraint on
    ego is concentrated in a single contact or a minority of contacts [1]_.
    It uses the Coleman-Theil disorder index to quantify the inequality of
    local constraints across contacts.

    Formally, the hierarchy of a node $u$, denoted $H(u)$, is defined by

    .. math::

       H(u) = \frac{\sum_{v \in N(u) \setminus \{u\}} \left(\frac{c_{uv}}{C(u) / N(u)}\right) \ln\left(\frac{c_{uv}}{C(u) / N(u)}\right)}{N(u) \ln(N(u))}

    where $N(u)$ is the set of neighbors of $u$ (excluding self-loops),
    $c_{uv}$ is the local constraint on $u$ with respect to contact $v$,
    and $C(u) = \sum_{v \in N(u) \setminus \{u\}} c_{uv}$ is the aggregate constraint on $u$ [1]_.
    The ratio $\frac{c_{uv}}{C(u) / N(u)}$ measures how much contact $v$ is a more
    severe source of constraint than the average contact of $u$.

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``nodes``. Directed graphs are treated like
        undirected graphs when computing neighbors of each node.

    nodes : container, optional (default=None)
        Container of nodes in the graph ``G`` to compute the hierarchy.
        If None, the hierarchy of every node is computed.

    weight : None or string, optional (default=None)
        If None, all edge weights are considered equal.
        Otherwise holds the name of the edge attribute used as weight.

    Returns
    -------
    dict
        Dictionary with nodes as keys and hierarchy values as values.

    Notes
    -----
    - Isolated nodes, including nodes which only have self-loop edges, do not
      have a well-defined hierarchy and return ``float("nan")``:

      >>> G = nx.Graph([(0, 1)])
      >>> G.add_node(2)
      >>> nx.hierarchy(G)
      {0: 1.0, 1: 1.0, 2: nan}

    - For nodes with only a single contact ($N(u) = 1$), all constraint is
      concentrated on that contact, and hierarchy equals 1.0.
    - For symmetric structures where constraint is uniformly distributed across
      all contacts (such as complete graphs $K_n$), hierarchy equals 0.0.

    See also
    --------
    constraint
    local_constraint
    effective_size
    structural_efficiency

    References
    ----------
    .. [1] Burt, Ronald S.
           *Structural Holes: The Social Structure of Competition.*
           Cambridge: Harvard University Press, 1995.

    .. [2] Burt, Ronald S.
           "The Network Structure of Social Capital."
           *Research in Organizational Behavior*, 2000.
           http://faculty.chicagobooth.edu/ronald.burt/research/files/NSSC.pdf
    """
    try:
        import numpy as np
        import scipy.sparse as sp

        has_scipy = True
    except:
        has_scipy = False

    if nodes is None and has_scipy:
        P = nx.adjacency_matrix(G, weight=weight)
        mutual_weights = P + P.T

        # Exclude diagonal (self-loops) for degree and contact counting
        mw_no_diag = mutual_weights.copy().tolil()
        mw_no_diag.setdiag(0)
        mw_no_diag = mw_no_diag.tocsr()

        degrees = np.diff(mw_no_diag.indptr)

        sum_mutual_weights = np.asarray(mutual_weights.sum(axis=1)).flatten()
        with np.errstate(divide="ignore"):
            normalized_mw = mutual_weights.astype(float)
            inv_sum = np.where(sum_mutual_weights == 0, 0.0, 1.0 / sum_mutual_weights)
            normalized_mw = normalized_mw.multiply(inv_sum[:, np.newaxis])

        # local_constraints: (P + P^2)^2
        P_sq = normalized_mw @ normalized_mw
        P_sum = normalized_mw + P_sq
        local_constraints = P_sum.multiply(P_sum)

        # Only keep constraints on actual contacts (excluding self)
        mask = mw_no_diag > 0
        contact_constraints = mask.multiply(local_constraints).tocsr()

        # Aggregate constraint per node
        agg_constraint = np.asarray(contact_constraints.sum(axis=1)).flatten()

        h = np.zeros(len(G), dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            valid_mask = (degrees > 1) & (agg_constraint > 0)

            scale_factor = np.zeros(len(G), dtype=float)
            scale_factor[valid_mask] = degrees[valid_mask] / agg_constraint[valid_mask]

            ratio_mat = contact_constraints.multiply(scale_factor[:, np.newaxis]).tocsr()
            ratio_data = ratio_mat.data
            pos_mask = ratio_data > 0
            term_data = np.zeros_like(ratio_data)
            term_data[pos_mask] = ratio_data[pos_mask] * np.log(ratio_data[pos_mask])

            term_mat = sp.csr_array(
                (term_data, ratio_mat.indices, ratio_mat.indptr), shape=ratio_mat.shape
            )
            numerator = np.asarray(term_mat.sum(axis=1)).flatten()

            denom = degrees * np.log(degrees)
            h[valid_mask] = numerator[valid_mask] / denom[valid_mask]
            h = np.clip(h, 0.0, 1.0)

            h[degrees == 0] = float("nan")
            h[degrees == 1] = 1.0
            h[(degrees > 1) & (agg_constraint == 0)] = 0.0

        return dict(zip(G, h.tolist()))

    # Iterative fallback for subset of nodes or environments without SciPy
    hierarchy_vals = {}
    if nodes is None:
        nodes = G
    for v in nodes:
        neighbors = set(nx.all_neighbors(G, v)) - {v}
        N = len(neighbors)
        if N == 0:
            hierarchy_vals[v] = float("nan")
            continue
        if N == 1:
            hierarchy_vals[v] = 1.0
            continue
        c = {w: local_constraint(G, v, w, weight=weight) for w in neighbors}
        C = sum(c.values())
        if C == 0:
            hierarchy_vals[v] = 0.0
            continue
        mean_c = C / N
        numerator = 0.0
        for w in neighbors:
            if c[w] > 0:
                ratio = c[w] / mean_c
                numerator += ratio * math.log(ratio)
        denom = N * math.log(N)
        val = numerator / denom
        hierarchy_vals[v] = max(0.0, min(1.0, float(val)))
    return hierarchy_vals


@nx._dispatchable(edge_attrs="weight")
def structural_efficiency(G, nodes=None, weight=None):
    r"""Returns the structural efficiency of all nodes in the graph ``G``.

    The *structural efficiency* of a node's ego network measures the
    nonredundant proportion of its contacts, defined by Ronald Burt as its
    effective size divided by its degree [1]_.

    Formally, the structural efficiency of a node $u$, denoted $\eta(u)$, is
    defined by

    .. math::

       \eta(u) = \frac{e(u)}{N(u)}

    where $e(u)$ is the effective size of node $u$, and $N(u)$ is the number
    of contacts (degree excluding self-loops) of $u$ [1]_.

    Parameters
    ----------
    G : NetworkX graph
        The graph containing ``nodes``. Directed graphs are treated like
        undirected graphs when computing neighbors of each node.

    nodes : container, optional (default=None)
        Container of nodes in the graph ``G`` to compute efficiency.
        If None, the structural efficiency of every node is computed.

    weight : None or string, optional (default=None)
        If None, all edge weights are considered equal.
        Otherwise holds the name of the edge attribute used as weight.

    Returns
    -------
    dict
        Dictionary with nodes as keys and structural efficiency as values.

    Notes
    -----
    Isolated nodes, including nodes which only have self-loop edges, do not
    have a well-defined efficiency and return ``float("nan")``:

    >>> G = nx.path_graph(3)
    >>> G.add_node(3)
    >>> nx.structural_efficiency(G)
    {0: 1.0, 1: 1.0, 2: 1.0, 3: nan}

    See also
    --------
    effective_size
    constraint
    hierarchy

    References
    ----------
    .. [1] Burt, Ronald S.
           *Structural Holes: The Social Structure of Competition.*
           Cambridge: Harvard University Press, 1995.
    """
    try:
        import numpy as np

        has_scipy = True
    except:
        has_scipy = False

    if nodes is None and has_scipy:
        esize_dict = effective_size(G, weight=weight)
        P = nx.adjacency_matrix(G, weight=weight)
        mutual_weights = P + P.T
        mw_no_diag = mutual_weights.copy().tolil()
        mw_no_diag.setdiag(0)
        degrees = np.diff(mw_no_diag.tocsr().indptr)

        esizes = np.array([esize_dict[n] for n in G], dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            eff = np.where(degrees == 0, float("nan"), esizes / degrees)
        return dict(zip(G, eff.tolist()))

    # Iterative fallback
    esize = effective_size(G, nodes=nodes, weight=weight)
    if nodes is None:
        nodes = G
    eff = {}
    for v in nodes:
        neighbors = set(nx.all_neighbors(G, v)) - {v}
        N = len(neighbors)
        if N == 0 or math.isnan(esize[v]):
            eff[v] = float("nan")
        else:
            eff[v] = esize[v] / N
    return eff


# Alias inside structuralholes module
efficiency = structural_efficiency
