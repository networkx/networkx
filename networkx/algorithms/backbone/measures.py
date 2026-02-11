"""Evaluation measures for comparing backbones against their original network."""

import numpy as np
from scipy import stats as sp_stats

import networkx as nx

__all__ = [
    "node_fraction",
    "edge_fraction",
    "weight_fraction",
    "reachability",
    "ks_degree",
    "ks_weight",
    "compare_backbones",
]


@nx._dispatchable
def node_fraction(original, backbone):
    """Compute the fraction of original nodes that appear in the backbone.

    Only nodes that have at least one edge in the respective graph are
    counted.  Isolated nodes are ignored.

    Parameters
    ----------
    original : graph
        The original NetworkX graph.
    backbone : graph
        The backbone NetworkX graph.

    Returns
    -------
    fraction : float
        Fraction in [0, 1].  Returns 0.0 if *original* has no nodes
        with edges.

    See Also
    --------
    edge_fraction : Fraction of edges preserved.
    weight_fraction : Fraction of total weight preserved.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import node_fraction
    >>> G = nx.path_graph(4)
    >>> H = nx.path_graph(3)
    >>> node_fraction(G, H)
    0.75
    """
    bb_nodes_with_edges = {n for n in backbone.nodes() if backbone.degree(n) > 0}
    orig_nodes_with_edges = {n for n in original.nodes() if original.degree(n) > 0}
    if len(orig_nodes_with_edges) == 0:
        return 0.0
    return len(bb_nodes_with_edges) / len(orig_nodes_with_edges)


@nx._dispatchable
def edge_fraction(original, backbone):
    """Compute the fraction of original edges preserved in the backbone.

    Parameters
    ----------
    original : graph
        The original NetworkX graph.
    backbone : graph
        The backbone NetworkX graph.

    Returns
    -------
    fraction : float
        Fraction in [0, 1].  Returns 0.0 if *original* has no edges.

    See Also
    --------
    node_fraction : Fraction of nodes preserved.
    weight_fraction : Fraction of total weight preserved.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import edge_fraction
    >>> G = nx.complete_graph(4)
    >>> H = nx.path_graph(4)
    >>> edge_fraction(G, H)
    0.5
    """
    if original.number_of_edges() == 0:
        return 0.0
    return backbone.number_of_edges() / original.number_of_edges()


@nx._dispatchable(edge_attrs="weight")
def weight_fraction(original, backbone, weight="weight"):
    """Compute the fraction of total edge weight preserved in the backbone.

    Parameters
    ----------
    original : graph
        The original NetworkX graph.
    backbone : graph
        The backbone NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.

    Returns
    -------
    fraction : float
        Fraction in [0, 1].  Returns 0.0 if *original* has zero total
        weight.

    See Also
    --------
    node_fraction : Fraction of nodes preserved.
    edge_fraction : Fraction of edges preserved.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import weight_fraction
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 2.0)])
    >>> H = nx.Graph()
    >>> H.add_weighted_edges_from([(0, 1, 3.0)])
    >>> weight_fraction(G, H)
    0.5
    """
    total_orig = sum(d.get(weight, 0) for _, _, d in original.edges(data=True))
    if total_orig == 0:
        return 0.0
    total_bb = sum(d.get(weight, 0) for _, _, d in backbone.edges(data=True))
    return total_bb / total_orig


@nx._dispatchable
def reachability(G):
    """Compute the fraction of node pairs that can communicate.

    For a connected graph this is 1.0.  For a graph with all isolated
    nodes this is 0.0.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    Returns
    -------
    fraction : float
        Fraction in [0, 1] of ordered node pairs *(i, j)* for which a
        path exists.

    See Also
    --------
    node_fraction : Fraction of nodes preserved.
    edge_fraction : Fraction of edges preserved.

    Notes
    -----
    Uses the formula ``R = (1 / (n*(n-1))) * sum_{i!=j} R_ij`` where
    ``R_ij = 1`` if a path exists between *i* and *j*.  For directed
    graphs, weakly connected components are used.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import reachability
    >>> G = nx.path_graph(4)
    >>> reachability(G)
    1.0
    >>> G = nx.Graph()
    >>> G.add_nodes_from([0, 1, 2])
    >>> reachability(G)
    0.0
    """
    n = G.number_of_nodes()
    if n <= 1:
        return 1.0
    total_pairs = n * (n - 1)

    if G.is_directed():
        components = nx.weakly_connected_components(G)
    else:
        components = nx.connected_components(G)

    reachable = 0
    for comp in components:
        c = len(comp)
        reachable += c * (c - 1)

    return reachable / total_pairs


