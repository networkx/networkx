========
Requests
========

**Temporary placeholder until we figure out where this should live.**

Wiki
====

These items are from the old wiki and we need to sort through them.

Design Specification
--------------------

Proposed API for Di/Multi/Graph

Mutating Methods:
~~~~~~~~~~~~~~~~~

-  add_node/add_nodes_from
-  add_edge/add_edges_from
-  add_weighted_edges
-  remove_node/remove_nodes_from
-  remove_edge/remove_edges_from
-  clear

Reporting Objects:
~~~~~~~~~~~~~~~~~~

-  ``G.graph`` : dict of graph attribute key/values
-  ``G.node`` : dict of node attribute dicts pointed to by node
-  ``G.adj`` : dict of neighbor dicts of edge data dicts. Only the inner
   edge datadicts are mutable.
-  ``G.succ`` : same as ``adj`` but successors for DiGraph
-  ``G.pred`` : same as ``adj`` but predecessors for DiGraph

Reporting Views:
~~~~~~~~~~~~~~~~

-  ``G.name`` : property linked to G.graph[‘name’]
-  ``G.nodes`` : NodeView [set-like and dict-like interface to node
   information]

   -  ``__iter__`` over nodes,
   -  ``__contains__``,
   -  ``__len__``,
   -  Set operations ``&, ^, |, -``,
   -  ``__getitem__`` provides nodedatadict,
   -  ``.keys(), .values(), .items(), .data(), .get()``, ``data`` is
      like ``__call__``
   -  ``__call__`` returns **NodeDataView** : Data controlled by
      arguments ``data`` and ``default``. If ``data`` is True, full
      datadict; if ``data`` is string-like, data is the indicated
      attribute’s value or ``default`` if not present.

      -  ``__len__``
      -  ``__iter__`` over node-data pairs
      -  ``__contains__`` node membership **OR** (node, data) 2-tuple
         membership check
      -  ``__getitem__`` get data for node
      -  ``__call__`` returns another NodeDataView

-  ``G.degree`` : DegreeView [Iterable lookup view of Degree Info.
   Weighted Degree using Edge Attribute prescribed by ``weight``
   argument as a string. If ``nbunch`` argument present limit iteration
   to nodes in ``nbunch``]

   -  ``__iter__`` over ``(node, degree)`` pairs for nodes in ``nbunch``
   -  ``__len__`` number of nodes
   -  ``__getitem__`` degree for given node

-  ``G.edges`` : EdgeView [set-like and dict-like interface for Edge
   Info]

   -  ``__iter__`` over edge tuples. 2-tuples for graph/digraph;
      3-tuples ``(u, v, key)`` for multigraphs
   -  ``__contains__`` check 2-tuples/3-tuples for membership
   -  Set operations ``&, ^, |, -``
   -  ``__getitem__`` return edge datadict for given 2-tuple/3-tuple
   -  ``__len__`` number of edges
   -  ``.keys(), .values(), .items(), .data(), .get()``, ``data`` is
      like ``__call__``
   -  ``__call__`` returns **EdgeDataView** : Data controlled by
      arguments ``data`` and ``default``. If ``data is True``, full
      datadict; if ``data is False``, no data; if ``data`` is
      string-like, data is the indicated attribute’s value or
      ``default`` if not present. Argument ``nbunch`` limits edges to
      those incident to nodes in nbunch.

      -  ``__iter__`` over edge data tuples: possibly
         ``(u, v, key, data)``. ``key`` only for multigraph when
         argument ``keys is True``, ``data`` controlled by the ``data``
         argument as described above.
      -  ``__contains__`` checks tuples ``(u, v, key, data)`` (or
         shorter see above) for membership.

Reporting Methods:
~~~~~~~~~~~~~~~~~~

-  ``G.neighbors(n)`` iterator over neighbors. Largely deprecated via
   ``G.adj[n]``. ``successors/predecessors`` are similar for DiGraph
-  ``G.get_edge_data(u,v)`` Return the edge datadict for an edge tuple.
   Largely deprecated by ``G.edges[u, v]`` and ``G.adj[u][v]``.
-  ``G.adjacency_iter()`` iterator over (node, neighbors-dict) pairs.
   Largely deprecated by ``G.adj.items()``
-  ``G.has_node(n)`` membership check for Nodes. Largely deprecated by
   ``node in G``, or ``node in G.nodes``
