# -*- coding: utf-8 -*-
# Copyright (C) 2019 by
#   Luca Cappelletti <luca.cappelletti@studenti.unimi.it>
#
# All rights reserved.
# BSD license.
"""Functions for computing probabilistically min cut using Karger algorithm."""
import networkx as nx
from math import ceil, log, factorial, inf
from multiprocessing import Pool, cpu_count
import random

__all__ = ["karger", "parallel_karger"]


def binomial(x, y):
    try:
        binom = factorial(x) // factorial(y) // factorial(x - y)
    except ValueError:
        binom = 0
    return binom


def _score(G, A, B, weight):
    return sum([
        (w[weight] if weight in w else 1) for u, v, w in G.edges(data=True)
        if (u in A and v in B) or (v in A and u in B)
    ])


def _get_key(key, groups):
    if key in groups:
        return key
    for g in groups:
        if key in groups[g]:
            return g


def karger_iterations(G):
    n = len(G)
    return ceil(binomial(n, 2)*log(n))


def karger(G, weight='weight', iterations=None):
    """Returns the weighted minimum edge cut using the Karger algorithm [1]_.

    Karger's algorithm is a randomized algorithm to compute a minimum
    cut of a connected graph. By iterating this basic algorithm a
    sufficient number of times, a minimum cut can be found with high
    probability. In weighted cases, all weights must be nonnegative.

    The algorithm is generally slower than the Stoer-Wagner algorithm,
    but it can be parallelized in an easier way.

    Parameters
    ----------
    G : NetworkX graph
        Edges of the graph are expected to have an attribute named by the
        weight parameter below. If this attribute is not present, the edge is
        considered to have unit weight.

    weight : string
        Name of the weight attribute of the edges. If the attribute is not
        present, unit weight is assumed. Default value: 'weight'.

    iterations : int
        Number of iterations to run. By default, the number is identyfied by running
        the function `karger_iterations`.

    Returns
    -------
    cut_value : integer or float
        The sum of weights of edges in a minimum cut.

    partition : pair of node lists
        A partitioning of the nodes that defines a minimum cut.
    
    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or a multigraph.

    NetworkXError
        If the graph has less than two nodes, is not connected or has a
        negative-weighted edge.

    References
    ----------
    .. [1] Karger, David R. "Global Min-cuts in RNC, and Other
    Ramifications of a Simple Min-Cut Algorithm." SODA. Vol. 93. 1993.
    """
    n = len(G)
    if n < 2:
        raise nx.NetworkXError('Graph has less than two nodes.')
    if not nx.is_connected(G):
        raise nx.NetworkXError('Graph is not connected.')
    if iterations is None:
        iterations = karger_iterations(G)
    min_score = inf
    min_cut = None
    for _ in range(iterations):
        groups = {u: [u] for u in G.nodes}
        while len(groups) > 2:
            u, v = random.choice([
                (u, v) for u, v in G.edges if (
                    u in groups and v not in groups[u]
                ) or (
                    v in groups and u not in groups[v]
                )
            ])
            u = _get_key(u, groups)
            v = _get_key(v, groups)
            groups[u] += groups.pop(v)
        score = _score(G, *groups.values(), weight)
        if min_score > score:
            min_score = score
            min_cut = groups
    return min_score, list(min_cut.values())


def _karger(task):
    return karger(*task)


def parallel_karger(G, weight='weight'):
    """Returns the weighted minimum edge cut using the parallel Karger [1]_ algorithm.

    Karger's algorithm is a randomized algorithm to compute a minimum
    cut of a connected graph. By iterating this basic algorithm a
    sufficient number of times, a minimum cut can be found with high
    probability. In weighted cases, all weights must be nonnegative.

    The algorithm is generally slower than the Stoer-Wagner algorithm,
    but it can be parallelized in an easier way.

    The algorithm parallilezes across all available cores.

    Parameters
    ----------
    G : NetworkX graph
        Edges of the graph are expected to have an attribute named by the
        weight parameter below. If this attribute is not present, the edge is
        considered to have unit weight.

    weight : string
        Name of the weight attribute of the edges. If the attribute is not
        present, unit weight is assumed. Default value: 'weight'.

    Returns
    -------
    cut_value : integer or float
        The sum of weights of edges in a minimum cut.

    partition : pair of node lists
        A partitioning of the nodes that defines a minimum cut.

    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or a multigraph.

    NetworkXError
        If the graph has less than two nodes, is not connected or has a
        negative-weighted edge.

    References
    ----------
    .. [1] Karger, David R. "Global Min-cuts in RNC, and Other
    Ramifications of a Simple Min-Cut Algorithm." SODA. Vol. 93. 1993.
    """
    n = len(G)
    if n < 2:
        raise nx.NetworkXError('Graph has less than two nodes.')
    if not nx.is_connected(G):
        raise nx.NetworkXError('Graph is not connected.')
    processes = cpu_count()
    n = ceil(karger_iterations(G) / processes)
    with Pool(processes) as p:
        scores, groups = zip(*list(
            p.imap(_karger, zip([G]*processes, [weight]*processes, [n]*processes,))
        ))
    min_score = min(scores)
    return min_score, groups[scores.index(min_score)]
