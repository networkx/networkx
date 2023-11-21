NetworkX 3.2.1
==============

Release date: 28 October 2023

Supports Python 3.9, 3.10, 3.11, and 3.12.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

API Changes
-----------

- Disallow negative number of nodes in ``complete_multipartite_graph`` (`#7057 <https://github.com/networkx/networkx/pull/7057>`_).

Enhancements
------------

- Add Tadpole graph (`#6999 <https://github.com/networkx/networkx/pull/6999>`_).

Bug Fixes
---------

- Fix listing of release notes on Releases page (`#7030 <https://github.com/networkx/networkx/pull/7030>`_).
- Fix syntax warning from bad escape sequence (`#7034 <https://github.com/networkx/networkx/pull/7034>`_).
- Fix triangles to avoid using ``is`` to compare nodes (`#7041 <https://github.com/networkx/networkx/pull/7041>`_).
- Fix error message for ``nx.mycielski_graph(0)`` (`#7056 <https://github.com/networkx/networkx/pull/7056>`_).
- Disallow negative number of nodes in ``complete_multipartite_graph`` (`#7057 <https://github.com/networkx/networkx/pull/7057>`_).

Documentation
-------------

- Update release process (`#7029 <https://github.com/networkx/networkx/pull/7029>`_).
- fix extendability function name in bipartite.rst (`#7042 <https://github.com/networkx/networkx/pull/7042>`_).
- Minor doc cleanups to remove doc build warnings (`#7048 <https://github.com/networkx/networkx/pull/7048>`_).

Maintenance
-----------

- fix: Explicitly check for None/False in edge_attr during import from np (`#6825 <https://github.com/networkx/networkx/pull/6825>`_).
- Add favicon (`#7043 <https://github.com/networkx/networkx/pull/7043>`_).
- Remove unused code resistance_distance (`#7053 <https://github.com/networkx/networkx/pull/7053>`_).
- Fix names of small graphs (`#7055 <https://github.com/networkx/networkx/pull/7055>`_).
- Improve error messages for misconfigured backend treatment (`#7062 <https://github.com/networkx/networkx/pull/7062>`_).

Other
-----

- Update convert_matrix.py (`#7018 <https://github.com/networkx/networkx/pull/7018>`_).

Contributors
------------

8 authors added to this release (alphabetically):

- `@peijenburg <https://github.com/peijenburg>`_
- AKSHAYA MADHURI (`@akshayamadhuri <https://github.com/akshayamadhuri>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Jonas Otto (`@ottojo <https://github.com/ottojo>`_)
- Jordan Matelsky (`@j6k4m8 <https://github.com/j6k4m8>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)

6 reviewers added to this release (alphabetically):

- `@peijenburg <https://github.com/peijenburg>`_
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Stefan van der Walt (`@stefanv <https://github.com/stefanv>`_)

_These lists are automatically generated, and may not be complete or may contain
duplicates._
