.. _multidigraph:


=================================================================
MultiDiGraph---Directed graphs with self loops and parallel edges
=================================================================

Overview
========
.. currentmodule:: networkx
.. autoclass:: MultiDiGraph

Methods
=======

Adding and Removing Nodes and Edges
-----------------------------------

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
   MultiDiGraph.new_edge_key
   MultiDiGraph.remove_edge
   MultiDiGraph.remove_edges_from
   MultiDiGraph.clear



Reporting nodes edges and neighbors
-----------------------------------
.. autosummary::
   :toctree: generated/

   MultiDiGraph.nodes
   MultiDiGraph.__iter__
   MultiDiGraph.has_node
   MultiDiGraph.__contains__
   MultiDiGraph.edges
   MultiDiGraph.out_edges
   MultiDiGraph.in_edges
   MultiDiGraph.has_edge
   MultiDiGraph.get_edge_data
   MultiDiGraph.neighbors
   MultiDiGraph.adj
   MultiDiGraph.__getitem__
   MultiDiGraph.successors
   MultiDiGraph.succ
   MultiDiGraph.predecessors
   MultiDiGraph.succ
   MultiDiGraph.adjacency
   MultiDiGraph.nbunch_iter


Counting nodes edges and neighbors
----------------------------------
.. autosummary::
   :toctree: generated/

   MultiDiGraph.order
   MultiDiGraph.number_of_nodes
   MultiDiGraph.__len__
   MultiDiGraph.degree
   MultiDiGraph.in_degree
   MultiDiGraph.out_degree
   MultiDiGraph.size
   MultiDiGraph.number_of_edges

Making copies and subgraphs
---------------------------
.. autosummary::
   :toctree: generated/

   MultiDiGraph.copy
   MultiDiGraph.to_undirected
   MultiDiGraph.to_directed
   MultiDiGraph.subgraph
   MultiDiGraph.edge_subgraph
   MultiDiGraph.reverse
   MultiDiGraph.fresh_copy
