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

- [`#5394 <https://github.com/networkx/networkx/pull/5394>`_]
  The function ``min_weight_matching`` no longer acts upon the parameter ``maxcardinality``
  because setting it to False would result in the min_weight_matching being no edges
  at all. The only resonable option is True. The parameter will be removed completely in v3.0.

Deprecations
------------

- [`#5227 <https://github.com/networkx/networkx/pull/5227>`_]
  Deprecate the ``n_communities`` parameter name in ``greedy_modularity_communities``
  in favor of ``cutoff``.


Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
