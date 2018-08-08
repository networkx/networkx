.. _classes:

***********
Graph types
***********

NetworkX provides data structures and methods for storing graphs.

All NetworkX graph classes allow (hashable) Python objects as nodes
and any Python object can be assigned as an edge attribute.

The choice of graph class depends on the structure of the
graph you want to represent.

Which graph class should I use?
===============================

===================  ========================
Graph Type           NetworkX Class
===================  ========================
Undirected Simple    Graph
Directed Simple      DiGraph
With Self-loops      Graph, DiGraph
With Parallel edges  MultiGraph, MultiDiGraph
===================  ========================

Basic graph types
=================

.. toctree::
   :maxdepth: 2

   graph
   digraph
   multigraph
   multidigraph
   ordered

.. note:: NetworkX uses `dicts` to store the nodes and neighbors in a graph.
   So the reporting of nodes and edges for the base graph classes will not
   necessarily be consistent across versions and platforms.  If you need the
   order of nodes and edges to be consistent (e.g., when writing automated
   tests), please see :class:`~networkx.OrderedGraph`,
   :class:`~networkx.OrderedDiGraph`, :class:`~networkx.OrderedMultiGraph`,
   or :class:`~networkx.OrderedMultiDiGraph`, which behave like the base
   graph classes but give a consistent order for reporting of nodes and edges.

Graph Views
===========

.. automodule:: networkx.classes.graphviews
.. autosummary::
   :toctree: generated/

   generic_graph_view
   subgraph_view
   reverse_view
