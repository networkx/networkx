*********************************
Version 2.0 Notes and API Changes
*********************************

This page includes more detailed release information and API changes from
NetworkX 1.9 to NetworkX 2.0.

Please send comments and questions to the networkx-discuss mailing list:
<http://groups.google.com/group/networkx-discuss>.

New functionalities
-------------------
* [`#823 <https://github.com/networkx/networkx/pull/823>`_]
  A :samp:`enumerate_all_cliques` function is added in the clique package
  (:samp:`networkx.algorithms.clique`) for enumerating all cliques (including
  nonmaximal ones) of undirected graphs.

* [`#1105 <https://github.com/networkx/networkx/pull/1105>`_]
  A coloring package (:samp:`networkx.algorithms.coloring`) is created for
  graph coloring algorithms. Initially, a :samp:`greedy_color` function is
  provided for coloring graphs using various greedy heuristics.

* [`#1193 <https://github.com/networkx/networkx/pull/1193>`_]
  A new generator :samp:`edge_dfs`, added to :samp:`networkx.algorithms.traversal`,
  implements a depth-first traversal of the edges in a graph. This complements
  functionality provided by a depth-first traversal of the nodes in a graph.
  For multigraphs, it allows the user to know precisely which edges were
  followed in a traversal. All NetworkX graph types are supported. A traversal
  can also reverse edge orientations or ignore them.

* [`#1210 <https://github.com/networkx/networkx/pull/1210>`_]
  Add a random generator for the duplication-divergence model.

Miscellaneous changes
---------------------

* [`#1192 <https://github.com/networkx/networkx/pull/1192>`_]
  Support for Python 2.6 is dropped.
