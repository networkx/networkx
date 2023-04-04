3.1 (unreleased)
================

Release date: TBD

Supports Python 3.8, 3.9, 3.10, and 3.11.

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

- Minor bug-fixes and speed-ups
- Improvements to plugin based backend infrastructure
- Minor documentation improvements
- Improved test coverage
- Last release supporting Python 3.8
- Stopped building PDF version of docs
- Use Ruff for linting

Improvements
------------

- [`#6461 <https://github.com/networkx/networkx/pull/6461>`_]
  Add simple cycle enumerator for undirected class
- [`#6404 <https://github.com/networkx/networkx/pull/6404>`_]
  Add spectral bisection for graphs using fiedler vector
- [`#6244 <https://github.com/networkx/networkx/pull/6244>`_]
  Improve handling of create_using to allow Mixins of type Protocol
- [`#5399 <https://github.com/networkx/networkx/pull/5399>`_]
  Add Laplace centrality measure

Deprecations
------------

- [`#6564 <https://github.com/networkx/networkx/pull/6564>`_]
  Deprecate ``single_target_shortest_path_length`` to change return value to a dict in v3.3.
  Deprecate ``shortest_path`` in case of all_pairs to change return value to a iterator in v3.3.
- [`#5602 <https://github.com/networkx/networkx/pull/5602>`_]
  Deprecate ``forest_str`` function (use ``write_network_text`` instead).

Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
