3.1 (unreleased)
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


API Changes
-----------


Deprecations
------------
- [`#6388 <https://github.com/networkx/networkx/issues/6388>`_]
  Deprecate ``dag_longest_path_length`` from ``networkx/algorithms/dag.py``.
  Use ``sum(G[u][v].get(weight, default) for u, v in pairwise(nx.dag_longest_path(G)))``


Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