@nx._dispatchable
def ks_degree(original, backbone):
    """Compute the Kolmogorov-Smirnov statistic between degree distributions.

    Measures how different the backbone's degree distribution is from
    the original's.  A value of 0 means identical distributions; 1 means
    maximally different.

    Parameters
    ----------
    original : graph
        The original NetworkX graph.
    backbone : graph
        The backbone NetworkX graph.

    Returns
    -------
    statistic : float
        KS statistic in [0, 1].

    See Also
    --------
    ks_weight : KS statistic between weight distributions.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import ks_degree
    >>> G = nx.complete_graph(5)
    >>> ks_degree(G, G)
    0.0
    """
    orig_deg = np.array([d for _, d in original.degree()])
    bb_deg = np.array([d for _, d in backbone.degree()])
    if len(orig_deg) == 0 or len(bb_deg) == 0:
        return 1.0
    stat, _ = sp_stats.ks_2samp(orig_deg, bb_deg)
    return float(stat)


@nx._dispatchable(edge_attrs="weight")
def ks_weight(original, backbone, weight="weight"):
    """Compute the Kolmogorov-Smirnov statistic between weight distributions.

    Parameters
    ----------
    original : graph
        The original NetworkX graph.
    backbone : graph
        The backbone NetworkX graph.
    weight : string, optional (default="weight")
        Edge attribute key used as the weight.

    Returns
    -------
    statistic : float
        KS statistic in [0, 1].

    See Also
    --------
    ks_degree : KS statistic between degree distributions.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import ks_weight
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 2.0)])
    >>> ks_weight(G, G)
    0.0
    """
    orig_w = np.array([d.get(weight, 0) for _, _, d in original.edges(data=True)])
    bb_w = np.array([d.get(weight, 0) for _, _, d in backbone.edges(data=True)])
    if len(orig_w) == 0 or len(bb_w) == 0:
        return 1.0
    stat, _ = sp_stats.ks_2samp(orig_w, bb_w)
    return float(stat)


def compare_backbones(original, backbones, measures=None, weight="weight"):
    """Compare multiple backbones on a set of evaluation measures.

    Parameters
    ----------
    original : graph
        The original NetworkX graph.
    backbones : dict
        Mapping ``{name: backbone_graph}``.
    measures : list of callable, optional
        Each callable has signature ``(original, backbone)`` and returns a
        float.  Defaults to ``[node_fraction, edge_fraction,
        weight_fraction]``.
    weight : string, optional (default="weight")
        Weight attribute (forwarded to :func:`weight_fraction`).

    Returns
    -------
    results : dict
        ``{backbone_name: {measure_name: value}}``.

    See Also
    --------
    node_fraction : Fraction of nodes preserved.
    edge_fraction : Fraction of edges preserved.
    weight_fraction : Fraction of total weight preserved.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.backbone import (
    ...     compare_backbones,
    ...     node_fraction,
    ...     edge_fraction,
    ... )
    >>> G = nx.complete_graph(5)
    >>> H = nx.path_graph(5)
    >>> results = compare_backbones(G, {"path": H}, measures=[edge_fraction])
    >>> "edge_fraction" in results["path"]
    True
    """
    if measures is None:
        measures = [node_fraction, edge_fraction, weight_fraction]

    results = {}
    for name, bb in backbones.items():
        results[name] = {}
        for m in measures:
            # weight_fraction needs extra arg
            if m is weight_fraction:
                results[name][m.__name__] = m(original, bb, weight=weight)
            else:
                results[name][m.__name__] = m(original, bb)
    return results
