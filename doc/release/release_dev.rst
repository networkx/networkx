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
empty_graph has taken over the functionality from
nx.convert._prep_create_using which was removed.

create_using should now be a Graph Constructor like nx.Graph or nx.DiGraph.
It can still be a graph instance which will be cleared before use, but the
preferred use is a constructor.

New Base Class Method: update
H.update(G) adds the nodes, edges and graph attributes of G to H.
H.update(edges=e, nodes=n) add the edges and nodes from containers e and n.
H.update(e), and H.update(nodes=n) are also allowed.
First argument is a graph if it has `edges` and `nodes` attributes.
Otherwise the first argument is treated as a list of edges.

Deprecations
------------


Contributors to this release
----------------------------

<output of contribs.py>


Pull requests merged in this release
------------------------------------

<output of contribs.py>
