3.2 (unreleased)
================

Release date: TBD

Supports Python 3.9, 3.10, and 3.11.

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

- [`#6654 <https://github.com/networkx/networkx/pull/6654>`_]
  Function ``cycle_basis`` switched from using Python sets to dicts so the
  results are now deterministic (not dependent on order reported by a set).

API Changes
-----------
- [`#6651 <https://github.com/networkx/networkx/pull/6651>`_]
  In `is_semiconnected`, the keyword argument `topo_order` has been removed.
  That argument resulted in silently incorrect results more often than not.



Deprecations
------------


Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
