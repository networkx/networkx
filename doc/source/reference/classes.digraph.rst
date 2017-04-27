.. _digraph:

=========================================
DiGraph - Directed graphs with self loops
=========================================

Overview
========
.. currentmodule:: networkx
.. autofunction:: DiGraph

=======
Methods
=======

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
   DiGraph.clear



Iterating over nodes and edges
==============================
.. autosummary::
   :toctree: generated/

   DiGraph.nodes
   DiGraph.__iter__
   DiGraph.edges
   DiGraph.out_edges
   DiGraph.in_edges
   DiGraph.get_edge_data
   DiGraph.neighbors
   DiGraph.__getitem__
   DiGraph.successors
   DiGraph.predecessors
   DiGraph.adjacency
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
   DiGraph.in_degree
   DiGraph.out_degree
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
   DiGraph.edge_subgraph
   DiGraph.reverse
 
