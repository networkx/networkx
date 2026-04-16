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

    The four cycles counted here are *butterflies* — complete bipartite
    subgraphs K_{2,2} where alternating nodes belong to different
    partitions.  See :func:`butterflies` for per-node butterfly counts.

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
    butterflies : per-node butterfly (four-cycle) counts
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

    return sum(butterflies(G).values()) / L_3


@nx._dispatchable
def butterflies(G, nodes=None):
    r"""Count the number of butterflies for each node in a bipartite graph.

    A *butterfly* is a complete bipartite subgraph K_{2,2} — four nodes
    (two from each partition) with all four cross-edges present.  It is
    the bipartite analogue of a triangle in unipartite graphs.

    .. code-block:: none

        A1   A2
        | \ / |
        |  X  |
        | / \ |
        B1   B2

    Equivalently, a butterfly is a 4-cycle (C_4) in which alternating
    nodes belong to different partitions of the bipartite graph.
    This structure is also called a *square* in the physics and
    complex-networks literature [3]_, and a *four-cycle* in the
    sociology literature [4]_.  The name *butterfly* is standard in
    the data-mining and bipartite-network literature [1]_ [2]_.

    Parameters
    ----------
    G : NetworkX graph
        An undirected bipartite graph.
    nodes : container of nodes, optional
        Return butterfly counts only for these nodes.  The computation
        always uses the full graph; ``nodes`` only filters the returned
        dictionary (same convention as :func:`~networkx.triangles`).
        When ``None`` (default), counts for all nodes are returned.
        Nodes not present in `G` are silently ignored.

    Returns
    -------
    butterflies : dict
        A dictionary keyed by node to the number of butterflies that
        node participates in.  Each butterfly is counted once per
        participating node, so::

            sum(butterflies(G).values()) == 4 * total_butterfly_count

    Raises
    ------
    NetworkXError
        If *G* is not bipartite.

    Examples
    --------
    A single K_{2,2} contains exactly one butterfly, and each of its
    four nodes participates in that butterfly:

    >>> from networkx.algorithms import bipartite
    >>> G = nx.Graph()
    >>> G.add_nodes_from([1, 2], bipartite=0)
    >>> G.add_nodes_from([3, 4], bipartite=1)
    >>> G.add_edges_from([(1, 3), (1, 4), (2, 3), (2, 4)])
    >>> bipartite.butterflies(G)
    {1: 1, 2: 1, 3: 1, 4: 1}

    The total number of butterflies is the sum divided by 4:

    >>> bt = bipartite.butterflies(G)
    >>> sum(bt.values()) // 4
    1

    K_{3,3} contains nine butterflies; every node participates in six:

    >>> G2 = nx.complete_bipartite_graph(3, 3)
    >>> bt2 = bipartite.butterflies(G2)
    >>> sum(bt2.values()) // 4
    9

    Nodes not in any butterfly receive count zero:

    >>> G3 = nx.Graph()
    >>> G3.add_nodes_from([0, 1], bipartite=0)
    >>> G3.add_nodes_from([2, 3], bipartite=1)
    >>> G3.add_edges_from([(0, 2), (0, 3)])  # node 1 has no edges
    >>> bipartite.butterflies(G3)[1]
    0

    Notes
    -----
    The wedge enumeration follows the vertex-priority approach of BFC-VP
    (Wang et al. [2]_): nodes are ranked by degree, neighbor lists are
    pre-sorted by ascending rank, and for each start node ``u`` only
    neighbors with lower rank are processed as middle and end nodes,
    with early termination on the sorted lists.  This gives time
    complexity :math:`O\!\bigl(\sum_{(u,v)\in E} \min(d(u), d(v))\bigr)
    = O(\alpha m)` where :math:`\alpha` is the arboricity and :math:`m`
    the number of edges.

    The per-node attribution (distributing butterfly credits to start,
    middle, and end nodes) is an extension of BFC-VP not present in the
    original paper, which computes only a global count.

    See Also
    --------
    robins_alexander_clustering : graph-level bipartite clustering
        coefficient whose numerator is ``4 * total butterfly count``.
    networkx.algorithms.cluster.square_clustering : per-node square
        clustering coefficient for general graphs.

    References
    ----------
    .. [1] Sanei-Mehri, S. V., Sariyuce, A. E., & Tirthapura, S.
       (2018).  Butterfly counting in bipartite networks.
       *Proceedings of the 24th ACM SIGKDD*, 2150–2159.
       https://doi.org/10.1145/3219819.3220097

    .. [2] Wang, K., Lin, X., Qin, L., Zhang, W., & Zhang, Y. (2023).
       Accelerated butterfly counting with vertex priority on bipartite
       graphs.  *The VLDB Journal*, 32, 257–281.
       https://doi.org/10.1007/s00778-022-00746-0

    .. [3] Lind, P. G., Gonzalez, M. C., & Herrmann, H. J. (2005).
       Cycles and clustering in bipartite networks.
       *Physical Review E*, 72, 056127.

    .. [4] Robins, G. and M. Alexander (2004). Small worlds among
       interlocking directors: Network structure and distance in
       bipartite graphs.  *Computational & Mathematical Organization
       Theory* 10(1), 69–94.
    """
    if not nx.is_bipartite(G):
        raise nx.NetworkXError("Graph is not bipartite")

    if G.number_of_edges() == 0:
        result = dict.fromkeys(G.nodes(), 0)
        return (
            {v: result[v] for v in G.nbunch_iter(nodes)}
            if nodes is not None
            else result
        )

    node_rank = {n: i for i, n in enumerate(G.nodes())}
    priority = {n: (G.degree(n), node_rank[n]) for n in G.nodes()}

    sorted_nbrs = {
        v: sorted(G.neighbors(v), key=lambda x: priority[x]) for v in G.nodes()
    }

    _bt = dict.fromkeys(G.nodes(), 0)

    for u in G.nodes():
        pu = priority[u]
        wedge_count = {}
        wedge_mid = {}

        for v in sorted_nbrs[u]:
            if priority[v] >= pu:
                break
            for w in sorted_nbrs[v]:
                if priority[w] >= pu:
                    break
                if w in wedge_count:
                    wedge_count[w] += 1
                    wedge_mid[w].append(v)
                else:
                    wedge_count[w] = 1
                    wedge_mid[w] = [v]

        for w, k in wedge_count.items():
            if k < 2:
                continue
            bf = k * (k - 1) // 2  # C(k, 2) butterflies for pair (u, w)
            _bt[u] += bf
            _bt[w] += bf
            for v in wedge_mid[w]:
                _bt[v] += k - 1  # each middle node pairs with k-1 others

    if nodes is None:
        return _bt
    return {v: _bt[v] for v in G.nbunch_iter(nodes)}


def _threepaths(G):
    paths = 0
    for v in G:
        for u in G[v]:
            for w in set(G[u]) - {v}:
                paths += len(set(G[w]) - {v, u})
    # Divide by two because we count each three path twice
    # one for each possible starting point
    return paths / 2
