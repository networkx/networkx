NetworkX 2.8
============

Release date: 9 April 2022

Supports Python 3.8, 3.9, and 3.10

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of over five weeks of work with 48 pull requests by
18 contributors. This is the last release before NetworkX 3.0. For a preview of the
upcoming 3.0 release, please see the draft of our
`migration guide <https://networkx.org/documentation/latest/release/migration_guide_from_2.x_to_3.0.html>`_
for people moving from 2.X to 3.0.


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
  at all. The only reasonable option is True. The parameter will be removed completely in v3.0.

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

- Fix docs
- Fix release notes
- Bump release version
- Fix missing backticks (#5381)
- Add Generator support to create_py_random_state. (#5380)
- modularity_max: introduce enforce_n_communities parameter (#5227)
- First draft. (#5359)
- Updated MultiDiGraph documentation to include more examples of actually (#5387)
- Multigraph docs update (#5389)
- Updates to greedy_modularity_communities docs (#5390)
- Finish up NXEP 4 first draft (#5391)
- Correct typo in docstring (int -> float) (#5398)
- DOC: examples code blacks needs a blank line (#5401)
- Add support for multigraphs to nx.bridges. (#5397)
- Update extrema bounding method for compute="eccentricities" parameter (#5409)
- Add Tutte polynomial (#5265)
- Update sparse6 urls to use https (#5424)
- Deprecate extrema bounding (#5422)
- Add NXEP4 to developer toctree and fix broken links (#5420)
- Rm _inherit_doc - default behavior as of Python 3.5. (#5416)
- Minor improvements from general code readthrough (#5414)
- Ignore formatting changes with black, pep8 for git blame (#5405)
- Deprecate dict to numpy helpers (#5427)
- Deprecate `to_tuple` (#5430)
- Fix average_neighbor_degree calculations for directed graph (#5404)
- Parametrize tutte polynomial tests (#5431)
- Update black (#5438)
- Ignore black formatting (#5440)
- Update sphinx (#5439)
- Use https links for conference.scipy.org (#5441)
- Don't use graph6 with directed graphs (#5443) (#5444)
- Fix min_weight_matching to convert edge weights without reciprocal (#5394)
- Make sympy extra dep (#5454)
- Optimize prim for mst (#5455)
- Adding more examples for to_numpy_array method's usage (#5451)
- MAINT: Prim MST test didn't pass algorithm name to all unit tests (#5457)
- Fixed wrong dict factory usage on MultiDiGraph (#5456)
- added extra condition for fancy arrow colors (#5407)
- Update dependencies (#5468)
- Update release notes
- Designate 2.8rc1 release
- Bump release version
- DOCS: add some guidelines for references (#5476)
- Fix for issue 5212 (#5471)
- shortest_path() example (#5491)
- Rm incorrect reference from spiral_layout docstring. (#5503)
- Improve docstring for bethe_hessian_matrix (#5458)
- Add notes about NumPy/SciPy integration to NX 2->3 migration guide (#5505)
- Run black on docs (#5513)

Contributors
------------

- Ross Barnowski
- Riccardo Bucco
- Matthias Bussonnier
- FabianBall
- Martha Frysztacki
- Chris Keefe
- Lukong123
- Peter Mawhorter
- Lucas H. McCabe
- Jarrod Millman
- Sultan Orazbayev
- Dan Schult
- Seon82
- Mridul Seth
- Nikita Sharma
- Dilara Tekinoglu
- blokhinnv
- yusuf-csdev
