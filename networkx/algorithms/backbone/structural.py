"""
Structural backbone extraction methods.

These methods use the network's topology (edge weights, shortest paths,
spanning trees, degree, neighborhood overlap) to identify the most
important substructure.

Methods
-------
global_threshold_filter
    Simple weight cutoff.
strongest_n_ties
    Per-node strongest edges.
high_salience_skeleton
    Grady et al. (2012) — shortest-path tree participation.
metric_backbone
    Simas et al. (2021) — edges on shortest paths (sum distances).
ultrametric_backbone
    Shortest paths using max distance.
doubly_stochastic_filter
    Slater (2009) — Sinkhorn-Knopp normalization.
h_backbone
    Zhang et al. (2018) — h-index inspired.
modularity_backbone
    Rajeh et al. (2022) — node vitality index.
planar_maximally_filtered_graph
    Tumminello et al. (2005) — planar constraint.
maximum_spanning_tree_backbone
    Maximum spanning tree.
neighborhood_overlap
    Raw count of shared neighbors for each edge.
jaccard_backbone
    Jaccard (1901) — neighborhood overlap / union.
dice_backbone
    Dice (1945) — twice overlap / sum of degrees.
cosine_backbone
    Cosine similarity — overlap / geometric mean of degrees.
"""

import heapq
import math
import networkx as nx
import numpy as np

__all__ = [
    "global_threshold_filter",
    "strongest_n_ties",
    "high_salience_skeleton",
    "metric_backbone",
    "ultrametric_backbone",
    "doubly_stochastic_filter",
    "h_backbone",
    "modularity_backbone",
    "planar_maximally_filtered_graph",
    "maximum_spanning_tree_backbone",
]


# =====================================================================
# 1. Global threshold filter
# =====================================================================

def global_threshold_filter(G, threshold, weight="weight"):
    """Return a subgraph containing only edges with weight >= threshold.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
    threshold : float
    weight : str

    Returns
    -------
    H : same type as G
        Subgraph.  All original nodes are preserved.
    """
    H = G.__class__()
    H.add_nodes_from(G.nodes(data=True))
    for u, v, data in G.edges(data=True):
        if data.get(weight, 0) >= threshold:
            H.add_edge(u, v, **data)
    return H


# =====================================================================
# 2. Per-node strongest-N ties
# =====================================================================

def strongest_n_ties(G, n=1, weight="weight"):
    """Retain the *n* strongest edges for every node (OR semantics).

    For directed graphs the selection is based on out-edges.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
    n : int  (>= 1)
    weight : str

    Returns
    -------
    H : same type as G
    """
    if n < 1:
        raise ValueError("n must be >= 1")

    kept_edges = set()
    if G.is_directed():
        for u in G.nodes():
            out = [(data.get(weight, 0), v) for v, data in G[u].items()]
            for _, v in heapq.nlargest(n, out):
                kept_edges.add((u, v))
    else:
        for u in G.nodes():
            nbrs = [(G[u][v].get(weight, 0), v) for v in G[u]]
            for _, v in heapq.nlargest(n, nbrs):
                kept_edges.add((u, v) if u <= v else (v, u))

    H = G.__class__()
    H.add_nodes_from(G.nodes(data=True))
    for u, v in kept_edges:
        H.add_edge(u, v, **G[u][v])
    return H


# =====================================================================
# 3. High salience skeleton — Grady et al. (2012)
# =====================================================================

def high_salience_skeleton(G, weight="weight"):
    """Compute edge salience: fraction of shortest-path trees containing each edge.

    Parameters
    ----------
    G : nx.Graph
        Undirected weighted graph.  All weights must be positive.
    weight : str

    Returns
    -------
    H : nx.Graph
        Copy with ``"salience"`` edge attribute in [0, 1].

    References
    ----------
    .. [1] Grady, D., Thiemann, C., & Brockmann, D. (2012). Robust
       classification of salient links in complex networks. *Nature
       Communications*, 3, 864.
    """
    if G.is_directed():
        raise nx.NetworkXError(
            "high_salience_skeleton is defined for undirected graphs only."
        )

    H = G.copy()
    n = G.number_of_nodes()
    salience_count = {(min(u, v), max(u, v)): 0 for u, v in G.edges()}

    dist_attr = "__hss_dist__"
    for u, v, data in H.edges(data=True):
        data[dist_attr] = 1.0 / data[weight]

    for root in G.nodes():
        pred = nx.dijkstra_predecessor_and_distance(H, root, weight=dist_attr)[0]
        for node, preds in pred.items():
            for p in preds:
                key = (min(node, p), max(node, p))
                if key in salience_count:
                    salience_count[key] += 1

    for u, v, data in H.edges(data=True):
        key = (min(u, v), max(u, v))
        data["salience"] = salience_count[key] / n
        data.pop(dist_attr, None)

    return H


