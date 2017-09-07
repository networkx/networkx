Announcement: NetworkX 2.0
==========================

We're happy to announce the release of NetworkX 2.0!
NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <http://networkx.github.io/>`_
and our `gallery of examples
<http://networkx.readthedocs.io/en/latest/auto_examples/index.html>`_.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of over two years of work with over 300 pull
requests by 85 contributors. Highlights include:

- We have made major changes to the methods in the Multi/Di/Graph classes.
  There is a `migration guide for people moving from 1.X to 2.0
  <http://networkx.readthedocs.org/en/latest/release/migration_guide_from_1.x_to_2.0.html>`_.

- We updated the documentation system.


API Changes
-----------

* Base Graph Class Changes
  With the release of NetworkX 2.0 we are moving towards a view/iterator reporting API.
  We used to have two methods for the same property of the graph, one that returns a
  list and one that returns an iterator. With 2.0 we have replaced them with a view.
  A view is a read-only object that is quick to create, automatically updated, and 
  provides basic access like iteration, membership and set operations where appropriate.
  For example, ``G.nodes()`` used to return a list and ``G.nodes_iter()`` an iterator.
  Now ``G.nodes()`` returns a view and ``G.nodes_iter()`` is removed. ``G.degree()``
  returns a view with ``(node, degree)`` iteration, so that ``dict(G.degree())``
  returns a dict keyed by node with degree as value.
  The old behavior

    >>> G = nx.complete_graph(5)
    >>> G.nodes()  # doctest: +SKIP
    [0, 1, 2, 3, 4]
    >>> G.nodes_iter()  # doctest: +SKIP
    <dictionary-keyiterator at ...>

  has changed to

    >>> G = nx.complete_graph(5)
    >>> G.nodes()
    NodeView((0, 1, 2, 3, 4))
    >>> list(G.nodes())
    [0, 1, 2, 3, 4]

  New feature include lookup of node and edge data from the views, property
  access without parentheses, and set operations.

    >>> G.add_node(3, color='blue')
    >>> G.nodes[3]
    {'color': 'blue'}
    >>> G.nodes & {3, 4, 5}
    set([3, 4])

  The following methods have changed:

    * Graph/MultiGraph

      * ``G.nodes()``
      * ``G.edges()``
      * ``G.neighbors()``
      * ``G.adjacency_list()`` and ``G.adjacency_iter()`` to ``G.adjacency()``
      * ``G.degree()``
      * ``G.subgraph()``
      * ``G.copy()``
      * ``G.__class__()`` should be replaced with ``G.fresh_copy()``

    * DiGraph/MultiDiGraph

      * ``G.nodes()``
      * ``G.edges()``
      * ``G.in_edges()``
      * ``G.out_edges()``
      * ``G.degree()``
      * ``G.in_degree()``
      * ``G.out_degree()``
      * ``G.reverse()``

  The following deprecated methods will be removed in a future release (3.0?).
      * ``G.node``, ``G.edge`` (replaced by G.nodes, G.edges)
      * ``G.add_path``, ``G.add_cycle``, ``G.add_star`` (Now ``nx.add_path(G,...``)
      * ``G.selfloop_edges``, ``G.nodes_with_selfloops``, ``G.number_of_selfloops``
        (Now ``nx.selfloop_edges(G)``, etc)

  Many subclasses have been changed accordingly such as:
    * AntiGraph
    * OrderedGraph and friends
    * Examples such as ThinGraph that inherit from Graph

* [`#2107 <https://github.com/networkx/networkx/pull/2107>`_]
  The Graph class methods ``add_edge`` and ``add_edges_from`` no longer
  allow the use of the ``attr_dict`` parameter.  Instead use keyword arguments.
  Thus ``G.add_edge(1, 2, {'color': 'red'})`` becomes
  ``G.add_edge(1, 2, color='red')``.
  Note that this only works if the attribute name is a string. For non-string
  attributes you will need to add the edge and then update manually using
  e.g. ``G.edges[1, 2].update({0: "zero"})``

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
  parameter. So existing code that did not explicitly name the optional
  ``weight`` parameter will need to be updated::

      >>> nx.minimum_spanning_tree(G, 'mass')  # old
      >>> nx.minimum_spanning_tree(G, weight='mass') # new

  In the above, we are still relying on the the functions being imported into the
  top-level  namespace. We do not have immediate plans to deprecate this approach,
  but we recommend the following instead::

       >>> from networkx.algorithms import tree
       # recommended
       >>> tree.minimum_spanning_tree(G, algorithm='kruskal', weight='mass')
       >>> tree.minimum_spanning_edges(G, algorithm='prim', weight='mass')

* [`#1445 <https://github.com/networkx/networkx/pull/1445>`_]
  Most of the ``shortest_path`` algorithms now raise a ``NodeNotFound`` exception
  when a source or a target are not present in the graph.

* [`#2326 <https://github.com/networkx/networkx/pull/2326>`_]
  Centrality algorithms were harmonized with respect to the default behavior of
  the weight parameter. The default value of the ``weight`` keyword argument has
  been changed from ``weight`` to ``None``.  This affects the
  following centrality functions:

  - :func:`approximate_current_flow_betweenness_centrality()`
  - :func:`current_flow_betweenness_centrality()`
  - :func:`current_flow_betweenness_centrality_subset()`
  - :func:`current_flow_closeness_centrality()`
  - :func:`edge_current_flow_betweenness_centrality()`
  - :func:`edge_current_flow_betweenness_centrality_subset()`
  - :func:`eigenvector_centrality()`
  - :func:`eigenvector_centrality_numpy()`
  - :func:`katz_centrality()`
  - :func:`katz_centrality_numpy()`

* [`#2420 <https://github.com/networkx/networkx/pull/2420>`_]
  New community detection algorithm provided. Fluid Communities is an
  asynchronous algorithm based on the simple idea of fluids interacting in an
  environment, expanding and pushing each other. The algorithm is completely
  described in `"Fluid Communities: A Competitive and Highly Scalable Community
  Detection Algorithm" <https://arxiv.org/pdf/1703.09307.pdf>`_.

* [`#2510 <https://github.com/networkx/networkx/pull/2510>`_ and
  `#2508 <https://github.com/networkx/networkx/pull/2508>`_]
  ``single_source_dijkstra``, ``multi_source_dijkstra`` and functions that use
  these now have new behavior when ``target`` is specified. Instead of
  returning dicts for distances and paths a 2-tuple of ``(distance, path)`` is
  returned.  When ``target`` is not specified the return value is still 2
  dicts.

* [`#2553 <https://github.com/networkx/networkx/issues/2553>`_]
  ``set_node_attributes()`` and ``set_edge_attributes()`` now accept
  dict-of-dict input of shape ``{node/edge: {name: value}}`` in addition to
  previous valid inputs: ``{node/edge: value}`` and ``value``. The order of the
  parameters changed also: The second parameter "values" is the value argument
  and the third parameter "name" is the name of the attribute. "name" has
  default value ``None`` in which case "values" must be the newly allowed form
  containing names. Previously "name" came second without default, and "values"
  came third.

* [`#2604 <https://github.com/networkx/networkx/pull/2604>`_] Move selfloop
  methods out of base classes to networkx functions.
  ``G.number_of_selfloops()``, ``G.selfloop_edges()``,
  ``G.nodes_with_selfloops()`` are now ``nx.number_of_selfloops(G)``,
  ``nx.selfloop_edges(G)``, ``nx.nodes_with_selfloops(G)``.

  ``G.node`` and ``G.edge`` are removed. Their functionality are replaced by
  ``G.nodes`` and ``G.edges``.

* [`#2558 <https://github.com/networkx/networkx/pull/2558>`_]
  Previously, the function ``from_pandas_dataframe`` assumed that the dataframe
  has edge-list like structures, but ``to_pandas_dataframe`` generates an
  adjacency matrix.  We now provide four functions ``from_pandas_edgelist``,
  ``to_pandas_edgelist``, ``from_pandas_adjacency``, and ``to_pandas_adjacency``.

* [`#2620 <https://github.com/networkx/networkx/pull/2620>`_]
  Removed ``draw_nx``, please use ``draw`` or ``draw_networkx``.

Deprecations
------------

The following deprecated functions will be removed in 2.1.

- The function ``bellman_ford`` has been deprecated in favor of
  ``bellman_ford_predecessor_and_distance``.

- The functions ``to_pandas_dataframe`` and ``from_pandas_dataframe`` have been
  deprecated in favor of ``to_pandas_adjacency``, ``from_pandas_adjacency``,
  ``to_pandas_edgelist``, and ``from_pandas_edgelist``.

Contributors to this release
----------------------------

<output of contribs.py>


Pull requests merged in this release
------------------------------------

<output of contribs.py>
