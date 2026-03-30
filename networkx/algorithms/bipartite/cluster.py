"""Functions for computing clustering of pairs"""

import itertools

import networkx as nx

__all__ = [
    "clustering",
    "average_clustering",
    "latapy_clustering",
    "robins_alexander_clustering",
    "butterflies",
]


def cc_dot(nu, nv):
    return len(nu & nv) / len(nu | nv)


def cc_max(nu, nv):
    return len(nu & nv) / max(len(nu), len(nv))


def cc_min(nu, nv):
    return len(nu & nv) / min(len(nu), len(nv))


modes = {"dot": cc_dot, "min": cc_min, "max": cc_max}


@nx._dispatchable
def latapy_clustering(G, nodes=None, mode="dot"):
    r"""Compute a bipartite clustering coefficient for nodes.

    The bipartite clustering coefficient is a measure of local density
    of connections defined as [1]_:

    .. math::

       c_u = \frac{\sum_{v \in N(N(u))} c_{uv} }{|N(N(u))|}

    where `N(N(u))` are the second order neighbors of `u` in `G` excluding `u`,
    and `c_{uv}` is the pairwise clustering coefficient between nodes
    `u` and `v`.

    The mode selects the function for `c_{uv}` which can be:

    `dot`:

    .. math::

       c_{uv}=\frac{|N(u)\cap N(v)|}{|N(u) \cup N(v)|}

    `min`:

    .. math::

       c_{uv}=\frac{|N(u)\cap N(v)|}{min(|N(u)|,|N(v)|)}

    `max`:

    .. math::

       c_{uv}=\frac{|N(u)\cap N(v)|}{max(|N(u)|,|N(v)|)}


    Parameters
    ----------
    G : graph
        A bipartite graph

    nodes : list or iterable (optional)
        Compute bipartite clustering for these nodes. The default
        is all nodes in G.

    mode : string
        The pairwise bipartite clustering method to be used in the computation.
        It must be "dot", "max", or "min".

    Returns
    -------
    clustering : dictionary
        A dictionary keyed by node with the clustering coefficient value.


    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)  # path graphs are bipartite
    >>> c = bipartite.clustering(G)
    >>> c[0]
    0.5
    >>> c = bipartite.clustering(G, mode="min")
    >>> c[0]
    1.0

    See Also
    --------
    robins_alexander_clustering
    average_clustering
    networkx.algorithms.cluster.square_clustering

    References
    ----------
    .. [1] Latapy, Matthieu, Clémence Magnien, and Nathalie Del Vecchio (2008).
       Basic notions for the analysis of large two-mode networks.
       Social Networks 30(1), 31--48.
    """
    if not nx.algorithms.bipartite.is_bipartite(G):
        raise nx.NetworkXError("Graph is not bipartite")

    try:
        cc_func = modes[mode]
    except KeyError as err:
        raise nx.NetworkXError(
            "Mode for bipartite clustering must be: dot, min or max"
        ) from err

    if nodes is None:
        nodes = G
    ccs = {}
    for v in nodes:
        cc = 0.0
        nbrs2 = {u for nbr in G[v] for u in G[nbr]} - {v}
        for u in nbrs2:
            cc += cc_func(set(G[u]), set(G[v]))
        if cc > 0.0:  # len(nbrs2)>0
            cc /= len(nbrs2)
        ccs[v] = cc
    return ccs


clustering = latapy_clustering


@nx._dispatchable(name="bipartite_average_clustering")
def average_clustering(G, nodes=None, mode="dot"):
    r"""Compute the average bipartite clustering coefficient.

    A clustering coefficient for the whole graph is the average,

    .. math::

       C = \frac{1}{n}\sum_{v \in G} c_v,

    where `n` is the number of nodes in `G`.

    Similar measures for the two bipartite sets can be defined [1]_

    .. math::

       C_X = \frac{1}{|X|}\sum_{v \in X} c_v,

    where `X` is a bipartite set of `G`.

    Parameters
    ----------
    G : graph
        a bipartite graph

    nodes : list or iterable, optional
        A container of nodes to use in computing the average.
        The nodes should be either the entire graph (the default) or one of the
        bipartite sets.

    mode : string
        The pairwise bipartite clustering method.
        It must be "dot", "max", or "min"

    Returns
    -------
    clustering : float
       The average bipartite clustering for the given set of nodes or the
       entire graph if no nodes are specified.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.star_graph(3)  # star graphs are bipartite
    >>> bipartite.average_clustering(G)
    0.75
    >>> X, Y = bipartite.sets(G)
    >>> bipartite.average_clustering(G, X)
    0.0
    >>> bipartite.average_clustering(G, Y)
    1.0

    See Also
    --------
    clustering

    Notes
    -----
    The container of nodes passed to this function must contain all of the nodes
    in one of the bipartite sets ("top" or "bottom") in order to compute
    the correct average bipartite clustering coefficients.
    See :mod:`bipartite documentation <networkx.algorithms.bipartite>`
    for further details on how bipartite graphs are handled in NetworkX.


    References
    ----------
    .. [1] Latapy, Matthieu, Clémence Magnien, and Nathalie Del Vecchio (2008).
        Basic notions for the analysis of large two-mode networks.
        Social Networks 30(1), 31--48.
    """
    if nodes is None:
        nodes = G
    ccs = latapy_clustering(G, nodes=nodes, mode=mode)
    return sum(ccs[v] for v in nodes) / len(nodes)


