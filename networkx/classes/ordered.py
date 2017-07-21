"""
Consistently ordered variants of the default base classes.

The Ordered (Di/Multi/MultiDi) Graphs give a consistent order for reporting of
nodes and edges.  The order of node reporting agrees with node adding, but for
edges, the order is not necessarily the order that the edges were added.

In general, you should use the default (i.e., unordered) graph classes.
However, there are times (e.g., when testing) when you may need the
order preserved.
"""
from collections import OrderedDict

from .graph import Graph
from .multigraph import MultiGraph
from .digraph import DiGraph
from .multidigraph import MultiDiGraph

__all__ = []

__all__.extend([
    'OrderedGraph',
    'OrderedDiGraph',
    'OrderedMultiGraph',
    'OrderedMultiDiGraph',
])


class OrderedGraph(Graph):
    """Consistently ordered variant of :class:`~networkx.Graph`."""
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class OrderedDiGraph(DiGraph):
    """Consistently ordered variant of :class:`~networkx.DiGraph`."""
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class OrderedMultiGraph(MultiGraph):
    """Consistently ordered variant of :class:`~networkx.MultiGraph`."""
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_key_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class OrderedMultiDiGraph(MultiDiGraph):
    """Consistently ordered variant of :class:`~networkx.MultiDiGraph`."""
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_key_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict
