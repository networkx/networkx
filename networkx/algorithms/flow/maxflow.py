# -*- coding: utf-8 -*-
"""
Maximum flow (and minimum cut) algorithms on capacitated graphs.
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2010 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.


__all__ = ['ford_fulkerson',
           'ford_fulkerson_flow',
           'max_flow',
           'min_cut']

import networkx as nx

def _create_auxiliary_digraph(G, capacity = 'capacity'):
    """Initialize an auxiliary digraph and dict of infinite capacity
    edges for a given graph G.
    Ignore edges with capacity <= 0.
    """
    auxiliary = nx.DiGraph()
    infcapFlows = {}

    if nx.is_directed(G):
        for edge in G.edges(data = True):
            if capacity in edge[2]:
                if edge[2][capacity] > 0:
                    auxiliary.add_edge(*edge)
            else:
                auxiliary.add_edge(*edge)
                infcapFlows[(edge[0], edge[1])] = 0
    else:
        for edge in G.edges(data = True):
            if capacity in edge[2]:
                if edge[2][capacity] > 0:
                    auxiliary.add_edge(*edge)
                    auxiliary.add_edge(edge[1], edge[0], edge[2])
            else:
                auxiliary.add_edge(*edge)
                auxiliary.add_edge(edge[1], edge[0], edge[2])
                infcapFlows[(edge[0], edge[1])] = 0
                infcapFlows[(edge[1], edge[0])] = 0

    return auxiliary, infcapFlows


def _create_flow_graph(G, H, infcapFlows, capacity = 'capacity'):
    """Creates the flow graph on G corresponding to the auxiliary
    digraph H and infinite capacity edges flows infcapFlows.
    """
    if nx.is_directed(G):
        flowGraph = nx.DiGraph(G)
    else:
        flowGraph = nx.Graph(G)

    for (u, v) in flowGraph.edges():
        if H.has_edge(u, v):
            try:
                flowGraph[u][v]['flow'] = abs(G[u][v][capacity]
                                              - H[u][v][capacity])
            except KeyError: # (u, v) has infinite capacity
                try:
                    flowGraph[u][v]['flow'] = H[v][u][capacity]
                except KeyError:
                    try: # Infinite capacity digon in the original graph.
                        if nx.is_directed(G):
                            flowDict[u][v] = max(infcapFlows[(u, v)]
                                             - infcapFlows[(v, u)], 0)
                        else:
                            flowDict[u][v] = abs(infcapFlows[(u, v)]
                                             - infcapFlows[(v, u)])
                    except KeyError: # Zero flow
                            flowDict[u][v] = 0
        else:
            flowGraph[u][v]['flow'] = G[u][v][capacity]

    return flowGraph


def _create_flow_dict(G, H, infcapFlows, capacity = 'capacity'):
    """Creates the flow dict of dicts on G corresponding to the
    auxiliary digraph H and infinite capacity edges flows infcapFlows.
    """
    flowDict = {}

    for u in G.nodes_iter():
        if not u in flowDict:
            flowDict[u] = {}
        for v in G.neighbors(u):
            if H.has_edge(u, v):
                try:
                    flowDict[u][v] = abs(G[u][v][capacity]
                                         - H[u][v][capacity])
                except KeyError: # (u, v) has infinite capacity
                    try:
                        flowDict[u][v] = H[v][u][capacity]
                    except KeyError:
                        try: # Infinite capacity digon in the original graph.
                            if nx.is_directed(G):
                                flowDict[u][v] = max(infcapFlows[(u, v)]
                                                 - infcapFlows[(v, u)], 0)
                            else:
                                flowDict[u][v] = abs(infcapFlows[(u, v)]
                                                 - infcapFlows[(v, u)])
                        except KeyError: # Zero flow
                            flowDict[u][v] = 0
            else:
                flowDict[u][v] = G[u][v][capacity]
    return flowDict


def ford_fulkerson(G, s, t, capacity = 'capacity'):
    """Find a maximum single-commodity flow using the Ford-Fulkerson algorithm.
    
    This algorithm uses Edmonds-Karp-Dinitz path selection rule which
    guarantees a running time of O(nm^2) for n nodes and m edges.


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

    Returns
    -------
    flowValue : integer, float
        Value of the maximum flow, i.e., net outflow from the source.

    flowDict : dictionary
        Dictionary of dictionaries keyed by nodes such that
        flowDict[u][v] is the flow edge (u, v).

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
    >>> G.add_edge('x','a', capacity = 3.0)
    >>> G.add_edge('x','b', capacity = 1.0)
    >>> G.add_edge('a','c', capacity = 3.0)
    >>> G.add_edge('b','c', capacity = 5.0)
    >>> G.add_edge('b','d', capacity = 4.0)
    >>> G.add_edge('d','e', capacity = 2.0)
    >>> G.add_edge('c','y', capacity = 2.0)
    >>> G.add_edge('e','y', capacity = 3.0)
    >>> flow,F=nx.ford_fulkerson(G, 'x', 'y')
    >>> flow
    3.0
    """
    if G.is_multigraph():
        raise nx.NetworkXError(
                'MultiGraph and MultiDiGraph not supported (yet).')

    auxiliary, infcapFlows = _create_auxiliary_digraph(G, capacity = capacity)
    flowValue = 0   # Initial feasible flow.

    # As long as there is an (s, t)-path in the auxiliary digraph, find
    # the shortest (with respect to the number of arcs) such path and
    # augment the flow on this path.
    while True:
        pathNodes = nx.bidirectional_shortest_path(auxiliary, s, t)
        if not pathNodes:
            break

        # Get the list of edges in the shortest path.
        pathEdges = []
        for i, u in enumerate(pathNodes[:-1]):
            v = pathNodes[i + 1]
            pathEdges.append((u, v, auxiliary[u][v]))

        # Find the minimum capacity of an edge in the path.
        try:
            pathCapacity = min([c[capacity]
                            for (u, v, c) in pathEdges
                            if capacity in c])
        except ValueError: 
            # path of infinite capacity implies no max flow
            raise nx.NetworkXUnbounded(
                    "Infinite capacity path, flow unbounded above.")
        
        flowValue += pathCapacity

        # Augment the flow along the path.
        for (u, v, c) in pathEdges:
            auxEdgeAttr = auxiliary[u][v]
            if capacity in auxEdgeAttr:
                auxEdgeAttr[capacity] -= pathCapacity
                if auxEdgeAttr[capacity] == 0:
                    auxiliary.remove_edge(u, v)
            else:
                infcapFlows[(u, v)] += pathCapacity

            if auxiliary.has_edge(v, u):
                if capacity in auxiliary[v][u]:
                    auxiliary[v][u][capacity] += pathCapacity
            else:
                auxiliary.add_edge(v, u, {capacity: pathCapacity})
    
    flowDict = _create_flow_dict(G, auxiliary, infcapFlows,
                                 capacity = capacity)
    return flowValue, flowDict


def ford_fulkerson_flow(G, s, t, capacity = 'capacity'):
    """Return a maximum flow for a single-commodity flow problem.

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

    Returns
    -------
    flowDict : dictionary
        Dictionary of dictionaries keyed by nodes such that
        flowDict[u][v] is the flow edge (u, v).

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
    >>> G.add_edge('x','a', capacity = 3.0)
    >>> G.add_edge('x','b', capacity = 1.0)
    >>> G.add_edge('a','c', capacity = 3.0)
    >>> G.add_edge('b','c', capacity = 5.0)
    >>> G.add_edge('b','d', capacity = 4.0)
    >>> G.add_edge('d','e', capacity = 2.0)
    >>> G.add_edge('c','y', capacity = 2.0)
    >>> G.add_edge('e','y', capacity = 3.0)
    >>> F=nx.ford_fulkerson_flow(G, 'x', 'y')
    >>> for u, v in G.edges_iter():
    ...     print('(%s, %s) %.2f' % (u, v, F[u][v]))
    ... 
    (a, c) 2.00
    (c, y) 2.00
    (b, c) 0.00
    (b, d) 1.00
    (e, y) 1.00
    (d, e) 1.00
    (x, a) 2.00
    (x, b) 1.00
    """
    return ford_fulkerson(G, s, t, capacity = capacity)[1]


def max_flow(G, s, t, capacity = 'capacity'):
    """Find the value of a maximum single-commodity flow.
    
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

    Returns
    -------
    flowValue : integer, float
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
    >>> G.add_edge('x','a', capacity = 3.0)
    >>> G.add_edge('x','b', capacity = 1.0)
    >>> G.add_edge('a','c', capacity = 3.0)
    >>> G.add_edge('b','c', capacity = 5.0)
    >>> G.add_edge('b','d', capacity = 4.0)
    >>> G.add_edge('d','e', capacity = 2.0)
    >>> G.add_edge('c','y', capacity = 2.0)
    >>> G.add_edge('e','y', capacity = 3.0)
    >>> flow=nx.max_flow(G, 'x', 'y')
    >>> flow
    3.0
    """
    return ford_fulkerson(G, s, t, capacity = capacity)[0]


def min_cut(G, s, t, capacity = 'capacity'):
    """Compute the value of a minimum (s, t)-cut.

    Use the max-flow min-cut theorem, i.e., the capacity of a minimum
    capacity cut is equal to the flow value of a maximum flow.

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

    Returns
    -------
    cutValue : integer, float
        Value of the minimum cut.
    
    Raises
    ------
    NetworkXUnbounded
        If the graph has a path of infinite capacity, all cuts have
        infinite capacity and the function raises a NetworkXError.
    
    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_edge('x','a', capacity = 3.0)
    >>> G.add_edge('x','b', capacity = 1.0)
    >>> G.add_edge('a','c', capacity = 3.0)
    >>> G.add_edge('b','c', capacity = 5.0)
    >>> G.add_edge('b','d', capacity = 4.0)
    >>> G.add_edge('d','e', capacity = 2.0)
    >>> G.add_edge('c','y', capacity = 2.0)
    >>> G.add_edge('e','y', capacity = 3.0)
    >>> nx.min_cut(G, 'x', 'y')
    3.0
    """

    try:
        return ford_fulkerson(G, s, t, capacity = capacity)[0]
    except nx.NetworkXUnbounded:
        raise nx.NetworkXUnbounded(
                "Infinite capacity path, no minimum cut.")

