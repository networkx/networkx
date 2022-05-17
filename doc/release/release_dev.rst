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


Improvements
------------

- Changed the treatment of directed graphs for `has_eulerian_path` which
  used to allow graphs with isolated nodes, i.e. nodes with zero degree to have
  an eulerian path. For undirected graphs, on the other hand, `has_eulerian_path`
  does not allow isolated nodes. For example:

      >>> G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])
      >>> G.add_node(3)
      >>> nx.has_eulerian_path(G)

  The above snippet used to produce `True` whereas the below one used to produce `False`.

      >>> G = nx.Graph([(0, 1), (1, 2), (2, 0)])
      >>> G.add_node(3)
      >>> nx.has_eulerian_path(G)

  The change makes the method consistent for both undirected and directed graph types so
  that it does not allow isolated nodes. (Both examples produce `False` now.)

- `is_bipartite_node_set` now raises an exception when the tested nodes are
  not distinct (previously this would not affect the outcome).
  This is to avoid surprising behaviour when using node sets in other bipartite
  algorithms, for example it yields incorrect results for `weighted_projected_graph`.

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
