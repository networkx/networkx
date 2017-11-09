# -*- coding: utf-8 -*-
from __future__ import print_function
import math
import networkx as nx
from operator import *

__author__ = 'Andrey Paramonov <paramon@acdlabs.ru>'

__all__ = [
    'graph_edit_distance'
]

def debug_print(*args, **kwargs):
    print(*args, **kwargs)

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

    Examples
    --------
    >>> G1 = cycle_graph(6)
    >>> G2 = wheel_graph(7)
    >>> graph_edit_distance(G1, G2)
    7

    See Also
    --------
    is_isomorphic (test for graph edit distance of 0)

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

    class CostMatrix:
        def __init__(self, C, lsa_row_ind, lsa_col_ind, ls):
            assert C.shape[0] == len(lsa_row_ind)
            assert C.shape[1] == len(lsa_col_ind)
            assert len(lsa_row_ind) == len(lsa_col_ind)
            assert set(lsa_row_ind) == set(range(len(lsa_row_ind)))
            assert set(lsa_col_ind) == set(range(len(lsa_col_ind)))
            assert ls == C[lsa_row_ind, lsa_col_ind].sum()
            self.C = C
            self.lsa_row_ind = lsa_row_ind
            self.lsa_col_ind = lsa_col_ind
            self.ls = ls

    def make_CostMatrix(C):
        lsa_row_ind, lsa_col_ind = linear_sum_assignment(C)
        return CostMatrix(C, lsa_row_ind, lsa_col_ind, C[lsa_row_ind, lsa_col_ind].sum())

    def extract_C(C, i, j, m, n):
        assert(C.shape == (m + n, m + n))
        row_ind = [k in i or k - m in j for k in range(m + n)]
        col_ind = [k in j or k - n in i for k in range(m + n)]
        return C[row_ind,:][:,col_ind]

    def reduce_C(C, i, j, m, n):
        assert(C.shape == (m + n, m + n))
        row_ind = [k not in i and k - m not in j for k in range(m + n)]
        col_ind = [k not in j and k - n not in i for k in range(m + n)]
        return C[row_ind,:][:,col_ind]

    def reduce_ind(ind, i):
        rind = ind[[k not in i for k in ind]]
        for k in set(i):
            rind[rind >= k] -= 1
        return rind

    class MaxCost:
        def __init__(self):
            # initial upper-bound estimate
            # NOTE: should work for empty graph
            self.value = len(G1.nodes) + len(G2.nodes) + len(G1.edges) + len(G2.edges)
    maxcost = MaxCost()
    inf = maxcost.value + 1

    def match_edges(u, v, pending_g, pending_h, Ce, matched_uv=[]):
        """
        Parameters:
            u, v: matched vertices, u=None or v=None for
               deletion/insertion
            pending_g, pending_h: lists of edges not yet mapped
            Ce: CostMatrix of pending edge mappings
            matched_uv: partial vertex edit path
                list of tuples (u, v) of previously matched vertex
                    mappings u<->v, u=None or v=None for
                    deletion/insertion

        Returns:
            list of (i, j): indices of edge mappings g<->h
            localCe: local CostMatrix of edge mappings
                (basically submatrix of Ce at cross of rows i, cols j)
        """
        m = len(pending_g)
        n = len(pending_h)
        assert Ce.C.shape == (m + n, m + n)

        g_ind = list(i for i in range(m)
                     if any(pending_g[i] in ((p, u), (u, p), (u, u))
                            for p, q in matched_uv))
        h_ind = list(j for j in range(n)
                     if any(pending_h[j] in ((q, v), (v, q), (v, v))
                            for p, q in matched_uv))
        C = extract_C(Ce.C, g_ind, h_ind, m, n)

        # forbid structurally invalid matches
        for k, i in zip(range(len(g_ind)), g_ind):
            g = pending_g[i]
            for l, j in zip(range(len(h_ind)), h_ind):
                h = pending_h[j]
                if not any(g in ((p, u), (u, p)) and h in ((q, v), (v, q))
                           or g == (u, u) and h == (v, v)
                           for p, q in matched_uv):
                    C[k, l] = inf

        localCe = make_CostMatrix(C)
        ij = list((g_ind[k] if k < len(g_ind) else m + h_ind[l],
                   h_ind[l] if l < len(h_ind) else n + g_ind[k])
                  for k, l in zip(localCe.lsa_row_ind, localCe.lsa_col_ind)
                  if k < len(g_ind) or l < len(h_ind))

        return ij, localCe

    def get_edit_ops(matched_uv, pending_u, pending_v, Cv,
                     pending_g, pending_h, Ce, matched_cost):
        """
        Parameters:
            matched_uv: partial vertex edit path
                list of tuples (u, v) of vertex mappings u<->v,
                u=None or v=None for deletion/insertion
            pending_u, pending_v: lists of vertices not yet mapped
            Cv: CostMatrix of pending vertex mappings
            pending_g, pending_h: lists of edges not yet mapped
            Ce: CostMatrix of pending edge mappings
            matched_cost: cost of partial edit path

        Returns:
            sequence of
                (i, j): indices of vertex mapping u<->v
                Cv_ij: reduced CostMatrix of pending vertex mappings
                    (basically Cv with row i, col j removed)
                list of (x, y): indices of edge mappings g<->h
                Ce_xy: reduced CostMatrix of pending edge mappings
                    (basically Ce with rows x, cols y removed)
                cost: total cost of edit operation
            NOTE: most promising ops first
        """
        m = len(pending_u)
        n = len(pending_v)
        assert Cv.C.shape == (m + n, m + n)
        assert matched_cost + Cv.ls + Ce.ls <= maxcost.value

        # 1) a vertex mapping from optimal linear sum assignment
        i, j = min((k, l) for k, l in zip(Cv.lsa_row_ind, Cv.lsa_col_ind)
                   if k < m or l < n)
        xy, localCe = match_edges(pending_u[i] if i < m else None, pending_v[j] if j < n else None,
                                  pending_g, pending_h, Ce, matched_uv)
        Ce_xy = make_CostMatrix(reduce_C(Ce.C, [k for k, l in xy], [l for k, l in xy],
                                         len(pending_g), len(pending_h)))
        assert Ce.ls <= localCe.ls + Ce_xy.ls
        if matched_cost + Cv.ls + localCe.ls + Ce_xy.ls < maxcost.value:
            # get reduced Cv efficiently
            Cv_ij = CostMatrix(reduce_C(Cv.C, (i,), (j,), m, n),
                               reduce_ind(Cv.lsa_row_ind, (i, m + j)),
                               reduce_ind(Cv.lsa_col_ind, (j, n + i)),
                               Cv.ls - Cv.C[i, j])
            yield (i, j), Cv_ij, xy, Ce_xy, Cv.C[i, j] + localCe.ls

        # 2) other candidates, sorted by lower-bound cost estimate
        other = list()
        fixed_i, fixed_j = i, j
        if m <= n:
            candidates = ((t, fixed_j) for t in range(m + n)
                          if t != fixed_i and (t < m or t == m + fixed_j))
        else:
            candidates = ((fixed_i, t) for t in range(m + n)
                          if t != fixed_j and (t < n or t == n + fixed_i))
        for i, j in candidates:
            if matched_cost + Cv.C[i, j] + Ce.ls >= maxcost.value:
                # prune
                continue
            Cv_ij = make_CostMatrix(reduce_C(Cv.C, (i,), (j,), m, n))
            assert Cv.ls <= Cv.C[i, j] + Cv_ij.ls
            if matched_cost + Cv.C[i, j] + Cv_ij.ls + Ce.ls >= maxcost.value:
                # prune
                continue
            xy, localCe = match_edges(pending_u[i] if i < m else None, pending_v[j] if j < n else None,
                                      pending_g, pending_h, Ce, matched_uv)
            if matched_cost + Cv.C[i, j] + Cv_ij.ls + localCe.ls >= maxcost.value:
                # prune
                continue
            Ce_xy = make_CostMatrix(reduce_C(Ce.C, [k for k, l in xy], [l for k, l in xy],
                                             len(pending_g), len(pending_h)))
            assert Ce.ls <= localCe.ls + Ce_xy.ls
            if matched_cost + Cv.C[i, j] + Cv_ij.ls + localCe.ls + Ce_xy.ls >= maxcost.value:
                # prune
                continue
            other.append(((i, j), Cv_ij, xy, Ce_xy, Cv.C[i, j] + localCe.ls))

        # yield from
        for t in sorted(other, key = lambda t: t[4] + t[1].ls + t[3].ls):
            yield t

    def get_edit_paths(matched_uv, pending_u, pending_v, Cv,
                       matched_gh, pending_g, pending_h, Ce, matched_cost):
        """
        Parameters:
            matched_uv: partial vertex edit path
                list of tuples (u, v) of vertex mappings u<->v,
                u=None or v=None for deletion/insertion
            pending_u, pending_v: lists of vertices not yet mapped
            Cv: CostMatrix of pending vertex mappings
            matched_gh: partial edge edit path
                list of tuples (g, h) of edge mappings g<->h,
                g=None or h=None for deletion/insertion
            pending_g, pending_h: lists of edges not yet mapped
            Ce: CostMatrix of pending edge mappings
            matched_cost: cost of partial edit path

        Returns:
            sequence of (path_uv, path_gh, cost)
                path_uv: complete vertex edit path
                    list of tuples (u, v) of vertex mappings u<->v,
                    u=None or v=None for deletion/insertion
                path_gh: complete edge edit path
                    list of tuples (g, h) of edge mappings g<->h,
                    g=None or h=None for deletion/insertion
                cost: total cost of edit path
            NOTE: path costs are non-increasing
        """
        #debug_print('matched-uv:', matched_uv)
        #debug_print('matched-gh:', matched_gh)
        #debug_print('matched-cost:', matched_cost)
        #debug_print('pending-u:', pending_u)
        #debug_print('pending-v:', pending_v)
        #debug_print(Cv.C)
        assert set(G1.nodes) == (set(u for u, v in matched_uv) | set(pending_u)) - set([None])
        assert len(G1.nodes) == len(list(u for u, v in matched_uv if u is not None)) + len(pending_u)
        assert set(G2.nodes) == (set(v for u, v in matched_uv) | set(pending_v)) - set([None])
        assert len(G2.nodes) == len(list(v for u, v in matched_uv if v is not None)) + len(pending_v)
        #debug_print('pending-g:', pending_g)
        #debug_print('pending-h:', pending_h)
        #debug_print(Ce.C)
        assert set(G1.edges) == (set(g for g, h in matched_gh) | set(pending_g)) - set([None])
        assert len(G1.edges) == len(list(g for g, h in matched_gh if g is not None)) + len(pending_g)
        assert set(G2.edges) == (set(h for g, h in matched_gh) | set(pending_h)) - set([None])
        assert len(G2.edges) == len(list(h for g, h in matched_gh if h is not None)) + len(pending_h)
        #debug_print()

        if not max(len(pending_u), len(pending_v)):
            assert not len(pending_g)
            assert not len(pending_h)
            # path completed!
            assert matched_cost < maxcost.value
            maxcost.value = min(maxcost.value, matched_cost)
            yield matched_uv, matched_gh, matched_cost

        else:
            edit_ops = get_edit_ops(matched_uv, pending_u, pending_v, Cv,
                                    pending_g, pending_h, Ce, matched_cost)
            for ij, Cv_ij, xy, Ce_xy, edit_cost in edit_ops:
                i, j = ij
                assert Cv.C[i, j] + sum(Ce.C[t] for t in xy) == edit_cost
                if matched_cost + edit_cost + Cv_ij.ls + Ce_xy.ls >= maxcost.value:
                    # prune
                    continue

                # dive deeper
                u = pending_u.pop(i) if i < len(pending_u) else None
                v = pending_v.pop(j) if j < len(pending_v) else None
                matched_uv.append((u, v))
                for x, y in xy:
                    matched_gh.append((pending_g[x] if x < len(pending_g) else None,
                                       pending_h[y] if y < len(pending_h) else None))
                sortedx = list(sorted(x for x, y in xy))
                sortedy = list(sorted(y for x, y in xy))
                G = list((pending_g.pop(x) if x < len(pending_g) else None)
                         for x in reversed(sortedx))
                H = list((pending_h.pop(y) if y < len(pending_h) else None)
                         for y in reversed(sortedy))

                # yield from
                for t in get_edit_paths(matched_uv, pending_u, pending_v, Cv_ij,
                                        matched_gh, pending_g, pending_h, Ce_xy,
                                        matched_cost + edit_cost):
                    yield t

                # backtrack
                if not u is None:
                    pending_u.insert(i, u)
                if not v is None:
                    pending_v.insert(j, v)
                matched_uv.pop()
                for x, g in zip(sortedx, reversed(G)):
                    if g is not None:
                        pending_g.insert(x, g)
                for y, h in zip(sortedy, reversed(H)):
                    if h is not None:
                        pending_h.insert(y, h)
                for t in xy:
                    matched_gh.pop()


    # Initialization

    pending_u = list(G1.nodes)
    pending_v = list(G2.nodes)

    # cost matrix of vertex mappings
    m = len(pending_u)
    n = len(pending_v)
    C = np.zeros((m + n, m + n))
    C[0:m, 0:n] = np.array([1 - int(node_match(G1.nodes[u], G2.nodes[v])) if node_match else 0
                            for u in pending_u for v in pending_v]).reshape(m, n)
    C[0:m, n:n+m] = np.array([1 if i == j else inf
                              for i in range(m) for j in range(m)]).reshape(m, m)
    C[m:m+n, 0:n] = np.array([1 if i == j else inf
                              for i in range(n) for j in range(n)]).reshape(n, n)
    Cv = make_CostMatrix(C)
    #debug_print('Cv: {} x {}'.format(m, n))
    #debug_print(Cv.C)

    pending_g = list(G1.edges)
    pending_h = list(G2.edges)

    # cost matrix of edge mappings
    m = len(pending_g)
    n = len(pending_h)
    C = np.zeros((m + n, m + n))
    C[0:m, 0:n] = np.array([1 - int(edge_match(G1.edges[g], G2.edges[h])) if edge_match else 0
                            for g in pending_g for h in pending_h]).reshape(m, n)
    C[0:m, n:n+m] = np.array([1 if i == j else inf
                              for i in range(m) for j in range(m)]).reshape(m, m)
    C[m:m+n, 0:n] = np.array([1 if i == j else inf
                              for i in range(n) for j in range(n)]).reshape(n, n)
    Ce = make_CostMatrix(C)
    #debug_print('Ce: {} x {}'.format(m, n))
    #debug_print(Ce.C)
    #debug_print()


    # Now go!

    # for #asserts
    bestcost = maxcost.value

    for path_uv, path_gh, cost in get_edit_paths([], pending_u, pending_v, Cv,
                                                 [], pending_g, pending_h, Ce, 0):
        #print(path_uv, path_gh, cost)
        #assert cost <= bestcost
        #assert cost == maxcost.value
        bestcost = cost

    #assert bestcost == maxcost.value
    return bestcost

def setup_module(module):
    """Fixture for nose tests."""
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
    try:
        import scipy
    except:
        raise SkipTest("SciPy not available")
