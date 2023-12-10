.. _classes:

*****
Class
*****

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
| MixedEdgeGraph | mixed      | Yes                | No                     |
+----------------+------------+--------------------+------------------------+


Basic graph types
=================

.. toctree::
   :maxdepth: 2

   mixed_edge_graph

.. note:: NetworkX uses `dicts` to store the nodes and neighbors in a graph.
   So the reporting of nodes and edges for the base graph classes may not
   necessarily be consistent across versions and platforms; however, the reporting
   for CPython is consistent across platforms and versions after 3.6.

Here is an example of its usage:

.. code:: pycon

   >>> import networkx as nx
   >>> G = nx.MixedEdgeGraph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
   >>> # adds a directed edge from x to y
   >>> G.add_edge("x", "y", edge_type="directed")
   >>> # adds a bidirected edge from x to y
   >>> G.add_edge("x", "y", edge_type="bidirected")
