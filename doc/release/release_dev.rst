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


API Changes
-----------
empty_graph has taken over the functionality from
nx.convert._prep_create_using which was removed.

create_using should now be a Graph Constructor like nx.Graph or nx.DiGraph.
It can still be a graph class which will be cleared before use, but the
preferred use is a constructor.

Deprecations
------------


Contributors to this release
----------------------------

<output of contribs.py>


Pull requests merged in this release
------------------------------------

<output of contribs.py>
