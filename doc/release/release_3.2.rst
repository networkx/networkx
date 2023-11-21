NetworkX 3.2
============

Release date: 18 October 2023

Supports Python 3.9, 3.10, 3.11, and 3.12.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

- Add ``@nx._dispatch`` decorator to most algorithms (`#6688 <https://github.com/networkx/networkx/pull/6688>`_).

API Changes
-----------

- Remove ``topo_order`` kwarg from ``is_semiconnected`` without deprecation (`#6651 <https://github.com/networkx/networkx/pull/6651>`_).
- deprecate Edmonds class (`#6785 <https://github.com/networkx/networkx/pull/6785>`_).
- Make weight part of the API for functions which had default assumptions (`#6814 <https://github.com/networkx/networkx/pull/6814>`_).
- ENH: let users set a default value in get_attr methods (`#6887 <https://github.com/networkx/networkx/pull/6887>`_).
- Rename function ``join`` as ``join_trees`` (`#6908 <https://github.com/networkx/networkx/pull/6908>`_).
- API: Add a decorator to deprecate positional args (`#6905 <https://github.com/networkx/networkx/pull/6905>`_).
- Expire deprecation for ``attrs`` kwarg in node_link module (`#6939 <https://github.com/networkx/networkx/pull/6939>`_).
- Minor touchup to the sort_neighbors deprecation (`#6942 <https://github.com/networkx/networkx/pull/6942>`_).
- Rm deprecated ``create_using`` kwarg from scale_free_graph (`#6940 <https://github.com/networkx/networkx/pull/6940>`_).
- Make position part of the API for geometric_edges (`#6816 <https://github.com/networkx/networkx/pull/6816>`_).
- Undeprecate literal_(de)stringizer (`#6943 <https://github.com/networkx/networkx/pull/6943>`_).
- Make new dtype param for incidence_matrix kwarg-only (`#6954 <https://github.com/networkx/networkx/pull/6954>`_).
- Make weight and seed for ``fast_label_propagation_communities`` kwarg only (`#6955 <https://github.com/networkx/networkx/pull/6955>`_).
- API: Rm default value from time_delta for cd_index (`#6953 <https://github.com/networkx/networkx/pull/6953>`_).
- Deprecate strongly_connected_components_recursive (`#6957 <https://github.com/networkx/networkx/pull/6957>`_).
- Rm deprecated clique helper functions (`#6941 <https://github.com/networkx/networkx/pull/6941>`_).

Enhancements
------------

- Update calculation of triangles (`#6258 <https://github.com/networkx/networkx/pull/6258>`_).
- Add single_source_all_shortest_paths and all_pairs_all_shortest_paths (`#5959 <https://github.com/networkx/networkx/pull/5959>`_).
- Add ``@nx._dispatch`` decorator to most algorithms (`#6688 <https://github.com/networkx/networkx/pull/6688>`_).
- Move benchmarks inside main repo (`#6835 <https://github.com/networkx/networkx/pull/6835>`_).
- ENH -- Replaced for-loops in :function:``rescale_layout`` with numpy vectorized methods (`#6879 <https://github.com/networkx/networkx/pull/6879>`_).
- Fast label propagation algorithm for community detection (`#6843 <https://github.com/networkx/networkx/pull/6843>`_).
- Add time series Visibility Graph generator (`#6880 <https://github.com/networkx/networkx/pull/6880>`_).
- Random trees & forests (`#6758 <https://github.com/networkx/networkx/pull/6758>`_).
- Add support for tuple-nodes to default gml parser (`#6950 <https://github.com/networkx/networkx/pull/6950>`_).
- Add Kemeny's constant (`#6929 <https://github.com/networkx/networkx/pull/6929>`_).
- Speedup resistance_distance (`#6925 <https://github.com/networkx/networkx/pull/6925>`_).
- Allow graph generators and conversion functions to be dispatched (`#6876 <https://github.com/networkx/networkx/pull/6876>`_).
- adding extendability problem (2nd try) (`#4890 <https://github.com/networkx/networkx/pull/4890>`_).

Bug Fixes
---------

