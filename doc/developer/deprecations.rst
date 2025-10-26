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

Procedure
---------
To set up a function for deprecation:

- Use a deprecation warning to warn users. For example::

      msg = "curly_hair is deprecated and will be removed in v3.0. Use sum() instead."
      warnings.warn(msg, DeprecationWarning)

- Add a warnings filter to ``networkx/conftest.py``::

      warnings.filterwarnings(
          "ignore", category=DeprecationWarning, message=<start of message>
      )

- Add a reminder to ``doc/developer/deprecations.rst`` for the team
  to remove the deprecated functionality in the future. For example:

  .. code-block:: rst

     * In ``utils/misc.py`` remove ``generate_unique_node`` and related tests.

.. note::

   To reviewers: make sure the merge message has a brief description of the
   change(s) and if the PR closes an issue add, for example, "Closes #123"
   where 123 is the issue number.

Todo
----

Make sure to review ``networkx/conftest.py`` after removing deprecated code.

Version 3.7
~~~~~~~~~~~
* Remove ``graph_could_be_isomorphic``, ``fast_graph_could_be_isomorphic``, and
  ``faster_graph_could_be_isomorphic``, from
  ``networkx.algorithms.isomorphism.isomorph``.
* Remove ``random_lobster`` from ``networkx.generators.random_graphs``.

Version 3.8
~~~~~~~~~~~
* Remove ``maybe_regular_expander`` from ``networkx.generators.expanders``.
* In ``algorithms/approximation/steinertree.py`` remove ``metric_closure`` and related tests.
