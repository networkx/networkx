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

This release is the result of 8 months of work with over 149 commits by
58 contributors. Highlights include:

- Add support for Python 3.7. This is the last release to support Python 2.
- Uniform random number generator (RNG) handling which defaults to global
  RNGs but allows specification of a single RNG for all random numbers in NX.
- Improved GraphViews to ease subclassing and remove cyclic references
  which caused trouble with deepcopy and pickle.
- New Graph method `G.update(H)`

Improvements
------------

Each function that uses random numbers now uses a `seed` argument to control
the random number generation (RNG). By default the global default RNG is
used. More precisely, the `random` package's default RNG or the numpy.random
default RNG. You can also create your own RNG and pass it into the `seed`
argument. Finally, you can use an integer to indicate the state to set for
the RNG. In this case a local RNG is created leaving the global RNG untouched.
Some functions use `random` and some use `numpy.random`, but we have written
a translater so that all functions CAN take a `numpy.random.RandomState`
object. So a single RNG can be used for the entire package.

Cyclic references between graph classes and views have been removed to ease
subclassing without memory leaks. Graphs no longer hold references to views.

Cyclic references between a graph and itself have been removed by eliminating
G.root_graph. It turns out this was an avoidable construct anyway.

GraphViews have been reformulated as functions removing much of the subclass
trouble with the copy/to_directed/subgraph methods. It also simplifies the
graph view code base and API. There are now three function that create
graph views: generic_graph_view(graph, create_using), reverse_view(digraph)
and subgraph_view(graph, node_filter, edge_filter).

GraphML can now be written with attributes using numpy numeric types.
In particular, np.float64 and np.int64 no longer need to convert to Python
float and int to be written. They are still written as generic floats so
reading them back in will not make the numpy values.

A generator following the Stochastic Block Model is now available.

New function `all_topolgical_sort` to generate all possible top_sorts.

New functions for tree width and tree decompositions.

Functions for Clauset-Newman-Moore modularity-max community detection.

Functions for small world analysis, directed clustering and perfect matchings,
eulerizing a graph, depth-limited BFS, percolation centrality,
planarity checking.

The shortest_path generic and convenience functions now have a `method`
parameter to choose between dijkstra and bellmon-ford in the weighted case.
Default is dijkstra (which was the only option before).

API Changes
-----------
empty_graph has taken over the functionality from
nx.convert._prep_create_using which was removed.

The `create_using` argument (used in many functions) should now be a
Graph Constructor like nx.Graph or nx.DiGraph.
It can still be a graph instance which will be cleared before use, but the
preferred use is a constructor.

New Base Class Method: update
H.update(G) adds the nodes, edges and graph attributes of G to H.
H.update(edges=e, nodes=n) add the edges and nodes from containers e and n.
H.update(e), and H.update(nodes=n) are also allowed.
First argument is a graph if it has `edges` and `nodes` attributes.
Otherwise the first argument is treated as a list of edges.

The bellman_ford predecessor dicts had sentinal value `[None]` for
source nodes. That has been changed so source nodes have pred value '[]'


Deprecations
------------

Graph class method `fresh_copy` - simply use `__class__`.
The GraphView classes are deprecated in preference to the function
interface. Specifically, `ReverseView` and `ReverseMultiView` are
replaced by `reverse_view`. `SubGraph`, `SubDiGraph`, `SubMultiGraph`
and `SubMultiDiGraph` are replaced by `subgraph_view`.
And `GraphView`, `DiGraphView`, `MultiGraphView`, `MultiDiGraphView`
are derecated in favor of `generic_graph_view(graph, create_using)`.


Contributors to this release
----------------------------

- Luca Baldesi
- William Bernoudy
- Alexander Condello
- Saurav Das
- Dormir30
- Graham Fetterman
- Robert Gmyr
- Thomas Grainger
- Benjamin M. Gyori
- Ramiro Gómez
- Darío Hereñú
- Mads Jensen
- Michael Johnson
- Pranay Kanwar
- Aabir Abubaker Kar
- Jacek Karwowski
- Mohammed Kashif
- David Kraeutmann
- Winni Kretzschmar
- Ivan Laković
- Daniel Leicht
- Katrin Leinweber
- Alexander Lenail
- Lonnen
- Ji Ma
- Erwan Le Merrer
- Jarrod Millman
- Baurzhan Muftakhidinov
- Neil
- Jens P
- Edward L Platt
- Guillaume Plique
- Miguel Sozinho Ramalho
- Lewis Robbins
- Romain
- Federico Rosato
- Tom Russell
- Dan Schult
- Gabe Schwartz
- Aaron Smith
- Leo Torres
- Martin Váňa
- Ruaridh Williamson
- Huon Wilson
- Haochen Wu
- Yuto Yamaguchi
- Felix Yan
- Jean-Gabriel Young
- aparamon
- armando1793
- aweltsch
- chebee7i
- hongshaoyang
- komo-fr
- leamingrad
- luzpaz
- mtrenfield
- regstrtn
