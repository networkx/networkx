.. _graph:

=========================================
Graph---Undirected graphs with self loops
=========================================

Overview
========
.. currentmodule:: networkx
.. autoclass:: Graph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

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



Reporting nodes edges and neighbors
-----------------------------------
.. autosummary::
   :toctree: generated/

   Graph.nodes
   Graph.__iter__
   Graph.has_node
   Graph.__contains__
   Graph.edges
   Graph.has_edge
   Graph.get_edge_data
   Graph.neighbors
   Graph.adj
   Graph.__getitem__
   Graph.adjacency
   Graph.nbunch_iter



Counting nodes edges and neighbors
----------------------------------
.. autosummary::
   :toctree: generated/

   Graph.order
   Graph.number_of_nodes
   Graph.__len__
   Graph.degree
   Graph.size
   Graph.number_of_edges


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   Graph.copy
   Graph.to_undirected
   Graph.to_directed
   Graph.subgraph
   Graph.edge_subgraph
   Graph.fresh_copy
