.. _classes:

***********
Graph types
***********

NetworkX provides data structures and methods for storing graphs.

All NetworkX graph classes allow (hashable) Python objects as nodes
and any Python object can be assigned as an edge attribute.

The choice of graph class depends on the structure of the
graph you want to represent.

Which graph class should I use?
===============================

+----------------+------------+--------------------+------------------------+
| Networkx Class | Type       | Self-loops allowed | Parallel edges allowed |
+================+============+====================+========================+
| Graph          | undirected | Yes                | No                     |
+----------------+------------+--------------------+------------------------+
| DiGraph        | directed   | Yes                | No                     |
+----------------+------------+--------------------+------------------------+
| MultiGraph     | undirected | Yes                | Yes                    |
+----------------+------------+--------------------+------------------------+
| MultiDiGraph   | directed   | Yes                | Yes                    |
+----------------+------------+--------------------+------------------------+

Basic graph types
=================

.. toctree::
   :maxdepth: 2

   graph
   digraph
   multigraph
   multidigraph

.. note:: NetworkX uses `dicts` to store the nodes and neighbors in a graph.
   So the reporting of nodes and edges for the base graph classes may not
   necessarily be consistent across versions and platforms; however, the reporting
   for CPython is consistent across platforms and versions after 3.6.

Graph Views
===========

.. automodule:: networkx.classes.graphviews
.. autosummary::
   :toctree: generated/

   generic_graph_view
   subgraph_view
   reverse_view

Core Views
==========

.. automodule:: networkx.classes.coreviews
.. autosummary::
   :toctree: generated/

   AtlasView
   AdjacencyView
   MultiAdjacencyView
   UnionAtlas
   UnionAdjacency
   UnionMultiInner
   UnionMultiAdjacency
   FilterAtlas
   FilterAdjacency
   FilterMultiInner
   FilterMultiAdjacency

Reporting Views
===============

NetworkX provides lightweight *reporting views* — read-only objects that
report information about a graph without copying it. The most commonly used
reporting views are:

- ``NodeView`` — returned by ``G.nodes`` or ``G.nodes(...)``.
- ``EdgeView`` — returned by ``G.edges`` or ``G.edges(...)``.
- ``DegreeView`` — returned by ``G.degree`` or ``G.degree(...)``.

Quick overview
--------------
Views are quick-to-create, live (they reflect changes to the graph), and
provide Pythonic access patterns:

- set-like membership and set operations for nodes and edges (``n in G.nodes``,
  ``G.nodes & H.nodes``, ``(u, v) in G.edges``),
- iteration (``for n in G.nodes``, ``for u, v in G.edges``),
- mapping-style lookups (``G.nodes[n]`` returns the node attribute dict;
  ``G.edges[u, v]`` returns the edge attribute dict),
- data-filtered iteration via ``.data(...)`` and conversion to concrete
  containers via ``list(...)`` or ``dict(...)``.

Common usage patterns
---------------------
**NodeView / NodeDataView**

- Use ``G.nodes`` when you need membership tests, set-like operations, or to
  look up a node's attribute dict with ``G.nodes[n]``.
- Use ``G.nodes(data=...)`` or ``G.nodes.data(attr_name, default=...)`` to
  iterate node/data pairs or to extract a single attribute for all nodes.

Example:

.. code-block:: python

    >>> G = nx.path_graph(3)
    >>> list(G.nodes)
    [0, 1, 2]
    >>> G.add_node(3, color="red")
    >>> list(G.nodes.data("color", default=None))
    [(0, None), (1, None), (2, None), (3, 'red')]

**EdgeView / EdgeDataView**

- Use ``G.edges`` to iterate or test membership for edges.
- Call ``G.edges(data=...)`` or ``G.edges(nbunch=..., data=..., keys=...)`` to
  iterate edges with data, restrict to edges incident to a set of nodes, or
  include multigraph keys.

.. note::
   Iteration of ``G.edges()`` yields node pairs as 2-tuples even for multigraphs.
   Use ``G.edges(keys=True)`` to receive 3-tuples ``(u, v, key)`` for multigraphs.

Example:

.. code-block:: python

    >>> G = nx.Graph()
    >>> G.add_edge(0, 1, weight=3)
    >>> list(G.edges(data="weight", default=1))
    [(0, 1, 3)]

**DegreeView**

- Use ``G.degree`` to iterate ``(node, degree)`` pairs or query a single node
  with ``G.degree[n]``.
- The function interface ``G.degree(nbunch=..., weight=...)`` allows:
  * ``weight="attr"`` to compute weighted degree using the named edge attribute, and
  * ``nbunch`` to restrict iteration to a subset of nodes while still allowing direct lookups.

Example:

.. code-block:: python

    >>> G = nx.cycle_graph(4)
    >>> dict(G.degree())
    {0: 2, 1: 2, 2: 2, 3: 2}
    >>> G.degree[0]
    2
    >>> # Add an edge with a weight attribute and compute weighted degrees:
    >>> G.add_edge(0, 1, weight=5)
    >>> dict(G.degree(weight="weight"))
    {0: 6, 1: 6, 2: 2, 3: 2}

Note on how degree is computed
------------------------------
NetworkX does not store a persistent degree value for each node. Instead, the
degree is computed when requested by examining the neighbor dictionary for a
node and counting or summing edge attributes as needed. For multigraphs the key
dict for each neighbor is scanned; for weighted degree the requested edge
attribute values are summed.

Because computing degree accesses the adjacency structures, some applications
cache degree values in a separate dictionary to avoid repeated recomputation:

.. code-block:: python

    >>> G_degree = dict(G.degree)   # make a cached snapshot of degrees

If you cache degrees, remember to update the cached dict when you modify edges.

Performance & pitfalls
----------------------
- Views are **read-only** wrappers — they do not copy graph data. If you need a stable snapshot
  (for example when you will modify the graph while iterating), materialize the view using
  ``list(view)`` or ``dict(view)``.
- Avoid modifying the graph while iterating over a view (same rule as iterating a dict).
- DataViews that return full attribute dicts expose writable dicts (modifying those dicts
  modifies the underlying graph attributes). Use this intentionally.
- Edge set operations on undirected graphs use 2-tuple representations; be careful when
  comparing sets that may contain both ``(u, v)`` and ``(v, u)``.
- DegreeView with ``weight`` performs a sum over edge attributes and can be more expensive
  than unweighted degree calculations.

Note
----
This is a short summary for the Graph Types reference page. For the full
implementation and detailed docstrings see :mod:`networkx.classes.reportviews`.

Filters
=======

.. note:: Filters can be used with views to restrict the view (or expand it).
   They can filter nodes or filter edges. These examples are intended to help
   you build new ones. They may instead contain all the filters you ever need.

.. automodule:: networkx.classes.filters
.. autosummary::
   :toctree: generated/

   no_filter
   hide_nodes
   hide_edges
   hide_diedges
   hide_multidiedges
   hide_multiedges
   show_nodes
   show_edges
   show_diedges
   show_multidiedges
   show_multiedges
