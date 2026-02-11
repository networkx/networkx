"""
Hybrid backbone extraction methods.

These methods combine statistical and structural approaches.

Methods
-------
glab_filter
    Zhang et al. (2014) — Globally and Locally Adaptive Backbone.
    Combines disparity filter with high salience skeleton.
"""

import math

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["glab_filter"]


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", returns_graph=True)
def glab_filter(G, weight="weight", c=0.5):
    r"""Compute GLAB (Globally and Locally Adaptive Backbone) p-values.

    The GLAB method [1]_ combines global and local information.  For each
    edge it computes an *involvement* score --- the fraction of all shortest
    paths that pass through the edge --- and then tests significance using a
    degree-dependent null model.

    The involvement $I(e)$ of edge $e = (u, v)$ is::

        I(e) = sum_{s,t} [sigma_{st}(e) / sigma_{st}]  /  [n*(n-1)/2]

    where $\sigma_{st}$ is the total number of shortest paths from *s* to
    *t* and $\sigma_{st}(e)$ is the number that pass through *e*.

    The p-value is computed as::

        p(e) = (1 - I(e))^((k_u * k_v)^c)

    where $k_u$, $k_v$ are the degrees of the endpoints and *c* controls
    how much degree amplifies significance.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key (used as ``distance = 1 / weight`` for
        shortest-path computation).
    c : float, optional (default=0.5)
        Involvement parameter controlling degree influence.  Higher
        values make high-degree endpoints more likely to be significant.

    Returns
    -------
    H : graph
        A copy of *G* with a ``"glab_pvalue"`` edge attribute.

    See Also
    --------
    disparity_filter : Local statistical backbone method.
    high_salience_skeleton : Salience based on shortest-path trees.

    References
    ----------
    .. [1] Zhang, X., Zhang, Z., Zhao, H., Wang, Q., & Zhu, J. (2014).
       Extracting the globally and locally adaptive backbone of complex
       networks. *PLoS ONE*, 9(6), e100428.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import glab_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 3.0), (0, 2, 1.0)])
    >>> H = glab_filter(G)
    >>> "glab_pvalue" in H[0][1]
    True
    """
    H = G.copy()
    n = G.number_of_nodes()
    if n <= 1 or G.number_of_edges() == 0:
        for u, v, data in H.edges(data=True):
            data["glab_pvalue"] = 1.0
        return H

    # Compute edge betweenness centrality (normalised by n*(n-1)/2 pairs)
    # NetworkX's edge_betweenness_centrality already normalises by
    # 2/(n*(n-1)) for undirected graphs, giving values in [0, 1].
    dist_attr = "__glab_dist__"
    for u, v, data in H.edges(data=True):
        data[dist_attr] = 1.0 / data[weight]

    eb = nx.edge_betweenness_centrality(H, weight=dist_attr, normalized=True)

    # Clean up temp attribute
    for u, v, data in H.edges(data=True):
        data.pop(dist_attr, None)

    degree = dict(G.degree())
    total_pairs = n * (n - 1) / 2.0

    for u, v, data in H.edges(data=True):
        involvement = eb.get((u, v), eb.get((v, u), 0.0))
        ku = degree[u]
        kv = degree[v]

        # Degree-dependent exponent
        exponent = (ku * kv) ** c

        # p-value: probability under null of seeing this involvement
        # Higher involvement -> smaller p-value (more significant)
        pval = (1.0 - involvement) ** exponent
        pval = max(min(pval, 1.0), 0.0)

        data["glab_pvalue"] = pval

    return H
