# -*- coding: utf-8 -*-
"""
Maximum flow (and minimum cut) algorithms on capacitated graphs.
"""
import networkx as nx

# Define the default flow function for computing maximum flow.
from .preflow_push import preflow_push
default_flow_func = preflow_push

__all__ = ['maximum_flow',
           'minimum_cut',
           'max_flow',
           'min_cut']


def maximum_flow(G, s, t, capacity='capacity', flow_func=None, 
                 value_only=True, **kwargs):
    """Find a maximum single-commodity flow.
    
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

    flow_func : function
        A function for computing the maximum flow among a pair of nodes 
        in a capacitated graph. The function has to accept at least three 
        parameters: a Graph or Digraph, a source node, and a target node. 
        And return a residual network that follows NetworkX conventions
        (see Notes). If flow_func is None the default maximum 
        flow function (:meth:`preflow_push`) is used. See below for 
        alternative algorithms. Default value: None.

    value_only : boolean
        If True compute only the value of the maximum flow. If False 
        compute the actual flows. Default value: True.

    kwargs : Any other keyword parameter is passed to the function that
        computes the maximum flow.

    Returns
    -------
    flow_value : integer, float
        Value of the maximum flow, i.e., net outflow from the source if
        value_only is True.

    flow_dict : dict
        A dictionary containing the value of the flow that went through
        each edge if value_only is False.

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
    :meth:`minimum_cut`
    :meth:`edmonds_karp`
    :meth:`ford_fulkerson`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    Notes
    -----
    The function used in the flow_func paramter has to return a residual
    network that follows NetworkX conventions:

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

    The legacy :meth:`ford_fulkerson` maximum flow implementation doesn't
    follow this conventions but it is supported as a valid flow_func.

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

    By default maximum_flow computes only the value of the
    maximum flow:

    >>> flow_value = nx.maximum_flow(G, 'x', 'y')
    >>> flow_value
    3.0

    If you want to compute all flows, you have to set to False the
    parameter value_only:

    >>> flow_dict = nx.maximum_flow(G, 'x', 'y', value_only=False)
    >>> print(flow_dict['x']['b'])
    1.0

    You can also use alternative algorithms for computing the 
    maximum flow by using the flow_func parameter.

    >>> assert(flow_value == 
    ...         nx.maximum_flow(G, 'x', 'y', 
    ...                         flow_func=nx.shortest_augmenting_path))

    """
    if flow_func is None:
        flow_func = default_flow_func

    if not callable(flow_func):
        raise nx.NetworkXError("flow_func has to be callable")

    # Handle legacy ford_fulkerson
    if flow_func is nx.ford_fulkerson:
        flow_value, flow_dict = flow_func(G, s, t, capacity=capacity)
        if value_only:
            return flow_value
        return flow_dict

    R = flow_func(G, s, t, capacity=capacity, value_only=value_only, **kwargs)

    if value_only:
        return R.node[t]['excess']

    # Build the flow dictionary
    flow_dict = {}
    for u in G:
        flow_dict[u] = dict((v, 0) for v in G[u])
        flow_dict[u].update((v, R[u][v]['flow']) for v in R[u]
                            if R[u][v]['flow'] > 0)
    return flow_dict


def minimum_cut(G, s, t, capacity='capacity', flow_func=None, 
                value_only=True, **kwargs):
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

    capacity : string
        Edges of the graph G are expected to have an attribute capacity
        that indicates how much flow the edge can support. If this
        attribute is not present, the edge is considered to have
        infinite capacity. Default value: 'capacity'.

    flow_func : function
        A function for computing the maximum flow among a pair of nodes 
        in a capacitated graph. The function has to accept at least three 
        parameters: a Graph or Digraph, a source node, and a target node. 
        And return a residual network that follows NetworkX conventions
        (see Notes). If flow_func is None the default maximum 
        flow function (:meth:`preflow_push`) is used. See below for 
        alternative algorithms. Default value: None.

    value_only : boolean
        If True compute only the value of the minimum cut. If False compute
        the set edges that form the minimum cut. Default value: True.

    kwargs : Any other keyword parameter is passed to the function that
        computes the maximum flow.

    Returns
    -------
    cut_value : integer, float
        Value of the minimum cut if value_only is True.

    partition : pair of node sets
        A partitioning of the nodes that defines a minimum cut if
        value_only is False.
    
    Raises
    ------
    NetworkXUnbounded
        If the graph has a path of infinite capacity, all cuts have
        infinite capacity and the function raises a NetworkXError.

    See also
    --------
    maximum_flow    
    :meth:`edmonds_karp`
    :meth:`ford_fulkerson`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    Notes
    -----
    The function used in the flow_func paramter has to return a residual
    network that follows NetworkX conventions:

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

    The legacy :meth:`ford_fulkerson` maximum flow implementation doesn't
    follow this conventions but it is supported as a valid flow_func.

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

    By default minimum_cut computes only the value of the
    minimum cut:

    >>> min_cut_value = nx.minimum_cut(G, 'x', 'y')
    >>> min_cut_value
    3.0

    If you want node partition that defines the minimum cut, you
    have to set the parameter value_only to False:

    >>> partition = nx.minimum_cut(G, 'x', 'y', value_only=False)
    >>> reachable, non_reachable = partition

    'partition' here is a tuple with the two sets of nodes that define
    the minimum cut. You can compute the cut set of edges that induce
    the minimum cut as follows:
    
    >>> cutset = set()
    >>> for u, nbrs in ((n, G[n]) for n in reachable):
    ...     cutset.update((u, v) for v in nbrs if v in non_reachable)
    >>> print(sorted(cutset))
    [('c', 'y'), ('x', 'b')]
    >>> assert(min_cut_value == sum(G.edge[u][v]['capacity'] for (u, v) in cutset))

    You can also use alternative algorithms for computing the 
    minimum cut by using the flow_func parameter.

    >>> assert(min_cut_value == 
    ...         nx.minimum_cut(G, 'x', 'y', flow_func=nx.shortest_augmenting_path))

    """
    if flow_func is None:
        flow_func = default_flow_func

    if not callable(flow_func):
        raise nx.NetworkXError("flow_func has to be callable")

    # Handle legacy ford_fulkerson.
    if flow_func is nx.ford_fulkerson:
        R = flow_func(G, s, t, capacity=capacity, legacy=False)
        if value_only:
            return R.graph['flow_value']
    else:
        R = flow_func(G, s, t, capacity=capacity, value_only=value_only, 
                      **kwargs)
        if value_only:
            return R.node[t]['excess']
        # Remove saturated edges from the residual network for computing
        # the minimum cut.
        R.remove_edges_from((u, v) for u, v, d in R.edges(data=True)
                            if d['capacity'] - d['flow'] == 0)

    # Reachable and non reachable nodes from source in the 
    # residual network form the node partition that defines
    # the minimum cut.
    reachable = set(nx.single_source_shortest_path(R, s))
    non_reachable = set(G) - reachable
    return (reachable, non_reachable)


# backwards compatibility
max_flow = maximum_flow
min_cut = minimum_cut
