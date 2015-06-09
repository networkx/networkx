# -*- coding: utf-8 -*-
#    Copyright (C) 2015
#    All rights reserved.
#    BSD license.

import random
import networkx as nx
from itertools import groupby
from collections import defaultdict


def asyn_lpa_communities(G, weight=None):
    """
    Asynchronous label propagation algorithm for community detection described
    on [1]_. The algorithm is non-deterministic and the found communities may
    vary on different executions.

    The algorithm follows these steps:

        1. Initialize the labels at all nodes in the network giving them unique
        identifiers.
        2. Set t=1.
        3. Arrange the nodes in the network in a random order and set it to X.
        4. For each x in X chosen in that specific order, get the label
        occurring with the highest frecuency among neighbors. Ties are broken
        uniformly randomly.
        5. If every node has a label that the maximun number of their neighbors
        have, then stop the algorithm. Else set t = t+1 and got to (3).

    Modified to be able to take into account the edge weights when assigning
    the labels to one node.

    Parameters
    ----------
    G : graph
        Network to be processed

    weight : string
        If the graph is weighted, the edge parameter representing the weight.
        If left to None edge weights are not taken into account.

    Returns
    -------
    communities : list
        List of communities (sets)

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
        nodes = nx.nodes(G)
        random.shuffle(nodes)
        # Calculate the label for each node
        for node in nodes:
            n_neighbors = G.neighbors(node)

            if len(n_neighbors) < 1:
                continue

            # Get label frequencies. Depending on the order they are processed
            # in some nodes with be in t and others in t-1, making the
            # algorithm asynchronous.
            label_freq = defaultdict(lambda: 0)
            for neighbor in n_neighbors:
                n_label = labels[neighbor]
                label_freq[n_label] += G.edge[neighbor][node][weight] if weight else 1

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
   
    return (set(v) for k, v in groupby(sorted(labels, key=labels.get), key=labels.get)) 
