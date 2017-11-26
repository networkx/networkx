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

* [`#2498 <https://github.com/networkx/networkx/pull/2498>`_]
  Starting in NetworkX 2.1 the parameter ``alpha`` is deprecated and replaced
  with the customizable ``p_dist`` function parameter, which defaults to r^-2
  if ``p_dist`` is not supplied. To reproduce networks of earlier NetworkX 
  versions, a custom function needs to be defined and passed as the ``p_dist``
  parameter. For example, if the parameter ``alpha`` = 2 was used in NetworkX 2.0,
  the custom function def custom_dist(r): r**-2 can be passed in versions >=2.1
  as the parameter p_dist = custom_dist to produce an equivalent network. Note the
  change in sign from +2 to -2 in this parameter change. 

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