# =====================================================================
# 4/5. Metric & ultrametric backbones — Simas et al. (2021)
# =====================================================================

def metric_backbone(G, weight="weight"):
    """Extract the metric backbone (sum-of-distances shortest paths).

    An edge (u, v) is in the backbone iff its direct distance equals the
    shortest-path distance between u and v.

    References
    ----------
    .. [1] Simas, T., Correia, R. B., & Rocha, L. M. (2021). The distance
       backbone of complex networks. *J. Complex Netw.*, 9, cnab021.
    """
    return _distance_backbone(G, weight=weight, ultrametric=False)


def ultrametric_backbone(G, weight="weight"):
    """Extract the ultrametric backbone (max-distance / minimax paths)."""
    return _distance_backbone(G, weight=weight, ultrametric=True)


def _distance_backbone(G, weight="weight", ultrametric=False):
    if G.is_directed():
        raise nx.NetworkXError("Distance backbones require an undirected graph.")

    H = G.__class__()
    H.add_nodes_from(G.nodes(data=True))

    dist_G = nx.Graph()
    for u, v, data in G.edges(data=True):
        dist_G.add_edge(u, v, dist=1.0 / data[weight])

    if ultrametric:
        mst = nx.minimum_spanning_tree(dist_G, weight="dist")
        for u, v, data in G.edges(data=True):
            direct_dist = 1.0 / data[weight]
            path = nx.shortest_path(mst, u, v, weight=None)
            max_edge = max(
                dist_G[path[i]][path[i + 1]]["dist"] for i in range(len(path) - 1)
            )
            if abs(direct_dist - max_edge) < 1e-12 or direct_dist <= max_edge:
                H.add_edge(u, v, **data)
    else:
        sp = dict(nx.all_pairs_dijkstra_path_length(dist_G, weight="dist"))
        for u, v, data in G.edges(data=True):
            direct_dist = 1.0 / data[weight]
            if abs(direct_dist - sp[u][v]) < 1e-12:
                H.add_edge(u, v, **data)

    return H


# =====================================================================
# 6. Doubly stochastic filter — Slater (2009)
# =====================================================================

def doubly_stochastic_filter(G, weight="weight", max_iter=1000, tol=1e-8):
    """Compute doubly-stochastic backbone.

    Transforms the adjacency matrix into a doubly stochastic matrix via
    iterative Sinkhorn-Knopp normalization, then stores the normalised
    weight as an edge attribute.

    Parameters
    ----------
    G : nx.Graph
        Undirected weighted graph.
    weight : str
    max_iter : int
        Max Sinkhorn-Knopp iterations.
    tol : float
        Convergence tolerance.

    Returns
    -------
    H : nx.Graph
        Copy with ``"ds_weight"`` edge attribute (doubly-stochastic
        normalised weight).

    References
    ----------
    .. [1] Slater, P. B. (2009). A two-stage algorithm for extracting
       the multiscale backbone of complex weighted networks. *PNAS*,
       106(26), E66.
    """
    if G.is_directed():
        raise nx.NetworkXError(
            "doubly_stochastic_filter is defined for undirected graphs only."
        )

    nodes = sorted(G.nodes())
    n = len(nodes)
    if n == 0:
        return G.copy()

    idx = {v: i for i, v in enumerate(nodes)}

    # Build adjacency matrix
    A = np.zeros((n, n), dtype=float)
    for u, v, data in G.edges(data=True):
        w = data.get(weight, 0)
        A[idx[u], idx[v]] = w
        A[idx[v], idx[u]] = w

    # Sinkhorn-Knopp iteration
    D = A.copy()
    for _ in range(max_iter):
        # Row normalise
        row_sums = D.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        D = D / row_sums
        # Column normalise
        col_sums = D.sum(axis=0, keepdims=True)
        col_sums[col_sums == 0] = 1.0
        D = D / col_sums
        # Check convergence
        rs = D.sum(axis=1)
        cs = D.sum(axis=0)
        if np.allclose(rs, 1, atol=tol) and np.allclose(cs, 1, atol=tol):
            break

    H = G.copy()
    for u, v, data in H.edges(data=True):
        data["ds_weight"] = D[idx[u], idx[v]]

    return H


