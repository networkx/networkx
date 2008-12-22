.. _labeleddigraph:

===============
Labeled DiGraph
===============

Overview
--------
.. currentmodule:: networkx
.. autoclass:: LabeledDiGraph


Adding and Removing Nodes and Edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   LabeledDiGraph.add_node
   LabeledDiGraph.add_nodes_from
   LabeledDiGraph.remove_node
   LabeledDiGraph.remove_nodes_from
   LabeledDiGraph.add_edge
   LabeledDiGraph.add_edges_from
   LabeledDiGraph.remove_edge
   LabeledDiGraph.remove_edges_from
   LabeledDiGraph.add_star
   LabeledDiGraph.add_path
   LabeledDiGraph.add_cycle
   LabeledDiGraph.clear



Iterating over nodes and edges
------------------------------
.. autosummary::
   :toctree: generated/

   LabeledDiGraph.nodes
   LabeledDiGraph.nodes_iter
   LabeledDiGraph.__iter__
   LabeledDiGraph.edges
   LabeledDiGraph.edges_iter
   LabeledDiGraph.get_edge_data
   LabeledDiGraph.neighbors
   LabeledDiGraph.neighbors_iter
   LabeledDiGraph.__getitem__
   LabeledDiGraph.successors
   LabeledDiGraph.successors_iter
   LabeledDiGraph.predecessors
   LabeledDiGraph.predecessors_iter
   LabeledDiGraph.adjacency_list
   LabeledDiGraph.adjacency_iter
   LabeledDiGraph.nbunch_iter


Information about graph structure
---------------------------------
.. autosummary::
   :toctree: generated/

   LabeledDiGraph.has_node
   LabeledDiGraph.__contains__
   LabeledDiGraph.has_edge
   LabeledDiGraph.has_neighbor
   LabeledDiGraph.nodes_with_selfloops
   LabeledDiGraph.selfloop_edges
   LabeledDiGraph.order
   LabeledDiGraph.number_of_nodes
   LabeledDiGraph.__len__
   LabeledDiGraph.size
   LabeledDiGraph.number_of_edges
   LabeledDiGraph.number_of_selfloops
   LabeledDiGraph.degree
   LabeledDiGraph.degree_iter


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   LabeledDiGraph.copy
   LabeledDiGraph.to_undirected
   LabeledDiGraph.subgraph
   LabeledDiGraph.reverse

