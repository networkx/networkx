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

- Better syncing between G._succ and G._adj for directed G.
  And slightly better speed from all the core adjacency data structures.
  G.adj is now a cached_property while still having the cache reset when
  G._adj is set to a new dict (which doesn't happen very often).
  Note: We have always assumed that G._succ and G._adj point to the same
  object. But we did not enforce it well. If you have somehow worked
  around our attempts and are relying on these private attributes being
  allowed to be different from each other due to loopholes in our previous
  code, you will have to look for other loopholes in our new code
  (or subclass DiGraph to explicitly allow this).
- If your code sets G._succ or G._adj to new dictionary-like objects, you no longer
  have to set them both. Setting either will ensure the other is set as well.
  And the cached_properties G.adj and G.succ will be rest accordingly too.
- If you use the presence of the attribute `_adj` as a criteria for the object
  being a Graph instance, that code may need updating. The graph classes
  themselves now have an attribute `_adj`. So, it is possible that whatever you
  are checking might be a class rather than an instance. We suggest you check
  for attribute `_adj` to verify it is like a NetworkX graph object or type and
  then `type(obj) is type` to check if it is a class.

Improvements
------------


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
