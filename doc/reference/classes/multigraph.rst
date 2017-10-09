.. _multigraph:

=================================================================
MultiGraph---Undirected graphs with self loops and parallel edges
=================================================================

Overview
========
.. currentmodule:: networkx
.. autoclass:: MultiGraph

Methods
=======

Adding and removing nodes and edges
-----------------------------------

.. autosummary::
   :toctree: generated/

   MultiGraph.__init__
   MultiGraph.add_node
   MultiGraph.add_nodes_from
   MultiGraph.remove_node
   MultiGraph.remove_nodes_from
   MultiGraph.add_edge
   MultiGraph.add_edges_from
   MultiGraph.add_weighted_edges_from
   MultiGraph.new_edge_key
   MultiGraph.remove_edge
   MultiGraph.remove_edges_from
   MultiGraph.clear



Reporting nodes edges and neighbors
-----------------------------------
.. autosummary::
   :toctree: generated/

   MultiGraph.nodes
   MultiGraph.__iter__
   MultiGraph.has_node
   MultiGraph.__contains__
   MultiGraph.edges
   MultiGraph.has_edge
   MultiGraph.get_edge_data
   MultiGraph.neighbors
   MultiGraph.adj
   MultiGraph.__getitem__
   MultiGraph.adjacency
   MultiGraph.nbunch_iter



Counting nodes edges and neighbors
----------------------------------
.. autosummary::
   :toctree: generated/

   MultiGraph.order
   MultiGraph.number_of_nodes
   MultiGraph.__len__
   MultiGraph.degree
   MultiGraph.size
   MultiGraph.number_of_edges


Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   MultiGraph.copy
   MultiGraph.to_undirected
   MultiGraph.to_directed
   MultiGraph.subgraph
   MultiGraph.edge_subgraph
   MultiGraph.fresh_copy
