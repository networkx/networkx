# -*- coding: utf-8 -*-
"""
Minimum cost flow algorithms on directed connected graphs.
"""

__author__ = """Loïc Séguin-C. <loicseguin@gmail.com>"""
# Copyright (C) 2010 Loïc Séguin-C. <loicseguin@gmail.com>
# All rights reserved.
# BSD license.


__all__ = ['network_simplex',
           'min_cost_flow_cost',
           'min_cost_flow',
           'cost_of_flow',
           'max_flow_min_cost']

import networkx as nx
from networkx.utils import generate_unique_node

def _initial_tree_solution(G, demand = 'demand', capacity = 'capacity',
                           weight = 'weight'):
    """Find a initial tree solution rooted at r.

    The initial tree solution is obtained by considering edges (r, v)
    for all nodes v with non-negative demand and (v, r) for all nodes
    with negative demand. If these edges do not exist, we add them to
    the graph and call them artificial edges.
    """
    H = nx.DiGraph((edge for edge in G.edges(data=True) if
                    edge[2].get(capacity, 1) > 0))
    demand_nodes = (node for node in G.nodes_iter(data=True) if
                    node[1].get(demand, 0) != 0)
    H.add_nodes_from(demand_nodes)
    r = H.nodes()[0]

    T = nx.DiGraph()
    y = {r: 0}
    artificialEdges = []
    flowCost = 0

    n = H.number_of_nodes()
    try:
        maxWeight = max(abs(d[weight]) for u, v, d in H.edges(data = True)
                        if weight in d)
    except ValueError:
        maxWeight = 0
    hugeWeight = 1 + n * maxWeight

    for v, d in H.nodes(data = True)[1:]:
        vDemand = d.get(demand, 0)
        if vDemand >= 0:
            if not (r, v) in H.edges():
                H.add_edge(r, v, {weight: hugeWeight, 'flow': vDemand})
                artificialEdges.append((r, v))
                y[v] = H[r][v].get(weight, 0)
                T.add_edge(r, v)
                flowCost += vDemand * H[r][v].get(weight, 0)

            else: # (r, v) in H.edges()
                if (not capacity in H[r][v]
                    or vDemand <= H[r][v][capacity]):
                    H[r][v]['flow'] = vDemand
                    y[v] = H[r][v].get(weight, 0)
                    T.add_edge(r, v)
                    flowCost += vDemand * H[r][v].get(weight, 0)

                else: # existing edge does not have enough capacity
                    newLabel = generate_unique_node()
                    H.add_edge(r, newLabel, {weight: hugeWeight, 'flow': vDemand})
                    H.add_edge(newLabel, v, {weight: hugeWeight, 'flow': vDemand})
                    artificialEdges.append((r, newLabel))
                    artificialEdges.append((newLabel, v))
                    y[v] = 2 * hugeWeight
                    y[newLabel] = hugeWeight
                    T.add_edge(r, newLabel)
                    T.add_edge(newLabel, v)
                    flowCost += 2 * vDemand * hugeWeight

        else: # vDemand < 0
            if not (v, r) in H.edges():
                H.add_edge(v, r, {weight: hugeWeight, 'flow': -vDemand})
                artificialEdges.append((v, r))
                y[v] = -H[v][r].get(weight, 0)
                T.add_edge(v, r)
                flowCost += -vDemand * H[v][r].get(weight, 0)

            else:
                if (not capacity in H[v][r]
                    or -vDemand <= H[v][r][capacity]):
                    H[v][r]['flow'] = -vDemand
                    y[v] = -H[v][r].get(weight, 0)
                    T.add_edge(v, r)
                    flowCost += -vDemand * H[v][r].get(weight, 0)
                else: # existing edge does not have enough capacity
                    newLabel = generate_unique_node()
                    H.add_edge(v, newLabel,
                               {weight: hugeWeight, 'flow': -vDemand})
                    H.add_edge(newLabel, r,
                               {weight: hugeWeight, 'flow': -vDemand})
                    artificialEdges.append((v, newLabel))
                    artificialEdges.append((newLabel, r))
                    y[v] = -2 * hugeWeight
                    y[newLabel] = -hugeWeight
                    T.add_edge(v, newLabel)
                    T.add_edge(newLabel, r)
                    flowCost += 2 * -vDemand * hugeWeight
            
    return H, T, y, artificialEdges, flowCost, r


