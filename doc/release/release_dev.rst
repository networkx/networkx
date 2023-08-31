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

- [`#6759 <https://github.com/networkx/networkx/pull/6759>`_]
  Function ``write_network_text`` has new argument ``vertical_chains``
  which, if true, reduces horizontal space by rendering chains of nodes
  vertically.

- [`#6892 <https://github.com/networkx/networkx/pull/6892>`_]
  The shortest path function `goldberg_radzik` handles a zero-weight-cycle
  correctly instead of raising an exception as a negative weight cycle.

API Changes
-----------
- [`#6651 <https://github.com/networkx/networkx/pull/6651>`_]
  In `is_semiconnected`, the keyword argument `topo_order` has been removed.
  That argument resulted in silently incorrect results more often than not.



Deprecations
------------

- [`#5925 <https://github.com/networkx/networkx/issues/5925>`_]
  The ``sort_neighbors`` input argument of ``nx.generic_bfs_edges`` is deprecated
  and will be removed in v3.4.  Use ``neighbors`` to sort the nodes if desired.
- [`#6785 <https://github.com/networkx/pull/6785>`_]
  Deprecate ``MultiDiGraph_EdgeKey`` subclass used in ``Edmonds`` class.
  Deprecate ``Edmonds`` class for computing minimum and maximum branchings and arborescences (use ``minimum_branching``, ``minimal_branching``, ``maximum_branching``, ``minimum_arborescence`` and ``maximum_arborescence`` directly).

Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
