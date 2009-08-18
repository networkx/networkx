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
		