# =====================================================================
# 7. h-backbone — Zhang et al. (2018)
# =====================================================================

def h_backbone(G, weight="weight"):
    """Extract the h-backbone.

    The h-backbone [1]_ is composed of two parts:

    1. **h-strength network**: find h such that there are at least h edges
       with weight >= h.  Keep those edges.
    2. **h-bridge network**: among the remaining edges, keep those whose
       edge betweenness centrality is in the top-h.

    The union of both subsets forms the h-backbone.

    Parameters
    ----------
    G : nx.Graph
        Undirected weighted graph.
    weight : str

    Returns
    -------
    H : nx.Graph
        The h-backbone subgraph.

    References
    ----------
    .. [1] Zhang, R. J., Stanley, H. E., & Ye, F. Y. (2018). Extracting
       h-backbone as a core structure in weighted networks. *Scientific
       Reports*, 8, 14356.
    """
    if G.is_directed():
        raise nx.NetworkXError("h_backbone is defined for undirected graphs only.")

    # Compute h-index of the weight sequence
    weights = sorted(
        [data[weight] for _, _, data in G.edges(data=True)], reverse=True
    )
    h = 0
    for i, w in enumerate(weights):
        if w >= i + 1:
            h = i + 1
        else:
            break

    # h-strength network: edges with weight >= h
    h_strength_edges = set()
    for u, v, data in G.edges(data=True):
        if data[weight] >= h:
            h_strength_edges.add((min(u, v), max(u, v)))

    # h-bridge network: top-h edges by betweenness among NON-h-strength edges
    remaining = G.copy()
    for u, v in list(h_strength_edges):
        if remaining.has_edge(u, v):
            remaining.remove_edge(u, v)

    h_bridge_edges = set()
    if remaining.number_of_edges() > 0 and h > 0:
        eb = nx.edge_betweenness_centrality(remaining, weight=weight)
        top_h = sorted(eb.items(), key=lambda x: x[1], reverse=True)[:h]
        for (u, v), _ in top_h:
            h_bridge_edges.add((min(u, v), max(u, v)))

    # Union
    backbone_edges = h_strength_edges | h_bridge_edges
    H = G.__class__()
    H.add_nodes_from(G.nodes(data=True))
    for u, v in backbone_edges:
        if G.has_edge(u, v):
            H.add_edge(u, v, **G[u][v])
    return H


# =====================================================================
# 8. Modularity backbone — Rajeh et al. (2022)
# =====================================================================

def modularity_backbone(G, weight="weight"):
    """Compute the modularity vitality index for each node.

    The vitality index [1]_ measures the change in modularity when a
    node is removed.  Nodes that contribute positively to community
    structure have positive vitality.

    Parameters
    ----------
    G : nx.Graph
        Undirected weighted graph.
    weight : str

    Returns
    -------
    H : nx.Graph
        Copy of *G* with ``"vitality"`` node attribute (float).  Filter
        with ``threshold_filter(..., filter_on="nodes")``.

    References
    ----------
    .. [1] Rajeh, S., Savonnet, M., Leclercq, E., & Cherifi, H. (2022).
       Modularity-based backbone extraction in weighted complex networks.
       *NetSci-X 2022*, 67-79.
    """
    if G.is_directed():
        raise nx.NetworkXError(
            "modularity_backbone is defined for undirected graphs only."
        )

    H = G.copy()

    # Baseline modularity
    try:
        communities_full = nx.community.louvain_communities(G, weight=weight, seed=42)
    except Exception:
        communities_full = [set(G.nodes())]
    mod_full = nx.community.modularity(G, communities_full, weight=weight)

    for node in G.nodes():
        G_reduced = G.copy()
        G_reduced.remove_node(node)
        if G_reduced.number_of_nodes() == 0:
            H.nodes[node]["vitality"] = 0.0
            continue
        try:
            communities_reduced = nx.community.louvain_communities(
                G_reduced, weight=weight, seed=42
            )
        except Exception:
            communities_reduced = [set(G_reduced.nodes())]
        mod_reduced = nx.community.modularity(
            G_reduced, communities_reduced, weight=weight
        )
        H.nodes[node]["vitality"] = mod_full - mod_reduced

    return H


