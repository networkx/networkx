"""
Proximity-based edge scoring methods.

These methods score each existing edge by the topological proximity
(similarity) of its endpoints.  They are useful for identifying
structurally embedded edges (high proximity) versus bridge edges
(low proximity) and can feed into any of the filtering utilities
in :mod:`backbone.filters`.

Local methods
-------------
neighborhood_overlap
    Raw common-neighbor count.
jaccard_backbone
    Jaccard coefficient of endpoint neighborhoods.
dice_backbone
    Dice / Sørensen coefficient of endpoint neighborhoods.
cosine_backbone
    Cosine / Salton index of endpoint neighborhoods.
hub_promoted_index
    Common neighbors normalised by the smaller degree.
hub_depressed_index
    Common neighbors normalised by the larger degree.
lhn_local_index
    Leicht–Holme–Newman local similarity index.
preferential_attachment_score
    Product of endpoint degrees.
adamic_adar_index
    Adamic–Adar index (inverse-log-degree–weighted common neighbors).
resource_allocation_index
    Resource-allocation index (inverse-degree–weighted common neighbors).

Quasi-local methods
-------------------
graph_distance_proximity
    Reciprocal shortest-path distance.
local_path_index
    Local path index (second- and third-order path counts).

References
----------
Lü, L. & Zhou, T. (2011). "Link prediction in complex networks:
A survey." *Physica A*, 390(6), 1150–1170.

Liben-Nowell, D. & Kleinberg, J. (2007). "The link-prediction problem
for social networks." *JASIST*, 58(7), 1019–1031.
"""

import math

import networkx as nx
import numpy as np


# =====================================================================
# Helper
# =====================================================================

def _neighbor_sets(G):
    """Return a dict mapping each node to its set of neighbors."""
    return {v: set(G.neighbors(v)) for v in G}


# =====================================================================
# Local methods — moved from structural.py
# =====================================================================

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


# =====================================================================
# Local methods — new
# =====================================================================

def hub_promoted_index(G):
    r"""Score each edge by the Hub Promoted Index of its endpoint neighborhoods.

    For each edge (u, v):

    .. math::

        \mathrm{HPI}_{uv} = \frac{|N(u) \cap N(v)|}{\min(k_u,\, k_v)}

    The denominator is the *smaller* of the two endpoint degrees, so
    edges adjacent to hubs (high-degree nodes) receive higher scores.
    The score is stored as the ``"hpi"`` edge attribute and ranges
    from 0 to 1.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, out-degree is used.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"hpi"`` edge attribute added.

    References
    ----------
    Ravasz, E., Somera, A. L., Mongru, D. A., Oltvai, Z. N. &
    Barabási, A.-L. (2002). "Hierarchical organization of modularity
    in metabolic networks." *Science*, 297(5586), 1551–1555.

    See Also
    --------
    hub_depressed_index, jaccard_backbone, cosine_backbone

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = hub_promoted_index(G)
    >>> round(H[0][1]["hpi"], 4)  # 2 / min(3,3) = 0.6667
    0.6667
    """
    H = G.copy()
    nbrs = _neighbor_sets(G)
    deg = dict(G.degree())
    for u, v in H.edges():
        intersection = len(nbrs[u] & nbrs[v])
        denom = min(deg[u], deg[v])
        H[u][v]["hpi"] = intersection / denom if denom > 0 else 0.0
    return H


def hub_depressed_index(G):
    r"""Score each edge by the Hub Depressed Index of its endpoint neighborhoods.

    For each edge (u, v):

    .. math::

        \mathrm{HDI}_{uv} = \frac{|N(u) \cap N(v)|}{\max(k_u,\, k_v)}

    The denominator is the *larger* of the two endpoint degrees, so
    edges adjacent to hubs (high-degree nodes) are penalised.  The
    score is stored as the ``"hdi"`` edge attribute and ranges from
    0 to 1.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, out-degree is used.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"hdi"`` edge attribute added.

    References
    ----------
    Ravasz, E., Somera, A. L., Mongru, D. A., Oltvai, Z. N. &
    Barabási, A.-L. (2002). "Hierarchical organization of modularity
    in metabolic networks." *Science*, 297(5586), 1551–1555.

    See Also
    --------
    hub_promoted_index, jaccard_backbone, cosine_backbone

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = hub_depressed_index(G)
    >>> round(H[0][1]["hdi"], 4)  # 2 / max(3,3) = 0.6667
    0.6667
    """
    H = G.copy()
    nbrs = _neighbor_sets(G)
    deg = dict(G.degree())
    for u, v in H.edges():
        intersection = len(nbrs[u] & nbrs[v])
        denom = max(deg[u], deg[v])
        H[u][v]["hdi"] = intersection / denom if denom > 0 else 0.0
    return H


