# -*- coding: utf-8 -*-
#    Copyright (C) 2015
#    All rights reserved.
#    BSD license.
"""Asynchronous label propagation algorithms for community detection."""

from collections import Counter
import random

from networkx.utils import groups

__all__ = ['asyn_lpa_communities']


def asyn_lpa_communities(G, weight=None):
    """Returns communities in `G` as detected by asynchronous label
    propagation.

    The asynchronous label propagation algorithm is described in
    [1]_. The algorithm is probabilistic and the found communities may
    vary on different executions.

    The algorithm proceeds as follows. After initializing each node with
    a unique label, the algorithm repeatedly sets the label of a node to
    be the label that appears most frequently among that nodes
    neighbors. The algorithm halts when each node has the label that
    appears most frequently among its neighbors. The algorithm is
    asynchronous because each node is updated without waiting for
    updates on the remaining nodes.

    This generalized version of the algorithm in [1]_ accepts edge
    weights.

    Parameters
    ----------
    G : Graph

    weight : string
        The edge attribute representing the weight of an edge.
        If None, each edge is assumed to have weight one. In this
        algorithm, the weight of an edge is used in determining the
        frequency with which a label appears among the neighbors of a
        node: a higher weight means the label appears more often.

    Returns
    -------
    communities : iterable
        Iterable of communities given as sets of nodes.

    Notes
    ------
    Edge weight attributes must be numerical.

    References
    ----------
    .. [1] Raghavan, Usha Nandini, Réka Albert, and Soundar Kumara. "Near
           linear time algorithm to detect community structures in large-scale
           networks." Physical Review E 76.3 (2007): 036106.
    """

    labels = {n: i for i, n in enumerate(G)}
    cont = True
    while cont:
        cont = False
        nodes = list(G)
        random.shuffle(nodes)
        # Calculate the label for each node
        for node in nodes:
            if len(G[node]) < 1:
                continue

            # Get label frequencies. Depending on the order they are processed
            # in some nodes with be in t and others in t-1, making the
            # algorithm asynchronous.
            label_freq = Counter()
            for v in G[node]:
                label_freq.update({labels[v]: G.edge[v][node][weight]
                                    if weight else 1})
            # Choose the label with the highest frecuency. If more than 1 label
            # has the highest frecuency choose one randomly.
            max_freq = max(label_freq.values())
            best_labels = [label for label, freq in label_freq.items()
                           if freq == max_freq]
            new_label = random.choice(best_labels)
            labels[node] = new_label
            # Continue until all nodes have a label that is better than other
            # neighbour labels (only one label has max_freq for each node).
            cont = cont or len(best_labels) > 1

    # TODO In Python 3.3 or later, this should be `yield from ...`.
    return iter(groups(labels).values())