- Fixing DOT format for to_agraph() (`#6474 <https://github.com/networkx/networkx/pull/6474>`_).
- Remove ``topo_order`` kwarg from ``is_semiconnected`` without deprecation (`#6651 <https://github.com/networkx/networkx/pull/6651>`_).
- Stabilize test of approximation.connected_components (`#6715 <https://github.com/networkx/networkx/pull/6715>`_).
- Fix minimum_cycle_basis and change to return cycle instead of set (`#6788 <https://github.com/networkx/networkx/pull/6788>`_).
- Refix minimum_cycle_basis and scipy.sparse conversions and add tests (`#6789 <https://github.com/networkx/networkx/pull/6789>`_).
- number_of_walks might use a weighted edge attribute (`#6815 <https://github.com/networkx/networkx/pull/6815>`_).
- GML: added support for reading multi-line values (`#6837 <https://github.com/networkx/networkx/pull/6837>`_).
- Avoid directed_laplacian_matrix causing nans in some cases (`#6866 <https://github.com/networkx/networkx/pull/6866>`_).
- Add test about zero weight cycles and fix goldberg-radzik (`#6892 <https://github.com/networkx/networkx/pull/6892>`_).
- Modify ``s_metric`` ``normalized`` default so function doesn't raise (`#6841 <https://github.com/networkx/networkx/pull/6841>`_).
- Error handling for invalid prufer sequence ``from_prufer_sequence``: issue #6420 (`#6457 <https://github.com/networkx/networkx/pull/6457>`_).
- FIX: Better default behaviour for percolation centrality with no node attrs (`#6894 <https://github.com/networkx/networkx/pull/6894>`_).
- FIX: MultiDiGraphs keys got lost in weighted shortest paths (`#6963 <https://github.com/networkx/networkx/pull/6963>`_).
- Handle edge cases in Laplacian centrality (`#6938 <https://github.com/networkx/networkx/pull/6938>`_).
- adding a formula that ignores self-loops at the each level of directed louvain algorithm (`#6630 <https://github.com/networkx/networkx/pull/6630>`_).
- Fix ``````is_k_edge_connected`````` for case of k=2 (`#7024 <https://github.com/networkx/networkx/pull/7024>`_).

Documentation
-------------

- Fix links in laplacian_centrality and laplacian_matrix (`#6623 <https://github.com/networkx/networkx/pull/6623>`_).
- Add Greedy Coloring Example to Gallery (`#6647 <https://github.com/networkx/networkx/pull/6647>`_).
- Add linting to contributor guide (`#6692 <https://github.com/networkx/networkx/pull/6692>`_).
- Minor fixups to equitable_coloring docstring (`#6673 <https://github.com/networkx/networkx/pull/6673>`_).
- Remove survey banner (`#6818 <https://github.com/networkx/networkx/pull/6818>`_).
- fix: make messages readable (`#6860 <https://github.com/networkx/networkx/pull/6860>`_).
- add docs for source input of dfs_predecessor and dfs_successor (`#6867 <https://github.com/networkx/networkx/pull/6867>`_).
- Clarify that basis generates simple cycles only (`#6882 <https://github.com/networkx/networkx/pull/6882>`_).
- Revert "Clarify that basis generates simple cycles only" (`#6885 <https://github.com/networkx/networkx/pull/6885>`_).
- updating TSP example docs (`#6794 <https://github.com/networkx/networkx/pull/6794>`_).
- MAINT: Point the PR template to pre-commit (`#6902 <https://github.com/networkx/networkx/pull/6902>`_).
- fix doc build errors/warnings (`#6907 <https://github.com/networkx/networkx/pull/6907>`_).
- DOC: stray backtick and double instead of simple backtick (`#6917 <https://github.com/networkx/networkx/pull/6917>`_).
- DOC: Add example for self loop multidigraph in contraction (`#6901 <https://github.com/networkx/networkx/pull/6901>`_).
- Fix sphinx docs rendering of dispatched functions (`#6895 <https://github.com/networkx/networkx/pull/6895>`_).
- added more examples on graphical degree sequence (`#5634 <https://github.com/networkx/networkx/pull/5634>`_).
- Minor touchup to the sort_neighbors deprecation (`#6942 <https://github.com/networkx/networkx/pull/6942>`_).
- Warning comment for float weights in betweenness.py (`#5171 <https://github.com/networkx/networkx/pull/5171>`_).
- DOC: Misc typos (`#6959 <https://github.com/networkx/networkx/pull/6959>`_).
- Fixing typo in effective_size documentation (`#6967 <https://github.com/networkx/networkx/pull/6967>`_).
- fix examples in tournament.py (`#6964 <https://github.com/networkx/networkx/pull/6964>`_).
- Fix a reference (`#6977 <https://github.com/networkx/networkx/pull/6977>`_).
- Add missing parameter to snap_aggregation docstring (`#6978 <https://github.com/networkx/networkx/pull/6978>`_).
- Update developer deprecation todo list (`#6985 <https://github.com/networkx/networkx/pull/6985>`_).
- Add "networkx.plugin_info" entry point and update docstring (`#6911 <https://github.com/networkx/networkx/pull/6911>`_).
- document graph type; add links; rm unused import (`#6992 <https://github.com/networkx/networkx/pull/6992>`_).
- Add GraphBLAS backend to online docs (`#6998 <https://github.com/networkx/networkx/pull/6998>`_).
- Add 3.2rc0 release notes (`#6997 <https://github.com/networkx/networkx/pull/6997>`_).
- Update release process for changelist (`#7005 <https://github.com/networkx/networkx/pull/7005>`_).
- Update contributing guide for changelist workflow (`#7004 <https://github.com/networkx/networkx/pull/7004>`_).
- Fix definition of $m$ parameter in docstring of ``modularity`` function (`#6990 <https://github.com/networkx/networkx/pull/6990>`_).
- updated docs of SA_tsp and TA_tsp (`#7013 <https://github.com/networkx/networkx/pull/7013>`_).
- Update katz_centrality missing default alpha value (`#7015 <https://github.com/networkx/networkx/pull/7015>`_).

