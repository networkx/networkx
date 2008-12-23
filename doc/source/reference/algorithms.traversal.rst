.. _traversal:

Traversal
=========

.. toctree::
   :maxdepth: 2

Components
----------
.. automodule:: networkx.algorithms.traversal.component
.. currentmodule:: networkx

Undirected Graphs
^^^^^^^^^^^^^^^^^
.. autosummary::
   :toctree: generated/

   is_connected
   number_connected_components
   connected_components
   connected_component_subgraphs
   node_connected_component

Directed Graphs
^^^^^^^^^^^^^^^
.. autosummary::
   :toctree: generated/

   is_strongly_connected
   number_strongly_connected_components
   strongly_connected_components
   strongly_connected_component_subgraphs
   strongly_connected_components_recursive
   kosaraju_strongly_connected_components

DAGs
----
.. automodule:: networkx.algorithms.traversal.dag
.. currentmodule:: networkx

.. autosummary::
   :toctree: generated/

   topological_sort
   topological_sort_recursive
   is_directed_acyclic_graph


Distance
--------
.. automodule:: networkx.algorithms.traversal.distance
.. currentmodule:: networkx

.. autosummary::
   :toctree: generated/

   eccentricity
   diameter
   radius
   periphery
   center

Shortest Paths 
--------------
.. automodule:: networkx.algorithms.traversal.path
.. currentmodule:: networkx

.. autosummary::
   :toctree: generated/

   average_shortest_path_length
   shortest_path
   shortest_path_length
   single_source_shortest_path
   single_source_shortest_path_length
   all_pairs_shortest_path
   all_pairs_shortest_path_length
   dijkstra_path
   dijkstra_path_length
   single_source_dijkstra_path
   single_source_dijkstra_path_length
   single_source_dijkstra
   bidirectional_dijkstra
   bidirectional_shortest_path
   dijkstra_predecessor_and_distance
   predecessor
   floyd_warshall

.. automodule:: networkx.algorithms.traversal.astar
.. currentmodule:: networkx

.. autosummary::
   :toctree: generated/

   astar_path
   astar_path_length   


Search
------
.. automodule:: networkx.algorithms.traversal.search
.. currentmodule:: networkx

.. autosummary::
   :toctree: generated/

   dfs_preorder
   dfs_postorder
   dfs_predecessor
   dfs_successor
   dfs_tree
