"""
Dynamic Networks.
"""

import inspect
import itertools
from collections.abc import Callable, Generator

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = (
    "gradient_network",
    "gradient_network_sequence",
)


def _positional_param_count(func: Callable) -> int | None:
    try:
        params = [
            p
            for p in inspect.signature(func).parameters.values()
            if p.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
            and p.default is inspect.Parameter.empty
        ]
        return len(params)
    except (ValueError, TypeError):
        return None


def _node_value_function(scalar_field_value):
    if callable(scalar_field_value):
        num_pos = _positional_param_count(scalar_field_value)
        if num_pos == 0:
            return lambda n, d: scalar_field_value()
        if num_pos == 1:
            return lambda n, d: scalar_field_value(n)
        if num_pos == 2:
            return scalar_field_value
        return lambda n, d: scalar_field_value(n, d)

    def attr_getter(n, d):
        val = d.get(scalar_field_value, 0)
        return val() if callable(val) else val

    return attr_getter


def _edge_distance_function(distance):
    if callable(distance):
        num_pos = _positional_param_count(distance)
        if num_pos == 0:
            return lambda u, v, d: distance()
        if num_pos == 1:
            return lambda u, v, d: distance(d)
        if num_pos == 2:
            return lambda u, v, d: distance(u, v)
        if num_pos == 3:
            return distance
        return lambda u, v, d: distance(u, v, d)

    def attr_getter(u, v, d):
        val = d.get(distance, 1.0)
        return val() if callable(val) else val

    return attr_getter


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable(
    node_attrs="scalar_field_value",
    edge_attrs="scalar_field_distance",
    returns_graph=True,
)
def gradient_network(
    G,
    scalar_field_value: str | Callable = "value",
    scalar_field_distance: str | Callable = "distance",
    ascending: bool = True,
) -> nx.DiGraph:
    r"""Returns a Gradient Network graph of an input substrate network graph.

    In network science, a Gradient Network is a directed subnetwork of an undirected
    "substrate" network where each node has an associated scalar potential and one
    out-link that points to the node with the largest (or smallest) potential in its
    neighborhood, defined as the union of itself and its neighbors on the substrate
    network [1]_, [2]_.

    ::

        Substrate Network (undirected):

               [h_1 = 3]
                 ( n1 )
                  /
                ( u ) --------- distance d --------- ( v )   <-- max potential in N(u) U {u}
              [h_u = 2] \                          [h_v = 8]
                         ( n2 )
                       [h_2 = 5]

            scalar_field_value:    supplies node potentials h_u, h_v, ...
            scalar_field_distance: supplies edge distance d between neighbors

        Gradient Network (directed, ascending):

                ( u ) ================ size ===============> ( v )
                             size = |h_u - h_v| / distance

    Parameters
    ----------
    G : NetworkX Graph
        Substrate network graph. Does not support directed graphs and multigraphs.
        The graph nodes should have an attribute as a source for the scalar field value.
        A node attribute may be either a `Number` (e.g. int, float, etc.) or a
        `Callable` that returns a Number.
        The graph edges may have an attribute as a source of a `distance` value.
        An edge `distance` attribute may be either a `Number` or a `Callable` that
        returns a Number.
    scalar_field_value : str or Callable, default 'value'
        The attribute name for the source of each node's scalar field value,
        or a callable that supplies the scalar value given ``(node, data)``,
        ``(node)``, or parameterless.
    scalar_field_distance : str or Callable, default 'distance'
        The attribute name for the source of the edge distance, or a callable
        that supplies the distance value given ``(u, v, data)`` or parameterless.
    ascending : bool, default True
        Choose an ascending (True) or descending (False) gradient graph.

    Returns
    -------
    NetworkX DiGraph
        The Gradient Network graph of the input substrate graph. Edge attribute
        ``size`` contains the normalized gradient magnitude ``|h_u - h_v| / distance``.
        Every node has an out-degree of 1. If a node is a local extremum (or isolated),
        its steepest neighbor is itself, resulting in a self-loop with ``size = 0.0``
        representing a sink of the gradient flow.

    Examples
    --------
    In a star graph where the central node has the highest potential, all leaf
    nodes point to the center, and the center points to itself in an ascending
    gradient network:

    >>> G = nx.star_graph(4)
    >>> potentials = {0: 10, 1: 2, 2: 3, 3: 4, 4: 5}
    >>> nx.set_node_attributes(G, potentials, "value")
    >>> H = nx.gradient_network(G)
    >>> sorted(H.edges())
    [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
    >>> H[1][0]["size"]
    8.0
    >>> H[0][0]["size"]
    0.0

    References
    ----------
    .. [1] Toroczkai, Zoltán; Kozma, Balázs; Bassler, Kevin E; Hengartner, N W;
           Korniss, G (2008-04-02).
           "Gradient networks". Journal of Physics A: Mathematical and Theoretical.
           IOP Publishing. 41 (15): 155103. arXiv:cond-mat/0408262.
           https://doi.org/10.1088/1751-8113/41/15/155103
    .. [2] Danila, Bogdan; Yu, Yong; Earl, Samuel; Marsh, John A.; Toroczkai, Zoltán;
           Bassler, Kevin E. (2006-10-19).
           "Congestion-gradient driven transport on complex networks".
           Physical Review E. 74 (4): 046114. arXiv:cond-mat/0603861.
           https://doi.org/10.1103/physreve.74.046114
    .. [3] "Gradient network", Wikipedia, https://en.wikipedia.org/wiki/Gradient_network
    """
    node_val_func = _node_value_function(scalar_field_value)
    node_values = {node: node_val_func(node, data) for node, data in G.nodes(data=True)}

    edge_dist_func = _edge_distance_function(scalar_field_distance)

    H = nx.DiGraph()
    H.add_nodes_from(G)

    scalar_operation = max if ascending else min
    for node in G:
        node_val = node_values[node]
        nbrs_and_self = itertools.chain(G.neighbors(node), (node,))
        neighbor = scalar_operation(nbrs_and_self, key=node_values.__getitem__)
        neighbor_val = node_values[neighbor]

        if node == neighbor:
            distance = 1.0
        else:
            distance = edge_dist_func(node, neighbor, G[node][neighbor])
            if callable(distance):
                distance = distance()
            if distance is None:
                distance = 1.0

        size = abs(node_val - neighbor_val) / distance
        H.add_edge(node, neighbor, size=size)

    return H