# =====================================================================
# 9. Planar Maximally Filtered Graph — Tumminello et al. (2005)
# =====================================================================

def planar_maximally_filtered_graph(G, weight="weight"):
    """Construct the Planar Maximally Filtered Graph (PMFG).

    Iteratively adds edges from heaviest to lightest, keeping only
    those whose addition preserves planarity [1]_.

    Parameters
    ----------
    G : nx.Graph
        Undirected weighted graph.
    weight : str

    Returns
    -------
    H : nx.Graph
        Planar subgraph of *G* with maximum total weight.

    Notes
    -----
    A planar graph on n nodes has at most 3(n-2) edges.  The algorithm
    sorts all m edges and tests planarity incrementally, giving
    O(m log m + m * planarity_test) complexity.

    References
    ----------
    .. [1] Tumminello, M., Aste, T., Di Matteo, T., & Mantegna, R. N.
       (2005). A tool for filtering information in complex systems.
       *PNAS*, 102(30), 10421-10426.
    """
    if G.is_directed():
        raise nx.NetworkXError("PMFG is defined for undirected graphs only.")

    n = G.number_of_nodes()
    max_edges = 3 * (n - 2) if n >= 3 else n - 1

    # Sort edges by weight descending
    edges = sorted(G.edges(data=True), key=lambda e: e[2].get(weight, 0), reverse=True)

    H = G.__class__()
    H.add_nodes_from(G.nodes(data=True))

    for u, v, data in edges:
        if H.number_of_edges() >= max_edges:
            break
        H.add_edge(u, v, **data)
        is_planar, _ = nx.check_planarity(H)
        if not is_planar:
            H.remove_edge(u, v)

    return H


# =====================================================================
# 10. Maximum spanning tree backbone
# =====================================================================

def maximum_spanning_tree_backbone(G, weight="weight"):
    """Extract the maximum spanning tree as a backbone.

    Parameters
    ----------
    G : nx.Graph
    weight : str

    Returns
    -------
    H : nx.Graph
    """
    if G.is_directed():
        raise nx.NetworkXError("Maximum spanning tree requires an undirected graph.")
    return nx.maximum_spanning_tree(G, weight=weight)

# =====================================================================
# 11. Neighborhood overlap backbones
# =====================================================================

def _neighbor_sets(G):
    """Return a dict mapping each node to its set of neighbors."""
    return {v: set(G.neighbors(v)) for v in G}


def neighborhood_overlap(G):
    """Score each edge by the raw neighborhood overlap of its endpoints.

    For each edge (u, v), the overlap is the number of common neighbors:
    ``|N(u) ∩ N(v)|``.  The score is stored as the ``"overlap"`` edge
    attribute.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, neighborhoods are defined by
        successors (out-neighbors).

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"overlap"`` edge attribute added.

    Notes
    -----
    The raw overlap count is not normalised by degree, so high-degree
    nodes will tend to have higher overlap values.  Use
    :func:`jaccard_backbone`, :func:`dice_backbone`, or
    :func:`cosine_backbone` for normalised variants.

    See Also
    --------
    jaccard_backbone, dice_backbone, cosine_backbone

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(4)
    >>> H = neighborhood_overlap(G)
    >>> H[1][2]["overlap"]
    0
    >>> G = nx.complete_graph(4)
    >>> H = neighborhood_overlap(G)
    >>> H[0][1]["overlap"]
    2
    """
    H = G.copy()
    nbrs = _neighbor_sets(G)
    for u, v in H.edges():
        H[u][v]["overlap"] = len(nbrs[u] & nbrs[v])
    return H


