*********************************
Version 1.4 notes and API changes
*********************************

We have made some API changes, detailed below, to add clarity.
This page reflects changes from networkx-1.3 to networkx-1.4.
For changes from earlier versions to networkx-1.0 see 
:doc:`Version 1.0 API changes <api_1.0>`.

Please send comments and questions to the networkx-discuss mailing list:
http://groups.google.com/group/networkx-discuss .


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

