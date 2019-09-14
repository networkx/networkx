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
    processes = cpu_count()
    n = ceil(karger_iterations(G) / processes)
    with Pool(processes) as p:
        scores, groups = zip(*list(
            p.imap(_karger, zip([G]*processes, [weight]*processes, [n]*processes,))
        ))
    min_score = min(scores)
    return min_score, groups[scores.index(min_score)]
