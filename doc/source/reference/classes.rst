.. _classes:

***********
Graph types
***********

NetworkX provides data structures and methods for storing graphs.

All NetworkX graph classes allow (hashable) Python objects as nodes.
Any Python object can be assigned to edges.  The choice of
graph class depends on the structure of the graph you want to represent.   


Basic graph types
=================

.. currentmodule:: networkx

.. toctree::
   :maxdepth: 1

   classes.graph
   classes.digraph
   classes.multigraph
   classes.multidigraph

Graphs with attributes
======================

The basic graph classes listed above allow arbitrary data to
be stored as nodes or edges.  In some cases (e.g. graph drawing)
a more specific interface to graph, node, and edges is useful.
The following classes provide explicit methods for adding, modifying,
and removing attributes for graphs, nodes, and edges.


.. toctree::
   :maxdepth: 1

   classes.attrgraph

.. warning::
   
   The attribute graph classes are experimental.  The functionality
   and API are subject to change.


Which graph class should I use?
===============================

===================  ========================
Graph Type           NetworkX Class
===================  ========================
Undirected Simple    Graph
Directed Simple      DiGraph
Self loops           Graph, DiGraph 
Parallel edges       MultiGraph, MultiDiGraph
===================  ========================



