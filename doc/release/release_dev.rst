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


- `is_bipartite_node_set` now raises an exception when the tested nodes are
  not distinct (previously this would not affect the outcome).
  This is to avoid surprising behaviour when using node sets in other bipartite
  algorithms, for example it yields incorrect results for `weighted_projected_graph`.

API Changes
-----------


Deprecations
------------


Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
