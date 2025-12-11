Reporting views
===============

NetworkX provides lightweight *reporting views* — read-only objects that report
information about a graph without copying it. The most commonly used reporting
views are:

- ``NodeView`` — returned by ``G.nodes`` or ``G.nodes(...)``.
- ``EdgeView`` — returned by ``G.edges`` or ``G.edges(...)``.
- ``DegreeView`` — returned by ``G.degree`` or ``G.degree(...)``.

These views are quick to create, reflect the live graph (they change when the
graph changes), and provide Pythonic access patterns:

- set-like membership and set operations for nodes and edges (``n in G.nodes``,
  ``G.nodes & H.nodes``, ``(u, v) in G.edges``),
- iteration (``for n in G.nodes``, ``for u, v in G.edges``),
- mapping-style lookups (``G.nodes[n]`` returns the node attribute dict;
  ``G.edges[u, v]`` returns the edge attribute dict),
- data-filtered iteration via ``.data(...)`` and conversion to concrete
  containers via ``list(...)`` or ``dict(...)``.

Note
----
Views are *read-only wrappers*. To materialize results into ordinary Python
containers use ``list(view)`` or ``dict(view)`` as appropriate.

NodeView
--------
A ``NodeView`` behaves like a set of nodes for membership testing and set
operations, and like a mapping when using ``.items()`` or ``.data(...)``.
Call ``G.nodes(data=...)`` to create a NodeDataView for iterating node/data pairs.

Examples:

.. code-block:: python

    >>> G = nx.path_graph(3)
    >>> 1 in G.nodes
    True
    >>> list(G.nodes)
    [0, 1, 2]
    >>> G.add_node(3, color='red')
    >>> list(G.nodes.data('color', default=None))
    [(0, None), (1, None), (2, None), (3, 'red')]

EdgeView
--------
An ``EdgeView`` iterates edges as node-tuples and supports membership tests and
set operations. Call ``G.edges(data=..., nbunch=..., keys=...)`` to get an
EdgeDataView which yields `(u, v, datadict)` or `(u, v, attr)` depending on
the ``data`` argument.

Examples:

.. code-block:: python

    >>> G = nx.Graph()
    >>> G.add_edge(0, 1, weight=3)
    >>> for u, v, d in G.edges(data=True):
    ...     print(u, v, d.get('weight'))
    0 1 3
    >>> list(G.edges(nbunch=[0]))
    [(0, 1)]

DegreeView
----------
A ``DegreeView`` reports degrees as ``(node, degree)`` pairs or supports
indexing for the degree of one node (``G.degree[n]``). Use ``weight='attr'``
for weighted degree and ``nbunch`` to restrict which nodes are reported.

Examples:

.. code-block:: python

    >>> G = nx.cycle_graph(4)
    >>> list(G.degree())
    [(0, 2), (1, 2), (2, 2), (3, 2)]
    >>> dict(G.degree())
    {0: 2, 1: 2, 2: 2, 3: 2}
    >>> G.degree[0]
    2
    >>> G.add_edge(0, 1, weight=5)
    >>> list(G.degree(weight='weight'))
    [(0, 3), (1, 3), (2, 2), (3, 2)]

See also
--------
- :mod:`networkx.classes.reportviews` (implementation and full docstrings)

