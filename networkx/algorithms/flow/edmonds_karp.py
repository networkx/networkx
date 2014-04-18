# -*- coding: utf-8 -*-
"""
Edmonds-Karp algorithm for maximum flow problems.
"""

__author__ = """ysitu <ysitu@users.noreply.github.com>"""
# Copyright (C) 2014 ysitu <ysitu@users.noreply.github.com>
# All rights reserved.
# BSD license.

import networkx as nx
from networkx.algorithms.flow.utils import *

__all__ = ['edmonds_karp']


def edmonds_karp_core(R, s, t):
    """Implementation of the Edmonds-Karp algorithm.
    """
    R_node = R.node
    R_pred = R.pred
    R_succ = R.succ

    inf = float('inf')
    def augment(path):
        """Augment flow along a path from s to t.
        """
        # Determine the path residual capacity.
        flow = inf
        it = iter(path)
        u = next(it)
        for v in it:
            attr = R_succ[u][v]
            flow = min(flow, attr['capacity'] - attr['flow'])
            u = v
        # Augment flow along the path.
        it = iter(path)
        u = next(it)
        for v in it:
            R_succ[u][v]['flow'] += flow
            R_succ[v][u]['flow'] -= flow
            u = v
        # Accumulate the flow values.
        R_node[s]['excess'] -= flow
        R_node[t]['excess'] += flow

    def bidirectional_bfs():
        """Bidirectional breadth-first search for an augmenting path.
        """
        pred = {s: None}
        q_s = [s]
        succ = {t: None}
        q_t = [t]
        while True:
            q = []
            if len(q_s) <= len(q_t):
                for u in q_s:
                    for v, attr in R_succ[u].items():
                        if v not in pred and attr['flow'] < attr['capacity']:
                            pred[v] = u
                            if v in succ:
                                return v, pred, succ
                            q.append(v)
                if not q:
                    return None, None, None
                q_s = q
            else:
                for u in q_t:
                    for v, attr in R_pred[u].items():
                        if v not in succ and attr['flow'] < attr['capacity']:
                            succ[v] = u
                            if v in pred:
                                return v, pred, succ
                            q.append(v)
                if not q:
                    return None, None, None
                q_t = q

    # Look for shortest augmenting paths using breadth-first search.
    while True:
        v, pred, succ = bidirectional_bfs()
        if pred is None:
            break
        path = [v]
        # Trace a path from s to v.
        u = v
        while u != s:
            u = pred[u]
            path.append(u)
        path.reverse()
        # Trace a path from v to t.
        u = v
        while u != t:
            u = succ[u]
            path.append(u)
        augment(path)


def edmonds_karp_impl(G, s, t, capacity):
    """Implementation of the Edmonds-Karp algorithm.
    """
    R = build_residual_network(G, s, t, capacity)

    edmonds_karp_core(R, s, t)

    return R


def edmonds_karp(G, s, t, capacity='capacity', value_only=False):
    """Find a maximum single-commodity flow using the Edmonds-Karp algorithm.

    This function returns the residual network resulting after computing 
    the maximum flow. See below for details about the conventions
    NetworkX uses for defining residual networks.

    This algorithm has a running time of `O(n m^2)` for `n` nodes and `m`
    edges.


    Parameters
    ----------
    G : NetworkX graph
        Edges of the graph are expected to have an attribute called
        'capacity'. If this attribute is not present, the edge is
        considered to have infinite capacity.

    s : node
        Source node for the flow.

    t : node
        Sink node for the flow.

    capacity : string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    value_only : bool
        If True compute only the value of the maximum flow. This parameter
        will be ignored by this algorithm because is not aplicable.

    Returns
    -------
    R : NetworkX DiGraph
        Residual network after computing the maximum flow.

    Raises
    ------
    NetworkXError
        The algorithm does not support MultiGraph and MultiDiGraph. If
        the input graph is an instance of one of these two classes, a
        NetworkXError is raised.

    NetworkXUnbounded
        If the graph has a path of infinite capacity, the value of a
        feasible flow on the graph is unbounded above and the function
        raises a NetworkXUnbounded.

    See also
    --------
    :meth:`maximum_flow`
    :meth:`minimum_cut`
    :meth:`ford_fulkerson`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    Notes
    -----
    The residual network :samp:`R` from an input graph :samp:`G` has the
    same nodes than :samp:`G`. :samp:`R` is a DiGraph that contains a pair
    of edges :samp:`(u, v)` and :samp:`(v, u)` iff :samp:`(u, v)` is not a
    self-loop, and at least one of :samp:`(u, v)` and :samp:`(v, u)` exists
    in :samp:`G`. For each node :samp:`u` in :samp:`R`,
    :samp:`R.node[u]['excess']` represents the difference between flow into
    :samp:`u` and flow out of :samp:`u`. Thus the maximum flow value is
    stored in :samp:`R.node[t]['excess']`, where :samp:`t` is the sink node.

    For each edge :samp:`(u, v)` in :samp:`R`, :samp:`R[u][v]['capacity']` 
    is equal to the capacity of :samp:`(u, v)` in :samp:`G` if it exists 
    in :samp:`G` or zero otherwise. If the capacity is infinite, 
    :samp:`R[u][v]['capacity']` will have a high arbitrary finite value 
    that does not affect the solution of the problem. For each edge 
    :samp:`(u, v)` in :samp:`R`, :samp:`R[u][v]['flow']` represents 
    the flow function of :samp:`(u, v)` and satisfies 
    :samp:`R[u][v]['flow'] == -R[v][u]['flow']`.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_edge('x','a', capacity=3.0)
    >>> G.add_edge('x','b', capacity=1.0)
    >>> G.add_edge('a','c', capacity=3.0)
    >>> G.add_edge('b','c', capacity=5.0)
    >>> G.add_edge('b','d', capacity=4.0)
    >>> G.add_edge('d','e', capacity=2.0)
    >>> G.add_edge('c','y', capacity=2.0)
    >>> G.add_edge('e','y', capacity=3.0)
    >>> R = nx.edmonds_karp(G, 'x', 'y')
    >>> flow_value = nx.maximum_flow(G, 'x', 'y')
    >>> flow_value
    3.0
    >>> assert(flow_value == R.node['y']['excess'])

    """
    R = edmonds_karp_impl(G, s, t, capacity)
    R.graph['algorithm'] = 'edmonds_karp'
    return R
