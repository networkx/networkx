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

Usually, our policy is to put in place a deprecation cycle over two releases.

Note that the 2-release deprecation cycle is not a strict rule and in some
cases, the developers can agree on a different procedure upon justification
(like when we can't detect the change, or it involves moving or deleting an
entire function for example).

Todo
----

Make sure to review ``networkx/conftest.py`` after removing deprecated code.

Version 3.0
~~~~~~~~~~~

* In ``networkx/readwrite/gml.py`` remove ``literal_stringizer`` and related tests.
* In ``networkx/readwrite/gml.py`` remove ``literal_destringizer`` and related tests.
* In ``networkx/utils/misc.py`` remove ``is_string_like`` and related tests.
* In ``networkx/utils/misc.py`` remove ``make_str`` and related tests.
* Remove ``networkx/utils/contextmanagers.py`` and related tests.
