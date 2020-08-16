Deprecations
============

.. _deprecation_policy:

Policy
------

If the behavior of the library has to be changed, a deprecation cycle must be
followed to warn users.

A deprecation cycle is *not* necessary when:

* adding a new function, or
* adding a new keyword argument to the *end* of a function signature, or
* fixing buggy behavior

A deprecation cycle is necessary for *any breaking API change*, meaning a
change where the function, invoked with the same arguments, would return a
different result after the change. This includes:

* changing the order of arguments or keyword arguments, or
* adding arguments or keyword arguments to a function, or
* changing the name of a function, class, method, etc., or
* moving a function, class, etc. to a different module, or
* changing the default value of a function's arguments.

Usually, our policy is to put in place a deprecation cycle over two minor
releases (e.g., if a deprecation warning appears in 2.3, then the functionality
should be removed in 2.5).  For major releases we usually require that all
deprecations have at least a 1-release deprecation cycle (e.g., if 3.0 occurs
after 2.5, then all removed functionality in 3.0 should be deprecated in 2.5).

Note that these 1- and 2-release deprecation cycles for major and minor
releases is not a strict rule and in some cases, the developers can agree on a
different procedure upon justification (like when we can't detect the change,
or it involves moving or deleting an entire function for example).

Todo
----

Make sure to review ``networkx/conftest.py`` after removing deprecated code.

Version 3.0
~~~~~~~~~~~

* In ``readwrite/gml.py`` remove ``literal_stringizer`` and related tests.
* In ``readwrite/gml.py`` remove ``literal_destringizer`` and related tests.
* In ``utils/misc.py`` remove ``is_string_like`` and related tests.
* In ``utils/misc.py`` remove ``make_str`` and related tests.
* Remove ``utils/contextmanagers.py`` and related tests.
* In ``drawing/nx_agraph.py`` remove ``display_pygraphviz`` and related tests.
* In ``algorithms/chordal.py`` replace ``chordal_graph_cliques`` with ``_chordal_graph_cliques``.
* In ``algorithms/centrality/betweenness_centrality_subset.py`` remove ``betweenness_centrality_source``.
* In ``algorithms/centrality/betweenness.py`` remove ``edge_betweeness``.
* In ``algorithms/community_modularity_max.py`` remove old name ``_naive_greedy_modularity_communities``.
