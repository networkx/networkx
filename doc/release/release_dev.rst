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


API Changes
-----------


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
