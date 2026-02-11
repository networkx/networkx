"""
Unweighted network backbone methods.

These methods sparsify unweighted graphs by scoring edges and filtering
based on local topology.

Methods
-------
sparsify
    Generic sparsification framework (score -> normalise -> filter -> connect).
lspar
    Local Sparsification (Satuluri et al. 2011) — Jaccard-based.
local_degree
    Local Degree model (Hamann et al. 2016) — degree-based scoring.
"""

import math
import networkx as nx
import numpy as np

__all__ = ["sparsify", "lspar", "local_degree"]


def sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=0.5, umst=False):
    """Generic sparsification framework.

    Follows the four-step pipeline from Neal (2022) [1]_:

    1. **Score**: Assign a relevance score to each edge.
    2. **Normalise**: Optionally rank-transform scores within each node's
       neighbourhood.
    3. **Filter**: Retain a fraction of edges per node or globally.
    4. **Connect**: Optionally add the union of minimum spanning trees
       to ensure connectivity.

    Parameters
    ----------
    G : nx.Graph
        Input unweighted graph.
    escore : str
        Edge scoring method:
        - ``"jaccard"``: Jaccard coefficient of endpoint neighbourhoods
        - ``"degree"``: Degree of the neighbour
        - ``"triangles"``: Number of triangles containing the edge
        - ``"quadrangles"``: Number of 4-cycles containing the edge
        - ``"random"``: Uniform random score
    normalize : str or None
        Normalisation method: ``"rank"`` (rank within neighbourhood) or
        ``None`` (no normalisation).
    filter : str
        Filtering method:
        - ``"degree"``: Each node keeps ceil(d^s) of its top-scored edges
        - ``"threshold"``: Keep edges with normalised score >= s
    s : float
        Sparsification parameter.  For ``filter="degree"``, controls
        density (0 = sparsest, 1 = keep all).  For ``filter="threshold"``,
        is the cutoff value.
    umst : bool
        If True, add the union of minimum spanning trees (using negative
        scores as weights) to guarantee connectivity.

    Returns
    -------
    H : nx.Graph
        Sparsified backbone.

    References
    ----------
    .. [1] Neal, Z. P. (2022). backbone: An R package to extract network
       backbones. *PLOS ONE*, 17(5), e0269137.
    """
    if G.is_directed():
        raise nx.NetworkXError("sparsify is defined for undirected graphs only.")

    # Step 1: Score edges
    scores = _score_edges(G, escore)

    # Step 2: Normalise
    if normalize == "rank":
        scores = _rank_normalise(G, scores)

    # Step 3: Filter
    if filter == "degree":
        kept = _degree_filter(G, scores, s)
    elif filter == "threshold":
        kept = {e for e, sc in scores.items() if sc >= s}
    else:
        raise ValueError(f"Unknown filter: {filter!r}")

    # Build the backbone
    H = G.__class__()
    H.add_nodes_from(G.nodes(data=True))
    for u, v in kept:
        if G.has_edge(u, v):
            H.add_edge(u, v, **G[u][v])

    # Step 4: Optionally add UMST
    if umst and nx.number_connected_components(H) > 1:
        # Use negative scores as weights for MST
        scored_G = G.copy()
        for u, v in scored_G.edges():
            key = (min(u, v), max(u, v))
            scored_G[u][v]["__sparsify_neg_score__"] = -scores.get(key, 0)
        mst = nx.minimum_spanning_tree(scored_G, weight="__sparsify_neg_score__")
        for u, v, data in mst.edges(data=True):
            if not H.has_edge(u, v):
                orig_data = G[u][v] if G.has_edge(u, v) else {}
                H.add_edge(u, v, **orig_data)

    return H


def lspar(G, s=0.5):
    """Local Sparsification backbone (Satuluri et al. 2011).

    Convenience wrapper: Jaccard scoring, rank normalisation, degree
    filtering.  Best for preserving community structure.

    Parameters
    ----------
    G : nx.Graph
    s : float
        Sparsification exponent (0 = sparsest, 1 = keep all).

    Returns
    -------
    H : nx.Graph

    References
    ----------
    .. [1] Satuluri, V., Parthasarathy, S., & Ruan, Y. (2011). Local
       graph sparsification for scalable clustering. *ACM SIGMOD*, 721-732.
    """
    return sparsify(G, escore="jaccard", normalize="rank", filter="degree", s=s)


