Next Release
============

Release date: TBD

Supports Python ...

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of X of work with over X pull requests by
X contributors. Highlights include:


Improvements
------------

- Correction to the treatment of directed graphs for `average_neighbor_degree`
  which used to sum the degrees of outgoing neighbors only but then divide by
  the number of "in" or "out" or "in+out" neighbors. So it wasn't even an average.
  The correction makes it an average degree of whatever population of neighbors
  is specified by `source` = "in" or "out" or "in+out".
  For example:

      >>> G = nx.path_graph(3, create_using=nx.DiGraph)
      >>> print(nx.average_neighbor_degree(G, source="in", target="in"))
      {0: 0.0, 1: 1.0, 2: 1.0}

  This used to produce `{0: 0.0, 1: 1.0, 2: 0.0}`
  Note: node 0 and 2 were treated nonsensically.
  Node 0 had calculated value 1/0 which was converted to 0.
  (numerator looking at successors while denominator counting predecessors)
  Node 2 had caluated value 0/1 = 0.0 (again succs on top, but preds in bottom)

  Now node 0 has calculated value 0.0/0 which we treat as 0.0. And node 2 has
  calculated value 1/1 = 1.0. Both handle the same nbrhood on top and bottom.

API Changes
-----------

- [`#5394 <https://github.com/networkx/networkx/pull/5394>`_]
  The function ``min_weight_matching`` no longer acts upon the parameter ``maxcardinality``
  because setting it to False would result in the min_weight_matching being no edges
  at all. The only resonable option is True. The parameter will be removed completely in v3.0.

Deprecations
------------

- [`#5227 <https://github.com/networkx/networkx/pull/5227>`_]
  Deprecate the ``n_communities`` parameter name in ``greedy_modularity_communities``
  in favor of ``cutoff``.
- [`#5422 <https://github.com/networkx/networkx/pull/5422>`_]
  Deprecate ``extrema_bounding``. Use the related distance measures with
  ``usebounds=True`` instead.
- [`#5427 <https://github.com/networkx/networkx/pull/5427>`_]
  Deprecate ``dict_to_numpy_array1`` and ``dict_to_numpy_array2`` in favor of
  ``dict_to_numpy_array``, which handles both.
- [`#5428 <https://github.com/networkx/networkx/pull/5428>`_]
  Deprecate ``utils.misc.to_tuple``.


Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
