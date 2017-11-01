# -*- coding: utf-8 -*-
import math
import itertools
import networkx as nx

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
        def __init__(self, Cv, lsa_row_ind, lsa_col_ind, ls):
            #assert Cv.shape[0] == len(lsa_row_ind)
            #assert Cv.shape[1] == len(lsa_col_ind)
            #assert len(lsa_row_ind) == len(lsa_col_ind)
            #assert set(lsa_row_ind) == set(range(len(lsa_row_ind)))
            #assert set(lsa_col_ind) == set(range(len(lsa_col_ind)))
            #assert ls == Cv[lsa_row_ind, lsa_col_ind].sum()
            self.Cv = Cv
            self.lsa_row_ind = lsa_row_ind
            self.lsa_col_ind = lsa_col_ind
            self.ls = ls

    def make_cost_lb(Cv):
        lsa_row_ind, lsa_col_ind = linear_sum_assignment(Cv)
        return CostMatrix(Cv, lsa_row_ind, lsa_col_ind, Cv[lsa_row_ind, lsa_col_ind].sum())

    class MaxCost:
        def __init__(self):
            # initial upper-bound estimate
            # NOTE: should work for empty graph
            self.value = len(G1.nodes) + len(G2.nodes) + len(G1.edges) + len(G2.edges)
    maxcost = MaxCost()

    def edit_cost(x, y, cost_f, cache):
        if (x is None) and (y is None):
            return 0
        elif (x is None) != (y is None):
            return 1
        else:
            if (x, y) in cache:
                c = cache[(x, y)]
            else:
                c = 1 - int(cost_f(x, y)) if cost_f else 0
                cache[(x, y)] = c
            return c

    if node_match:
        _node_cost_f = lambda u, v: node_match(G1.nodes[u], G2.nodes[v])
    else:
        _node_cost_f = None
    def node_edit_cost(u, v, cache = dict()):
        return edit_cost(u, v, _node_cost_f, cache)

    if edge_match:
        _edge_cost_f = lambda g, h: edge_match(G1.edges[g], G2.edges[h])
    else:
        _edge_cost_f = None
    def edge_edit_cost(g, h, cache = dict()):
        return edit_cost(g, h, _edge_cost_f, cache)

    def get_g(startpath, u, v):
        """Cost of adding mapping u<->v to partial edit path startpath.
        """
        c = node_edit_cost(u, v)
        u_edges = G1[u] if u is not None else ()
        v_edges = G2[v] if v is not None else ()
        for p, q in startpath:
            if p in u_edges:
                g = (u, p)
            else:
                g = None
            if q in v_edges:
                h = (v, q)
            else:
                h = None
            c += edge_edit_cost(g, h)
        return c

    def reduce_Cv(Cv, i, j, k, l):
        row_ind = [t for t in range(Cv.shape[0]) if t != i and t != k]
        col_ind = [t for t in range(Cv.shape[1]) if t != j and t != l]
        return Cv[row_ind,:][:,col_ind]

    def reduce_ind(ind, i, k):
        rind = ind[[t != i and t != k for t in ind]]
        rind[rind >= i] -= 1
        if i != k:
            rind[rind >= k] -= 1
        return rind

    def get_other_edit_nodes(startpath, startcost, pending_u, pending_v,
                             cost_lb, k, l, m, n):
        if n <= m:
            candidates = ((k, t) for t in range(m + n)
                          if k < m and t != l and (t < n or t == n + k))
        else:
            candidates = ((t, l) for t in range(m + n)
                          if l < n and t != k and (t < m or t == m + l))
        for i, j in candidates:
            g = get_g(startpath, pending_u[i] if i < m else None,
                      pending_v[j] if j < n else None)
            if startcost + g - cost_lb.Cv[i, j] + cost_lb.ls >= maxcost.value:
                # prune
                continue
            c = make_cost_lb(reduce_Cv(cost_lb.Cv, i, j, m + j, n + i))
            #assert cost_lb.ls - cost_lb.Cv[i, j] <= c.ls
            if startcost + g + c.ls >= maxcost.value:
                # prune
                continue
            yield i, j, g, c

    def get_edit_nodes(startpath, startcost, pending_u, pending_v, cost_lb):
        m = len(pending_u)
        n = len(pending_v)

        # get most promising mapping (minimum under-estimation of
        # actual mapping cost) quickly
        i, j, g = min(((k, l, get_g(startpath, pending_u[k] if k < m else None,
                                    pending_v[l] if l < n else None))
                       for k, l in zip(cost_lb.lsa_row_ind, cost_lb.lsa_col_ind)
                       if k < m or l < n),
                      key = lambda klg: klg[2] - cost_lb.Cv[klg[0], klg[1]])
        #assert cost_lb.Cv[i, j] <= g
        if startcost + g + cost_lb.ls - cost_lb.Cv[i, j] < maxcost.value:
            # update cost matrix efficiently
            c = CostMatrix(reduce_Cv(cost_lb.Cv, i, j, m + j, n + i),
                           reduce_ind(cost_lb.lsa_row_ind, i, m + j),
                           reduce_ind(cost_lb.lsa_col_ind, j, n + i),
                           cost_lb.ls - cost_lb.Cv[i, j])
            yield i, j, g, c

        # other candidate mappings, sorted by lower-bound cost estimate
        other = get_other_edit_nodes(startpath, startcost, pending_u, pending_v,
                                     cost_lb, i, j, m, n)
        for i, j, g, c in sorted(other, key = lambda ijgc: ijgc[2] + ijgc[3].ls):
            yield i, j, g, c

    def get_edit_paths(startpath, startcost, pending_u, pending_v, cost_lb):
        """
        Parameters:
            startpath: partial edit path
                list of tuples (u, v) of vertex mappings u<->v,
                u=None or v=None for insertion/deletion
            startcost: cost of startpath
            pending_u, pending_v: lists of vertices not yet mapped
            cost_lb: CostMatrix of pending vertex mappings
                (lower-bound estimate)

        Returns:
            sequence of (path, cost)
                path: complete edit path
                    list of tuples (u, v) of vertex mappings u<->v,
                    u=None or v=None for insertion/deletion
                cost: total cost of path
            NOTE: path costs are non-increasing
        """
        #debug_print(startpath, ':', startcost)
        #debug_print('pending-u:', pending_u)
        #debug_print('pending-v:', pending_v)
        #assert set(G1.nodes) == (set(u for u, v in startpath) | set(pending_u)) - set([None])
        #assert set(G2.nodes) == (set(v for u, v in startpath) | set(pending_v)) - set([None])

        if not max(len(pending_u), len(pending_v)):
            # path completed!
            #assert startcost < maxcost.value
            maxcost.value = min(maxcost.value, startcost)
            yield startpath, startcost

        else:
            edit_nodes = get_edit_nodes(startpath, startcost,
                                        pending_u, pending_v, cost_lb)
            for i, j, g, cost_lb_ij in edit_nodes:
                #assert cost_lb.Cv[i, j] <= g
                #assert startcost + g + cost_lb_ij.ls <= maxcost.value

                # go deeper
                if i < len(pending_u):
                    u = pending_u.pop(i)
                else:
                    u = None
                if j < len(pending_v):
                    v = pending_v.pop(j)
                else:
                    v = None
                startpath.append((u, v))

                #debug_print(u, '<->', v, ':', g)
                for path, cost in get_edit_paths(startpath, startcost + g,
                                                 pending_u, pending_v, cost_lb_ij):
                    yield path, cost

                # backtrack
                if not u is None:
                    pending_u.insert(i, u)
                if not v is None:
                    pending_v.insert(j, v)
                startpath.pop()

    pending_u = list(G1.nodes)
    pending_v = list(G2.nodes)

    # cost matrix of u<->v mappings (lower-bound estimate)
    m = len(pending_u)
    n = len(pending_v)
    Cv = np.zeros((m + n, m + n))
    Cv[0:m, 0:n] = np.array([node_edit_cost(u, v)
                             for u in pending_u for v in pending_v]).reshape(m, n)
    Cv[0:m, n:n+m] = np.array([node_edit_cost(pending_u[i], None)
                               if i == j else maxcost.value + 1
                               for i in range(m) for j in range(m)]).reshape(m, m)
    Cv[m:m+n, 0:n] = np.array([node_edit_cost(pending_v[i], None)
                               if i == j else maxcost.value + 1
                               for i in range(n) for j in range(n)]).reshape(n, n)
    #debug_print(m, 'x', n)
    #debug_print(Cv)

    # for #asserts
    bestcost = maxcost.value

    for path, cost in get_edit_paths([], 0, pending_u, pending_v, make_cost_lb(Cv)):
        #print(path, cost)
        #assert cost <= bestcost
        #assert cost == maxcost.value
        bestcost = cost

    #assert bestcost == maxcost.value
    return bestcost