def _find_entering_edge(H, c, capacity = 'capacity'):
    """Find an edge which creates a negative cost cycle in the actual
    tree solution.

    The reduced cost of every edge gives the value of the cycle
    obtained by adding that edge to the tree solution. If that value is
    negative, we will augment the flow in the direction indicated by
    the edge. Otherwise, we will augment the flow in the reverse
    direction.

    If no edge is found, return and empty tuple. This will cause the
    main loop of the algorithm to terminate.
    """
    newEdge = ()
    for u, v, d in H.edges_iter(data = True):
        if d.get('flow', 0) == 0:
            if c[(u, v)] < 0:
                newEdge = (u, v)
                break
        else:
            if capacity in d:
                if (d.get('flow', 0) == d[capacity]
                    and c[(u, v)] > 0):
                    newEdge = (u, v)
                    break
    return newEdge


def _find_leaving_edge(H, T, cycle, newEdge, capacity = 'capacity'):
    """Find an edge that will leave the basis and the value by which we
    can increase or decrease the flow on that edge.

    The leaving arc rule is used to prevent cycling.
    
    If cycle has no reverse edge and no forward edge of finite
    capacity, it means that cycle is a negative cost infinite capacity
    cycle. This implies that the cost of a flow satisfying all demands
    is unbounded below. An exception is raised in this case.
    """
    eps = False
    leavingEdge = ()

    # If cycle is a digon, newEdge is always a reverse edge (otherwise,
    # there would be no leaving edge).
    if len(cycle) == 3:
        u, v = newEdge
        if H[u][v].get('flow', 0) > H[v][u].get('flow', 0):
            return (v, u), H[v][u].get('flow', 0)
        else:
            return (u, v), H[u][v].get('flow', 0)

    # Find the forward edge with the minimum value for capacity - 'flow'
    # and the reverse edge with the minimum value for 'flow'.
    for index, u in enumerate(cycle[:-1]):
        edgeCapacity = False
        edge = ()
        v = cycle[index + 1]
        if (u, v) in T.edges() + [newEdge]: #forward edge
            if capacity in H[u][v]: # edge (u, v) has finite capacity
                edgeCapacity = H[u][v][capacity] - H[u][v].get('flow', 0)
                edge = (u, v)
        else: #reverse edge
            edgeCapacity = H[v][u].get('flow', 0)
            edge = (v, u)

        # Determine if edge might be the leaving edge.
        if edge:
            if leavingEdge:
                if edgeCapacity < eps:
                    eps = edgeCapacity
                    leavingEdge = edge
            else:
                eps = edgeCapacity
                leavingEdge = edge

    if not leavingEdge:
        raise nx.NetworkXUnbounded(
                "Negative cost cycle of infinite capacity found. "
                + "Min cost flow unbounded below.")

    return leavingEdge, eps


def _create_flow_dict(G, H):
    """Creates the flow dict of dicts of graph G with auxiliary graph H."""
    flowDict = dict([(u, {}) for u in G])

    for u in G.nodes_iter():
        for v in G.neighbors(u):
            if H.has_edge(u, v):
                flowDict[u][v] = H[u][v].get('flow', 0)
            else:
                flowDict[u][v] = 0
    return flowDict


