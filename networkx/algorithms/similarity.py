# -*- coding: utf-8 -*-
import math
import networkx as nx

__author__ = 'Andrey Paramonov <paramon@acdlabs.ru>'

__all__ = [
    'graph_edit_distance'
]

def graph_edit_distance(G1, G2, node_match=None, edge_match=None):
    """Returns GED (graph edit distance) between graphs G1 and G2.

    Parameters
    ----------
    G1, G2: graphs
        The two graphs G1 and G2 must be the same type.

    node_match : callable
        A function that returns True if node n1 in G1 and n2 in G2 should
        be considered equal during matching.
        If node_match is not specified then node attributes are not considered.

        The function will be called like

           node_match(G1.nodes[n1], G2.nodes[n2]).

        That is, the function will receive the node attribute dictionaries
        for n1 and n2 as inputs.

    edge_match : callable
        A function that returns True if the edge attribute dictionary
        for the pair of nodes (u1, v1) in G1 and (u2, v2) in G2 should
        be considered equal during matching.  If edge_match is not specified
        then edge attributes are not considered.

        The function will be called like

           edge_match(G1[u1][v1], G2[u2][v2]).

        That is, the function will receive the edge attribute dictionaries
        of the edges under consideration.

    TODO:
    Examples
    See Also

    References
    ----------
    .. [1] Zeina Abu-Aisheh, Romain Raveaux, Jean-Yves Ramel, Patrick
       Martineau. An Exact Graph Edit Distance Algorithm for Solving
       Pattern Recognition Problems. 4th International Conference on
       Pattern Recognition Applications and Methods 2015, Jan 2015,
       Lisbon, Portugal. 2015,
       <10.5220/0005209202710278>. <hal-01168816>
       https://hal.archives-ouvertes.fr/hal-01168816
"""
    # TODO: support DiGraph

    import numpy as np
    from scipy.optimize import linear_sum_assignment

    if len(G1.nodes) < len(G2.nodes):
        (G1, G2) = (G2, G1)

    def edge(g):
        return tuple(sorted(g))

    # cost of vertex mappings
    cv = dict()
    for u, uattr in G1.nodes(data=True):
        for v, vattr in G2.nodes(data=True):
            cv[(u, v)] = 1 - int(node_match(uattr, vattr)) if node_match else 0
        cv[(u, None)] = 1
    for v in G2.nodes:
        cv[(v, None)] = 1

    # cost of edge mappings
    ce = dict()
    for u, v, uvattr in G1.edges(data=True):
        for p, q, pqattr in G2.edges(data=True):
            ce[(edge((u, v)), edge((p, q)))] = 1 - int(edge_match(uvattr, pqattr)) if edge_match else 0
        ce[(edge((u, v)), None)] = 1
    for p, q in G2.edges:
        ce[(edge((p, q)), None)] = 1

    # initial upper-bound estimate
    # NOTE: should work for empty graph
    maxcost = len(G1.nodes) + len(G2.nodes) + len(G1.edges) + len(G2.edges)

    def update(startpath, startcost, u, v):
        """
        Parameters:
            startpath: partial edit path
                list of tuples (p, q) of vertex mappings p<->q,
                p=None or q=None means insertion/deletion
            startcost: cost value of startpath

        Returns:
            tuple (path, cost)
                path: updated edit path
                cost: cost value of path
        """
        pass

    def getcost(startpath, u, v):
        c = 0
        for p, q in startpath:
            if not p is None and u in G1[p]:
                g = edge((u, p))
            else:
                g = None
            if not q is None and v in G2[q]:
                h = edge((v, q))
            else:
                h = None
            if not g is None:
                c += ce[(g, h)]
            elif not h is None:
                c += ce[(h, g)]
        return c + cv[(u, v)]

    def lb(startpath):
        ignore_u = set(p for p, q in startpath)
        ignore_v = set(q for p, q in startpath)
        pending_u = [u for u in G1.nodes if u not in ignore_u]
        pending_v = [v for v in G2.nodes if v not in ignore_v]
        m = len(pending_u)
        n = len(pending_v)

        Cv = np.zeros((m + n, m + n))
        Cv[0:m, 0:n] = np.array([cv[(u, v)] + abs(len(G1.edges(u)) - len(G2.edges(v)))
                                 for u in pending_u for v in pending_v]).reshape(m, n)
        Cv[0:m, n:n+m] = np.array([1 + len(G1.edges(pending_u[i])) if i == j else maxcost + 1
                                   for i in range(m) for j in range(m)]).reshape(m, m)
        Cv[m:m+n, 0:n] = np.array([1 + len(G2.edges(pending_v[j])) if i == j else maxcost + 1
                                   for i in range(n) for j in range(n)]).reshape(n, n)

        row_ind, col_ind = linear_sum_assignment(Cv)
        return Cv[row_ind, col_ind].sum()

    def candidate_mappings(startpath):
        """
        Parameters:
            startpath: partial edit path
                list of tuples (p, q) of vertex mappings p<->q,
                p=None or q=None means insertion/deletion

        Returns:
            sequence of (u, v, cost) sorted by cost *estimate*
                u, v: vertices, u=None or v=None means insertion/deletion
                cost: cost value of u<->v mapping
        """
        ignore_u = set(p for p, q in startpath)
        ignore_v = set(q for p, q in startpath)
        pending_u = [u for u in G1.nodes if u not in ignore_u]
        pending_v = [v for v in G2.nodes if v not in ignore_v]
        u = pending_u[0]
        for v in sorted(pending_v + [None], key = lambda v: getcost(startpath, u, v) + lb(startpath + [(u, v)])):
            yield u, v, getcost(startpath, u, v)

    def process(startpath, startcost, maxcost):
        """
        Parameters:
            startpath: partial edit path
                list of tuples (u, v) of vertex mappings u<->v,
                u=None or v=None means insertion/deletion
            startcost: cost value of startpath
            maxcost: max cost of complete edit path to return

        Returns:
            sequence of (path, cost)
                path: complete edit path
                    list of tuples (u, v) of vertex mappings u<->v,
                    u=None or v=None means insertion/deletion
                cost: cost value of path
        """
        if startcost > maxcost:
            # prune
            return

        if len(startpath) < len(G1):
            for u, v, c in candidate_mappings(startpath):
                for path, cost in process(startpath + [(u, v)], startcost + c, maxcost):
                    if cost < maxcost:
                        # update immediately
                        maxcost = cost
                    if cost <= maxcost:
                        yield path, cost
        else:
            yield startpath, startcost

    return min(cost for path, cost in process([], 0, maxcost))
