Announcement: NetworkX 2.2
==========================

We're happy to announce the release of NetworkX 2.2!
NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <http://networkx.github.io/>`_
and our `gallery of examples
<https://networkx.github.io/documentation/latest/auto_examples/index.html>`_.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of X of work with over X pull requests by
X contributors. Highlights include:


Improvements
------------

Cyclic references between graph classes and views have been removed to ease
subclassing without memory leaks. Graphs no longer hold references to view.

Cyclic references between a graph and itself have been removed by eliminating
G.root_graph. It turns out this was an avoidable construct anyway.

API Changes
-----------


Deprecations
------------


Contributors to this release
----------------------------

<output of contribs.py>


Pull requests merged in this release
------------------------------------

<output of contribs.py>
