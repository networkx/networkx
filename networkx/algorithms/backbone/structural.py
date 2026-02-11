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
from networkx.utils import not_implemented_for

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
    "neighborhood_overlap",
    "jaccard_backbone",
    "dice_backbone",
    "cosine_backbone",
]


# =====================================================================
# 1. Global threshold filter
# =====================================================================


@nx._dispatchable(edge_attrs="weight", preserve_edge_attrs=True, returns_graph=True)
def global_threshold_filter(G, threshold, weight="weight"):
    """Return a subgraph containing only edges whose weight meets a threshold.

    Construct a new graph of the same type as *G* that keeps every node
    but retains only edges whose *weight* attribute is greater than or
    equal to *threshold*.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    threshold : float
        Minimum edge weight required.  Edges with
        ``data[weight] >= threshold`` are kept.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.

    Returns
    -------
    H : graph
        A new graph of the same type as *G*.  All original nodes are
        preserved; only edges meeting the threshold are included.

    See Also
    --------
    strongest_n_ties : Keep the *n* heaviest edges per node.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import global_threshold_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = global_threshold_filter(G, threshold=3.0)
    >>> sorted(H.edges())
    [(0, 1), (1, 2)]
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


@nx._dispatchable(edge_attrs="weight", preserve_edge_attrs=True, returns_graph=True)
def strongest_n_ties(G, n=1, weight="weight"):
    """Retain the *n* strongest edges for every node.

    For each node, select the *n* incident edges with the largest
    *weight* value.  An edge is kept if *either* endpoint selects it
    (OR semantics).  For directed graphs the selection is based on
    out-edges.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    n : int, optional (default=1)
        Number of strongest edges to keep per node.  Must be at least 1.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.

    Returns
    -------
    H : graph
        A new graph of the same type as *G* containing only the
        selected edges.  All original nodes are preserved.

    Raises
    ------
    ValueError
        If *n* < 1.

    See Also
    --------
    global_threshold_filter : Keep edges above a global weight threshold.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import strongest_n_ties
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = strongest_n_ties(G, n=1)
    >>> sorted(H.edges())
    [(0, 1), (1, 2)]
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


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", preserve_edge_attrs=True, returns_graph=True)
def high_salience_skeleton(G, weight="weight"):
    """Compute edge salience from shortest-path tree participation.

    For every node *r*, a shortest-path tree rooted at *r* is computed
    (using inverse weights as distances).  The salience of an edge is the
    fraction of these trees that contain it.  The salience is stored as
    the ``"salience"`` edge attribute on the returned graph.

    Parameters
    ----------
    G : graph
        A NetworkX graph.  All weights must be positive.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.

    Returns
    -------
    H : graph
        A copy of *G* with an additional ``"salience"`` edge attribute
        whose value lies in [0, 1].

    See Also
    --------
    metric_backbone : Backbone based on shortest-path distances.
    maximum_spanning_tree_backbone : Maximum spanning tree extraction.

    Notes
    -----
    The algorithm iterates over all *n* nodes, computing a shortest-path
    tree for each.  Overall complexity is dominated by the *n* calls to
    Dijkstra's algorithm, i.e. *O(n (m + n) log n)*.

    References
    ----------
    .. [1] Grady, D., Thiemann, C., & Brockmann, D. (2012). Robust
       classification of salient links in complex networks. *Nature
       Communications*, 3, 864.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import high_salience_skeleton
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = high_salience_skeleton(G)
    >>> H[0][1]["salience"] >= 0
    True
    """
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


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", preserve_edge_attrs=True, returns_graph=True)
def metric_backbone(G, weight="weight"):
    """Extract the metric backbone using sum-of-distances shortest paths.

    An edge *(u, v)* is in the metric backbone if and only if its direct
    distance (the inverse of its weight) equals the shortest-path
    distance between *u* and *v* computed over the full graph.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.  All weights must be
        positive.

    Returns
    -------
    H : graph
        A new graph of the same type as *G* containing only edges that
        lie on shortest paths.  All original nodes are preserved.

    See Also
    --------
    ultrametric_backbone : Backbone using max-distance (minimax) paths.
    high_salience_skeleton : Salience based on shortest-path trees.

    Notes
    -----
    The metric backbone retains every edge whose direct distance matches
    the shortest-path distance, ensuring that the pairwise distance
    matrix of the backbone is identical to that of the original graph.

    References
    ----------
    .. [1] Simas, T., Correia, R. B., & Rocha, L. M. (2021). The distance
       backbone of complex networks. *J. Complex Netw.*, 9, cnab021.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import metric_backbone
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = metric_backbone(G)
    >>> H.number_of_edges() <= G.number_of_edges()
    True
    """
    return _distance_backbone(G, weight=weight, ultrametric=False)


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", preserve_edge_attrs=True, returns_graph=True)
def ultrametric_backbone(G, weight="weight"):
    """Extract the ultrametric backbone using max-distance (minimax) paths.

    An edge *(u, v)* is in the ultrametric backbone if its direct
    distance is no greater than the minimax path distance between *u*
    and *v* (the path that minimises the maximum edge distance along
    the path).

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.  All weights must be
        positive.

    Returns
    -------
    H : graph
        A new graph of the same type as *G* containing only edges that
        satisfy the ultrametric condition.  All original nodes are
        preserved.

    See Also
    --------
    metric_backbone : Backbone using sum-of-distances shortest paths.

    Notes
    -----
    The ultrametric backbone uses the minimum spanning tree of the
    distance graph to determine the minimax path between each pair of
    endpoints.

    References
    ----------
    .. [1] Simas, T., Correia, R. B., & Rocha, L. M. (2021). The distance
       backbone of complex networks. *J. Complex Netw.*, 9, cnab021.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import ultrametric_backbone
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = ultrametric_backbone(G)
    >>> H.number_of_edges() <= G.number_of_edges()
    True
    """
    return _distance_backbone(G, weight=weight, ultrametric=True)


