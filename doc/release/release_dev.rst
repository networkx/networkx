Announcement: NetworkX 2.6
==========================

We're happy to announce the release of NetworkX 2.6!
NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <http://networkx.github.io/>`_
and our `gallery of examples
<https://networkx.github.io/documentation/latest/auto_examples/index.html>`_.
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
  Deprecate `to_numpy_matrix` and `from_numpy_matrix`.

Contributors to this release
----------------------------

<output of contribs.py>


Pull requests merged in this release
------------------------------------

<output of contribs.py>
