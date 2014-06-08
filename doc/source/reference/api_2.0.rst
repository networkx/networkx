*********************************
Version 2.0 notes and API changes
*********************************

This page reflects API changes from NetworkX 1.9 to NetworkX 2.0.

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


Miscellaneous changes
---------------------

* [`#1192 <https://github.com/networkx/networkx/pull/1192>`_]
  Support for Python 2.6 is dropped.
