"""
OrderedDict variants of the default base classes.

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
    node_dict_factory = OrderedDict
    adjlist_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class OrderedDiGraph(DiGraph):
    node_dict_factory = OrderedDict
    adjlist_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class OrderedMultiGraph(MultiGraph):
    node_dict_factory = OrderedDict
    adjlist_dict_factory = OrderedDict
    edge_key_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict


class OrderedMultiDiGraph(MultiDiGraph):
    node_dict_factory = OrderedDict
    adjlist_dict_factory = OrderedDict
    edge_key_dict_factory = OrderedDict
    edge_attr_dict_factory = OrderedDict
