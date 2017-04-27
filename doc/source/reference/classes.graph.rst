.. _graph:

==========================================
Graph -- Undirected graphs with self loops
==========================================

Overview
========
.. currentmodule:: networkx
.. autofunction:: Graph

=======
Methods
=======

Adding and removing nodes and edges
===================================

.. autosummary::
   :toctree: generated/

   Graph.__init__
   Graph.add_node
   Graph.add_nodes_from
   Graph.remove_node
   Graph.remove_nodes_from
   Graph.add_edge
   Graph.add_edges_from
   Graph.add_weighted_edges_from
   Graph.remove_edge
   Graph.remove_edges_from
   Graph.clear



Iterating over nodes and edges
==============================
.. autosummary::
   :toctree: generated/

   Graph.nodes
   Graph.__iter__
   Graph.edges
   Graph.get_edge_data
   Graph.neighbors
   Graph.__getitem__
   Graph.adjacency
   Graph.nbunch_iter



Information about graph structure
=================================
.. autosummary::
   :toctree: generated/

   Graph.has_node
   Graph.__contains__
   Graph.has_edge
   Graph.order
   Graph.number_of_nodes
   Graph.__len__
   Graph.degree
   Graph.size
   Graph.number_of_edges
   Graph.nodes_with_selfloops
   Graph.selfloop_edges
   Graph.number_of_selfloops


Making copies and subgraphs
===========================
.. autosummary::
   :toctree: generated/

   Graph.copy
   Graph.to_undirected
   Graph.to_directed
   Graph.subgraph
   Graph.edge_subgraph
