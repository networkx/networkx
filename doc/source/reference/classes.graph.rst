.. _graph:

=====
Graph
=====

Overview
--------
.. currentmodule:: networkx
.. autoclass:: Graph

Adding and Removing Nodes and Edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   Graph.add_node
   Graph.add_nodes_from
   Graph.remove_node
   Graph.remove_nodes_from
   Graph.add_edge
   Graph.add_edges_from
   Graph.remove_edge
   Graph.remove_edges_from
   Graph.add_star
   Graph.add_path
   Graph.add_cycle
   Graph.clear



Iterating over nodes and edges
------------------------------
.. autosummary::
   :toctree: generated/

   Graph.nodes
   Graph.nodes_iter
   Graph.__iter__
   Graph.edges
   Graph.edges_iter
   Graph.get_edge
   Graph.neighbors
   Graph.neighbors_iter
   Graph.__getitem__
   Graph.adjacency_list
   Graph.adjacency_iter
   Graph.nbunch_iter



Information about graph structure
---------------------------------
.. autosummary::
   :toctree: generated/

   Graph.has_node
   Graph.__contains__
   Graph.has_edge
   Graph.has_neighbor
   Graph.nodes_with_selfloops
   Graph.selfloop_edges
   Graph.order
   Graph.number_of_nodes
   Graph.__len__
   Graph.size
   Graph.number_of_edges
   Graph.number_of_selfloops
   Graph.degree
   Graph.degree_iter


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   Graph.copy
   Graph.to_directed
   Graph.subgraph




