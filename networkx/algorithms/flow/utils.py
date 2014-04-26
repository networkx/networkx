# -*- coding: utf-8 -*-
"""
Utility classes and functions for network flow algorithms.
"""

__author__ = """ysitu <ysitu@users.noreply.github.com>"""
# Copyright (C) 2014 ysitu <ysitu@users.noreply.github.com>
# All rights reserved.
# BSD license.

from collections import deque
import networkx as nx

__all__ = ['CurrentEdge', 'Level', 'GlobalRelabelThreshold',
           'build_residual_network', 'detect_unboundedness', 'build_flow_dict']


class CurrentEdge(object):
    """Mechanism for iterating over out-edges incident to a node in a circular
    manner. StopIteration exception is raised when wraparound occurs.
    """
    __slots__ = ('_edges', '_it', '_curr')

    def __init__(self, edges):
        self._edges = edges
        if self._edges:
            self._rewind()

    def get(self):
        return self._curr

    def move_to_next(self):
        try:
            self._curr = next(self._it)
        except StopIteration:
            self._rewind()
            raise

    def _rewind(self):
        self._it = iter(self._edges.items())
        self._curr = next(self._it)


class Level(object):
    """Active and inactive nodes in a level.
    """
    __slots__ = ('active', 'inactive')

    def __init__(self):
        self.active = set()
        self.inactive = set()


class GlobalRelabelThreshold(object):
    """Measurement of work before the global relabeling heuristic should be
    applied.
    """

    def __init__(self, n, m, freq):
        self._threshold = (n + m) / freq if freq else float('inf')
        self._work = 0

    def add_work(self, work):
        self._work += work

    def is_reached(self):
        return self._work >= self._threshold

    def clear_work(self):
        self._work = 0


def build_residual_network(G, s, t, capacity):
    """Build a residual network and initialize a zero flow.
    """
    if G.is_multigraph():
        raise nx.NetworkXError(
            'MultiGraph and MultiDiGraph not supported (yet).')

    if s not in G:
        raise nx.NetworkXError('node %s not in graph' % str(s))
    if t not in G:
        raise nx.NetworkXError('node %s not in graph' % str(t))
    if s == t:
        raise nx.NetworkXError('source and sink are the same node')

    R = nx.DiGraph()
    R.add_nodes_from(G)

    inf = float('inf')
    # Extract edges with positive capacities. Self loops excluded.
    edge_list = [(u, v, attr) for u, v, attr in G.edges_iter(data=True)
                 if u != v and attr.get(capacity, inf) > 0]
    # Simulate infinity with three times the sum of the finite edge capacities
    # or any positive value if the sum is zero. This allows the
    # infinite-capacity edges to be distinguished for unboundedness detection
    # and directly participate in residual capacity calculation. If the maximum
    # flow is finite, these edges cannot appear in the minimum cut and thus
    # guarantee correctness. Since the residual capacity of an
    # infinite-capacity edge is always at least 2/3 of inf, while that of an
    # finite-capacity edge is at most 1/3 of inf, if an operation moves more
    # than 1/3 of inf units of flow to t, there must be an infinite-capacity
    # s-t path in G.
    inf = 3 * sum(attr[capacity] for u, v, attr in edge_list
                  if capacity in attr and attr[capacity] != inf) or 1
    if G.is_directed():
        for u, v, attr in edge_list:
            r = min(attr.get(capacity, inf), inf)
            if not R.has_edge(u, v):
                # Both (u, v) and (v, u) must be present in the residual
                # network.
                R.add_edge(u, v, capacity=r)
                R.add_edge(v, u, capacity=0)
            else:
                # The edge (u, v) was added when (v, u) was visited.
                R[u][v]['capacity'] = r
    else:
        for u, v, attr in edge_list:
            # Add a pair of edges with equal residual capacities.
            r = min(attr.get(capacity, inf), inf)
            R.add_edge(u, v, capacity=r)
            R.add_edge(v, u, capacity=r)

    # Record the value simulating infinity.
    R.graph['inf'] = inf

    return R


def detect_unboundedness(R, s, t):
    """Detect an infinite-capacity s-t path in R.
    """
    q = deque([s])
    seen = set([s])
    inf = R.graph['inf']
    while q:
        u = q.popleft()
        for v, attr in R[u].items():
            if attr['capacity'] == inf and v not in seen:
                if v == t:
                    raise nx.NetworkXUnbounded(
                        'Infinite capacity path, flow unbounded above.')
                seen.add(v)
                q.append(v)


def build_flow_dict(G, R):
    """Build a flow dictionary from a residual network.
    """
    flow_dict = {}
    for u in G:
        flow_dict[u] = dict((v, 0) for v in G[u])
        flow_dict[u].update((v, attr['flow']) for v, attr in R[u].items()
                            if attr['flow'] > 0)
    return flow_dict
