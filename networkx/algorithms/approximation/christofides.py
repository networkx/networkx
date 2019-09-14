# -*- coding: utf-8 -*-
# Copyright (C) 2019 by
#   Luca Cappelletti <luca.cappelletti@studenti.unimi.it>
#
# All rights reserved.
# BSD license.
"""Functions for computing a 3/2-approximation of TSP using Christofides algorithm."""
import networkx as nx

__all__ = ["christofides"]

def shortcutting(circuit):
    nodes = []
    for u, v in circuit:
        if v in nodes:
            continue
        yield (v, nodes[-1] if nodes else u)
        if not nodes:
            nodes.append(u)
        nodes.append(v)
    yield(nodes[0], nodes[-1])

def christofides(G, weight='weight', algorithm='kruskal'):
    """Compute a 3/2-approximation of TSP in given graph using Christofides [1] algorithm.

    Parameters
    ----------
    G : NetworkX graph
      Undirected complete graph

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight.
       If key not found, uses 1 as weight.

    algorithm : string
       The algorithm to use when finding a minimum spanning tree. Valid
       choices are 'kruskal', 'prim', or 'boruvka'. The default is
       'kruskal'.

    Returns
    -------
    Generator of list of edges forming a 3/2-approximation of the minimal
    Hamiltonian cycle.

    References
    ----------
    .. [1] Christofides, Nicos. "Worst-case analysis of a new heuristic for 
    the travelling salesman problem." No. RR-388. Carnegie-Mellon Univ
    Pittsburgh Pa Management Sciences Research Group, 1976.
    """
    if not G.is_complete():
        raise ValueError("Christofides algorithm works only for complete graph.")
    T = nx.minimum_spanning_tree(G, weight=weight, algorithm=algorithm)
    L = nx.Graph(G)
    L.remove_nodes_from([v for v, degree in T.degree if not (degree % 2)])
    MG = nx.MultiGraph()
    MG.add_edges_from(T.edges)
    MG.add_edges_from(nx.min_weight_matching(L, maxcardinality=True, weight=weight))
    return shortcutting(nx.eulerian_circuit(MG))