def network_simplex(G, demand = 'demand', capacity = 'capacity',
                    weight = 'weight'):
    """Find a minimum cost flow satisfying all demands in digraph G.
    
    This is a primal network simplex algorithm that uses the leaving
    arc rule to prevent cycling.

    G is a digraph with edge costs and capacities and in which nodes
    have demand, i.e., they want to send or receive some amount of
    flow. A negative demand means that the node wants to send flow, a
    positive demand means that the node want to receive flow. A flow on
    the digraph G satisfies all demand if the net flow into each node
    is equal to the demand of that node.

    Parameters
    ----------
    G : NetworkX graph
        DiGraph on which a minimum cost flow satisfying all demands is
        to be found.

    demand: string
        Nodes of the graph G are expected to have an attribute demand
        that indicates how much flow a node wants to send (negative
        demand) or receive (positive demand). Note that the sum of the
        demands should be 0 otherwise the problem in not feasible. If
        this attribute is not present, a node is considered to have 0
        demand. Default value: 'demand'.

    capacity: string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    weight: string
        Edges of the graph G are expected to have an attribute weight
        that indicates the cost incurred by sending one unit of flow on
        that edge. If not present, the weight is considered to be 0.
        Default value: 'weight'.

    Returns
    -------
    flowCost: integer, float
        Cost of a minimum cost flow satisfying all demands.

    flowDict: dictionary
        Dictionary of dictionaries keyed by nodes such that
        flowDict[u][v] is the flow edge (u, v).

    Raises
    ------
    NetworkXError
        This exception is raised if the input graph is not directed,
        not connected or is a multigraph.

    NetworkXUnfeasible
        This exception is raised in the following situations:
            * The sum of the demands is not zero. Then, there is no
              flow satisfying all demands.
            * There is no flow satisfying all demand.

    NetworkXUnbounded
        This exception is raised if the digraph G has a cycle of
        negative cost and infinite capacity. Then, the cost of a flow
        satisfying all demands is unbounded below.

    Notes
    -----
    This algorithm is not guaranteed to work if edge weights
    are floating point numbers (overflows and roundoff errors can 
    cause problems). 
        
    See also
    --------
    cost_of_flow, max_flow_min_cost, min_cost_flow, min_cost_flow_cost
               
    Examples
    --------
    A simple example of a min cost flow problem.

    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_node('a', demand = -5)
    >>> G.add_node('d', demand = 5)
    >>> G.add_edge('a', 'b', weight = 3, capacity = 4)
    >>> G.add_edge('a', 'c', weight = 6, capacity = 10)
    >>> G.add_edge('b', 'd', weight = 1, capacity = 9)
    >>> G.add_edge('c', 'd', weight = 2, capacity = 5)
    >>> flowCost, flowDict = nx.network_simplex(G)
    >>> flowCost
    24
    >>> flowDict # doctest: +SKIP
    {'a': {'c': 1, 'b': 4}, 'c': {'d': 1}, 'b': {'d': 4}, 'd': {}}

    The mincost flow algorithm can also be used to solve shortest path
    problems. To find the shortest path between two nodes u and v,
    give all edges an infinite capacity, give node u a demand of -1 and
    node v a demand a 1. Then run the network simplex. The value of a
    min cost flow will be the distance between u and v and edges
    carrying positive flow will indicate the path.

    >>> G=nx.DiGraph()
    >>> G.add_weighted_edges_from([('s','u',10), ('s','x',5), 
    ...                            ('u','v',1), ('u','x',2), 
    ...                            ('v','y',1), ('x','u',3), 
    ...                            ('x','v',5), ('x','y',2), 
    ...                            ('y','s',7), ('y','v',6)])
    >>> G.add_node('s', demand = -1)
    >>> G.add_node('v', demand = 1)
    >>> flowCost, flowDict = nx.network_simplex(G)
    >>> flowCost == nx.shortest_path_length(G, 's', 'v', weight = 'weight')
    True
    >>> [(u, v) for u in flowDict for v in flowDict[u] if flowDict[u][v] > 0]
    [('x', 'u'), ('s', 'x'), ('u', 'v')]
    >>> nx.shortest_path(G, 's', 'v', weight = 'weight')
    ['s', 'x', 'u', 'v']

    It is possible to change the name of the attributes used for the
    algorithm.

    >>> G = nx.DiGraph()
    >>> G.add_node('p', spam = -4)
    >>> G.add_node('q', spam = 2)
    >>> G.add_node('a', spam = -2)
    >>> G.add_node('d', spam = -1)
    >>> G.add_node('t', spam = 2)
    >>> G.add_node('w', spam = 3)
    >>> G.add_edge('p', 'q', cost = 7, vacancies = 5)
    >>> G.add_edge('p', 'a', cost = 1, vacancies = 4)
    >>> G.add_edge('q', 'd', cost = 2, vacancies = 3)
    >>> G.add_edge('t', 'q', cost = 1, vacancies = 2)
    >>> G.add_edge('a', 't', cost = 2, vacancies = 4)
    >>> G.add_edge('d', 'w', cost = 3, vacancies = 4)
    >>> G.add_edge('t', 'w', cost = 4, vacancies = 1)
    >>> flowCost, flowDict = nx.network_simplex(G, demand = 'spam',
    ...                                         capacity = 'vacancies',
    ...                                         weight = 'cost')
    >>> flowCost
    37
    >>> flowDict  # doctest: +SKIP
    {'a': {'t': 4}, 'd': {'w': 2}, 'q': {'d': 1}, 'p': {'q': 2, 'a': 2}, 't': {'q': 1, 'w': 1}, 'w': {}}

    References
    ----------
    W. J. Cook, W. H. Cunningham, W. R. Pulleyblank and A. Schrijver.
    Combinatorial Optimization. Wiley-Interscience, 1998.

    """

    if not G.is_directed():
        raise nx.NetworkXError("Undirected graph not supported.")
    if not nx.is_connected(G.to_undirected()):
        raise nx.NetworkXError("Not connected graph not supported.")
    if G.is_multigraph():
        raise nx.NetworkXError("MultiDiGraph not supported.")
    if sum(d[demand] for v, d in G.nodes(data = True) 
           if demand in d) != 0:
        raise nx.NetworkXUnfeasible("Sum of the demands should be 0.")

    # Fix an arbitrarily chosen root node and find an initial tree solution.
    H, T, y, artificialEdges, flowCost, r = \
            _initial_tree_solution(G, demand = demand, capacity = capacity,
                                   weight = weight)

    # Initialize the reduced costs.
    c = {}
    for u, v, d in H.edges_iter(data = True):
        c[(u, v)] = d.get(weight, 0) + y[u] - y[v]

    # Print stuff for debugging.
    # print('-' * 78)
    # nbIter = 0
    # print('Iteration %d' % nbIter)
    # nbIter += 1
    # print('Tree solution: %s' % T.edges())
    # print(' Edge %11s%10s' % ('Flow', 'Red Cost'))
    # for u, v, d in H.edges(data = True):
    #     flag = ''
    #     if (u, v) in artificialEdges:
    #         flag = '*'
    #     print('(%s, %s)%1s%10d%10d' % (u, v, flag, d.get('flow', 0),
    #                                    c[(u, v)]))
    # print('Distances: %s' % y)

    # Main loop.
    while True:
        newEdge = _find_entering_edge(H, c, capacity = capacity)
        if not newEdge:
            break # Optimal basis found. Main loop is over.
        cycleCost = abs(c[newEdge])

        # Find the cycle created by adding newEdge to T.
        path1 = nx.shortest_path(T.to_undirected(), r, newEdge[0])
        path2 = nx.shortest_path(T.to_undirected(), r, newEdge[1])
        join = r
        for index, node in enumerate(path1[1:]):
            if index + 1 < len(path2) and node == path2[index + 1]:
                join = node
            else:
                break
        path1 = path1[path1.index(join):]
        path2 = path2[path2.index(join):]
        cycle = []
        if H[newEdge[0]][newEdge[1]].get('flow', 0) == 0:
            path2.reverse()
            cycle = path1 + path2
        else: # newEdge is at capacity
            path1.reverse()
            cycle = path2 + path1

        # Find the leaving edge. Will stop here if cycle is an infinite
        # capacity negative cost cycle.
        leavingEdge, eps = _find_leaving_edge(H, T, cycle, newEdge,
                                              capacity = capacity)

        # Actual augmentation happens here. If eps = 0, don't bother.
        if eps:
            flowCost -= cycleCost * eps
            if len(cycle) == 3:
                u, v = newEdge
                H[u][v]['flow'] -= eps
                H[v][u]['flow'] -= eps
            else:
                for index, u in enumerate(cycle[:-1]):
                    v = cycle[index + 1]
                    if (u, v) in T.edges() + [newEdge]:
                        H[u][v]['flow'] = H[u][v].get('flow', 0) + eps
                    else: # (v, u) in T.edges():
                        H[v][u]['flow'] -= eps

        # Update tree solution.
        T.add_edge(*newEdge)
        T.remove_edge(*leavingEdge)

        # Update distances and reduced costs.
        if newEdge != leavingEdge:
            forest = nx.DiGraph(T)
            forest.remove_edge(*newEdge)
            R, notR = nx.connected_component_subgraphs(forest.to_undirected())
            if r in notR.nodes(): # make sure r is in R
                R, notR = notR, R
            if newEdge[0] in R.nodes():
                for v in notR.nodes():
                    y[v] += c[newEdge]
            else:
                for v in notR.nodes():
                    y[v] -= c[newEdge]
            for u, v in H.edges():
                if u in notR.nodes() or v in notR.nodes():
                    c[(u, v)] = H[u][v].get(weight, 0) + y[u] - y[v]

        # Print stuff for debugging.
        # print('-' * 78)
        # print('Iteration %d' % nbIter)
        # nbIter += 1
        # print('Tree solution: %s' % T.edges())
        # print('New edge:      (%s, %s)' % (newEdge[0], newEdge[1]))
        # print('Leaving edge:  (%s, %s)' % (leavingEdge[0], leavingEdge[1]))
        # print('Cycle:         %s' % cycle)
        # print('eps:           %d' % eps)
        # print(' Edge %11s%10s' % ('Flow', 'Red Cost'))
        # for u, v, d in H.edges(data = True):
        #     flag = ''
        #     if (u, v) in artificialEdges:
        #         flag = '*'
        #     print('(%s, %s)%1s%10d%10d' % (u, v, flag, d.get('flow', 0),
        #                                    c[(u, v)]))
        # print('Distances: %s' % y)


    # If an artificial edge has positive flow, the initial problem was
    # not feasible.
    for u, v in artificialEdges:
        if H[u][v]['flow'] != 0:
            raise nx.NetworkXUnfeasible("No flow satisfying all demands.")
        H.remove_edge(u, v)

    for u in H.nodes():
        if not u in G:
            H.remove_node(u)

    flowDict = _create_flow_dict(G, H)

    return flowCost, flowDict