def _distance_backbone(G, weight="weight", ultrametric=False):
    """Shared helper for metric and ultrametric backbones."""
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


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", preserve_edge_attrs=True, returns_graph=True)
def doubly_stochastic_filter(G, weight="weight", max_iter=1000, tol=1e-8):
    """Compute the doubly-stochastic backbone via Sinkhorn-Knopp normalization.

    Transforms the adjacency matrix into a doubly stochastic matrix via
    iterative Sinkhorn-Knopp normalization, then stores the normalised
    weight as the ``"ds_weight"`` edge attribute on the returned graph.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.
    max_iter : int, optional (default=1000)
        Maximum number of Sinkhorn-Knopp iterations.
    tol : float, optional (default=1e-8)
        Convergence tolerance.  Iteration stops when every row sum and
        column sum is within *tol* of 1.

    Returns
    -------
    H : graph
        A copy of *G* with an additional ``"ds_weight"`` edge attribute
        (doubly-stochastic normalised weight).

    See Also
    --------
    global_threshold_filter : Simple weight cutoff.

    Notes
    -----
    Sinkhorn-Knopp normalization alternately normalises rows and columns
    of the weight matrix until convergence.  The procedure is guaranteed
    to converge for non-negative matrices with total support.

    References
    ----------
    .. [1] Slater, P. B. (2009). A two-stage algorithm for extracting
       the multiscale backbone of complex weighted networks. *PNAS*,
       106(26), E66.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import doubly_stochastic_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = doubly_stochastic_filter(G)
    >>> "ds_weight" in H[0][1]
    True
    """
    import numpy as np

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
        data["ds_weight"] = float(D[idx[u], idx[v]])

    return H


