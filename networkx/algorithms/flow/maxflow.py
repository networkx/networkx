# -*- coding: utf-8 -*-
"""
Maximum flow (and minimum cut) algorithms on capacitated graphs.
"""

import networkx as nx
from .ford_fulkerson import ford_fulkerson_value
from .preflow_push import preflow_push_value
# Define the default flow value function for computing the maximum flow.
default_flow_value_func = ford_fulkerson_value

__all__ = ['max_flow', 'min_cut']


def max_flow(G, s, t, capacity='capacity', flow_func=None):
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

    flow_func : Maximum Flow function (default=None)
        A function for computing the maximum flow among a pair of nodes 
        in a capacitated graph. The function has to accept three parameters:
        a Graph or Digraph, a source node, and a target node. And return 
        the maximum flow value. If flow_func is None the default maximum 
        flow function (:doc:`networkx.algorithms.flow.ford_fulkerson_value`) 
        is used. An alternative function you can use is 
        :doc:`networkx.algorithms.flow.preflow_push_value`.

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
    >>> flow = nx.max_flow(G, 'x', 'y')
    >>> flow
    3.0

    """
    if flow_func is None:
        flow_func = default_flow_value_func
    return flow_func(G, s, t, capacity=capacity)


def min_cut(G, s, t, capacity='capacity', flow_func=None):
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

    flow_func : Maximum Flow function (default=None)
        A function for computing the maximum flow among a pair of nodes 
        in a capacitated graph. The function has to accept three parameters:
        a Graph or Digraph, a source node, and a target node. And return 
        the maximum flow value. If flow_func is None the default maximum 
        flow function (:doc:`networkx.algorithms.flow.ford_fulkerson_value`) 
        is used. An alternative function you can use is 
        :doc:`networkx.algorithms.flow.preflow_push_value`.

    Returns
    -------
    cut_value : integer, float
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
    if flow_func is None:
        flow_func = default_flow_value_func
    return default_flow_value_func(G, s, t, capacity=capacity)
