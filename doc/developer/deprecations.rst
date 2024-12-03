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

Version 3.5
~~~~~~~~~~~
* Remove ``all_triplets`` from ``algorithms/triads.py``
* Remove ``random_triad`` from ``algorithms/triad.py``.
* Remove ``d_separated`` from ``algorithms/d_separation.py``.
* Remove ``minimal_d_separator`` from ``algorithms/d_separation.py``.
* Add `not_implemented_for("multigraph”)` decorator to ``k_core``, ``k_shell``, ``k_crust`` and ``k_corona`` functions.
* Change ``single_target_shortest_path_length`` in ``algorithms/shortest_path/unweighted.py``
  to return a dict. See #6527
* Change ``shortest_path`` in ``algorithms/shortest_path/generic.py``
  to return a iterator. See #6527
* Remove ``total_spanning_tree_weight`` from ``linalg/laplacianmatrix.py``
* Remove ``create`` keyword argument from ``nonisomorphic_trees`` in 
  ``generators/nonisomorphic_trees``.

Version 3.6
~~~~~~~~~~~
* Remove ``compute_v_structures`` from ``algorithms/dag.py``.
* Remove ``link`` kwarg from ``readwrite/json_graph/node_link.py``;
  Remove the ``FutureWarning`` re: the default value of ``edges`` and change the
  default value to ``"edges"``.
