# -*- coding: utf-8 -*-
# Copyright (C) 2019 by
#   Luca Cappelletti <luca.cappelletti@studenti.unimi.it>
#
# All rights reserved.
# BSD license.
"""Functions for computing a 2-approximation of Center Selection."""

import networkx as nx
import random
from math import inf

__all__ = ["center_selection"]


def center_selection(G, k, weight='weight'):
    """Return a tuple with the max radius and the selected centers.

    In graph theory, the metric k-center or metric facility location
    problem is a combinatorial optimization problem: given $n$ cities
    with specified distances, one wants to build $k$ warehouses
    in different cities and minimize the maximum distance of a city
    to a warehouse. In graph theory this means finding a set of $k$
    vertices for which the largest distance of any point to its
    closest vertex in the k-set is minimum. The vertices must be in
    a metric space, providing a complete graph that satisfies the triangle inequality.

    The proposed algorithm is a 2-approximation, meaning it achieves
    a solution with a factor 2 of the optimal one.

    Parameters
    ----------
    G : NetworkX graph
      Undirected complete graph

    k : int
        Number of centers to be selected.

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight.
       If key not found, uses 1 as weight.

    Returns
    -------
    Tuple with the max radius and the selected centers.

    Raises
    ------
    NetworkXError
        If the graph is not complete.

    NetworkXError
        If the number of centers is not a strictly positive integer.

    NetworkXError
        If the graph weights are not positive.

    NetworkXError
        If the number of centers is more than available nodes.

    """
    if not G.is_complete():
        raise nx.NetworkXError("Graph must be complete.")
    if k < 1 or not isinstance(k, int):
        raise nx.NetworkXError(
            "Number of centers is not a strictly positive integer.")
    if k > len(G):
        raise nx.NetworkXError(
            "Number of centers is more than available nodes.")
    if any([(w[weight] if weight in w else 1) < 0 for _, _, w in G.edges(data=True)]):
        raise nx.NetworkXError("Graph weights are not positive.")
    centers = [random.choice(list(G.nodes))]
    max_radius = inf
    for _ in range(1, k):
        radius, center = max([
            ((w[weight] if weight in w else 1), v)
            for _, v, w in G.edges(centers[-1], data=True)
            if v not in centers
        ])
        max_radius = min(radius, max_radius)
        centers.append(center)
    return max_radius, centers