def local_degree(G, s=0.3):
    """Local Degree backbone (Hamann et al. 2016).

    Convenience wrapper: degree scoring, rank normalisation, degree
    filtering.  Best for preserving hub-and-spoke structure.

    Parameters
    ----------
    G : nx.Graph
    s : float
        Sparsification exponent.

    Returns
    -------
    H : nx.Graph

    References
    ----------
    .. [1] Hamann, M., Lindner, G., Meyerhenke, H., Staudt, C. L., &
       Wagner, D. (2016). Structure-preserving sparsification methods for
       social networks. *Social Network Analysis and Mining*, 6(1), 22.
    """
    return sparsify(G, escore="degree", normalize="rank", filter="degree", s=s)


# =====================================================================
# Internal helpers
# =====================================================================

def _score_edges(G, method):
    """Compute edge scores.  Returns dict {(min(u,v), max(u,v)): score}."""
    scores = {}

    if method == "jaccard":
        for u, v in G.edges():
            nu = set(G.neighbors(u))
            nv = set(G.neighbors(v))
            inter = len(nu & nv)
            union = len(nu | nv)
            sc = inter / union if union > 0 else 0.0
            scores[(min(u, v), max(u, v))] = sc

    elif method == "degree":
        # Score = degree of the neighbour (from each endpoint, take max)
        deg = dict(G.degree())
        for u, v in G.edges():
            scores[(min(u, v), max(u, v))] = max(deg[u], deg[v])

    elif method == "triangles":
        for u, v in G.edges():
            nu = set(G.neighbors(u))
            nv = set(G.neighbors(v))
            scores[(min(u, v), max(u, v))] = len(nu & nv)

    elif method == "quadrangles":
        for u, v in G.edges():
            nu = set(G.neighbors(u)) - {v}
            nv = set(G.neighbors(v)) - {u}
            # Count 4-cycles: paths u-x-...-y-v where x!=v, y!=u
            count = 0
            for x in nu:
                nx_nbrs = set(G.neighbors(x)) - {u}
                count += len(nx_nbrs & nv)
            scores[(min(u, v), max(u, v))] = count

    elif method == "random":
        rng = np.random.default_rng(42)
        for u, v in G.edges():
            scores[(min(u, v), max(u, v))] = rng.random()

    else:
        raise ValueError(f"Unknown edge scoring method: {method!r}")

    return scores


def _rank_normalise(G, scores):
    """Rank-normalise scores within each node's neighbourhood."""
    normalised = {}

    for u in G.nodes():
        # Get all edges incident to u with their scores
        edge_scores = []
        for v in G.neighbors(u):
            key = (min(u, v), max(u, v))
            edge_scores.append((key, scores.get(key, 0)))

        if not edge_scores:
            continue

        # Sort by score ascending, assign ranks
        edge_scores.sort(key=lambda x: x[1])
        n = len(edge_scores)
        for rank, (key, _) in enumerate(edge_scores):
            rank_val = (rank + 1) / n  # normalised rank in (0, 1]
            # Take the max rank across both endpoints
            if key in normalised:
                normalised[key] = max(normalised[key], rank_val)
            else:
                normalised[key] = rank_val

    return normalised


def _degree_filter(G, scores, s):
    """Keep ceil(d^s) top-scored edges per node (OR semantics)."""
    kept = set()

    for u in G.nodes():
        d = G.degree(u)
        if d == 0:
            continue
        n_keep = max(1, math.ceil(d ** s))

        # Get edges with scores
        edge_scores = []
        for v in G.neighbors(u):
            key = (min(u, v), max(u, v))
            edge_scores.append((scores.get(key, 0), key))

        # Keep top n_keep
        edge_scores.sort(reverse=True)
        for _, key in edge_scores[:n_keep]:
            kept.add(key)

    return kept