-  ``G.has_edge(u, v)`` membership check for edge tuples. Largely
   deprecated by ``(u, v) in G.edges``
-  ``G.number_of_nodes/order()`` Largely deprecated by ``len(G.nodes)``
-  ``G.number of edges()`` with no arguments same as ``len(G.edges)``,
   with arguments ``u, v`` return how many edges between those two
   nodes.
-  G.copy
-  G.to_(un)directed
-  G.subgraph
-  G.nodes_with_selfloops
-  G.selfloop_edges
-  G.number_of_selfloops

Helper Functions/Filters:

-  ``G.nbunch_iter`` return an iterator over nodes in both ``nbunch``
   and ``G``.

For Directed Graphs we also have in/out_neighbors, in/out_edges,
in/out_degree. Neighbors and edges are out_neighbors and out_edges.
Degree is the sum of in_degree and out_degree.

Performance
~~~~~~~~~~~

It is often hard to predict performance with Python because there are so
many things that affect it. So the following are general rules of thumb
and you need to profile your code to find out what is the bottleneck in
your specific case.

-  In general, it is better to stay close to compiled code rather than
   interpreted code. It is better not to have to look up functions. It
   is sometimes better to not have to look up variables or object
   attributes. Do these things outside of your inner loops wherever
   possible.

-  Performance is often better with integer nodes (see
   ``convert_node_labels_to_integers``). Depending on what you are doing
   with node or edge attributes, it may be better to store them off of
   the Graph object as e.g. NumPy arrays. This is not the case when
   using NetworkX algorithms that access the attributes. But some
   applications only require NetworkX to report connection structure.

-  A common question is the relative performance of the base Graph
   methods. There are a few places where there is more than one way to
   get the same information. Which is better performance? Generally, use
   methods that are closer to the underlying dict methods;
   e.g. \ ``len(G)`` is slightly better than ``G.number_of_nodes()``.

**Neighbors of a node** (iteration): ``G.adj[n]`` is slightly faster
than ``G.neighbors(n)`` which is usually faster than ``G.edges(n)``. But
if you are iterating over all nodes, finding the neighbors of each,
``G.adj.items()`` works well but covers each edge twice, while
``G.edges()`` is slightly slower because it covers each edge once. For
DiGraphs ``G.pred[n]`` is better than ``G.predecessors(n)`` is better
than ``G.in_edges(n)``. And ``G.adj.items()`` is about the same as
``G.edges()``.

**Neighbor of a node?** (contains): ``G.adj[n]`` is much better than
``G.neighbors(n)`` or ``G.edges(n)``. (It uses the dict contains method
instead of list.)

**Degree of all nodes**: ``G.degree`` is usually what you want.
``dict(G.degree)`` when you will be repeatedly looking up.
``[d for n,d in G.degree]`` is a list of the degree values. But
``[len(nbrs) for n, nbrs in G.adj.items()]`` may be faster.

**Degree of one node**: ``G.degree[n]`` is usually what you want.
``len(G.adj[n])`` may be slightly faster, but usually not worth it.

NetworkX 2.0 API ~ DRAFT
------------------------


These are some ideas discussed regarding the 2.0 API

