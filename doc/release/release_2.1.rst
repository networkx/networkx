Announcement: NetworkX 2.1
==========================

We're happy to announce the release of NetworkX 2.1!
NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <http://networkx.github.io/>`_
and our `gallery of examples
<https://networkx.github.io/documentation/latest/auto_examples/index.html>`_.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of four months of work with 75 pull requests by
37 contributors. Highlights include:

  - Arrows for drawing DiGraph edges are vastly improved!
    And an example to show them.

  - More than 12 new functions for graph generation, manipulation and/or
    new graph algorithms.

    - Add a large clique size heuristic function (#2830)
    - Add rooted product function (#2825)
    - Label Propagation Community Detection (#2821)
    - Minimum cycle basis (#2823)
    - Add Mycielski Operator (#2785)
    - Adds prefix_tree, dag_to_branching, and example. (#2784)
    - Add inverse_line_graph generator from #2241 (#2782)
    - Steiner tree and metric closure. (#2252)
    - Add flow based node and edge disjoint paths. (#2063)
    - Update geometric networks with new models (#2498)
    - Graph edit distance (#2729)
    - Added function for finding a k-edge-augmentation (#2572)

  - G.name is no longer processed by graph operators. It remains as a
    property mechanism to access ``G.graph['name']`` but the user is in
    charge of updating or changing it for copies, subgraphs, unions and
    other graph operations.

Improvements
------------

  - Many bug fixes, documentation changes.
  - Speed improvements especially for subgraphs.
  - Changed input variable names for functions using ``**kwds``
    to avoid name collisions -- especially ``add_node``
  - New examples for arrows and spectral embedding of the grid graph.

API Changes
-----------

* [`#2498 <https://github.com/networkx/networkx/pull/2498>`_]
  In ``geographical_threshold_graph``, starting in NetworkX 2.1 the parameter
  ``alpha`` is deprecated and replaced with the customizable ``p_dist``
  function parameter, which defaults to r^-2
  if ``p_dist`` is not supplied. To reproduce networks of earlier NetworkX
  versions, a custom function needs to be defined and passed as the ``p_dist``
  parameter. For example, if the parameter ``alpha`` = 2 was used in NetworkX 2.0,
  the custom function def custom_dist(r): r**-2 can be passed in versions >=2.1
  as the parameter p_dist = custom_dist to produce an equivalent network.
  Note the change in sign from +2 to -2 in this parameter change.

* [`#2554 <https://github.com/networkx/networkx/issues/2554>`_]
  New algorithms for finding k-edge-connected components and k-edge-connected
  subgraphs in directed and undirected graphs. Efficient implementations are
  provided for the special case of k=1 and k=2. The new functionality is
  provided by:

     :func:`k_edge_components()`

     :func:`k_edge_subgraphs()`

* [`#2572 <https://github.com/networkx/networkx/issues/2572>`_]
  New algorithm finding for finding k-edge-augmentations in undirected graphs.
  Efficient implementations are provided for the special case of k=1 and k=2.
  New functionality is provided by:

   - :func:`k_edge_augmentation()`

* [`#2812 <https://github.com/networkx/networkx/pull/2812>`_]
  Removed ``bellman_ford``, please use
  ``bellman_ford_predecessor_and_distance``.

* [`#2811 <https://github.com/networkx/networkx/pull/2811>`_]
  Removed ``to_pandas_dataframe`` and ``from_pandas_dataframe``, please use
  ``to_pandas_adjacency``, ``from_pandas_adjacency``, ``to_pandas_edgelist``,
  or ``from_pandas_edgelist``.

* [`#2766 <https://github.com/networkx/networkx/pull/2766>`_]
  Add seed keyword argument to random_layout and spring_layout

* [`#2776 <https://github.com/networkx/networkx/pull/2776>`_]
  Add threshold option to spring layout

* [`#2774 <https://github.com/networkx/networkx/pull/2774>`_]
  max_weight_matching returns set of edges

* [`#2753 <https://github.com/networkx/networkx/pull/2753>`_]
  Add directed graphs support for jit_graph reading

* [`#2788 <https://github.com/networkx/networkx/pull/2788>`_]
  Control node-border color in draw_networkx_nodes

Deprecations
------------

* [`#2819 <https://github.com/networkx/networkx/pull/2819>`_]
  Deprecate ``connected_component_subgraphs``, ``biconnected_component_subgraphs``,
  ``attracting_component_subgraphs``, ``strongly_connected_component_subgraphs``,
  ``weakly_connected_component_subgraphs``.
  Instead use: ``[G.subgraph(c) for c in *_components]``

Contributors to this release
----------------------------

- Jack Amadeo
- Boskovits
- Daniel Bradburn
- David Bradway
- Ariel Chinn
- Jon Crall
- Rodrigo Dorantes-Gilardi
- Bradley Ellert
- Adam Erispaha
- Ioannis Filippidis
- ForFer
- Louis Gatin
- Aric Hagberg
- Harry
- Huston Hedinger
- Charles Tapley Hoyt
- James Lamb
- Sanghack Lee
- MD
- Cole MacLean
- Marco
- Jarrod Millman
- Sanggyu Nam
- Viraj Parimi
- Dima Pasechnik
- Richard Penney
- Naresh Peshwe
- Zachary Sailer
- Dan Schult
- Jordi Torrents
- John Wegis
- aparamon
- aweltsch
- gfyoung
- md0000
- mddddd
- talhum


Pull requests merged in this release
------------------------------------

- Update Release Notes for v2.1 (#2839)
- Update release notes (#2838)
- Update copyright (#2837)
- Add a large clique size heuristic function (#2830)
- Remove automatic processing of G.name attribute (#2829)
- Add rooted product function (#2825)
- Label Propagation Community Detection (#2821)
- change variable names to avoid kwargs clobber (#2824)
- Minimum cycle basis (#2823)
- Deprecate component_subgraphs functions (#2819)
- Temporarily disable sphinx doctests (#2818)
- Adjust docs for graph class edge attrib assignment (#2817)
- Add directed graphs support for jit_graph reading (#2753)
- Arrows as a plot example. (#2801)
- Fix bug in len(edges) for self-loops (#2816)
- MRG: Remove ``to_pandas_dataframe`` and ``from_pandas_dataframe`` (#2811)
- Fix Pydot tests so works with new version 1.2.4 (#2815)
- MRG: Remove ``bellman_ford`` (#2812)
- Combine generator modules and tweak docs (#2814)
- Legacy array printing for NumPy 1.14+ (#2810)
- Fix rare structurally forbidden mappings bug. (#2798)
- Digraph Arrows to fix #2757 (#2760)
- use a generic Integral type for parameters check (#2800)
- Control node-border color in draw_networkx_nodes (#2788)
- Add seed keyword argument to random_layout and spring_layout (#2766)
- Add Mycielski Operator (#2785)
- Adds prefix_tree, dag_to_branching, and example. (#2784)
- Add inverse_line_graph generator from #2241 (#2782)
- Add docs for steiner_tree and metric_closure (#2783)
- Steiner tree and metric closure. (#2252)
- Correct docstring for weight parameter (#2781)
- Switch to xcode 7.3 for osx_image in .travis.yml (#2780)
- Change how sparse6 tests filenames (#2779)
- Add flow based node and edge disjoint paths. (#2063)
- Update geometric networks with new models (#2498)
- [WIP] Graph edit distance 2361 (#2729)
- max_weight_matching returns set of edges (#2774)
- Avoid keyword and attribute clash (#2775)
- Add threshold option to spring layout (#2776)
- Fix bug in expected_degree_graph generator (#2773)
- Add support for incomplete partitions in quotient_graph. (#2771)
- Fix SOURCE_DATE_EPOCH ignored bug (#2735) (#2736)
- Makes write_graph6 less memory-intensive. (#2299)
- all_simple_paths should not return cycles. Fix issue #2762 (#2770)
- Fix typo in write_gml and add test (#2769)
- Fix bug and add checks for non-convergent fiedler_vector (#2681)
- Dictionary comprehensions from #1700 merged conflicts (#2768)
- Fix 2763: Typo `furether` in networkx tutorial documentation (#2764)
- Fix #2726: ensure add_path to add the first node (#2759)
- a minor correction in docs (#2751)
- Speedups for subgraph and copy methods (#2744)
- fix typo in tutorial (#2746)
- Expand documentation regarding strong connectivity (#2732)
- Correct when we raise NetworkXNotImplemented (#2731)
- removed list conversion from _triangles_and_degree_iter (#2725)
- nx_shp fixes (#2721)
- removed reference to create_using from union docs (#2722)
- Copy graph in transitive closure algorithm. (#2718)
- Fix dag_longest_path bug (#2703)
- Fix for inter_community_edges (#2713)
- Fix shortest_simple_paths. Issue #2427 (#2712)
- Update migration_guide_from_1.x_to_2.0.rst (#2694)
- mention `doc.txt` in `requirements/README.md` (#2699)
- docs(centrality/dispersion): updating contributor email address (#2698)
- Fixes bug #2503 by removing arrow labels (#2696)
- Add example of spectral embedding of the grid graph (#2690)
- Fix create_using of nx.from_pandas_adjacency() (#2693)
- Added function for finding a k-edge-augmentation (#2572)
- rm arg `strict` from function `networkx.drawing.nx_pydot.to_pydot` (#2672)
- Fixed problem parsing graphml with nodes in groups (#2644)
- Remove unused imports (#2653)
- Improve subgraph node iteration (#2687)
- Added Kamada-Kawai functions to Sphinx documentation (#2680)
- unpacked dict to provide kwargs when creating nodes from shapefiles (#2678)
- Fix typo in documentation (#2677)
