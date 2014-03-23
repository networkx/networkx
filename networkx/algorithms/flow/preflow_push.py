# -*- coding: utf-8 -*-
"""
Highest-label preflow-push algorithm for maximum flow problems.
"""

__author__ = """ysitu <ysitu@users.noreply.github.com>"""
# Copyright (C) 2014 ysitu <ysitu@users.noreply.github.com>
# All rights reserved.
# BSD license.

from itertools import islice
import networkx as nx

__all__ = ['preflow_push',
           'preflow_push_value',
           'preflow_push_flow']


class _CurrentEdge(object):
    """Mechanism for iterating over out-edges incident to a node in a circular
    manner. StopIteration exception is raised when wraparound occurs.
    """

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


class _Level(object):
    """Active and inactive nodes in a level.
    """

    def __init__(self):
        self.active = set()
        self.inactive = set()


class _GlobalRelabelThreshold(object):
    """Measurement of work before the global relabeling heuristic should be
    applied.
    """

    def __init__(self, n, m, freq):
        self._threshold = freq * (n + m)
        self._work = 0

    def add_work(self, work):
        self._work += work

    def is_reached(self):
        return self._work >= self._threshold

    def clear_work(self):
        self._work = 0


def _build_residual_network(G, s, t, capacity):
    """Build the residual network. Initialize the edge capacities so that they
    correspond to a zero flow.
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

    # Extract edges with positive capacities. Self loops excluded.
    edge_list = [(u, v, attr) for u, v, attr in G.edges_iter(data=True)
                 if u != v and (capacity not in attr or attr[capacity] > 0)]
    # Simulate infinity with twice the sum of the finite edge capacities or any
    # positive value if the sum is zero. This allows the infinite-capacity
    # edges to be distinguished for detecting unboundedness. If the maximum
    # flow is finite, these edge still cannot appear in the minimum cut and
    # thus guarantee correctness.
    inf = float('inf')
    inf = 2 * sum(attr[capacity] for u, v, attr in edge_list
                  if capacity in attr and attr[capacity] != inf) or 1
    if G.is_directed():
        for u, v, attr in edge_list:
            r = attr[capacity] if capacity in attr else inf
            if not R.has_edge(u, v):
                # Both (u, v) and (v, u) must be present in the residual
                # network.
                R.add_edge(u, v, capacity=r, flow=0)
                R.add_edge(v, u, capacity=0, flow=0)
            else:
                # The edge (u, v) was added when (v, u) was visited.
                R[u][v]['capacity'] = r
    else:
        for u, v, attr in edge_list:
            # Add a pair of edges with equal residual capacities.
            r = attr[capacity] if capacity in attr else inf
            R.add_edge(u, v, capacity=r, flow=0)
            R.add_edge(v, u, capacity=r, flow=0)

    # Detect unboundedness by determining reachability of t from s using only
    # infinite-capacity edges.
    R_inf = nx.DiGraph((u, v) for u, v, attr in R.edges_iter(data=True)
                       if attr['capacity'] == inf)
    if s in R_inf and t in R_inf and nx.has_path(R_inf, s, t):
        raise nx.NetworkXUnbounded(
                'Infinite capacity path, flow unbounded above.')

    return R


def _preflow_push_impl(G, s, t, capacity, global_relabel_freq, compute_flow):
    """Implementation of the highest-label preflow-push algorithm.
    """
    R = _build_residual_network(G, s, t, capacity)

    # Initialize heights (or labels) of nodes.
    T = nx.DiGraph((u, v) for u, v, attr in R.edges_iter(data=True)
                   if attr['capacity'] > 0)
    T.add_node(t)
    heights = nx.shortest_path_length(T, target=t)

    if s not in heights:
        # t is not reachable from s in the residual network. The maximum flow
        # must be zero.
        if compute_flow:
            flow_dict = {}
            for u in G:
                flow_dict[u] = {}
                for v in G[u]:
                    flow_dict[u][v] = 0
            return (0, flow_dict)
        else:
            return 0

    n = len(R)
    max_height = max(heights[u] for u in heights if u != s)
    heights[s] = n

    if global_relabel_freq is None:
        global_relabel_freq = float('inf')
    grt = _GlobalRelabelThreshold(n, R.size(), global_relabel_freq)

    # Initialize height, excesses and 'current edge' data structures of the
    # nodes.
    for u in R:
        R.node[u]['height'] = heights[u] if u in heights else n + 1
        R.node[u]['excess'] = 0
        R.node[u]['curr_edge'] = _CurrentEdge(R[u])

    def push(u, v, flow):
        """Push flow units of flow from u to v.
        """
        R[u][v]['flow'] += flow
        R[v][u]['flow'] -= flow
        R.node[u]['excess'] -= flow
        R.node[v]['excess'] += flow

    # The maximum flow must be nonzero now. Initialize the preflow by
    # saturating all edges emanating from s.
    for u, attr in R[s].items():
        flow = attr['capacity']
        if flow > 0:
            push(s, u, flow)

    # Partition nodes into levels.
    levels = [_Level() for i in range(2 * n - 1)]
    for u in R:
        if u != s and u != t:
            level = levels[R.node[u]['height']]
            if R.node[u]['excess'] > 0:
                level.active.add(u)
            else:
                level.inactive.add(u)

    def activate(v):
        """Move a node from the inactive set to the active set of its level.
        """
        if v != s and v != t:
            level = levels[R.node[v]['height']]
            if v in level.inactive:
                level.inactive.remove(v)
                level.active.add(v)

    def relabel(u):
        """Relabel a node to create an admissible edge.
        """
        R.node[u]['height'] = min(R.node[v]['height']
                                  for v, attr in R[u].items()
                                  if attr['flow'] < attr['capacity']) + 1
        grt.add_work(len(R[u]))

    def discharge(u):
        """Discharge a node until it becomes inactive.
        """
        levels[R.node[u]['height']].active.remove(u)
        while True:
            v, attr = R.node[u]['curr_edge'].get()
            if (R.node[u]['height'] == R.node[v]['height'] + 1 and
                attr['flow'] < attr['capacity']):
                flow = min(R.node[u]['excess'],
                           attr['capacity'] - attr['flow'])
                push(u, v, flow)
                activate(v)
                if R.node[u]['excess'] == 0:
                    break
            try:
                R.node[u]['curr_edge'].move_to_next()
            except StopIteration:
                relabel(u)
        levels[R.node[u]['height']].inactive.add(u)

    def gap_heuristic(height):
        """Apply the gap heuristic.
        """
        for level in islice(levels, height + 1, max_height + 1):
            for u in level.active:
                R.node[u]['height'] = n + 1
                levels[n + 1].active.add(u)
            for u in level.inactive:
                R.node[u]['height'] = n + 1
                levels[n + 1].inactive.add(u)
            level.active.clear()
            level.inactive.clear()

    def global_relabel(from_sink):
        """Apply the global relabeling heuristic.
        """
        T = nx.DiGraph((u, v) for u, v, attr in R.edges_iter(data=True)
                       if attr['flow'] < attr['capacity'])
        target = t if from_sink else s
        T.add_node(target)
        heights = nx.shortest_path_length(T, target=target)
        max_height = max(heights.values())
        if from_sink:
            # Also mark nodes from which t is unreachable for relabeling. This
            # serves the same purpose as the gap heuristic.
            for u in R:
                if u not in heights and R.node[u]['height'] < n:
                    heights[u] = n + 1
        else:
            # Shift the computed heights because the height of s is n.
            for u in heights:
                heights[u] += n
        for u in heights:
            if u != s and u != t and heights[u] != R.node[u]['height']:
                if u in levels[R.node[u]['height']].active:
                    levels[R.node[u]['height']].active.remove(u)
                    levels[heights[u]].active.add(u)
                else:
                    levels[R.node[u]['height']].inactive.remove(u)
                    levels[heights[u]].inactive.add(u)
                R.node[u]['height'] = heights[u]
        return max_height

    # Phase 1: Find the maximum preflow by pushing as much flow as possible to
    # t.

    height = max_height
    while height > 0:
        # Discharge active nodes in the current level.
        while True:
            level = levels[height]
            if not level.active:
                # All active nodes in the current level have been discharged.
                # Move to the next lower level.
                height -= 1
                break
            # Record the old height and level for the gap heuristic.
            old_height = height
            old_level = level
            u = next(iter(level.active))
            discharge(u)
            # Gap heuristic: If the level at old_height is empty (a 'gap'),
            # a minimum cut has been identified. All nodes with heights above
            # old_height can have their heights set to n + 1 and not be
            # further processed before a maximum preflow is found.
            if not old_level.active and not old_level.inactive:
                gap_heuristic(old_height)
                max_height = old_height - 1
            if not grt.is_reached():
                # u may have been relabeled during discharge and introduced new
                # active nodes above the old level. Therefore, height should
                # be set to its new height, bounded by max_height, so that
                # those new active nodes can be discharged.
                height = R.node[u]['height']
                if height < n:
                    max_height = max(max_height, height)
            else:
                # Global relabeling heuristic: Recompute the exact heights of
                # all nodes.
                height = global_relabel(True)
                max_height = height
                grt.clear_work()

    # A maximum preflow has been found. The excess at t is the maximum flow
    # value.
    if not compute_flow:
        return R.node[t]['excess']

    # Phase 2: Convert the maximum preflow to a maximum flow by returning the
    # excess to s.

    # Relabel all nodes so that they have accurate heights.
    global_relabel(False)
    grt.clear_work()

    # Continue to discharge the active nodes.
    height = 2 * n - 2
    while height > n:
        # Discharge active nodes in the current level.
        while True:
            level = levels[height]
            if not level.active:
                # All active nodes in the current level have been discharged.
                # Move to the next lower level.
                height -= 1
                break
            u = next(iter(level.active))
            discharge(u)
            if not grt.is_reached():
                height = R.node[u]['height']
            else:
                height = global_relabel(False)
                grt.clear_work()

    # Convert the residual network to a dictionary.
    flow_dict = {}
    for u in G:
        flow_dict[u] = {}
        for v in G[u]:
            flow_dict[u][v] = 0
    for u in G:
        flow_dict[u].update((v, R[u][v]['flow']) for v in R[u]
                            if R[u][v]['flow'] > 0)
    return (R.node[t]['excess'], flow_dict)


def preflow_push(G, s, t, capacity='capacity', global_relabel_freq=1):
    """Find a maximum single-commodity flow using the highest-label
    preflow-push algorithm.

    This algorithm has a running time of `O(n^2 m^(1/2))` for `n` nodes and
    `m` edges.


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

    capacity: string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    global_relabel_freq: integer, float
        Relative frequency of applying the global relabeling heuristic to speed
        up the algorithm. If it is None, the heuristic is disabled. Default
        value: 1.

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
    >>> flow, F = nx.ford_fulkerson(G, 'x', 'y')
    >>> flow
    3.0
    """
    return _preflow_push_impl(G, s, t, capacity, global_relabel_freq, True)


def preflow_push_value(G, s, t, capacity='capacity', global_relabel_freq=1):
    """Find a maximum single-commodity flow using the highest-label preflow-
    push algorithm.

    This algorithm has a running time of `O(n^2 m^(1/2))` for `n` nodes and
    `m` edges.


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

    capacity: string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    global_relabel_freq: integer, float
        Relative frequency of applying the global relabeling heuristic to speed
        up the algorithm. If it is None, the heuristic is disabled. Default
        value: 1.

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
    >>> flow, F = nx.ford_fulkerson(G, 'x', 'y')
    >>> flow
    3.0
    """
    return _preflow_push_impl(G, s, t, capacity, global_relabel_freq, False)


def preflow_push_flow(G, s, t, capacity='capacity', global_relabel_freq=1):
    """Find a maximum single-commodity flow using the highest-label preflow-
    push algorithm.

    This algorithm has a running time of `O(n^2 m^(1/2))` for `n` nodes and
    `m` edges.


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

    capacity: string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    global_relabel_freq: integer, float
        Relative frequency of applying the global relabeling heuristic to speed
        up the algorithm. If it is None, the heuristic is disabled. Default
        value: 1.

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
    >>> flow, F = nx.ford_fulkerson(G, 'x', 'y')
    >>> flow
    3.0
    """
    return _preflow_push_impl(G, s, t, capacity, global_relabel_freq, True)[1]