-  Rename all ``G.func_iter`` over ``G.func`` without changing the
   existing interfaces. ([@MridulS](https://github.com/MridulS) is
   currently working on it)
-  Look at other (non-method) functions that currently produce lists
   which should produce iterators. Triangles, clustering_coefficient
   come to mind.
-  Add a ``G.query(u, v, key, data)`` function for database-style edge
   data queries.
   `#1246(comment) <https://github.com/networkx/networkx/issues/1246#issuecomment-53139093>`__
   looks like a good place to start discussion regarding the
   ``G.query()`` function
-  Should API differ for Di/Multi/Graphs? We should definitely
   investigate further this.
   `#1246(comment) <https://github.com/networkx/networkx/issues/1246#issuecomment-73827675>`__
   is a good place to start.
-  Support for MixedGraph and MixedMultiGraph
   `#1168 <https://github.com/networkx/networkx/issues/1168>`__
-  `Design
   Specification <https://github.com/networkx/networkx/wiki/Design-Specification>`__
   contains a previously proposed API.
-  Behaviour of
   ``G[u][v]/G[u][v][data]/G[u][v][key]/G[u][v][key][data]`` (How often
   do these show up in the existing codebase?)
-  Drop ability to ``freeze`` a graph. See
   `#1698 <https://github.com/networkx/networkx/issues/1698>`__

Related issues:
`#1246 <https://github.com/networkx/networkx/issues/1246>`__,
`#1382 <https://github.com/networkx/networkx/issues/1382>`__

Issues
======

All of these are feature additions that have been requested and/or
have started implementations.
If you are interested in implementing one of these feature additions,
please check on the mailing list and/or issue tracker to see whether
this functionality is suitable for NetworkX before investing heavily
in implementing anything.

Algorithms
----------
- Borukva's (or modified) algorithm for minimum spanning tree: https://github.com/networkx/networkx/issues/417

- Detect a graph chordless cycles: https://github.com/networkx/networkx/issues/526

- k_path centrality algorithm: https://github.com/networkx/networkx/issues/612

- Canonical graph labelling: https://github.com/networkx/networkx/issues/678

- Chu-Liu/Edmonds algorithm: https://github.com/networkx/networkx/issues/639

- Louvain Modularity Community Detection algorithm: https://github.com/networkx/networkx/issues/951

- Densest k-subgraph problem: https://github.com/networkx/networkx/issues/999

- Sampling a tree: https://github.com/networkx/networkx/issues/1125

- s-core analysis for weighted networks: https://github.com/networkx/networkx/issues/1180

- min-cost perfect matching for generic graphs: https://github.com/networkx/networkx/issues/1304

- Incremental topological sort and strongly connected components: https://github.com/networkx/networkx/issues/1457

- Sparsification of Graphs: https://github.com/networkx/networkx/issues/1609

- Low-stretch spanning tree algorithms: https://github.com/networkx/networkx/issues/1610

- Iterative Deepening Search: https://github.com/networkx/networkx/issues/1909

- Generate a random planar graph: https://github.com/networkx/networkx/issues/2034

- More traversal algorithms for Multigraphs: https://github.com/networkx/networkx/issues/1120

- Postprocessing heuristic to improve approximate dominating set: https://github.com/networkx/networkx/issues/1572

- Edmonds algorithm improvements: https://github.com/networkx/networkx/issues/2115

- Condensation edge mapping: https://github.com/networkx/networkx/issues/2239

- Transitivity for weighted graphs: https://github.com/networkx/networkx/issues/2243

- Approximation algorithm for feedback vertex set: https://github.com/networkx/networkx/issues/2270

- SPQR tree for finding triconnected components and 2-vertex cuts: https://github.com/networkx/networkx/issues/2315

- Graph Edit Distance: https://github.com/networkx/networkx/issues/2361

- Find all faces for a planar graph: https://github.com/networkx/networkx/issues/2807

- Permutations of topological_sort: https://github.com/networkx/networkx/issues/2720

- Enhancements to line graph algorithms: https://github.com/networkx/networkx/issues/1567

- Maximally matchable edges: https://github.com/networkx/networkx/issues/2991

- Split-decomposition via graph-labelled-trees: https://github.com/networkx/networkx/issues/3085

- Check antichains for speedups for node_cuts: https://github.com/networkx/networkx/issues/3088

- Topological overlap: https://github.com/networkx/networkx/issues/3186

- Weighted Graph Support for Semi-Syncronous Label Propagation: https://github.com/networkx/networkx/issues/3242

- Graph generators and embedding methods: https://github.com/networkx/networkx/issues/3496

- 'hierarchical' positioning algorithm for plotting trees: https://github.com/networkx/networkx/issues/3420

- Eulerization of graphs: https://github.com/networkx/networkx/issues/3456

- Signed and Weighted Clustering Coefficient: https://github.com/networkx/networkx/issues/3490


Data Structues
--------------

- Data structures for mixed graph types: https://github.com/networkx/networkx/issues/1168

Interoperability
----------------

- Load Street Matps from OSM: https://github.com/networkx/networkx/issues/307

- Smallgraph interface: https://github.com/networkx/networkx/issues/1373

- Read and write METIS/DIMACS graphs: https://github.com/networkx/networkx/issues/2820

- XGMML support: https://github.com/networkx/networkx/issues/3474

- Geopandas interface: https://github.com/networkx/networkx/issues/3067