Maintenance
-----------

- Replacing codecov Python CLI with gh action (`#6635 <https://github.com/networkx/networkx/pull/6635>`_).
- Bump pyupgrade minimum Python version to 3.9 (`#6634 <https://github.com/networkx/networkx/pull/6634>`_).
- MAINT: minor coverage cleanup (`#6674 <https://github.com/networkx/networkx/pull/6674>`_).
- Rm unreachable code for validating input (`#6675 <https://github.com/networkx/networkx/pull/6675>`_).
- Pin sphinx<7 as temporary fix for doc CI failures (`#6680 <https://github.com/networkx/networkx/pull/6680>`_).
- Example of improving test granularity related to #5092 (`#5094 <https://github.com/networkx/networkx/pull/5094>`_).
- MAINT: Bump scipy version and take advantage of lazy loading (`#6704 <https://github.com/networkx/networkx/pull/6704>`_).
- Drop support for Python 3.8 per SPEC0 (`#6733 <https://github.com/networkx/networkx/pull/6733>`_).
- Update pygraphviz (`#6724 <https://github.com/networkx/networkx/pull/6724>`_).
- Update core dependencies per SPEC0 (`#6734 <https://github.com/networkx/networkx/pull/6734>`_).
- Test on Python 3.12-beta2 (`#6737 <https://github.com/networkx/networkx/pull/6737>`_).
- update the OSMnx example (`#6775 <https://github.com/networkx/networkx/pull/6775>`_).
- Minor fixups to clear up numpy deprecation warnings (`#6776 <https://github.com/networkx/networkx/pull/6776>`_).
- Add label-check workflow (`#6797 <https://github.com/networkx/networkx/pull/6797>`_).
- Use dependabot (`#6799 <https://github.com/networkx/networkx/pull/6799>`_).
- Bump webfactory/ssh-agent from 0.7.0 to 0.8.0 (`#6800 <https://github.com/networkx/networkx/pull/6800>`_).
- Attach milestone to merged PRs (`#6802 <https://github.com/networkx/networkx/pull/6802>`_).
- Add preserve_all_attrs to convert_from_nx to make it concise (`#6812 <https://github.com/networkx/networkx/pull/6812>`_).
- Bump scientific-python/attach-next-milestone-action from f94a5235518d4d34911c41e19d780b8e79d42238 to bc07be829f693829263e57d5e8489f4e57d3d420 (`#6830 <https://github.com/networkx/networkx/pull/6830>`_).
- Relax threshold in test of ``betweenness_centrality`` (`#6827 <https://github.com/networkx/networkx/pull/6827>`_).
- Add @nx._dispatch to {single_source,all_pairs}_all_shortest_paths, cd_index (`#6832 <https://github.com/networkx/networkx/pull/6832>`_).
- ci: Add distribution verification checks to nightly wheel upload (`#6831 <https://github.com/networkx/networkx/pull/6831>`_).
- MAINT: fix link to nightly releases wheels (`#6845 <https://github.com/networkx/networkx/pull/6845>`_).
- Don't test numpy2 nightlies (`#6852 <https://github.com/networkx/networkx/pull/6852>`_).
- MAINT: replace numpy aliases in scipy namespace (`#6857 <https://github.com/networkx/networkx/pull/6857>`_).
- Unpin scipy upperbound for tests (`#6727 <https://github.com/networkx/networkx/pull/6727>`_).
- Temporary work-around for NEP 51 numpy scalar reprs + NX doctests (`#6856 <https://github.com/networkx/networkx/pull/6856>`_).
- Unpin numpy nightly wheels (`#6854 <https://github.com/networkx/networkx/pull/6854>`_).
- fix: make messages readable (`#6860 <https://github.com/networkx/networkx/pull/6860>`_).
- Revert "Pin sphinx<7 as temporary fix for doc CI failures (#6680)" (`#6859 <https://github.com/networkx/networkx/pull/6859>`_).
- Change ``_dispatch`` to a class instead of a closure (`#6840 <https://github.com/networkx/networkx/pull/6840>`_).
- Move random_state decorators before ``@nx._dispatch`` (`#6878 <https://github.com/networkx/networkx/pull/6878>`_).
- MAINT: Make GEXF and graphml writer work with numpy 2.0 (`#6900 <https://github.com/networkx/networkx/pull/6900>`_).
- Rename function ``join`` as ``join_trees`` (`#6908 <https://github.com/networkx/networkx/pull/6908>`_).
- add missing ``join`` deprecation stuff to release_dev and conftest (`#6933 <https://github.com/networkx/networkx/pull/6933>`_).
- MAINT: move dispatch test workflow as an independent CI job (`#6934 <https://github.com/networkx/networkx/pull/6934>`_).
- MAINT: Use importlib.resources instead of file dunder to access files (`#6936 <https://github.com/networkx/networkx/pull/6936>`_).
- DOC, MAINT: Deduplicate docs instructions (`#6937 <https://github.com/networkx/networkx/pull/6937>`_).
- MAINT: Raise clean error with random_triad for graph with <3 nodes (`#6962 <https://github.com/networkx/networkx/pull/6962>`_).
- Update numpydoc (`#6773 <https://github.com/networkx/networkx/pull/6773>`_).
- MAINT: update pre-commit tools deps (`#6965 <https://github.com/networkx/networkx/pull/6965>`_).
- MAINT: Clean up commented out code in triads (`#6961 <https://github.com/networkx/networkx/pull/6961>`_).
- MAINT: Scipy nightly failing with np alias (`#6969 <https://github.com/networkx/networkx/pull/6969>`_).
- Bump actions/checkout from 3 to 4 (`#6970 <https://github.com/networkx/networkx/pull/6970>`_).
- Add for testing new pydata-sphinx-theme PR (`#6982 <https://github.com/networkx/networkx/pull/6982>`_).
- MAINT: Disable building delaunay geospatial example temporarily (`#6981 <https://github.com/networkx/networkx/pull/6981>`_).
- Revert "MAINT: Disable building delaunay geospatial example temporarily" (`#6984 <https://github.com/networkx/networkx/pull/6984>`_).
- Enhancements change default join trees 6947 (`#6948 <https://github.com/networkx/networkx/pull/6948>`_).
- Update sphinx theme (`#6930 <https://github.com/networkx/networkx/pull/6930>`_).
- Generate requirements files from pyproject.toml (`#6987 <https://github.com/networkx/networkx/pull/6987>`_).
- Use trusted publisher (`#6988 <https://github.com/networkx/networkx/pull/6988>`_).
- Prefer "backend" instead of "plugin" (`#6989 <https://github.com/networkx/networkx/pull/6989>`_).
- CI: Pin scientific-python/upload-nightly-action to 0.2.0 (`#6993 <https://github.com/networkx/networkx/pull/6993>`_).
- Support Python 3.12 (`#7009 <https://github.com/networkx/networkx/pull/7009>`_).
- pip install nx-cugraph from git, not nightly wheels, for docs (`#7011 <https://github.com/networkx/networkx/pull/7011>`_).
- Fix typos (`#7012 <https://github.com/networkx/networkx/pull/7012>`_).