def _time_node_value_factory(scalar_field_value):
    if callable(scalar_field_value):
        num_pos = _positional_param_count(scalar_field_value)
        if num_pos == 1:
            return lambda t: lambda n, d: scalar_field_value(t)
        if num_pos == 2:
            return lambda t: lambda n, d: scalar_field_value(n, t)
        return lambda t: lambda n, d: scalar_field_value(n, d, t)

    def bind_t(t):
        def val_func_from_attr(node, data):
            val = data.get(scalar_field_value, 0)
            if isinstance(val, dict):
                return val.get(t, 0)
            if callable(val):
                try:
                    return val(t)
                except TypeError:
                    return val()
            return val

        return val_func_from_attr

    return bind_t


def _time_edge_distance_factory(distance):
    if callable(distance):
        num_pos = _positional_param_count(distance)
        if num_pos == 1:
            return lambda t: lambda u, v, d: distance(t)
        if num_pos == 3:
            return lambda t: lambda u, v, d: distance(u, v, t)
        return lambda t: lambda u, v, d: distance(u, v, d, t)

    def bind_t(t):
        def dist_func_from_attr(u, v, data):
            val = data.get(distance, 1.0)
            if isinstance(val, dict):
                return val.get(t, 1.0)
            if callable(val):
                try:
                    return val(t)
                except TypeError:
                    return val()
            return val if val is not None else 1.0

        return dist_func_from_attr

    return bind_t


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable(
    node_attrs="scalar_field_value",
    edge_attrs="scalar_field_distance",
)
def gradient_network_sequence(
    G,
    times,
    scalar_field_value: str | Callable = "value",
    scalar_field_distance: str | Callable = "distance",
    ascending: bool = True,
) -> Generator[tuple[object, nx.DiGraph], None, None]:
    r"""Yields time-synchronized gradient network snapshots over an iterable of times.

    In dynamic network systems, node potentials and edge distances may evolve over
    time due to flow, sources, and sinks on the network [1]_, [2]_. For each time
    step $t$ in `times`, this generator synchronizes the potential field across all
    nodes and edges to time $t$ and yields the pair ``(t, H_t)``, where $H_t$ is
    the directed gradient network snapshot at that time.

    The yielded graph $H_t$ also stores the timestamp in its graph attributes
    dict as ``H_t.graph["time"] = t``.

    Parameters
    ----------
    G : NetworkX Graph
        Substrate network graph. Does not support directed graphs and multigraphs.
    times : Iterable
        An iterable of time points (e.g. integers, floats, or timestamps) at which
        to evaluate the gradient network.
    scalar_field_value : str or Callable, default 'value'
        Source of each node's scalar field value across time.
        If a callable, it may accept ``(node, data, t)``, ``(node, t)``, or ``(t)``.
        If a string, node attribute values may be a dictionary mapping time $t$ to
        a scalar value, a callable accepting time $t$, or a static value.
    scalar_field_distance : str or Callable, default 'distance'
        Source of edge distance across time.
        If a callable, it may accept ``(u, v, data, t)``, ``(u, v, t)``, or ``(t)``.
        If a string, edge attribute values may be a dictionary mapping time $t$ to
        a distance, a callable accepting time $t$, or a static value.
    ascending : bool, default True
        Choose an ascending (True) or descending (False) gradient graph.

    Yields
    ------
    t : object
        The current time point from `times`.
    H : NetworkX DiGraph
        The gradient network snapshot at time $t$.

    Examples
    --------
    Simulate a network where the peak potential moves over time:

    >>> G = nx.star_graph(2)
    >>> potentials = {
    ...     0: {0: 10.0, 1: 0.0},
    ...     1: {0: 1.0, 1: 5.0},
    ...     2: {0: 2.0, 1: 2.0},
    ... }
    >>> nx.set_node_attributes(G, potentials, "value")
    >>> snapshots = list(nx.gradient_network_sequence(G, times=[0, 1]))
    >>> snapshots[0][0]
    0
    >>> sorted(snapshots[0][1].edges())
    [(0, 0), (1, 0), (2, 0)]
    >>> snapshots[1][0]
    1
    >>> sorted(snapshots[1][1].edges())
    [(0, 1), (1, 1), (2, 2)]

    References
    ----------
    .. [1] Toroczkai, Zoltán; Kozma, Balázs; Bassler, Kevin E; Hengartner, N W;
           Korniss, G (2008-04-02).
           "Gradient networks". Journal of Physics A: Mathematical and Theoretical.
           IOP Publishing. 41 (15): 155103. arXiv:cond-mat/0408262.
           https://doi.org/10.1088/1751-8113/41/15/155103
    .. [2] Danila, Bogdan; Yu, Yong; Earl, Samuel; Marsh, John A.; Toroczkai, Zoltán;
           Bassler, Kevin E. (2006-10-19).
           "Congestion-gradient driven transport on complex networks".
           Physical Review E. 74 (4): 046114. arXiv:cond-mat/0603861.
           https://doi.org/10.1103/physreve.74.046114
    """
    node_val_factory = _time_node_value_factory(scalar_field_value)
    edge_dist_factory = _time_edge_distance_factory(scalar_field_distance)

    for t in times:
        val_func = node_val_factory(t)
        dist_func = edge_dist_factory(t)
        H = gradient_network(
            G,
            scalar_field_value=val_func,
            scalar_field_distance=dist_func,
            ascending=ascending,
        )
        H.graph["time"] = t
        yield t, H
