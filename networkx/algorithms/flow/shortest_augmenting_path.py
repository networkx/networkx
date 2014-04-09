# -*- coding: utf-8 -*-
"""
Shortest augmenting path algorithm for maximum flow problems.
"""

__author__ = """ysitu <ysitu@users.noreply.github.com>"""
# Copyright (C) 2014 ysitu <ysitu@users.noreply.github.com>
# All rights reserved.
# BSD license.

from collections import deque
import networkx as nx
from networkx.algorithms.flow.utils import *

__all__ = ['shortest_augmenting_path', 'shortest_augmenting_path_value',
           'shortest_augmenting_path_flow']


def shortest_augmenting_path_impl(G, s, t, capacity, two_phase):
    """Implementation of the shortest augmenting path algorithm.
    """
    R = build_residual_network(G, s, t, capacity)

    # Initialize heights of the nodes.
    heights = {t: 0}
    q = deque([(t, 0)])
    while q:
        u, height = q.popleft()
        height += 1
        for v, u, attr in R.in_edges_iter(u, data=True):
            if v not in heights and attr['flow'] < attr['capacity']:
                heights[v] = height
                q.append((v, height))

    if s not in heights:
        # t is not reachable from s in the residual network. The maximum flow
        # must be zero.
        return R

    n = len(G)
    m = R.size() / 2

    # Initialize heights and 'current edge' data structures of the nodes.
    for u in R:
        R.node[u]['height'] = heights[u] if u in heights else n
        R.node[u]['curr_edge'] = CurrentEdge(R[u])

    # Initialize counts of nodes in each level.
    counts = [0] * (2 * n - 1)
    for u in R:
        counts[R.node[u]['height']] += 1

    inf = float('inf')
    def augment(path):
        """Augment flow along a path from s to t.
        """
        # Determine the path residual capacity.
        flow = inf
        it = iter(path)
        u = next(it)
        for v in it:
            attr = R[u][v]
            flow = min(flow, attr['capacity'] - attr['flow'])
            u = v
        # Augment flow along the path.
        it = iter(path)
        u = next(it)
        for v in it:
            R[u][v]['flow'] += flow
            R[v][u]['flow'] -= flow
            u = v
        # Accumulate the flow values.
        R.node[s]['excess'] -= flow
        R.node[t]['excess'] += flow

    def relabel(u):
        """Relabel a node to create an admissible edge.
        """
        height = n - 1
        for v, attr in R[u].items():
            if attr['flow'] < attr['capacity']:
                height = min(height, R.node[v]['height'])
        return height + 1

    # Phase 1: Look for shortest augmenting paths using depth-first search.

    path = [s]
    u = s
    d = n if not two_phase else int(min(m ** 0.5, 2 * n ** (2. / 3)))
    done = R.node[s]['height'] >= d
    while not done:
        height = R.node[u]['height']
        curr_edge = R.node[u]['curr_edge']
        # Depth-first search for the next node on the path to t.
        while True:
            v, attr = curr_edge.get()
            if (height == R.node[v]['height'] + 1 and
                attr['flow'] < attr['capacity']):
                # Advance to the next node following an admissible edge.
                path.append(v)
                u = v
                break
            try:
                curr_edge.move_to_next()
            except StopIteration:
                counts[height] -= 1
                if counts[height] == 0:
                    # Gap heuristic: If relabeling causes a level to become
                    # empty, a minimum cut has been identified. The algorithm
                    # can now be terminated.
                    return R
                height = relabel(u)
                if u == s and height >= d:
                    if not two_phase:
                        # t is disconnected from s in the residual network. No
                        # more augmenting paths exist.
                        return R
                    else:
                        # t is at least d steps away from s. End of phase 1.
                        done = True
                        break
                counts[height] += 1
                R.node[u]['height'] = height
                if u != s:
                    # After relabeling, the last edge on the path is no longer
                    # admissible. Retreat one step to look for an alternative.
                    path.pop()
                    u = path[-1]
                    break
        if u == t:
            # t is reached. Augment flow along the path and reset it for a new
            # depth-first search.
            augment(path)
            path = [s]
            u = s

    # Phase 2: Look for shortest augmenting paths using breadth-first search.
    while True:
        pred = {s: None}
        q = deque([s])
        done = False
        while not done and q:
            u = q.popleft()
            for v, attr in R[u].items():
                if v not in pred and attr['flow'] < attr['capacity']:
                    pred[v] = u
                    if v == t:
                        done = True
                        break
                    q.append(v)
        if not done:
            # No augmenting path found.
            return R
        # Trace a s-t path using the predecessor array.
        path = [t]
        u = t
        while True:
            u = pred[u]
            path.append(u)
            if u == s:
                break
        path.reverse()
        augment(path)


def shortest_augmenting_path(G, s, t, capacity='capacity', two_phase=False):
    """Find a maximum single-commodity flow using the shortest augmenting path
    algorithm.

    This algorithm has a running time of `O(n^2 m)` for `n` nodes and `m`
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

    two_phase : bool
        If True, a two-phase variant is used. The two-phase variant improves
        the running time on unit-capacity networks from `O(nm)` to
        `O(\min(n^{2/3}, m^{1/2}) m)`. Default value: False.

    Returns
    -------
    flow_value : integer, float
        Value of the maximum flow, i.e., net outflow from the source.

    flow_dict : dictionary
        Dictionary of dictionaries keyed by nodes such that
        flow_dict[u][v] is the flow edge (u, v).

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
    >>> flow, F = nx.shortest_augmenting_path(G, 'x', 'y')
    >>> flow, F['a']['c']
    (3.0, 2.0)
    """
    R = shortest_augmenting_path_impl(G, s, t, capacity, two_phase)
    return (R.node[t]['excess'], build_flow_dict(G, R))


def shortest_augmenting_path_value(G, s, t, capacity='capacity',
                                   two_phase=False):
    """Find a maximum single-commodity flow using the shortest augmenting path
    algorithm.

    This algorithm has a running time of `O(n^2 m)` for `n` nodes and `m`
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

    two_phase : bool
        If True, a two-phase variant is used. The two-phase variant improves
        the running time on unit-capacity networks from `O(nm)` to
        `O(\min(n^{2/3}, m^{1/2}) m)`. Default value: False.

    Returns
    -------
    flow_value : integer, float
        Value of the maximum flow, i.e., net outflow from the source.

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
    >>> flow = nx.shortest_augmenting_path_value(G, 'x', 'y')
    >>> flow
    3.0
    """
    R = shortest_augmenting_path_impl(G, s, t, capacity, two_phase)
    return R.node[t]['excess']


def shortest_augmenting_path_flow(G, s, t, capacity='capacity',
                                  two_phase=False):
    """Find a maximum single-commodity flow using the shortest augmenting path
    algorithm.

    This algorithm has a running time of `O(n^2 m)` for `n` nodes and `m`
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

    two_phase : bool
        If True, a two-phase variant is used. The two-phase variant improves
        the running time on unit-capacity networks from `O(nm)` to
        `O(\min(n^{2/3}, m^{1/2}) m)`. Default value: False.

    Returns
    -------
    flow_dict : dictionary
        Dictionary of dictionaries keyed by nodes such that
        flow_dict[u][v] is the flow edge (u, v).

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
    >>> F = nx.shortest_augmenting_path_flow(G, 'x', 'y')
    >>> F['a']['c']
    2.0
    """
    R = shortest_augmenting_path_impl(G, s, t, capacity, two_phase)
    return build_flow_dict(G, R)
