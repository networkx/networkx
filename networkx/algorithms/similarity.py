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

    def edit_cost(x, y, cache, cost_f):
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
        return edit_cost(u, v, cache, _node_cost_f)

    if edge_match:
        _edge_cost_f = lambda g, h: edge_match(G1.edges[g], G2.edges[h])
    else:
        _edge_cost_f = None
    def edge_edit_cost(g, h, cache = dict()):
        return edit_cost(g, h, cache, _edge_cost_f)

    def get_g(startpath, u, v):
        """
        Cost of adding mapping u<->v to partial edit path startpath.
        """
        c = node_edit_cost(u, v)
        for p, q in startpath:
            if not p is None and u in G1[p]:
                g = (u, p)
            else:
                g = None
            if not q is None and v in G2[q]:
                h = (v, q)
            else:
                h = None
            c += edge_edit_cost(g, h)
        return c

    def get_lb(Cv):
        """
        Lower-bound estimate of additional cost to complete
        partial edit path startpath.
        """
        row_ind, col_ind = linear_sum_assignment(Cv)
        return Cv[row_ind, col_ind].sum()

    def get_edit_nodes(startpath, pending_v, Cv, startcost, maxcost, u, i, m, n):
        if not u is None:
            vs = list(pending_v) + [None]
            js = list(range(len(vs))) + [None]
        else:
            vs = pending_v
            js = range(len(vs))
        for v, j in zip(vs, js):
            g = get_g(startpath, u, v)
            if startcost + g > maxcost:
                continue
            row_ind = [k for k in range(m + n) if k != i and k - m != j]
            col_ind = [l for l in range(m + n) if l != j and l - n != i]
            Cvj = Cv[row_ind,:][:,col_ind]
            lb = get_lb(Cvj)
            if startcost + g + lb > maxcost:
                continue
            yield v, j, Cvj, g, lb

    def get_edit_paths(startpath, pending_u, pending_v, Cv, startcost, maxcost):
        """
        Parameters:
            startpath: partial edit path
                list of tuples (u, v) of vertex mappings u<->v,
                u=None or v=None for insertion/deletion
            pending_u, pending_v: lists of vertices not yet mapped
            Cv: vertex mapping cost matrix (lower-bound estimate)
            startcost: cost of startpath
            maxcost: max cost of complete edit path to return

        Returns:
            sequence of (path, cost)
                path: complete edit path
                    list of tuples (u, v) of vertex mappings u<->v,
                    u=None or v=None for insertion/deletion
                cost: total cost of path
            NOTE: path costs are non-increasing
        """
        if startcost > maxcost:
            # prune
            return

        m = len(pending_u)
        n = len(pending_v)
        if max(m, n):
            if m:
                i = m - 1
                u = pending_u.pop()
            else:
                i = None
                u = None
            edit_nodes = get_edit_nodes(startpath, pending_v, Cv, startcost, maxcost, u, i, m, n)
            for v, j, Cvj, g, lb in sorted(edit_nodes, key = lambda v: v[3] + v[4]):
                if not v is None:
                    pending_v.pop(j)
                startpath.append((u, v))
                for path, cost in get_edit_paths(startpath, pending_u, pending_v, Cvj, startcost + g, maxcost):
                    if cost < maxcost:
                        # update immediately
                        maxcost = cost
                    if cost <= maxcost:
                        yield path, cost
                startpath.pop()
                if not v is None:
                    pending_v.insert(j, v)
            if not u is None:
                pending_u.insert(i, u)
        else:
            yield startpath, startcost

    # initial upper-bound estimate
    # NOTE: should work for empty graph
    maxcost = len(G1.nodes) + len(G2.nodes) + len(G1.edges) + len(G2.edges)

    pending_u = list(G1.nodes)
    pending_v = list(G2.nodes)

    # cost matrix of u<->v mappings (lower-bound estimate)
    m = len(pending_u)
    n = len(pending_v)
    Cv = np.zeros((m + n, m + n))
    Cv[0:m, 0:n] = np.array([node_edit_cost(u, v) + abs(len(G1.edges(u)) - len(G2.edges(v)))
                             for u in pending_u for v in pending_v]).reshape(m, n)
    Cv[0:m, n:n+m] = np.array([node_edit_cost(pending_u[i], None) +
                               sum(edge_edit_cost(g, None) for g in G1.edges(pending_u[i]))
                               if i == j else maxcost + 1
                               for i in range(m) for j in range(m)]).reshape(m, m)
    Cv[m:m+n, 0:n] = np.array([node_edit_cost(pending_v[i], None) +
                               sum(edge_edit_cost(h, None) for h in G2.edges(pending_v[i]))
                               if i == j else maxcost + 1
                               for i in range(n) for j in range(n)]).reshape(n, n)

    for path, cost in get_edit_paths([], pending_u, pending_v, Cv, 0, maxcost):
        #print(path, cost)
        bestcost = cost
    return bestcost
