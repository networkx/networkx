"""
OrderedDict variants of the default base classes.

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
    """Ordered variant of Graph."""
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class OrderedDiGraph(DiGraph):
    """Ordered variant of DiGraph."""
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class OrderedMultiGraph(MultiGraph):
    """Ordered variant of MultiGraph."""
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_key_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class OrderedMultiDiGraph(MultiDiGraph):
    """Ordered variant of MultiDiGraph."""
    node_dict_factory = OrderedDict
    adjlist_outer_dict_factory = OrderedDict
    adjlist_inner_dict_factory = OrderedDict
    edge_key_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict
