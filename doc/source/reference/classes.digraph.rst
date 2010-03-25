.. _digraph:

=========================================
DiGraph - Directed graphs with self loops
=========================================

Overview
========
.. currentmodule:: networkx
.. autofunction:: DiGraph


Adding and removing nodes and edges
===================================

.. autosummary::
   :toctree: generated/

   DiGraph.__init__
   DiGraph.add_node
   DiGraph.add_nodes_from
   DiGraph.remove_node
   DiGraph.remove_nodes_from
   DiGraph.add_edge
   DiGraph.add_edges_from
   DiGraph.add_weighted_edges_from
   DiGraph.remove_edge
   DiGraph.remove_edges_from
   DiGraph.add_star
   DiGraph.add_path
   DiGraph.add_cycle
   DiGraph.clear



Iterating over nodes and edges
==============================
.. autosummary::
   :toctree: generated/

   DiGraph.nodes
   DiGraph.nodes_iter
   DiGraph.__iter__
   DiGraph.edges
   DiGraph.edges_iter
   DiGraph.out_edges
   DiGraph.out_edges_iter
   DiGraph.in_edges
   DiGraph.in_edges_iter
   DiGraph.get_edge_data
   DiGraph.neighbors
   DiGraph.neighbors_iter
   DiGraph.__getitem__
   DiGraph.successors
   DiGraph.successors_iter
   DiGraph.predecessors
   DiGraph.predecessors_iter
   DiGraph.adjacency_list
   DiGraph.adjacency_iter
   DiGraph.nbunch_iter


Information about graph structure
=================================
.. autosummary::
   :toctree: generated/

   DiGraph.has_node
   DiGraph.__contains__
   DiGraph.has_edge
   DiGraph.order
   DiGraph.number_of_nodes
   DiGraph.__len__
   DiGraph.degree
   DiGraph.degree_iter
   DiGraph.in_degree
   DiGraph.in_degree_iter
   DiGraph.out_degree
   DiGraph.out_degree_iter
   DiGraph.size
   DiGraph.number_of_edges
   DiGraph.nodes_with_selfloops
   DiGraph.selfloop_edges
   DiGraph.number_of_selfloops


Making copies and subgraphs
===========================
.. autosummary::
   :toctree: generated/

   DiGraph.copy
   DiGraph.to_undirected
   DiGraph.to_directed
   DiGraph.subgraph
   DiGraph.reverse
 