def lhn_local_index(G):
    r"""Score each edge by the Leicht–Holme–Newman local similarity index.

    For each edge (u, v):

    .. math::

        \mathrm{LHN}_{uv} = \frac{|N(u) \cap N(v)|}{k_u \cdot k_v}

    This normalises the common-neighbor count by the *product* of
    endpoint degrees, giving the ratio of observed to expected common
    neighbors under a configuration-model null.  The score is stored
    as the ``"lhn_local"`` edge attribute.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, out-degree is used.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"lhn_local"`` edge attribute added.

    References
    ----------
    Leicht, E. A., Holme, P. & Newman, M. E. J. (2006). "Vertex
    similarity in networks." *Physical Review E*, 73(2), 026120.

    See Also
    --------
    cosine_backbone, jaccard_backbone, hub_promoted_index

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = lhn_local_index(G)
    >>> round(H[0][1]["lhn_local"], 4)  # 2 / (3*3) = 0.2222
    0.2222
    """
    H = G.copy()
    nbrs = _neighbor_sets(G)
    deg = dict(G.degree())
    for u, v in H.edges():
        intersection = len(nbrs[u] & nbrs[v])
        denom = deg[u] * deg[v]
        H[u][v]["lhn_local"] = intersection / denom if denom > 0 else 0.0
    return H


def preferential_attachment_score(G):
    r"""Score each edge by the preferential attachment index.

    For each edge (u, v):

    .. math::

        \mathrm{PA}_{uv} = k_u \cdot k_v

    The score equals the product of endpoint degrees.  Unlike overlap-
    based indices, this metric does not examine shared neighbors; it
    captures the intuition that high-degree nodes are more likely to
    form new connections.  The score is stored as the ``"pa"`` edge
    attribute.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, out-degree is used.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"pa"`` edge attribute added.

    References
    ----------
    Barabási, A.-L. & Albert, R. (1999). "Emergence of scaling in
    random networks." *Science*, 286(5439), 509–512.

    See Also
    --------
    neighborhood_overlap, lhn_local_index

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = preferential_attachment_score(G)
    >>> H[0][1]["pa"]  # 3 * 3 = 9
    9
    """
    H = G.copy()
    deg = dict(G.degree())
    for u, v in H.edges():
        H[u][v]["pa"] = deg[u] * deg[v]
    return H


def adamic_adar_index(G):
    r"""Score each edge by the Adamic–Adar index.

    For each edge (u, v):

    .. math::

        \mathrm{AA}_{uv} = \sum_{z \,\in\, N(u) \cap N(v)}
                           \frac{1}{\log k_z}

    Each common neighbor *z* contributes inversely to the logarithm
    of its degree, giving more weight to common neighbors that are
    themselves sparsely connected.  The score is stored as the
    ``"adamic_adar"`` edge attribute.

    Common neighbors with degree 1 are skipped because they would
    produce a division by zero (:math:`\log 1 = 0`).  In practice
    a common neighbor of *u* and *v* must have degree ≥ 2.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, out-degree is used.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"adamic_adar"`` edge attribute added.

    References
    ----------
    Adamic, L. A. & Adar, E. (2003). "Friends and neighbors on the
    Web." *Social Networks*, 25(3), 211–230.

    See Also
    --------
    resource_allocation_index, neighborhood_overlap

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = adamic_adar_index(G)
    >>> round(H[0][1]["adamic_adar"], 4)  # 2 * 1/log(3) ≈ 1.8205
    1.8205
    """
    H = G.copy()
    nbrs = _neighbor_sets(G)
    deg = dict(G.degree())
    for u, v in H.edges():
        common = nbrs[u] & nbrs[v]
        score = sum(1.0 / math.log(deg[z]) for z in common if deg[z] > 1)
        H[u][v]["adamic_adar"] = score
    return H