def min_cost_flow_cost(G, demand = 'demand', capacity = 'capacity',
                        weight = 'weight'):
    """Find the cost of a minimum cost flow satisfying all demands in digraph G.
    
    G is a digraph with edge costs and capacities and in which nodes
    have demand, i.e., they want to send or receive some amount of
    flow. A negative demand means that the node wants to send flow, a
    positive demand means that the node want to receive flow. A flow on
    the digraph G satisfies all demand if the net flow into each node
    is equal to the demand of that node.

    Parameters
    ----------
    G : NetworkX graph
        DiGraph on which a minimum cost flow satisfying all demands is
        to be found.

    demand: string
        Nodes of the graph G are expected to have an attribute demand
        that indicates how much flow a node wants to send (negative
        demand) or receive (positive demand). Note that the sum of the
        demands should be 0 otherwise the problem in not feasible. If
        this attribute is not present, a node is considered to have 0
        demand. Default value: 'demand'.

    capacity: string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    weight: string
        Edges of the graph G are expected to have an attribute weight
        that indicates the cost incurred by sending one unit of flow on
        that edge. If not present, the weight is considered to be 0.
        Default value: 'weight'.

    Returns
    -------
    flowCost: integer, float
        Cost of a minimum cost flow satisfying all demands.

    Raises
    ------
    NetworkXError
        This exception is raised if the input graph is not directed or
        not connected.

    NetworkXUnfeasible
        This exception is raised in the following situations:
            * The sum of the demands is not zero. Then, there is no
              flow satisfying all demands.
            * There is no flow satisfying all demand.

    NetworkXUnbounded
        This exception is raised if the digraph G has a cycle of
        negative cost and infinite capacity. Then, the cost of a flow
        satisfying all demands is unbounded below.
        
    See also
    --------
    cost_of_flow, max_flow_min_cost, min_cost_flow, network_simplex

    Examples
    --------
    A simple example of a min cost flow problem.

    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_node('a', demand = -5)
    >>> G.add_node('d', demand = 5)
    >>> G.add_edge('a', 'b', weight = 3, capacity = 4)
    >>> G.add_edge('a', 'c', weight = 6, capacity = 10)
    >>> G.add_edge('b', 'd', weight = 1, capacity = 9)
    >>> G.add_edge('c', 'd', weight = 2, capacity = 5)
    >>> flowCost = nx.min_cost_flow_cost(G)
    >>> flowCost
    24
    """
    return network_simplex(G, demand = demand, capacity = capacity,
                           weight = weight)[0]


