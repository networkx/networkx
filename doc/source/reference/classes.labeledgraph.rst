.. _labeledgraph:

=============
Labeled Graph
=============

Overview
--------
.. currentmodule:: networkx
.. autoclass:: LabeledGraph


Adding and Removing Nodes and Edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   LabeledGraph.add_node
   LabeledGraph.add_nodes_from
   LabeledGraph.remove_node
   LabeledGraph.remove_nodes_from
   LabeledGraph.add_edge
   LabeledGraph.add_edges_from
   LabeledGraph.remove_edge
   LabeledGraph.remove_edges_from
   LabeledGraph.add_star
   LabeledGraph.add_path
   LabeledGraph.add_cycle
   LabeledGraph.clear



Iterating over nodes and edges
------------------------------
.. autosummary::
   :toctree: generated/

   LabeledGraph.nodes
   LabeledGraph.nodes_iter
   LabeledGraph.__iter__
   LabeledGraph.edges
   LabeledGraph.edges_iter
   LabeledGraph.get_edge
   LabeledGraph.neighbors
   LabeledGraph.neighbors_iter
   LabeledGraph.__getitem__
   LabeledGraph.adjacency_list
   LabeledGraph.adjacency_iter
   LabeledGraph.nbunch_iter



Information about graph structure
---------------------------------
.. autosummary::
   :toctree: generated/

   LabeledGraph.has_node
   LabeledGraph.__contains__
   LabeledGraph.has_edge
   LabeledGraph.has_neighbor
   LabeledGraph.nodes_with_selfloops
   LabeledGraph.selfloop_edges
   LabeledGraph.order
   LabeledGraph.number_of_nodes
   LabeledGraph.__len__
   LabeledGraph.size
   LabeledGraph.number_of_edges
   LabeledGraph.number_of_selfloops
   LabeledGraph.degree
   LabeledGraph.degree_iter


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   LabeledGraph.copy
   LabeledGraph.to_directed
   LabeledGraph.subgraph