def resource_allocation_index(G):
    r"""Score each edge by the resource-allocation index.

    For each edge (u, v):

    .. math::

        \mathrm{RA}_{uv} = \sum_{z \,\in\, N(u) \cap N(v)}
                           \frac{1}{k_z}

    Each common neighbor *z* contributes the reciprocal of its degree.
    Compared to the Adamic–Adar index, resource allocation penalises
    high-degree common neighbors more heavily.  The score is stored as
    the ``"resource_allocation"`` edge attribute.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph. For directed graphs, out-degree is used.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"resource_allocation"`` edge attribute
        added.

    References
    ----------
    Zhou, T., Lü, L. & Zhang, Y.-C. (2009). "Predicting missing links
    via local information." *European Physical Journal B*, 71(4),
    623–630.

    See Also
    --------
    adamic_adar_index, neighborhood_overlap

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = resource_allocation_index(G)
    >>> round(H[0][1]["resource_allocation"], 4)  # 2 * 1/3 ≈ 0.6667
    0.6667
    """
    H = G.copy()
    nbrs = _neighbor_sets(G)
    deg = dict(G.degree())
    for u, v in H.edges():
        common = nbrs[u] & nbrs[v]
        score = sum(1.0 / deg[z] for z in common if deg[z] > 0)
        H[u][v]["resource_allocation"] = score
    return H


# =====================================================================
# Quasi-local methods
# =====================================================================

def graph_distance_proximity(G):
    r"""Score each edge by the reciprocal of shortest-path distance.

    For each edge (u, v):

    .. math::

        s_{uv} = \frac{1}{d(u, v)}

    where :math:`d(u, v)` is the shortest-path length.  For edges in a
    connected graph this is always 1 (since adjacent nodes are distance
    1 apart), but the function is included for completeness and is most
    useful when applied to *all* vertex pairs rather than just existing
    edges.  The score is stored as the ``"dist"`` edge attribute.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"dist"`` edge attribute added.

    References
    ----------
    Liben-Nowell, D. & Kleinberg, J. (2007). "The link-prediction
    problem for social networks." *JASIST*, 58(7), 1019–1031.

    See Also
    --------
    local_path_index, neighborhood_overlap

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(4)
    >>> H = graph_distance_proximity(G)
    >>> H[0][1]["dist"]
    1.0
    """
    H = G.copy()
    for u, v in H.edges():
        try:
            d = nx.shortest_path_length(G, u, v)
            H[u][v]["dist"] = 1.0 / d if d > 0 else 0.0
        except nx.NetworkXNoPath:
            H[u][v]["dist"] = 0.0
    return H


def local_path_index(G, epsilon=0.01):
    r"""Score each edge by the local path index.

    For each edge (u, v):

    .. math::

        \mathrm{LP}_{uv} = (A^2)_{uv} + \varepsilon \, (A^3)_{uv}

    where *A* is the adjacency matrix and :math:`\varepsilon` is a free
    parameter controlling the weight of third-order paths.  The first
    term counts the number of common neighbors (paths of length 2) and
    the second term counts the number of length-3 paths between *u*
    and *v*.  The score is stored as the ``"lp"`` edge attribute.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph.
    epsilon : float, optional (default=0.01)
        Weight for third-order paths.  Larger values give more
        importance to indirect connections.

    Returns
    -------
    H : nx.Graph or nx.DiGraph
        Copy of *G* with the ``"lp"`` edge attribute added.

    References
    ----------
    Lü, L., Jin, C.-H. & Zhou, T. (2009). "Similarity index based on
    local random walk and superposed with the AA index." *EPL
    (Europhysics Letters)*, 89(1), 18001.

    See Also
    --------
    neighborhood_overlap, adamic_adar_index, graph_distance_proximity

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> H = local_path_index(G)
    >>> H[0][1]["lp"] > 0
    True
    """
    H = G.copy()
    nodelist = list(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodelist)
    A2 = A @ A
    A3 = A2 @ A
    S = A2 + epsilon * A3
    node_idx = {node: i for i, node in enumerate(nodelist)}
    for u, v in H.edges():
        i, j = node_idx[u], node_idx[v]
        H[u][v]["lp"] = float(S[i, j])
    return H
