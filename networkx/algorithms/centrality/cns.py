# -*- coding: utf-8 -*-
#
# cns.py - cumulative nomination scheme centrality
#
# Copyright 2009 "dheerajrav".
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for computing the cumulative nomination scheme centrality.

"""
from __future__ import division

from itertools import chain

import numpy as np

import networkx as nx
from networkx.utils import not_implemented_for


__all__ = ['cns_centrality']

chaini = chain.from_iterable


def growthrate(G, tol):
    """Returns the growth rate of the power iteration method on the
    graph.

    The *growth rate* is the ratio `x_i^t / x_i^{t - 1}` for each
    component `x_i` in the vector `x` computing the dominant
    eigenvector.

    """
    A = nx.adjacency_matrix(G) + np.eye(len(G))
    prev_vector = np.array([-float('inf') for v in G])
    vector = A * np.mat(np.ones(len(G))).T
    prev_rate = np.array([-float('inf') for v in G])
    rate = vector / np.ones(len(G))
    while np.amax(rate - prev_rate) > tol:
        prev_rate = rate
        prev_vector = vector
        vector = A * vector
        rate = vector / prev_vector
    return {v: r[0] for v, r in zip(G, rate)}


def cns_centrality_connected(G, tol):
    """Returns a dictionary mapping each node in ``G`` to its CNS centrality.

    ``G`` must be a connected undirected graph.

    """
    A = nx.adjacency_matrix(G) + np.eye(len(G))
    # The popularity index matrix is initialized to one.
    prev_vector = np.array([-float('inf') for v in G])
    vector = A * np.mat(np.ones(len(G))).T
    # Normalise the column vector so it has the first order popularity index.
    vector /= sum(vector)
    # Compute the next approximation of the vector via the power
    # iteration method. Continue while the l0 distance between the
    # vectors is still large enough.
    while np.amax(vector - prev_vector) > tol:
        prev_vector = vector
        vector = A * vector
        vector /= sum(vector)
    n = G.number_of_nodes()
    return {v: value[0] * n for v, value in zip(G, vector)}


def cns_centrality_disconnected(G, components, tol):
    """Returns a dictionary mapping each node in ``G`` to its CNS centrality.

    ``G`` may be a disconnected graph. ``components`` must be an
    iterable of the connected component subgraphs of ``G``, as
    computed by ``nx.connected_component_subgraphs(G)``.

    """
    centralities = {H: cns_centrality_connected(H, tol) for H in components}
    cns = dict(chaini(c.items() for c in centralities.values()))
    sizes = dict(chaini(((v, len(H) / len(G)) for v in H)
                        for H in centralities))
    # The entire graph G is used to compute the growth rate.
    growth = growthrate(G, tol)
    return {v: cns[v] * growth[v] * sizes[v] for v in G}


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def cns_centrality(G, tol=1e-6):
    """Computes cumulative nomination scheme centrality of a graph.

    The *cumulative nomination scheme centrality* of a node is defined
    in [1].

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    tol : float
        Error tolerance used to check convergence in power iteration
        method.

    Returns
    -------
    dictionary
        Dictionary mapping each node to its cumulative nomination scheme
        centrality.

    References
    ----------
    .. [1] Poulin, Robert, M-C. Boily, and Benoît R. Mâsse.
           "Dynamical systems to define centrality in social networks."
           Social networks 22.3 (2000): 187--220.
           <http://dx.doi.org/10.1016/S0378-8733(00)00020-4>

    """
    components = list(nx.connected_component_subgraphs(G))
    if len(components) <= 1:
        return cns_centrality_connected(G, tol)
    return cns_centrality_disconnected(G, components, tol)
