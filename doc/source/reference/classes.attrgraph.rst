.. _attrgraph:

=========================================================
AttrGraph -- Graphs with graph, node, and edge attributes
=========================================================

Overview
--------
.. currentmodule:: networkx
.. autoclass:: AttrGraph

Adding and Removing Nodes and Edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   AttrGraph.add_node
   AttrGraph.add_nodes_from
   AttrGraph.remove_node
   AttrGraph.remove_nodes_from
   AttrGraph.add_edge
   AttrGraph.add_edges_from
   AttrGraph.remove_edge
   AttrGraph.remove_edges_from
   AttrGraph.add_star
   AttrGraph.add_path
   AttrGraph.add_cycle
   AttrGraph.clear



Iterating over nodes and edges
------------------------------
.. autosummary::
   :toctree: generated/

   AttrGraph.nodes
   AttrGraph.nodes_iter
   AttrGraph.__iter__
   AttrGraph.edges
   AttrGraph.edges_iter
   AttrGraph.get_edge_data
   AttrGraph.neighbors
   AttrGraph.neighbors_iter
   AttrGraph.__getitem__
   AttrGraph.adjacency_list
   AttrGraph.adjacency_iter
   AttrGraph.nbunch_iter



Information about graph structure
---------------------------------
.. autosummary::
   :toctree: generated/

   AttrGraph.has_node
   AttrGraph.__contains__
   AttrGraph.has_edge
   AttrGraph.has_neighbor
   AttrGraph.nodes_with_selfloops
   AttrGraph.selfloop_edges
   AttrGraph.order
   AttrGraph.number_of_nodes
   AttrGraph.__len__
   AttrGraph.size
   AttrGraph.number_of_edges
   AttrGraph.number_of_selfloops
   AttrGraph.degree
   AttrGraph.degree_iter


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   AttrGraph.copy
   AttrGraph.to_directed
   AttrGraph.subgraph
   AttrGraph.to_weighted