# =====================================================================
# 7. h-backbone — Zhang et al. (2018)
# =====================================================================


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", preserve_edge_attrs=True, returns_graph=True)
def h_backbone(G, weight="weight"):
    r"""Extract the h-backbone of a weighted graph.

    The h-backbone [1]_ is composed of two parts:

    1. **h-strength network**: find *h* such that there are at least *h*
       edges with weight >= *h*.  Keep those edges.
    2. **h-bridge network**: among the remaining edges, keep those whose
       edge betweenness centrality is in the top-*h*.

    The union of both subsets forms the h-backbone.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.

    Returns
    -------
    H : graph
        The h-backbone subgraph.  All original nodes are preserved.

    See Also
    --------
    metric_backbone : Backbone based on shortest-path distances.
    modularity_backbone : Backbone based on modularity vitality.

    Notes
    -----
    The h-index of the weight sequence is computed analogously to the
    academic h-index: the largest *h* such that at least *h* edges have
    weight >= *h*.

    References
    ----------
    .. [1] Zhang, R. J., Stanley, H. E., & Ye, F. Y. (2018). Extracting
       h-backbone as a core structure in weighted networks. *Scientific
       Reports*, 8, 14356.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import h_backbone
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = h_backbone(G)
    >>> H.number_of_edges() <= G.number_of_edges()
    True
    """
    # Compute h-index of the weight sequence
    weights = sorted([data[weight] for _, _, data in G.edges(data=True)], reverse=True)
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


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", preserve_all_attrs=True, returns_graph=True)
def modularity_backbone(G, weight="weight"):
    """Compute the modularity vitality index for each node.

    The vitality index [1]_ measures the change in modularity when a
    node is removed.  Nodes that contribute positively to community
    structure have positive vitality.  The vitality is stored as the
    ``"vitality"`` node attribute on the returned graph.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.

    Returns
    -------
    H : graph
        A copy of *G* with an additional ``"vitality"`` node attribute
        (float).

    See Also
    --------
    h_backbone : Backbone using the h-index of edge weights.
    high_salience_skeleton : Salience based on shortest-path trees.

    Notes
    -----
    For each node *v*, the Louvain algorithm is run on the full graph
    and on the graph with *v* removed.  The vitality of *v* is the
    difference in modularity.  Complexity is *O(n)* calls to community
    detection.

    References
    ----------
    .. [1] Rajeh, S., Savonnet, M., Leclercq, E., & Cherifi, H. (2022).
       Modularity-based backbone extraction in weighted complex networks.
       *NetSci-X 2022*, 67-79.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import modularity_backbone
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = modularity_backbone(G)
    >>> "vitality" in H.nodes[0]
    True
    """
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


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", preserve_edge_attrs=True, returns_graph=True)
def planar_maximally_filtered_graph(G, weight="weight"):
    """Construct the Planar Maximally Filtered Graph (PMFG).

    Iteratively adds edges from heaviest to lightest, keeping only
    those whose addition preserves planarity [1]_.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.

    Returns
    -------
    H : graph
        A planar subgraph of *G* with maximum total weight.  All
        original nodes are preserved.

    See Also
    --------
    maximum_spanning_tree_backbone : Maximum spanning tree extraction.

    Notes
    -----
    A planar graph on *n* nodes has at most ``3(n - 2)`` edges.  The
    algorithm sorts all *m* edges and tests planarity incrementally,
    giving *O(m log m + m * planarity_test)* complexity.

    References
    ----------
    .. [1] Tumminello, M., Aste, T., Di Matteo, T., & Mantegna, R. N.
       (2005). A tool for filtering information in complex systems.
       *PNAS*, 102(30), 10421-10426.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import planar_maximally_filtered_graph
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = planar_maximally_filtered_graph(G)
    >>> H.number_of_edges() <= G.number_of_edges()
    True
    """
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


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", preserve_edge_attrs=True, returns_graph=True)
def maximum_spanning_tree_backbone(G, weight="weight"):
    """Extract the maximum spanning tree as a backbone.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.

    Returns
    -------
    H : graph
        The maximum spanning tree of *G*.

    See Also
    --------
    high_salience_skeleton : Salience based on shortest-path trees.
    planar_maximally_filtered_graph : Planar subgraph with maximum weight.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import maximum_spanning_tree_backbone
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = maximum_spanning_tree_backbone(G)
    >>> H.number_of_edges()
    2
    """
    return nx.maximum_spanning_tree(G, weight=weight)


# =====================================================================
# 11. Neighborhood overlap backbones
# =====================================================================


def _neighbor_sets(G):
    """Return a dict mapping each node to its set of neighbors."""
    return {v: set(G.neighbors(v)) for v in G}


