.. _classes:

***********
Graph types
***********

NetworkX provides data structures and methods for storing graphs.

All NetworkX graph classes allow (hashable) Python objects as nodes.
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
	
   classes.graph
   classes.digraph
   classes.multigraph
   classes.multidigraph

.. note:: NetworkX uses `dicts` to store the nodes and neighbors in a graph.
   So the reporting of nodes and edges for the base graph classes will not
   necessarily be the same as the order in which they were created.  If you
   need the order preserved (e.g., when writing automated tests), please see
   `OrderedGraph`, `OrderedDiGraph`, `OrderedMultiGraph`, or
   `OrderedMultiDiGraph`, which behave like the base graph classes but
   preserve the order in which nodes and edges are added.
