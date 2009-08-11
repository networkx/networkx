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

.. toctree::
   :maxdepth: 3
	
   classes.graph
   classes.digraph
   classes.multigraph
   classes.multidigraph
		

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



