*********************************
Version 2.0 notes and API changes
*********************************

This page includes more detailed release information and API changes from
NetworkX 1.10 to NetworkX 2.0.

Please send comments and questions to the networkx-discuss mailing list:
<http://groups.google.com/group/networkx-discuss>.

API changes
-----------
* [`#1577 <https://github.com/networkx/networkx/pull/1577>`_]
  In addition to minimum spanning trees, a new function for calculating maximum
  spanning trees is now provided. The new API consists of four functions:
  ``minimum_spanning_edges``, ``maximum_spanning_edges``,
  ``minimum_spanning_tree``, and ``maximum_spanning_tree``.
  All of these functions accept an ``algorithm`` parameter which specifies the
  algorithm to use when finding the minimum or maximum spanning tree. Currently,
  Kruskal's and Prim's algorithms are implemented, defined as 'kruskal' and
  'prim', respectively. If nothing is specified, Kruskal's algorithm is used.
  For example, to calculate the maximum spanning tree of a graph using Kruskal's
  algorithm, the function ``maximum_spanning_tree`` has to be called like::

      >>> nx.maximum_spanning_tree(G, algorithm='kruskal')

  The ``algorithm`` parameter is new and appears before the existing ``weight``
  parameter. So existing code that did not explicitly name the optional ``weight``
  parameter will need to be updated::

      >>> nx.minimum_spanning_tree(G, 'mass')  # old
      >>> nx.minimum_spanning_tree(G, weight='mass') # new

  In the above, we are still relying on the the function being imported into the
  top-level  namespace. We recommend the following instead, but do not have
  immediate plans to deprecate the other approach::

       >>> from networkx.algorithms import tree
       >>> tree.minimum_spanning_tree(G, weight='mass') # recommended

  As for ``minimum_spanning_edges``/``maximum_spanning_edges``, they are not
  imported in the top-level namespace. This approach should be used to
  work with these functions::

       >>> from networkx.algorithms import tree
       >>> tree.minimum_spanning_edges(G, algorithm='prim', weight='mass')


