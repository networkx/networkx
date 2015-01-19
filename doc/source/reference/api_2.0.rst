*********************************
Version 2.0 notes and API changes
*********************************

This page includes more detailed release information and API changes from
NetworkX 1.9 to NetworkX 2.0.

Please send comments and questions to the networkx-discuss mailing list:
<http://groups.google.com/group/networkx-discuss>.

New functionalities
-------------------

* [`#823 <https://github.com/networkx/networkx/pull/823>`_]
  A ``enumerate_all_cliques`` function is added in the clique package
  (``networkx.algorithms.clique``) for enumerating all cliques (including
  nonmaximal ones) of undirected graphs.

* [`#1105 <https://github.com/networkx/networkx/pull/1105>`_]
  A coloring package (``networkx.algorithms.coloring``) is created for
  graph coloring algorithms. Initially, a ``greedy_color`` function is
  provided for coloring graphs using various greedy heuristics.

* [`#1193 <https://github.com/networkx/networkx/pull/1193>`_]
  A new generator ``edge_dfs``, added to ``networkx.algorithms.traversal``,
  implements a depth-first traversal of the edges in a graph. This complements
  functionality provided by a depth-first traversal of the nodes in a graph.
  For multigraphs, it allows the user to know precisely which edges were
  followed in a traversal. All NetworkX graph types are supported. A traversal
  can also reverse edge orientations or ignore them.

* [`#1194 <https://github.com/networkx/networkx/pull/1194>`_]
  A ``find_cycle`` function is added to the ``networkx.algorithms.cycles``
  package to find a cycle in a graph. Edge orientations can be optionally
  reversed or ignored.

* [`#1210 <https://github.com/networkx/networkx/pull/1210>`_]
  Add a random generator for the duplication-divergence model.

* [`#1241 <https://github.com/networkx/networkx/pull/1241>`_]
  A new ``networkx.algorithms.dominance`` package is added for
  dominance/dominator algorithms on directed graphs. It contains a
  ``immediate_dominators`` function for computing immediate
  dominators/dominator trees and a ``dominance_frontiers`` function for
  computing dominance frontiers.

* [`#1269 <https://github.com/networkx/networkx/pull/1269>`_]
  The GML reader/parser and writer/generator are rewritten to remove the
  dependence on pyparsing and enable handling of arbitrary graph data.

* [`#1280 <https://github.com/networkx/networkx/pull/1280>`_]
  The network simplex method in the ``networkx.algorithms.flow`` package is
  rewritten to improve its performance and support multi- and disconnected
  networks. For some cases, the new implementation is two or three orders of
  magnitude faster than the old implementation.

* [`#1286 <https://github.com/networkx/networkx/pull/1286>`_]
  Added the Margulis-Gabber-Galil graph to ``networkx.generators``.

* [`#1338 <https://github.com/networkx/networkx/pull/1338>`_]
  Added support for finding optimum branchings and arborescences.

Removed functionalities
-----------------------

* [`#1236 <https://github.com/networkx/networkx/pull/1236>`_]
  The legacy ``ford_fulkerson`` maximum flow function is removed.

Miscellaneous changes
---------------------

* [`#1192 <https://github.com/networkx/networkx/pull/1192>`_]
  Support for Python 2.6 is dropped.
