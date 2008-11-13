.. _classes:

*************
Graph classes
*************

Basic Graphs
=============

The Graph and DiGraph classes provide simple graphs which
allow self-loops.
The default Graph and DiGraph are weighted graphs with 
edge weight equal to 1 but arbitrary edge data can be assigned.

.. toctree::
   :maxdepth: 1

   classes.graph
   classes.digraph

Multigraphs
===========

The MultiGraph and MultiDiGraph classes
extend the basic graphs by allowing multiple
(parallel) edges between nodes.

.. toctree::
   :maxdepth: 1

   classes.multigraph
   classes.multidigraph


Labeled Graphs
==============

The LabeledGraph and LabeledDiGraph classes
extend the basic graphs by allowing arbitrary label 
data to be assigned to nodes. 

.. toctree::
   :maxdepth: 1

   classes.labeledgraph
   classes.labeleddigraph

