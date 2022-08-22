NetworkX 1.4
============

Release date:  23 January 2011

New features
------------
 - :mod:`k-shell,k-crust,k-corona <networkx.algorithms.core>`
 - :mod:`read GraphML files from yEd <networkx.readwrite.graphml>`
 - :mod:`read/write GEXF format files <networkx.readwrite.gexf>`
 - :mod:`find cycles in a directed graph <networkx.algorithms.cycles>`
 - :mod:`DFS <networkx.algorithms.traversal.depth_first_search>` and :mod:`BFS <networkx.algorithms.traversal.breadth_first_search>` algorithms
 - :mod:`chordal graph functions <networkx.algorithms.chordal.chordal_alg>`
 - :mod:`Prim's algorithm for minimum spanning tree <networkx.algorithms.mst>`
 - :mod:`r-ary tree generator <networkx.generators.classic>`
 - :mod:`rich club coefficient <networkx.algorithms.richclub>`
 - NumPy matrix version of :mod:`Floyd's algorithm for all-pairs shortest path  <networkx.algorithms.shortest_paths.dense>`
 - :mod:`read GIS shapefiles <networkx.readwrite.nx_shp>`
 - :mod:`functions to get and set node and edge attributes <networkx.classes.function>`
 - and more, see  https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.4

API changes
-----------
 - :mod:`gnp_random_graph() <networkx.generators.random_graphs>` now takes a
   directed=True|False keyword instead of create_using
 - :mod:`gnm_random_graph() <networkx.generators.random_graphs>` now takes a
   directed=True|False keyword instead of create_using


Algorithms changed
==================

Shortest path
-------------

astar_path(), astar_path_length(), shortest_path(), shortest_path_length(),
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bidirectional_shortest_path(), dijkstra_path(), dijkstra_path_length(),
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bidirectional_dijkstra()
^^^^^^^^^^^^^^^^^^^^^^^^
   These algorithms now raise an exception when a source and a target are
   specified and no path exist between these two nodes. The exception is
   a NetworkXNoPath exception.

