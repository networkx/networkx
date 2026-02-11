"""
Evaluation measures for comparing backbones against their original network.
"""

import networkx as nx
import numpy as np
from scipy import stats as sp_stats

__all__ = [
    "node_fraction",
    "edge_fraction",
    "weight_fraction",
    "reachability",
    "ks_degree",
    "ks_weight",
    "compare_backbones",
]


def node_fraction(original, backbone):
    """Fraction of original nodes that appear in the backbone (with edges)."""
    bb_nodes_with_edges = {n for n in backbone.nodes() if backbone.degree(n) > 0}
    orig_nodes_with_edges = {n for n in original.nodes() if original.degree(n) > 0}
    if len(orig_nodes_with_edges) == 0:
        return 0.0
    return len(bb_nodes_with_edges) / len(orig_nodes_with_edges)


def edge_fraction(original, backbone):
    """Fraction of original edges preserved in the backbone."""
    if original.number_of_edges() == 0:
        return 0.0
    return backbone.number_of_edges() / original.number_of_edges()


def weight_fraction(original, backbone, weight="weight"):
    """Fraction of total edge weight preserved in the backbone."""
    total_orig = sum(d.get(weight, 0) for _, _, d in original.edges(data=True))
    if total_orig == 0:
        return 0.0
    total_bb = sum(d.get(weight, 0) for _, _, d in backbone.edges(data=True))
    return total_bb / total_orig


def reachability(G):
    """Fraction of node pairs that can communicate (are in the same component).

    For a connected graph this is 1.0.  For a graph with all isolated
    nodes this is 0.0.

    Uses the formula R = (1 / n(n-1)) * sum_{i!=j} R_ij where R_ij = 1
    if a path exists between i and j.
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


def ks_degree(original, backbone):
    """Kolmogorov-Smirnov statistic between degree distributions.

    Measures how different the backbone's degree distribution is from
    the original's.  A value of 0 means identical distributions; 1 means
    maximally different.

    Parameters
    ----------
    original : nx.Graph or nx.DiGraph
    backbone : nx.Graph or nx.DiGraph

    Returns
    -------
    float
        KS statistic in [0, 1].
    """
    orig_deg = np.array([d for _, d in original.degree()])
    bb_deg = np.array([d for _, d in backbone.degree()])
    if len(orig_deg) == 0 or len(bb_deg) == 0:
        return 1.0
    stat, _ = sp_stats.ks_2samp(orig_deg, bb_deg)
    return float(stat)


def ks_weight(original, backbone, weight="weight"):
    """Kolmogorov-Smirnov statistic between edge weight distributions.

    Parameters
    ----------
    original : nx.Graph or nx.DiGraph
    backbone : nx.Graph or nx.DiGraph
    weight : str

    Returns
    -------
    float
        KS statistic in [0, 1].
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
    original : nx.Graph or nx.DiGraph
        The original network.
    backbones : dict
        Mapping ``{name: backbone_graph}``.
    measures : list of callables, optional
        Each callable has signature ``(original, backbone)`` and returns a
        float.  Defaults to ``[node_fraction, edge_fraction, weight_fraction]``.
    weight : str
        Weight attribute (forwarded to weight_fraction).

    Returns
    -------
    dict
        ``{backbone_name: {measure_name: value}}``.
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