def min_cost_flow(G, demand = 'demand', capacity = 'capacity',
                  weight = 'weight'):
    """Return a minimum cost flow satisfying all demands in digraph G.
    
    G is a digraph with edge costs and capacities and in which nodes
    have demand, i.e., they want to send or receive some amount of
    flow. A negative demand means that the node wants to send flow, a
    positive demand means that the node want to receive flow. A flow on
    the digraph G satisfies all demand if the net flow into each node
    is equal to the demand of that node.

    Parameters
    ----------
    G : NetworkX graph
        DiGraph on which a minimum cost flow satisfying all demands is
        to be found.

    demand: string
        Nodes of the graph G are expected to have an attribute demand
        that indicates how much flow a node wants to send (negative
        demand) or receive (positive demand). Note that the sum of the
        demands should be 0 otherwise the problem in not feasible. If
        this attribute is not present, a node is considered to have 0
        demand. Default value: 'demand'.

    capacity: string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    weight: string
        Edges of the graph G are expected to have an attribute weight
        that indicates the cost incurred by sending one unit of flow on
        that edge. If not present, the weight is considered to be 0.
        Default value: 'weight'.

    Returns
    -------
    flowDict: dictionary
        Dictionary of dictionaries keyed by nodes such that
        flowDict[u][v] is the flow edge (u, v).

    Raises
    ------
    NetworkXError
        This exception is raised if the input graph is not directed or
        not connected.

    NetworkXUnfeasible
        This exception is raised in the following situations:
            * The sum of the demands is not zero. Then, there is no
              flow satisfying all demands.
            * There is no flow satisfying all demand.

    NetworkXUnbounded
        This exception is raised if the digraph G has a cycle of
        negative cost and infinite capacity. Then, the cost of a flow
        satisfying all demands is unbounded below.
        
    See also
    --------
    cost_of_flow, max_flow_min_cost, min_cost_flow_cost, network_simplex

    Examples
    --------
    A simple example of a min cost flow problem.

    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_node('a', demand = -5)
    >>> G.add_node('d', demand = 5)
    >>> G.add_edge('a', 'b', weight = 3, capacity = 4)
    >>> G.add_edge('a', 'c', weight = 6, capacity = 10)
    >>> G.add_edge('b', 'd', weight = 1, capacity = 9)
    >>> G.add_edge('c', 'd', weight = 2, capacity = 5)
    >>> flowDict = nx.min_cost_flow(G)
    >>> flowDict
    {'a': {'c': 1, 'b': 4}, 'c': {'d': 1}, 'b': {'d': 4}, 'd': {}}
    """
    return network_simplex(G, demand = demand, capacity = capacity,
                           weight = weight)[1]


