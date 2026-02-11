"""
Filtering utilities for backbone extraction.

After a backbone method annotates edges (or nodes) with scores or p-values,
these functions extract the final subgraph.
"""

import networkx as nx

__all__ = [
    "threshold_filter",
    "fraction_filter",
    "boolean_filter",
    "consensus_backbone",
]


@nx._dispatchable(returns_graph=True)
def threshold_filter(G, score, threshold, mode="below", filter_on="edges"):
    """Retain edges or nodes whose score passes a threshold test.

    Parameters
    ----------
    G : graph
        A NetworkX graph with a computed score attribute on edges or nodes.
    score : string
        Attribute name to filter on.
    threshold : float
        Cutoff value.
    mode : {"below", "above"}, optional (default="below")
        ``"below"`` keeps elements with ``score < threshold`` (typical for
        p-values).  ``"above"`` keeps elements with ``score >= threshold``
        (typical for salience or importance scores).
    filter_on : {"edges", "nodes"}, optional (default="edges")
        Whether to filter edges or nodes.

    Returns
    -------
    H : graph
        Filtered subgraph of the same type as *G*.  When filtering edges,
        all original nodes are preserved.  When filtering nodes, only
        retained nodes and their mutual edges are preserved.

    Raises
    ------
    ValueError
        If *mode* is not ``"below"`` or ``"above"``, or if *filter_on* is
        not ``"edges"`` or ``"nodes"``.

    See Also
    --------
    fraction_filter : Retain a fixed fraction of elements.
    boolean_filter : Retain edges with a boolean attribute.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import disparity_filter, threshold_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 2.0)])
    >>> H = disparity_filter(G)
    >>> filtered = threshold_filter(H, "disparity_pvalue", 0.5)
    >>> filtered.number_of_edges() <= H.number_of_edges()
    True
    """
    if mode not in ("below", "above"):
        raise ValueError(f"mode must be 'below' or 'above', got {mode!r}")

    if filter_on == "edges":
        H = G.__class__()
        H.add_nodes_from(G.nodes(data=True))
        for u, v, data in G.edges(data=True):
            val = data.get(score)
            if val is None:
                continue
            if (mode == "below" and val < threshold) or (
                mode == "above" and val >= threshold
            ):
                H.add_edge(u, v, **data)
        return H

    elif filter_on == "nodes":
        keep = set()
        for node, data in G.nodes(data=True):
            val = data.get(score)
            if val is None:
                continue
            if (mode == "below" and val < threshold) or (
                mode == "above" and val >= threshold
            ):
                keep.add(node)
        return G.subgraph(keep).copy()

    else:
        raise ValueError(f"filter_on must be 'edges' or 'nodes', got {filter_on!r}")


@nx._dispatchable(returns_graph=True)
def fraction_filter(G, score, fraction, ascending=True, filter_on="edges"):
    """Retain the top or bottom fraction of edges or nodes by score.

    Parameters
    ----------
    G : graph
        A NetworkX graph with a computed score attribute.
    score : string
        Attribute name to sort on.
    fraction : float
        Fraction of elements to retain, in (0, 1].
    ascending : bool, optional (default=True)
        If ``True``, keep the elements with the *smallest* scores (e.g.
        lowest p-values).  If ``False``, keep the *largest*.
    filter_on : {"edges", "nodes"}, optional (default="edges")
        Whether to filter edges or nodes.

    Returns
    -------
    H : graph
        Filtered subgraph of the same type as *G*.

    Raises
    ------
    ValueError
        If *fraction* is not in (0, 1] or *filter_on* is invalid.

    See Also
    --------
    threshold_filter : Filter by an absolute score cutoff.
    boolean_filter : Retain edges with a boolean attribute.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import disparity_filter, fraction_filter
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 2.0)])
    >>> H = disparity_filter(G)
    >>> filtered = fraction_filter(H, "disparity_pvalue", 0.5)
    >>> filtered.number_of_edges() <= H.number_of_edges()
    True
    """
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")

    if filter_on == "edges":
        scored = [
            (u, v, data, data.get(score, float("inf") if ascending else float("-inf")))
            for u, v, data in G.edges(data=True)
        ]
        scored.sort(key=lambda x: x[3], reverse=not ascending)
        n_keep = max(1, int(len(scored) * fraction))
        keep = scored[:n_keep]

        H = G.__class__()
        H.add_nodes_from(G.nodes(data=True))
        for u, v, data, _ in keep:
            H.add_edge(u, v, **data)
        return H

    elif filter_on == "nodes":
        scored = [
            (node, data, data.get(score, float("inf") if ascending else float("-inf")))
            for node, data in G.nodes(data=True)
        ]
        scored.sort(key=lambda x: x[2], reverse=not ascending)
        n_keep = max(1, int(len(scored) * fraction))
        keep = {s[0] for s in scored[:n_keep]}
        return G.subgraph(keep).copy()

    else:
        raise ValueError(f"filter_on must be 'edges' or 'nodes', got {filter_on!r}")


@nx._dispatchable(returns_graph=True)
def boolean_filter(G, score):
    """Retain edges whose boolean score attribute is truthy.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    score : string
        Edge attribute name (should contain boolean values).

    Returns
    -------
    H : graph
        A new graph of the same type as *G* containing only edges for
        which ``data[score]`` is truthy.  All original nodes are preserved.

    See Also
    --------
    threshold_filter : Filter by a numeric score threshold.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import boolean_filter
    >>> G = nx.Graph()
    >>> G.add_edge(0, 1, keep=True)
    >>> G.add_edge(1, 2, keep=False)
    >>> H = boolean_filter(G, "keep")
    >>> sorted(H.edges())
    [(0, 1)]
    """
    H = G.__class__()
    H.add_nodes_from(G.nodes(data=True))
    for u, v, data in G.edges(data=True):
        if data.get(score):
            H.add_edge(u, v, **data)
    return H


def consensus_backbone(*backbones):
    """Return the intersection of multiple backbone graphs.

    An edge is in the consensus backbone if and only if it appears in
    **every** input backbone.  Only nodes that are endpoints of consensus
    edges are retained.

    Parameters
    ----------
    *backbones : graph
        Two or more backbone graphs (must share the same node identifiers).

    Returns
    -------
    H : graph
        A new graph of the same type as the first backbone, containing
        only edges present in every input.

    Raises
    ------
    ValueError
        If fewer than 2 backbones are provided.

    See Also
    --------
    threshold_filter : Filter a single backbone by score.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import consensus_backbone
    >>> G1 = nx.Graph([(0, 1), (1, 2)])
    >>> G2 = nx.Graph([(0, 1), (2, 3)])
    >>> H = consensus_backbone(G1, G2)
    >>> sorted(H.edges())
    [(0, 1)]
    """
    if len(backbones) < 2:
        raise ValueError("consensus_backbone requires at least 2 graphs")

    edge_sets = []
    for bb in backbones:
        if bb.is_directed():
            edge_sets.append(set(bb.edges()))
        else:
            edge_sets.append({(min(u, v), max(u, v)) for u, v in bb.edges()})

    common = edge_sets[0]
    for es in edge_sets[1:]:
        common &= es

    ref = backbones[0]
    H = ref.__class__()
    for u, v in common:
        if ref.has_edge(u, v):
            H.add_edge(u, v, **ref[u][v])
        elif not ref.is_directed() and ref.has_edge(v, u):
            H.add_edge(v, u, **ref[v][u])

    return H
