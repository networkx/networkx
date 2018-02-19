.. _digraph:

=========================================
DiGraph---Directed graphs with self loops
=========================================

Overview
========
.. currentmodule:: networkx
.. autoclass:: DiGraph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

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



Reporting nodes edges and neighbors
-----------------------------------
.. autosummary::
   :toctree: generated/

   DiGraph.nodes
   DiGraph.__iter__
   DiGraph.has_node
   DiGraph.__contains__
   DiGraph.edges
   DiGraph.out_edges
   DiGraph.in_edges
   DiGraph.has_edge
   DiGraph.get_edge_data
   DiGraph.neighbors
   DiGraph.adj
   DiGraph.__getitem__
   DiGraph.successors
   DiGraph.succ
   DiGraph.predecessors
   DiGraph.pred
   DiGraph.adjacency
   DiGraph.nbunch_iter


Counting nodes edges and neighbors
----------------------------------
.. autosummary::
   :toctree: generated/

   DiGraph.order
   DiGraph.number_of_nodes
   DiGraph.__len__
   DiGraph.degree
   DiGraph.in_degree
   DiGraph.out_degree
   DiGraph.size
   DiGraph.number_of_edges


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   DiGraph.copy
   DiGraph.to_undirected
   DiGraph.to_directed
   DiGraph.subgraph
   DiGraph.edge_subgraph
   DiGraph.reverse
   DiGraph.fresh_copy
