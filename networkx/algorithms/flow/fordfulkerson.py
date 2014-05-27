# -*- coding: utf-8 -*-
"""
Legacy implementation of the Edmonds-Karp algorithm for maximum flow problems.
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2010 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.

import networkx as nx

__all__ = ['ford_fulkerson']


def ford_fulkerson_impl(G, s, t, capacity):
    """Legacy implementation of the Edmonds-Karp algorithm"""
    if G.is_multigraph():
        raise nx.NetworkXError(
                'MultiGraph and MultiDiGraph not supported (yet).')

    if s not in G:
        raise nx.NetworkXError('node %s not in graph' % str(s))
    if t not in G:
        raise nx.NetworkXError('node %s not in graph' % str(t))
    if s == t:
        raise nx.NetworkXError('source and sink are the same node')

    auxiliary = _create_auxiliary_digraph(G, capacity=capacity)
    inf_capacity_flows = auxiliary.graph['inf_capacity_flows']

    flow_value = 0   # Initial feasible flow.

    # As long as there is an (s, t)-path in the auxiliary digraph, find
    # the shortest (with respect to the number of arcs) such path and
    # augment the flow on this path.
    while True:
        try:
            path_nodes = nx.bidirectional_shortest_path(auxiliary, s, t)
        except nx.NetworkXNoPath:
            break

        # Get the list of edges in the shortest path.
        path_edges = list(zip(path_nodes[:-1], path_nodes[1:]))

        # Find the minimum capacity of an edge in the path.
        try:
            path_capacity = min([auxiliary[u][v][capacity]
                                for u, v in path_edges
                                if capacity in auxiliary[u][v]])
        except ValueError:
            # path of infinite capacity implies no max flow
            raise nx.NetworkXUnbounded(
                    "Infinite capacity path, flow unbounded above.")

        flow_value += path_capacity

        # Augment the flow along the path.
        for u, v in path_edges:
            edge_attr = auxiliary[u][v]
            if capacity in edge_attr:
                edge_attr[capacity] -= path_capacity
                if edge_attr[capacity] == 0:
                    auxiliary.remove_edge(u, v)
            else:
                inf_capacity_flows[(u, v)] += path_capacity

            if auxiliary.has_edge(v, u):
                if capacity in auxiliary[v][u]:
                    auxiliary[v][u][capacity] += path_capacity
            else:
                auxiliary.add_edge(v, u, {capacity: path_capacity})

    auxiliary.graph['inf_capacity_flows'] = inf_capacity_flows
    return flow_value, auxiliary


def _create_auxiliary_digraph(G, capacity='capacity'):
    """Initialize an auxiliary digraph and dict of infinite capacity
    edges for a given graph G.
    Ignore edges with capacity <= 0.
    """
    auxiliary = nx.DiGraph()
    auxiliary.add_nodes_from(G)
    inf_capacity_flows = {}
    if nx.is_directed(G):
        for edge in G.edges(data = True):
            if capacity in edge[2]:
                if edge[2][capacity] > 0:
                    auxiliary.add_edge(*edge)
            else:
                auxiliary.add_edge(*edge)
                inf_capacity_flows[(edge[0], edge[1])] = 0
    else:
        for edge in G.edges(data = True):
            if capacity in edge[2]:
                if edge[2][capacity] > 0:
                    auxiliary.add_edge(*edge)
                    auxiliary.add_edge(edge[1], edge[0], edge[2])
            else:
                auxiliary.add_edge(*edge)
                auxiliary.add_edge(edge[1], edge[0], edge[2])
                inf_capacity_flows[(edge[0], edge[1])] = 0
                inf_capacity_flows[(edge[1], edge[0])] = 0

    auxiliary.graph['inf_capacity_flows'] = inf_capacity_flows
    return auxiliary


def _create_flow_dict(G, H, capacity='capacity'):
    """Creates the flow dict of dicts on G corresponding to the
    auxiliary digraph H and infinite capacity edges flows
    inf_capacity_flows.
    """
    inf_capacity_flows = H.graph['inf_capacity_flows']
    flow = dict([(u, {}) for u in G])

    if G.is_directed():
        for u, v in G.edges_iter():
            if H.has_edge(u, v):
                if capacity in G[u][v]:
                    flow[u][v] = max(0, G[u][v][capacity] - H[u][v][capacity])
                elif G.has_edge(v, u) and not capacity in G[v][u]:
                    flow[u][v] = max(0, inf_capacity_flows[(u, v)] -
                                     inf_capacity_flows[(v, u)])
                else:
                    flow[u][v] = max(0, H[v].get(u, {}).get(capacity, 0) -
                                     G[v].get(u, {}).get(capacity, 0))
            else:
                flow[u][v] = G[u][v][capacity]

    else: # undirected
        for u, v in G.edges_iter():
            if H.has_edge(u, v):
                if capacity in G[u][v]:
                    flow[u][v] = abs(G[u][v][capacity] - H[u][v][capacity])
                else:
                    flow[u][v] = abs(inf_capacity_flows[(u, v)] -
                                     inf_capacity_flows[(v, u)])
            else:
                flow[u][v] = G[u][v][capacity]
            flow[v][u] = flow[u][v]

    return flow

def ford_fulkerson(G, s, t, capacity='capacity'):
    """Find a maximum single-commodity flow using the Ford-Fulkerson
    algorithm.

    This is the legacy implementation of maximum flow. See Notes below.

    This algorithm uses Edmonds-Karp-Dinitz path selection rule which
    guarantees a running time of `O(nm^2)` for `n` nodes and `m` edges.


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

    Returns
    -------
    R : NetworkX DiGraph
        The residual network after computing the maximum flow. This is a 
        legacy implementation, se Notes and Examples.

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
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    Notes
    -----
    This is a legacy implementation of maximum flow (before 1.9).
    This function used to return a tuple with the flow value and the
    flow dictionary. Now it returns the residual network resulting 
    after computing the maximum flow, in order to follow the new
    interface to flow algorithms introduced in NetworkX 1.9.

    Note however that the residual network returned by this function
    does not follow the conventions for residual networks used by the
    new algorithms introduced in 1.9. This residual network has edges
    with capacity equal to the capacity of the edge in the original
    network minus the flow that went throught that edge. A dictionary
    with infinite capacity edges can be found as an attribute of the
    residual network.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.flow import ford_fulkerson

    The functions that implement flow algorithms and output a residual
    network, such as this one, are not imported to the base NetworkX
    namespace, so you have to explicitly import them from the flow package.

    >>> G = nx.DiGraph()
    >>> G.add_edge('x','a', capacity=3.0)
    >>> G.add_edge('x','b', capacity=1.0)
    >>> G.add_edge('a','c', capacity=3.0)
    >>> G.add_edge('b','c', capacity=5.0)
    >>> G.add_edge('b','d', capacity=4.0)
    >>> G.add_edge('d','e', capacity=2.0)
    >>> G.add_edge('c','y', capacity=2.0)
    >>> G.add_edge('e','y', capacity=3.0)

    This function returns the residual network after computing the
    maximum flow. This network has graph attributes that contain: 
    a dictionary with edges with infinite capacity flows, the flow 
    value, and a dictionary of flows:

    >>> R = ford_fulkerson(G, 'x', 'y')
    >>> # A dictionary with infinite capacity flows can be found as an
    >>> # attribute of the residual network
    >>> inf_capacity_flows = R.graph['inf_capacity_flows']
    >>> # There are also attributes for the flow value and the flow dict
    >>> flow_value = R.graph['flow_value']
    >>> flow_dict = R.graph['flow_dict']

    You can use the interface to flow algorithms introduced in 1.9 to get
    the output that the function ford_fulkerson used to produce:

    >>> flow_value, flow_dict = nx.maximum_flow(G, 'x', 'y',
    ...                                         flow_func=ford_fulkerson)

    """
    flow_value, R = ford_fulkerson_impl(G, s, t, capacity=capacity)
    flow_dict = _create_flow_dict(G, R, capacity=capacity)
    R.graph['flow_value'] = flow_value
    R.graph['flow_dict'] = flow_dict
    R.graph['algorithm'] = 'ford_fulkerson_legacy'
    return R