def cost_of_flow(G, flowDict, weight = 'weight'):
    """Compute the cost of the flow given by flowDict on graph G.

    Note that this function does not check for the validity of the
    flow flowDict. This function will fail if the graph G and the
    flow don't have the same edge set.

    Parameters
    ----------
    G : NetworkX graph
        DiGraph on which a minimum cost flow satisfying all demands is
        to be found.

    weight: string
        Edges of the graph G are expected to have an attribute weight
        that indicates the cost incurred by sending one unit of flow on
        that edge. If not present, the weight is considered to be 0.
        Default value: 'weight'.

    flowDict: dictionary
        Dictionary of dictionaries keyed by nodes such that
        flowDict[u][v] is the flow edge (u, v).

    Returns
    -------
    cost: Integer, float
        The total cost of the flow. This is given by the sum over all
        edges of the product of the edge's flow and the edge's weight.

    See also
    --------
    max_flow_min_cost, min_cost_flow, min_cost_flow_cost, network_simplex
    """
    return sum((flowDict[u][v] * d.get(weight, 0)
                for u, v, d in G.edges_iter(data = True)))


def max_flow_min_cost(G, s, t, capacity = 'capacity', weight = 'weight'):
    """Return a maximum (s, t)-flow of minimum cost.
    
    G is a digraph with edge costs and capacities. There is a source
    node s and a sink node t. This function finds a maximum flow from
    s to t whose total cost is minimized.

    Parameters
    ----------
    G : NetworkX graph
        DiGraph on which a minimum cost flow satisfying all demands is
        to be found.

    s: node label
        Source of the flow.

    t: node label
        Destination of the flow.

    capacity: string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    weight: string
        Edges of the graph G are expected to have an attribute weight
        that indicates the cost incurred by sending one unit of flow on
        that edge. If not present, the weight is considered to be 0.
        Default value: 'weight'.

    Returns
    -------
    flowDict: dictionary
        Dictionary of dictionaries keyed by nodes such that
        flowDict[u][v] is the flow edge (u, v).

    Raises
    ------
    NetworkXError
        This exception is raised if the input graph is not directed or
        not connected.

    NetworkXUnbounded
        This exception is raised if there is an infinite capacity path
        from s to t in G. In this case there is no maximum flow. This
        exception is also raised if the digraph G has a cycle of
        negative cost and infinite capacity. Then, the cost of a flow
        is unbounded below.

    See also
    --------
    cost_of_flow, ford_fulkerson, min_cost_flow, min_cost_flow_cost,
    network_simplex

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> G.add_edges_from([(1, 2, {'capacity': 12, 'weight': 4}),
    ...                   (1, 3, {'capacity': 20, 'weight': 6}),
    ...                   (2, 3, {'capacity': 6, 'weight': -3}),
    ...                   (2, 6, {'capacity': 14, 'weight': 1}),
    ...                   (3, 4, {'weight': 9}),
    ...                   (3, 5, {'capacity': 10, 'weight': 5}),
    ...                   (4, 2, {'capacity': 19, 'weight': 13}),
    ...                   (4, 5, {'capacity': 4, 'weight': 0}),
    ...                   (5, 7, {'capacity': 28, 'weight': 2}),
    ...                   (6, 5, {'capacity': 11, 'weight': 1}),
    ...                   (6, 7, {'weight': 8}),
    ...                   (7, 4, {'capacity': 6, 'weight': 6})])
    >>> mincostFlow = nx.max_flow_min_cost(G, 1, 7)
    >>> nx.cost_of_flow(G, mincostFlow)
    373
    >>> maxFlow = nx.ford_fulkerson_flow(G, 1, 7)
    >>> nx.cost_of_flow(G, maxFlow)
    428
    >>> mincostFlowValue = (sum((mincostFlow[u][7] for u in G.predecessors(7)))
    ...                     - sum((mincostFlow[7][v] for v in G.successors(7))))
    >>> mincostFlowValue == nx.max_flow(G, 1, 7)
    True
    
    
    """
    maxFlow = nx.max_flow(G, s, t, capacity = capacity)
    H = nx.DiGraph(G)
    H.add_node(s, demand = -maxFlow)
    H.add_node(t, demand = maxFlow)
    return min_cost_flow(H, capacity = capacity, weight = weight)