Other
-----

- Update release process (`#6622 <https://github.com/networkx/networkx/pull/6622>`_).
- Add Lowest Common Ancestor example to Gallery (`#6542 <https://github.com/networkx/networkx/pull/6542>`_).
- Add examples to bipartite centrality.py (`#6613 <https://github.com/networkx/networkx/pull/6613>`_).
- Remove Python 3.8 from CI (`#6636 <https://github.com/networkx/networkx/pull/6636>`_).
- Fix links in eigenvector.py and katz_centrality.py (`#6640 <https://github.com/networkx/networkx/pull/6640>`_).
- Use the correct namespace for girvan_newman examples (`#6643 <https://github.com/networkx/networkx/pull/6643>`_).
- Preserve node order in bipartite_layout (`#6644 <https://github.com/networkx/networkx/pull/6644>`_).
- Make cycle_basis() deterministic (`#6654 <https://github.com/networkx/networkx/pull/6654>`_).
- Added docstrings examples for clique.py (`#6576 <https://github.com/networkx/networkx/pull/6576>`_).
- Fix output of is_chordal for empty graphs (`#6563 <https://github.com/networkx/networkx/pull/6563>`_).
- Allow multiple graphs for ``@nx._dispatch`` (`#6628 <https://github.com/networkx/networkx/pull/6628>`_).
- Adding GitHub Links next to Dheeraj's name in the contributors list (`#6670 <https://github.com/networkx/networkx/pull/6670>`_).
- Adding is_tounament to main namespace (`#6498 <https://github.com/networkx/networkx/pull/6498>`_).
- Use unpacking operator on dicts to prevent constructing intermediate objects (`#6040 <https://github.com/networkx/networkx/pull/6040>`_).
- Added tests to test_correlation.py (`#6590 <https://github.com/networkx/networkx/pull/6590>`_).
- Improve test coverage for neighbor_degree.py (`#6589 <https://github.com/networkx/networkx/pull/6589>`_).
- Added docstring examples for nx_pylab.py (`#6616 <https://github.com/networkx/networkx/pull/6616>`_).
- Improve Test Coverage for current_flow_closeness.py (`#6677 <https://github.com/networkx/networkx/pull/6677>`_).
- try adding circleci artifact secret (`#6679 <https://github.com/networkx/networkx/pull/6679>`_).
- Improve test coverage for reaching.py (`#6678 <https://github.com/networkx/networkx/pull/6678>`_).
- added tests to euler.py (`#6608 <https://github.com/networkx/networkx/pull/6608>`_).
- codespell: pre-commit, config, typos fixed (`#6662 <https://github.com/networkx/networkx/pull/6662>`_).
- Improve test coverage for mst.py (`#6540 <https://github.com/networkx/networkx/pull/6540>`_).
- Handle weights as ``distance=`` in testing dispatch (`#6671 <https://github.com/networkx/networkx/pull/6671>`_).
- remove survey banner (`#6687 <https://github.com/networkx/networkx/pull/6687>`_).
- CircleCI: add token for image redirector (`#6695 <https://github.com/networkx/networkx/pull/6695>`_).
- MAINT: Add subgraph_view and reverse_view to nx namespace directly through graphviews (`#6689 <https://github.com/networkx/networkx/pull/6689>`_).
- Added docstring example for dense.py (`#6669 <https://github.com/networkx/networkx/pull/6669>`_).
- MAINT: Add a github action cron job to upload nightly wheels (`#6701 <https://github.com/networkx/networkx/pull/6701>`_).
- MAINT: fix file path in nightly build workflow (`#6702 <https://github.com/networkx/networkx/pull/6702>`_).
- Add example script for shortest path (`#6534 <https://github.com/networkx/networkx/pull/6534>`_).
- Added doctrings for generic_graph_view (`#6697 <https://github.com/networkx/networkx/pull/6697>`_).
- Doc: wrong underline length (`#6708 <https://github.com/networkx/networkx/pull/6708>`_).
- MAINT: cron job to test against nightly deps every week (`#6705 <https://github.com/networkx/networkx/pull/6705>`_).
- simplify stack in dfs (`#6366 <https://github.com/networkx/networkx/pull/6366>`_).
- optimize generic_bfs_edges function (`#6359 <https://github.com/networkx/networkx/pull/6359>`_).
- Optimize _plain_bfs functions (`#6340 <https://github.com/networkx/networkx/pull/6340>`_).
- Added girth computation function (`#6633 <https://github.com/networkx/networkx/pull/6633>`_).
- MAINT: Stop CI from uploading nightly on forks (`#6717 <https://github.com/networkx/networkx/pull/6717>`_).
- Performance improvement for astar_path (`#6723 <https://github.com/networkx/networkx/pull/6723>`_).
- Skip scipy-1.11.0rc1 due to known issue (`#6726 <https://github.com/networkx/networkx/pull/6726>`_).
- Add an optional argument to the incidence_matrix function to provide … (`#6725 <https://github.com/networkx/networkx/pull/6725>`_).
- Graph walks implementation by jfinkels & dtekinoglu (`#5908 <https://github.com/networkx/networkx/pull/5908>`_).
- DOCS: Add walks to algorithms.index (`#6736 <https://github.com/networkx/networkx/pull/6736>`_).
- Add note about using latex formatting in docstring in the contributor guide (`#6535 <https://github.com/networkx/networkx/pull/6535>`_).
- Fix intersection_all method (`#6744 <https://github.com/networkx/networkx/pull/6744>`_).
- Fix Johnson method for unweighted graphs (`#6760 <https://github.com/networkx/networkx/pull/6760>`_).
- MAINT: Ignore SciPy v1.11 in requirements (`#6769 <https://github.com/networkx/networkx/pull/6769>`_).
- Replace deprecated numpy.alltrue method (`#6768 <https://github.com/networkx/networkx/pull/6768>`_).
- keep out scipy 1.11.1 (`#6772 <https://github.com/networkx/networkx/pull/6772>`_).
- Document additional imports required for building the documentation (`#6766 <https://github.com/networkx/networkx/pull/6766>`_).
- modified max_weight_matching to be non-recursive (`#6684 <https://github.com/networkx/networkx/pull/6684>`_).
- Rewrite NXEP 3 (`#6648 <https://github.com/networkx/networkx/pull/6648>`_).
- Refactor edmonds algorithm (`#6743 <https://github.com/networkx/networkx/pull/6743>`_).
- Docstring improvement for nx_pylab.py (`#6602 <https://github.com/networkx/networkx/pull/6602>`_).
- Use pyproject.toml (`#6774 <https://github.com/networkx/networkx/pull/6774>`_).
- Include missing package_data (`#6780 <https://github.com/networkx/networkx/pull/6780>`_).
- [BUG] Patch doc and functionality for ``is_minimal_d_separator`` (`#6427 <https://github.com/networkx/networkx/pull/6427>`_).
- Update to the documentation of eigenvector centrality (`#6009 <https://github.com/networkx/networkx/pull/6009>`_).
- Fix typo in contributing page (`#6784 <https://github.com/networkx/networkx/pull/6784>`_).
- Fix empty graph zero division error  for louvain (`#6791 <https://github.com/networkx/networkx/pull/6791>`_).
- Vertical chains for network text (`#6759 <https://github.com/networkx/networkx/pull/6759>`_).
- Time dependent module (`#6682 <https://github.com/networkx/networkx/pull/6682>`_).
- Allow user to opt out of edge attributes in from_numpy_array (`#6259 <https://github.com/networkx/networkx/pull/6259>`_).
- modifies ``````bfs_edges`````` and adds warning to ``````generic_bfs_edges`````` (`#5925 <https://github.com/networkx/networkx/pull/5925>`_).
- Spelling (`#6752 <https://github.com/networkx/networkx/pull/6752>`_).
- Added test cases for join operation and fixed join operation to handle label_attributes (`#6503 <https://github.com/networkx/networkx/pull/6503>`_).
- Remove serialisation artifacts on adjacency_graph (`#6041 <https://github.com/networkx/networkx/pull/6041>`_).
- Patch view signature (`#6267 <https://github.com/networkx/networkx/pull/6267>`_).
- Doc add nongraphical examples 6944 (`#6946 <https://github.com/networkx/networkx/pull/6946>`_).
- feat: docstring examples for algorithms/operators/all.py (`#6974 <https://github.com/networkx/networkx/pull/6974>`_).