def jaccard_backbone(G):
    r"""Score each edge by the Jaccard similarity of its endpoint neighborhoods.

    For each edge (u, v):

    .. math::

        J_{uv} = \frac{|N(u) \cap N(v)|}{|N(u) \cup N(v)|}
               = \frac{n_{uv}}{k_u + k_v - n_{uv}}

    where :math:`n_{uv} = |N(u) \cap N(v)|` is the number of common
    neighbors and :math:`k_u, k_v` are the degrees of *u* and *v*.  The
    score is stored as the ``"jaccard"`` edge attribute.

    The Jaccard coefficient ranges from 0 (no common neighbors) to 1
    (structurally equivalent: identical neighborhoods).  Edges connecting
    structurally embedded nodes — nodes that share many neighbors — score
    high, while edges bridging otherwise disconnected parts of the
    network score low.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, neighborhoods are defined by
        successors (out-neighbors) and degrees are out-degrees, following
        the out-similarity convention.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"jaccard"`` edge attribute added.

    References
    ----------
    Jaccard, P. (1901). "Distribution de la flore alpine dans le bassin
    des Dranses et dans quelques régions voisines." *Bulletin de la
    Société Vaudoise des Sciences Naturelles*, 37, 241–272.

    See Also
    --------
    dice_backbone, cosine_backbone, neighborhood_overlap

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = jaccard_backbone(G)
    >>> H[0][1]["jaccard"]  # 2 common / (3+3-2) = 0.5
    0.5
    """
    H = G.copy()
    nbrs = _neighbor_sets(G)
    for u, v in H.edges():
        nu = nbrs[u]
        nv = nbrs[v]
        intersection = len(nu & nv)
        union = len(nu | nv)
        H[u][v]["jaccard"] = intersection / union if union > 0 else 0.0
    return H


def dice_backbone(G):
    r"""Score each edge by the Dice similarity of its endpoint neighborhoods.

    For each edge (u, v):

    .. math::

        D_{uv} = \frac{2 \, |N(u) \cap N(v)|}{k_u + k_v}
               = \frac{2 \, n_{uv}}{k_u + k_v}

    The Dice coefficient is the harmonic mean of the two inclusion
    probabilities and ranges from 0 to 1.  It gives more credit to
    overlap between low-degree nodes than the raw overlap count.

    The score is stored as the ``"dice"`` edge attribute.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, out-degree is used.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"dice"`` edge attribute added.

    References
    ----------
    Dice, L. R. (1945). "Measures of the amount of ecologic association
    between species." *Ecology*, 26(3), 297–302.
    https://doi.org/10.2307/1932409

    See Also
    --------
    jaccard_backbone, cosine_backbone, neighborhood_overlap

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = dice_backbone(G)
    >>> round(H[0][1]["dice"], 4)  # 2*2 / (3+3) = 0.6667
    0.6667
    """
    H = G.copy()
    nbrs = _neighbor_sets(G)
    deg = dict(G.degree())
    for u, v in H.edges():
        intersection = len(nbrs[u] & nbrs[v])
        denom = deg[u] + deg[v]
        H[u][v]["dice"] = (2.0 * intersection) / denom if denom > 0 else 0.0
    return H


def cosine_backbone(G):
    r"""Score each edge by the cosine similarity of its endpoint neighborhoods.

    For each edge (u, v):

    .. math::

        C_{uv} = \frac{|N(u) \cap N(v)|}{\sqrt{k_u \, k_v}}
               = \frac{n_{uv}}{\sqrt{k_u \, k_v}}

    The denominator is the geometric mean of the two degrees.  Cosine
    similarity ranges from 0 to 1 and penalises degree disparity less
    than Jaccard while penalising it more than Dice.

    The score is stored as the ``"cosine"`` edge attribute.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, out-degree is used.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"cosine"`` edge attribute added.

    References
    ----------
    Salton, G. & McGill, M. J. (1983). *Introduction to Modern
    Information Retrieval*. McGraw-Hill.

    See Also
    --------
    jaccard_backbone, dice_backbone, neighborhood_overlap

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = cosine_backbone(G)
    >>> round(H[0][1]["cosine"], 4)  # 2 / sqrt(3*3) = 0.6667
    0.6667
    """
    H = G.copy()
    nbrs = _neighbor_sets(G)
    deg = dict(G.degree())
    for u, v in H.edges():
        intersection = len(nbrs[u] & nbrs[v])
        denom = math.sqrt(deg[u] * deg[v])
        H[u][v]["cosine"] = intersection / denom if denom > 0 else 0.0
    return H
