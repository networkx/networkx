.. _multidigraph:


=================================================================
MultiDiGraph - Directed graphs with self loops and parallel edges
=================================================================

Overview
========
.. currentmodule:: networkx
.. autofunction:: MultiDiGraph

Adding and Removing Nodes and Edges
===================================

.. autosummary::
   :toctree: generated/

   MultiDiGraph.__init__
   MultiDiGraph.add_node
   MultiDiGraph.add_nodes_from
   MultiDiGraph.remove_node
   MultiDiGraph.remove_nodes_from
   MultiDiGraph.add_edge
   MultiDiGraph.add_edges_from
   MultiDiGraph.add_weighted_edges_from
   MultiDiGraph.remove_edge
   MultiDiGraph.remove_edges_from
   MultiDiGraph.add_star
   MultiDiGraph.add_path
   MultiDiGraph.add_cycle
   MultiDiGraph.clear



Iterating over nodes and edges
==============================
.. autosummary::
   :toctree: generated/

   MultiDiGraph.nodes
   MultiDiGraph.nodes_iter
   MultiDiGraph.__iter__
   MultiDiGraph.edges
   MultiDiGraph.edges_iter
   MultiDiGraph.out_edges
   MultiDiGraph.out_edges_iter
   MultiDiGraph.in_edges
   MultiDiGraph.in_edges_iter
   MultiDiGraph.get_edge_data
   MultiDiGraph.neighbors
   MultiDiGraph.neighbors_iter
   MultiDiGraph.__getitem__
   MultiDiGraph.successors
   MultiDiGraph.successors_iter
   MultiDiGraph.predecessors
   MultiDiGraph.predecessors_iter
   MultiDiGraph.adjacency_list
   MultiDiGraph.adjacency_iter
   MultiDiGraph.nbunch_iter


Information about graph structure
=================================
.. autosummary::
   :toctree: generated/

   MultiDiGraph.has_node
   MultiDiGraph.__contains__
   MultiDiGraph.has_edge
   MultiDiGraph.order
   MultiDiGraph.number_of_nodes
   MultiDiGraph.__len__
   MultiDiGraph.degree
   MultiDiGraph.degree_iter
   MultiDiGraph.in_degree
   MultiDiGraph.in_degree_iter
   MultiDiGraph.out_degree
   MultiDiGraph.out_degree_iter
   MultiDiGraph.size
   MultiDiGraph.number_of_edges
   MultiDiGraph.nodes_with_selfloops
   MultiDiGraph.selfloop_edges
   MultiDiGraph.number_of_selfloops





Making copies and subgraphs
===========================
.. autosummary::
   :toctree: generated/

   MultiDiGraph.copy
   MultiDiGraph.to_undirected
   MultiDiGraph.to_directed
   MultiDiGraph.subgraph
   MultiDiGraph.reverse

