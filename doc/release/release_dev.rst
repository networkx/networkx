NetworkX 3.0 (unreleased)
=========================

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

Better speed from the core adjacency data structures and better syncing
between G._succ and G._adj for directed G. We have always assumed that these
attributes are pointing to the same object. But we did not enforce it well.
If you have somehow worked around our attempts and are relying on these
private attributes being allowed to be different from each other due to
loopholes in our previous rules, you will have to look for other loopholes
in our new rules (or subclass DiGraph to explicitly allow this).
If you set G._succ or G._adj to new dictionary-like objects, you no longer
have to set them both. Setting either will ensure the other is set as well.
And the cached_properties G.adj and G.succ will be rest accordingly too.

Improvements
------------
- [`#5663 <https://github.com/networkx/networkx/pull/5663>`_]
  Implements edge swapping for directed graphs.

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
