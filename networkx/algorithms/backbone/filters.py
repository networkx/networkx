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


def threshold_filter(G, score, threshold, mode="below", filter_on="edges"):
    """Retain edges/nodes whose score passes a threshold test.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Graph with a computed score attribute on edges or nodes.
    score : str
        Attribute name to filter on.
    threshold : float
        Cutoff value.
    mode : {"below", "above"}
        ``"below"`` keeps elements with score < threshold (typical for
        p-values).  ``"above"`` keeps elements with score ≥ threshold
        (typical for salience / importance scores).
    filter_on : {"edges", "nodes"}
        Whether to filter edges or nodes.

    Returns
    -------
    H : same type as G
        Filtered subgraph.  When filtering edges, all original nodes are
        preserved.  When filtering nodes, only retained nodes and their
        mutual edges are preserved.
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


def fraction_filter(G, score, fraction, ascending=True, filter_on="edges"):
    """Retain the top or bottom fraction of edges/nodes by score.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
    score : str
        Attribute name.
    fraction : float
        Fraction of elements to retain, in (0, 1].
    ascending : bool
        If True, keep the elements with the *smallest* scores (e.g.
        lowest p-values).  If False, keep the *largest*.
    filter_on : {"edges", "nodes"}

    Returns
    -------
    H : same type as G
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


def boolean_filter(G, score):
    """Retain edges whose boolean score attribute is True.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
    score : str
        Edge attribute name (should contain bool values).

    Returns
    -------
    H : same type as G
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
    *backbones : nx.Graph
        Two or more backbone graphs (must share the same node identifiers).

    Returns
    -------
    H : same type as first backbone
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
