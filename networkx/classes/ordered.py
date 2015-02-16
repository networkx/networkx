"""
OrderedDict variants of the default base classes.

"""
try:
    # Python 2.7+
    from collections import OrderedDict
except ImportError:
    # Oython 2.6
    try:
        from ordereddict import OrderedDict
    except ImportError:
        OrderedDict = None

from .graph import Graph
from .multigraph import MultiGraph
from .digraph import DiGraph
from .multidigraph import MultiDiGraph

__all__ = []

if OrderedDict is not None:
    __all__.extend([
    'OrderedGraph',
    'OrderedDiGraph',
    'OrderedMultiGraph',
    'OrderedMultiDiGraph'
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
