Announcement: NetworkX 2.6
==========================

We're happy to announce the release of NetworkX 2.6!
NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our `gallery of examples
<https://networkx.org/documentation/latest/auto_examples/index.html>`_.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of X of work with over X pull requests by
X contributors. Highlights include:

- NumPy, SciPy, Matplotlib, and pandas are now default requirements.

Improvements
------------


API Changes
-----------

- [`#4190 <https://github.com/networkx/networkx/pull/4190>`_]
  Removed ``tracemin_chol``.  Use ``tracemin_lu`` instead.

- [`#4216 <https://github.com/networkx/networkx/pull/4216>`_]
  In `to_*_array/matrix`, nodes in nodelist but not in G now raise an exception.
  Use G.add_nodes_from(nodelist) to add them to G before converting.

Deprecations
------------

- [`#4238 <https://github.com/networkx/networkx/pull/4238>`_]
  Deprecate ``to_numpy_matrix`` and ``from_numpy_matrix``.
- [`#4279 <https://github.com/networkx/networkx/pull/4279>`_]
  Deprecate ``networkx.utils.misc.is_iterator``.
  Use ``isinstance(obj, collections.abc.Iterator)`` instead.
- [`#4280 <https://github.com/networkx/networkx/pull/4280>`_]
  Deprecate ``networkx.utils.misc.is_list_of_ints`` as it is no longer used.
  See ``networkx.utils.misc.make_list_of_ints`` for related functionality.
- [`#4281 <https://github.com/networkx/networkx/pull/4281>`_]
  Deprecate ``read_yaml`` and ``write_yaml``.

Contributors to this release
----------------------------

<output of contribs.py>


Pull requests merged in this release
------------------------------------

<output of contribs.py>