@nx._dispatchable(preserve_edge_attrs=True, returns_graph=True)
def neighborhood_overlap(G):
    """Score each edge by the raw neighborhood overlap of its endpoints.

    For each edge *(u, v)*, the overlap is the number of common
    neighbors: ``|N(u) & N(v)|``.  The score is stored as the
    ``"overlap"`` edge attribute.

    Parameters
    ----------
    G : graph
        A NetworkX graph.  For directed graphs, neighborhoods are
        defined by successors (out-neighbors).

    Returns
    -------
    H : graph
        A copy of *G* with the ``"overlap"`` edge attribute added.

    See Also
    --------
    jaccard_backbone : Overlap normalised by union size.
    dice_backbone : Overlap normalised by sum of degrees.
    cosine_backbone : Overlap normalised by geometric mean of degrees.

    Notes
    -----
    The raw overlap count is not normalised by degree, so high-degree
    nodes will tend to have higher overlap values.  Use
    :func:`jaccard_backbone`, :func:`dice_backbone`, or
    :func:`cosine_backbone` for normalised variants.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import neighborhood_overlap
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


@nx._dispatchable(preserve_edge_attrs=True, returns_graph=True)
def jaccard_backbone(G):
    r"""Score each edge by the Jaccard similarity of its endpoint neighborhoods.

    For each edge *(u, v)*:

    .. math::

        J_{uv} = \frac{|N(u) \cap N(v)|}{|N(u) \cup N(v)|}
               = \frac{n_{uv}}{k_u + k_v - n_{uv}}

    where :math:`n_{uv} = |N(u) \cap N(v)|` is the number of common
    neighbors and :math:`k_u, k_v` are the degrees of *u* and *v*.  The
    score is stored as the ``"jaccard"`` edge attribute.

    The Jaccard coefficient ranges from 0 (no common neighbors) to 1
    (structurally equivalent: identical neighborhoods).  Edges connecting
    structurally embedded nodes -- nodes that share many neighbors --
    score high, while edges bridging otherwise disconnected parts of the
    network score low.

    Parameters
    ----------
    G : graph
        A NetworkX graph.  For directed graphs, neighborhoods are
        defined by successors (out-neighbors) and degrees are
        out-degrees, following the out-similarity convention.

    Returns
    -------
    H : graph
        A copy of *G* with the ``"jaccard"`` edge attribute added.

    See Also
    --------
    dice_backbone : Dice similarity of endpoint neighborhoods.
    cosine_backbone : Cosine similarity of endpoint neighborhoods.
    neighborhood_overlap : Raw common-neighbor count.

    References
    ----------
    .. [1] Jaccard, P. (1901). Distribution de la flore alpine dans le
       bassin des Dranses et dans quelques regions voisines. *Bulletin
       de la Societe Vaudoise des Sciences Naturelles*, 37, 241-272.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import jaccard_backbone
    >>> G = nx.complete_graph(4)
    >>> H = jaccard_backbone(G)
    >>> H[0][1]["jaccard"]
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


@nx._dispatchable(preserve_edge_attrs=True, returns_graph=True)
def dice_backbone(G):
    r"""Score each edge by the Dice similarity of its endpoint neighborhoods.

    For each edge *(u, v)*:

    .. math::

        D_{uv} = \frac{2 \, |N(u) \cap N(v)|}{k_u + k_v}
               = \frac{2 \, n_{uv}}{k_u + k_v}

    The Dice coefficient is the harmonic mean of the two inclusion
    probabilities and ranges from 0 to 1.  It gives more credit to
    overlap between low-degree nodes than the raw overlap count.

    The score is stored as the ``"dice"`` edge attribute.

    Parameters
    ----------
    G : graph
        A NetworkX graph.  For directed graphs, out-degree is used.

    Returns
    -------
    H : graph
        A copy of *G* with the ``"dice"`` edge attribute added.

    See Also
    --------
    jaccard_backbone : Jaccard similarity of endpoint neighborhoods.
    cosine_backbone : Cosine similarity of endpoint neighborhoods.
    neighborhood_overlap : Raw common-neighbor count.

    References
    ----------
    .. [1] Dice, L. R. (1945). Measures of the amount of ecologic
       association between species. *Ecology*, 26(3), 297-302.
       https://doi.org/10.2307/1932409

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import dice_backbone
    >>> G = nx.complete_graph(4)
    >>> H = dice_backbone(G)
    >>> round(H[0][1]["dice"], 4)
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


@nx._dispatchable(preserve_edge_attrs=True, returns_graph=True)
def cosine_backbone(G):
    r"""Score each edge by the cosine similarity of its endpoint neighborhoods.

    For each edge *(u, v)*:

    .. math::

        C_{uv} = \frac{|N(u) \cap N(v)|}{\sqrt{k_u \, k_v}}
               = \frac{n_{uv}}{\sqrt{k_u \, k_v}}

    The denominator is the geometric mean of the two degrees.  Cosine
    similarity ranges from 0 to 1 and penalises degree disparity less
    than Jaccard while penalising it more than Dice.

    The score is stored as the ``"cosine"`` edge attribute.

    Parameters
    ----------
    G : graph
        A NetworkX graph.  For directed graphs, out-degree is used.

    Returns
    -------
    H : graph
        A copy of *G* with the ``"cosine"`` edge attribute added.

    See Also
    --------
    jaccard_backbone : Jaccard similarity of endpoint neighborhoods.
    dice_backbone : Dice similarity of endpoint neighborhoods.
    neighborhood_overlap : Raw common-neighbor count.

    References
    ----------
    .. [1] Salton, G. & McGill, M. J. (1983). *Introduction to Modern
       Information Retrieval*. McGraw-Hill.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import cosine_backbone
    >>> G = nx.complete_graph(4)
    >>> H = cosine_backbone(G)
    >>> round(H[0][1]["cosine"], 4)
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
