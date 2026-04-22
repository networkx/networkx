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

.. automodule:: networkx.classes.reportviews
.. autosummary::
   :toctree: generated/

   NodeView
   NodeDataView
   EdgeView
   EdgeDataView
   DegreeView

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