@nx._dispatchable
def robins_alexander_clustering(G):
    r"""Compute the bipartite clustering of G.

    Robins and Alexander [1]_ defined bipartite clustering coefficient as
    four times the number of four cycles `C_4` divided by the number of
    three paths `L_3` in a bipartite graph:

    .. math::

       CC_4 = \frac{4 * C_4}{L_3}

    Parameters
    ----------
    G : graph
        a bipartite graph

    Returns
    -------
    clustering : float
       The Robins and Alexander bipartite clustering for the input graph.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.davis_southern_women_graph()
    >>> print(round(bipartite.robins_alexander_clustering(G), 3))
    0.468

    See Also
    --------
    latapy_clustering
    networkx.algorithms.cluster.square_clustering

    References
    ----------
    .. [1] Robins, G. and M. Alexander (2004). Small worlds among interlocking
           directors: Network structure and distance in bipartite graphs.
           Computational & Mathematical Organization Theory 10(1), 69–94.

    """
    if G.order() < 4 or G.size() < 3:
        return 0
    L_3 = _threepaths(G)
    if L_3 == 0:
        return 0
    C_4 = _four_cycles(G)
    return (4.0 * C_4) / L_3




@nx._dispatchable
def butterflies(G, nodes=None):
    r"""Count the number of butterflies for each node in a bipartite graph.

    A *butterfly* is a complete bipartite subgraph on four nodes — two from
    each partition — with all four possible edges present.  It is the
    bipartite analogue of a triangle in unipartite graphs.

    .. math::

        \text{Left} \quad \text{Right}  \\
        u_1 - v_1                       \\
        |  \quad \quad  |               \\
        u_2 - v_2

    where :math:`u_1, u_2` are in one partition and :math:`v_1, v_2` in the
    other, and all four edges :math:`(u_1,v_1), (u_1,v_2), (u_2,v_1),
    (u_2,v_2)` are present.

    Parameters
    ----------
    G : NetworkX graph
        An undirected bipartite graph.
    nodes : container of nodes, optional
        Compute butterflies only for the specified nodes. The default
        (``None``) computes for all nodes in *G*.

    Returns
    -------
    butterflies : dict
        A dictionary keyed by node to the number of butterflies that node
        participates in.  Each butterfly is counted once per node it contains,
        so the sum of all values equals ``4 * total_butterfly_count``.

    Raises
    ------
    NetworkXError
        If *G* is not bipartite.

    Examples
    --------
    A single :math:`K_{2,2}` contains exactly one butterfly, and each of its
    four nodes participates in that butterfly:

    >>> from networkx.algorithms import bipartite
    >>> G = nx.Graph()
    >>> G.add_nodes_from([1, 2], bipartite=0)
    >>> G.add_nodes_from([3, 4], bipartite=1)
    >>> G.add_edges_from([(1, 3), (1, 4), (2, 3), (2, 4)])
    >>> bipartite.butterflies(G)
    {1: 1, 2: 1, 3: 1, 4: 1}

    The total number of butterflies in *G* is the sum of per-node counts
    divided by 4 (each butterfly has four nodes):

    >>> bt = bipartite.butterflies(G)
    >>> sum(bt.values()) // 4
    1

    :math:`K_{3,3}` contains nine butterflies; every node participates in
    six of them:

    >>> G2 = nx.complete_bipartite_graph(3, 3)
    >>> bt2 = bipartite.butterflies(G2)
    >>> sum(bt2.values()) // 4
    9

    For nodes not in any butterfly the count is zero:

    >>> G3 = nx.Graph()
    >>> G3.add_nodes_from([0, 1], bipartite=0)
    >>> G3.add_nodes_from([2, 3], bipartite=1)
    >>> G3.add_edges_from([(0, 2), (0, 3)])   # node 1 has no edges
    >>> bipartite.butterflies(G3)[1]
    0

    Notes
    -----
    The algorithm uses wedge-based counting [1]_:

    1. Rank nodes by ascending degree.  Processing low-degree nodes first
       keeps the wedge map compact and mirrors the PARBUTTERFLY strategy [2]_.
    2. For each *pivot* node ``v`` in the chosen partition, enumerate all
       pairs of neighbours ``(u1, u2)`` in the opposite partition — each pair
       is a *wedge* centred at ``v``.
    3. Count how many times each ``(u1, u2)`` pair appears.  If pair
       ``(u1, u2)`` appears ``k`` times, it contributes
       :math:`\binom{k}{2} = k(k-1)/2` butterflies to the total, and each
       of the ``k`` pivot nodes contributes ``k - 1`` butterflies.

    When ``nodes`` is ``None`` the pivot partition is chosen automatically
    as the smaller bipartite set.

    **Time complexity:** :math:`O\!\left(\sum_v d(v)^2\right)` where the
    sum is over nodes in the pivot partition.
    **Space complexity:** :math:`O(E)` for the wedge map.

    The function is equivalent to, but more efficient than, calling
    :func:`~networkx.algorithms.bipartite.cluster.robins_alexander_clustering`
    and recovering per-node counts.

    See Also
    --------
    robins_alexander_clustering : uses :math:`4 \times` butterfly count
        as the numerator of the bipartite clustering coefficient.
    latapy_clustering

    References
    ----------
    .. [1] Sanei-Mehri, S. V., Sariyuce, A. E., & Tirthapura, S. (2018).
       Butterfly counting in bipartite networks.
       *Proceedings of the 24th ACM SIGKDD*, 2150–2159.
       https://doi.org/10.1145/3219819.3220097

    .. [2] Shi, B., Dhulipala, L., & Shun, J. (2020).
       Parallel algorithms for butterfly computations.
       *SIAM Symposium on Algorithmic Principles of Computer Systems*, 16–30.
    """
    if not nx.is_bipartite(G):
        raise nx.NetworkXError("Graph is not bipartite")

    # ------------------------------------------------------------------ #
    # Determine pivot partition
    # ------------------------------------------------------------------ #
    if nodes is None:
        # Use bipartite node attribute when present; fall back to BFS
        attr = nx.get_node_attributes(G, "bipartite")
        if attr:
            left  = {n for n, v in attr.items() if v == 0}
            right = {n for n, v in attr.items() if v == 1}
            pivot = left if len(left) <= len(right) else right
        else:
            # BFS 2-colouring — handles disconnected graphs without
            # raising AmbiguousSolution (unlike nx.bipartite.sets)
            color = {}
            for start in G.nodes():
                if start in color:
                    continue
                color[start] = 0
                queue = [start]
                while queue:
                    v = queue.pop()
                    for nbr in G.neighbors(v):
                        if nbr not in color:
                            color[nbr] = 1 - color[v]
                            queue.append(nbr)
            left  = {n for n, c in color.items() if c == 0}
            right = {n for n, c in color.items() if c == 1}
            pivot = left if len(left) <= len(right) else right
    else:
        pivot = set(nodes)

    # ------------------------------------------------------------------ #
    # Wedge enumeration with degree ranking
    # ------------------------------------------------------------------ #
    # Sort pivot nodes by ascending degree so that high-degree nodes are
    # processed last — this keeps wedge-map entries concentrated and
    # matches the PARBUTTERFLY vertex-ranking strategy.
    ranked = sorted(pivot, key=lambda v: (G.degree(v), v))

    # wedge_counts[(u1, u2)] = number of pivot nodes connected to both
    wedge_counts = {}
    # wedge_pivots[(u1, u2)] = list of pivot nodes that produced this wedge
    wedge_pivots = {}

    for v in ranked:
        nbrs = list(G.neighbors(v))
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                u1, u2 = nbrs[i], nbrs[j]
                # Canonical key — smaller id first
                key = (u1, u2) if u1 < u2 else (u2, u1)
                if key in wedge_counts:
                    wedge_counts[key] += 1
                    wedge_pivots[key].append(v)
                else:
                    wedge_counts[key] = 1
                    wedge_pivots[key] = [v]

    # ------------------------------------------------------------------ #
    # Accumulate per-node butterfly counts
    # ------------------------------------------------------------------ #
    # Accumulate over all nodes first, then filter
    _bt = dict.fromkeys(G.nodes(), 0)

    for (u1, u2), k in wedge_counts.items():
        if k < 2:
            continue
        bf = k * (k - 1) // 2          # C(k, 2) butterflies for this pair
        _bt[u1] += bf
        _bt[u2] += bf
        for v in wedge_pivots[(u1, u2)]:
            _bt[v] += k - 1             # each pivot pairs with k-1 others

    # Match nx.triangles convention: return only requested nodes
    if nodes is None:
        return _bt
    return {v: _bt[v] for v in nodes}

def _four_cycles(G):
    # Also see `square_clustering` which counts squares in a similar way
    cycles = 0
    seen = set()
    G_adj = G._adj
    for v in G:
        seen.add(v)
        v_neighbors = set(G_adj[v])
        if len(v_neighbors) < 2:
            # Can't form a square without at least two neighbors
            continue
        two_hop_neighbors = set().union(*(G_adj[u] for u in v_neighbors))
        two_hop_neighbors -= seen
        for x in two_hop_neighbors:
            p2 = len(v_neighbors.intersection(G_adj[x]))
            cycles += p2 * (p2 - 1)
    return cycles / 4


def _threepaths(G):
    paths = 0
    for v in G:
        for u in G[v]:
            for w in set(G[u]) - {v}:
                paths += len(set(G[w]) - {v, u})
    # Divide by two because we count each three path twice
    # one for each possible starting point
    return paths / 2
