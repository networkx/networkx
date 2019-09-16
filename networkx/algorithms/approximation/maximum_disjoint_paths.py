# -*- coding: utf-8 -*-
# Copyright (C) 2019 by
#   Luca Cappelletti <luca.cappelletti@studenti.unimi.it>
#
# All rights reserved.
# BSD license.
r"""Functions for computing a $(2\sqrt{m}+1)$-approximation of Maximum Disjoint Paths."""

import networkx as nx

__all__ = ["maximum_disjoint_paths"]


def nodes_to_path(nodes):
    """Return generator yielding path passing through given nodes."""
    start = nodes[0]
    for u in nodes[1:]:
        yield (start, u)
        start = u


def maximum_disjoint_paths(G, requests, weight="weight"):
    r"""Return triple with the obtained paths, the satisfied requests and the unsatisfied requests.
    
    The algorithm returns a a $(2\sqrt{m}+1)$-approximation of the optimal maximum disjoint paths,
    where $m$ is the number of edges in the graph.

    Parameters
    ----------
    G : NetworkX graph
      Undirected complete graph

    requests : list of tuples (source, sink)
        List of requests to be satisfied.

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight.
       If key not found, uses 1 as weight.

    Returns
    -------
    Triple with the obtained paths, the satisfied requests and the unsatisfied requests.
    """
    C = nx.Graph(G)
    paths, satisfied, unsatisfied = [], [], []
    for e in requests:
        try:
            paths.append(list(nodes_to_path(nx.shortest_path(
                C,
                *e,
                weight=weight
            ))))
            C.remove_edges_from(paths[-1])
            satisfied.append(e)
        except nx.NodeNotFound:
            unsatisfied.append(e)
    return paths, satisfied, unsatisfied
