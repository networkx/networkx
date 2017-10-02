Announcement: NetworkX 2.X
==========================

We're happy to announce the release of NetworkX 2.X!
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


* [`#2554 <https://github.com/networkx/networkx/issues/2554>`_]
  New algorithms for finding k-edge-connected components and k-edge-connected
  subgraphs in directed and undirected graphs. Efficient implementations are
  provided for the special case of k=1 and k=2. The new functionality is
  provided by:
   - :func:`k_edge_components()`
   - :func:`k_edge_subgraphs()`


* [`#2572 <https://github.com/networkx/networkx/issues/2572>`_]
  New algorithm finding for finding k-edge-augmentations in undirected graphs.
  Efficient implementations are provided for the special case of k=1 and k=2.
  New functionality is provided by:
   - :func:`k_edge_augmentation()`


Deprecations
------------


Contributors to this release
----------------------------

<output of contribs.py>


Pull requests merged in this release
------------------------------------

<output of contribs.py>
