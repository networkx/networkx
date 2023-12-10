.. _mixed-edge-graph:

=================================================
MixedEdgeGraph---Graphs with different edge types
=================================================

Overview
========
.. currentmodule:: networkx
.. autoclass:: MixedEdgeGraph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   MixedEdgeGraph.__init__
   MixedEdgeGraph.add_node
   MixedEdgeGraph.add_nodes_from
   MixedEdgeGraph.remove_node
   MixedEdgeGraph.remove_nodes_from
   MixedEdgeGraph.add_edge
   MixedEdgeGraph.add_edges_from
   MixedEdgeGraph.add_weighted_edges_from
   MixedEdgeGraph.new_edge_key
   MixedEdgeGraph.remove_edge
   MixedEdgeGraph.remove_edges_from
   MixedEdgeGraph.update
   MixedEdgeGraph.clear
   MixedEdgeGraph.clear_edges



Reporting nodes edges and neighbors
-----------------------------------
.. autosummary::
   :toctree: generated/

   MixedEdgeGraph.nodes
   MixedEdgeGraph.__iter__
   MixedEdgeGraph.has_node
   MixedEdgeGraph.__contains__
   MixedEdgeGraph.edges
   MixedEdgeGraph.has_edge
   MixedEdgeGraph.get_edge_data
   MixedEdgeGraph.neighbors
   MixedEdgeGraph.adj
   MixedEdgeGraph.__getitem__
   MixedEdgeGraph.adjacency
   MixedEdgeGraph.nbunch_iter



Counting nodes edges and neighbors
----------------------------------
.. autosummary::
   :toctree: generated/

   MixedEdgeGraph.order
   MixedEdgeGraph.number_of_nodes
   MixedEdgeGraph.__len__
   MixedEdgeGraph.degree
   MixedEdgeGraph.size
   MixedEdgeGraph.number_of_edges


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   MixedEdgeGraph.copy
   MixedEdgeGraph.to_undirected
   MixedEdgeGraph.to_directed
   MixedEdgeGraph.subgraph
   MixedEdgeGraph.edge_subgraph
