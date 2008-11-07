.. _digraph:

=======
DiGraph
=======

Overview
--------
.. currentmodule:: networkx
.. autoclass:: DiGraph

Methods
-------

.. autosummary::
   :toctree: generated/

   DiGraph.add_node
   DiGraph.add_nodes_from
   DiGraph.remove_node
   DiGraph.remove_nodes_from
   DiGraph.nodes_iter
   DiGraph.nodes
   DiGraph.number_of_nodes
   DiGraph.order
   DiGraph.has_node
   DiGraph.add_edge
   DiGraph.add_edges_from
   DiGraph.remove_edge
   DiGraph.remove_edges_from
   DiGraph.has_neighbor
   DiGraph.has_edge
   DiGraph.neighbors
   DiGraph.neighbors_iter
   DiGraph.edges
   DiGraph.edges_iter
   DiGraph.get_edge
   DiGraph.adjacency_list
   DiGraph.adjacency_iter
   DiGraph.degree
   DiGraph.degree_iter
   DiGraph.clear
   DiGraph.copy
   DiGraph.to_directed
   DiGraph.to_undirected
   DiGraph.subgraph
   DiGraph.nodes_with_selfloops
   DiGraph.selfloop_edges
   DiGraph.number_of_selfloops
   DiGraph.size
   DiGraph.number_of_edges
   DiGraph.add_star
   DiGraph.add_path
   DiGraph.add_cycle
   DiGraph.nbunch_iter


DiGraph only
------------
.. autosummary::
   :toctree: generated/

   DiGraph.has_successor
   DiGraph.has_predecessor
   DiGraph.successors
   DiGraph.predecessors
   DiGraph.successors_iter
   DiGraph.predecessors_iter
   DiGraph.reverse

Special Methods
---------------

.. autosummary::
   :toctree: generated/


   DiGraph.__init__
   DiGraph.__str__
   DiGraph.__iter__
   DiGraph.__contains__
   DiGraph.__len__
   DiGraph.__getitem__