Contributors
------------

70 authors added to this release (alphabetically):

- =510 (`@diohabara <https://github.com/diohabara>`_)
- `@achluma <https://github.com/achluma>`_
- `@anthonimes <https://github.com/anthonimes>`_
- `@axtavt <https://github.com/axtavt>`_
- `@cnfionawu <https://github.com/cnfionawu>`_
- `@dependabot[bot] <https://github.com/apps/dependabot>`_
- `@DiamondJoseph <https://github.com/DiamondJoseph>`_
- `@gsemer <https://github.com/gsemer>`_
- `@IbrH <https://github.com/IbrH>`_
- `@peijenburg <https://github.com/peijenburg>`_
- `@Tortar <https://github.com/Tortar>`_
- Adam Li (`@adam2392 <https://github.com/adam2392>`_)
- Adam Richardson (`@AdamWRichardson <https://github.com/AdamWRichardson>`_)
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- AKSHAYA MADHURI (`@akshayamadhuri <https://github.com/akshayamadhuri>`_)
- Alex Markham (`@Alex-Markham <https://github.com/Alex-Markham>`_)
- Alimi Qudirah (`@Qudirah <https://github.com/Qudirah>`_)
- Andreas Wilm (`@andreas-wilm <https://github.com/andreas-wilm>`_)
- Anthony Labarre (`@alabarre <https://github.com/alabarre>`_)
- Arturo (`@ArturoSbr <https://github.com/ArturoSbr>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Davide Bonin (`@davidbonin92 <https://github.com/davidbonin92>`_)
- Davide D'Ascenzo (`@Kidara <https://github.com/Kidara>`_)
- Dhaval Kumar (`@still-n0thing <https://github.com/still-n0thing>`_)
- Dheeraj Ravindranath (`@dheerajrav <https://github.com/dheerajrav>`_)
- Dilara Tekinoglu (`@dtekinoglu <https://github.com/dtekinoglu>`_)
- Efrem Braun (`@EfremBraun <https://github.com/EfremBraun>`_)
- Eirini Kafourou (`@eirinikafourou <https://github.com/eirinikafourou>`_)
- Eran Rivlis (`@erivlis <https://github.com/erivlis>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Evgenia Pampidi (`@evgepab <https://github.com/evgepab>`_)
- Florine W. Dekker (`@FWDekker <https://github.com/FWDekker>`_)
- Geoff Boeing (`@gboeing <https://github.com/gboeing>`_)
- Haoyang Li (`@thirtiseven <https://github.com/thirtiseven>`_)
- Ian Thompson (`@it176131 <https://github.com/it176131>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Jeremy Foote (`@jdfoote <https://github.com/jdfoote>`_)
- Jim Kitchen (`@jim22k <https://github.com/jim22k>`_)
- Jon Crall (`@Erotemic <https://github.com/Erotemic>`_)
- Jordan Matelsky (`@j6k4m8 <https://github.com/j6k4m8>`_)
- Josh Soref (`@jsoref <https://github.com/jsoref>`_)
- Juanita Gomez (`@juanis2112 <https://github.com/juanis2112>`_)
- Kelly Boothby (`@boothby <https://github.com/boothby>`_)
- Kian-Meng Ang (`@kianmeng <https://github.com/kianmeng>`_)
- Koen van Walstijn (`@kbvw <https://github.com/kbvw>`_)
- Lovro Šubelj (`@lovre <https://github.com/lovre>`_)
- Lukong Anne (`@Lukong123 <https://github.com/Lukong123>`_)
- Matt Schwennesen (`@mjschwenne <https://github.com/mjschwenne>`_)
- Matthew Feickert (`@matthewfeickert <https://github.com/matthewfeickert>`_)
- Matthias Bussonnier (`@Carreau <https://github.com/Carreau>`_)
- Mohamed Rezk (`@mohamedrezk122 <https://github.com/mohamedrezk122>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Navya Agarwal (`@navyagarwal <https://github.com/navyagarwal>`_)
- Nishant Bhansali (`@nishantb06 <https://github.com/nishantb06>`_)
- Omkar Yadav (`@yadomkar <https://github.com/yadomkar>`_)
- Paul Brodersen (`@paulbrodersen <https://github.com/paulbrodersen>`_)
- Paula Pérez Bianchi (`@paulitapb <https://github.com/paulitapb>`_)
- Pieter Eendebak (`@eendebakpt <https://github.com/eendebakpt>`_)
- Pieter Kuppens (`@pkuppens <https://github.com/pkuppens>`_)
- Purvi Chaurasia (`@PurviChaurasia <https://github.com/PurviChaurasia>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Salim BELHADDAD (`@salym <https://github.com/salym>`_)
- Sebastiano Vigna (`@vigna <https://github.com/vigna>`_)
- Siri (`@sirichandana-v <https://github.com/sirichandana-v>`_)
- Stefan van der Walt (`@stefanv <https://github.com/stefanv>`_)
- Sultan Orazbayev (`@SultanOrazbayev <https://github.com/SultanOrazbayev>`_)
- Vanshika Mishra (`@vanshika230 <https://github.com/vanshika230>`_)
- William Zijie Zhang (`@Transurgeon <https://github.com/Transurgeon>`_)
- Yaroslav Halchenko (`@yarikoptic <https://github.com/yarikoptic>`_)
- Zhaoyuan Deng (`@dzy49 <https://github.com/dzy49>`_)

41 reviewers added to this release (alphabetically):

- `@gsemer <https://github.com/gsemer>`_
- `@IbrH <https://github.com/IbrH>`_
- `@peijenburg <https://github.com/peijenburg>`_
- `@Tortar <https://github.com/Tortar>`_
- Aaron Z. (`@aaronzo <https://github.com/aaronzo>`_)
- Adam Li (`@adam2392 <https://github.com/adam2392>`_)
- Adam Richardson (`@AdamWRichardson <https://github.com/AdamWRichardson>`_)
- Alimi Qudirah (`@Qudirah <https://github.com/Qudirah>`_)
- Andreas Wilm (`@andreas-wilm <https://github.com/andreas-wilm>`_)
- Anthony Labarre (`@alabarre <https://github.com/alabarre>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Davide Bonin (`@davidbonin92 <https://github.com/davidbonin92>`_)
- Dilara Tekinoglu (`@dtekinoglu <https://github.com/dtekinoglu>`_)
- Efrem Braun (`@EfremBraun <https://github.com/EfremBraun>`_)
- Eirini Kafourou (`@eirinikafourou <https://github.com/eirinikafourou>`_)
- Eran Rivlis (`@erivlis <https://github.com/erivlis>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Evgenia Pampidi (`@evgepab <https://github.com/evgepab>`_)
- Ian Thompson (`@it176131 <https://github.com/it176131>`_)
- James Trimble's ONS work (`@jtrim-ons <https://github.com/jtrim-ons>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Jim Kitchen (`@jim22k <https://github.com/jim22k>`_)
- Jordan Matelsky (`@j6k4m8 <https://github.com/j6k4m8>`_)
- Josh Soref (`@jsoref <https://github.com/jsoref>`_)
- Kelly Boothby (`@boothby <https://github.com/boothby>`_)
- Lukong Anne (`@Lukong123 <https://github.com/Lukong123>`_)
- Matt Schwennesen (`@mjschwenne <https://github.com/mjschwenne>`_)
- Matthew Feickert (`@matthewfeickert <https://github.com/matthewfeickert>`_)
- Matthias Bussonnier (`@Carreau <https://github.com/Carreau>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Navya Agarwal (`@navyagarwal <https://github.com/navyagarwal>`_)
- Nishant Bhansali (`@nishantb06 <https://github.com/nishantb06>`_)
- Orion Sehn (`@OrionSehn-personal <https://github.com/OrionSehn-personal>`_)
- Purvi Chaurasia (`@PurviChaurasia <https://github.com/PurviChaurasia>`_)
- Robert (`@ImHereForTheCookies <https://github.com/ImHereForTheCookies>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Salim BELHADDAD (`@salym <https://github.com/salym>`_)
- Sebastiano Vigna (`@vigna <https://github.com/vigna>`_)
- Sultan Orazbayev (`@SultanOrazbayev <https://github.com/SultanOrazbayev>`_)
- Vanshika Mishra (`@vanshika230 <https://github.com/vanshika230>`_)
- Yaroslav Halchenko (`@yarikoptic <https://github.com/yarikoptic>`_)

_These lists are automatically generated, and may not be complete or may contain
duplicates._

