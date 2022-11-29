NetworkX 2.8.6
==============

Release date: 22 August 2022

Supports Python 3.8, 3.9, and 3.10.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

Minor documentation and bug fixes.

Merged PRs
----------

A total of 30 changes have been committed.

- Add 2.8.5 release notes
- update all_pairs_lca docstrings (#5876)
- Improve LCA input validation (#5877)
- strategy_saturation_largest_first now accepts partial colorings (#5888)
- Fixed unused root argument in has_bridges (#5846)
- Update docs to include description of the `return_seen` kwarg (#5891)
- Add cache reset for when G._node is changed (#5894)
- Add weight distance metrics (#5305)
- Allow classes to relabel nodes -- casting (#5903)
- Update lattice.py (#5914)
- docstring updates for `union`, `disjoint_union`, and `compose` (#5892)
- Adds ```nx.bfs_layers``` method (#5879)
- Add to about_us.rst (#5919)
- Update precommit hooks (#5923)
- Remove old Appveyor cruft (#5924)
- signature change for `node_link` functions: for issue #5787 (#5899)
- Allow unsortable nodes in approximation.treewidth functions (#5921)
- Fix Louvain_partitions by yielding a copy of the sets in the partition gh-5901 (#5902)
- Replace LCA with naive implementations (#5883)
- Add function bfs_layers to docs (#5932)
- Bump nodelink args deprecation expiration to v3.2 (#5933)
- Update mapping logic in `relabel_nodes` (#5912)
- Propose to make new node_link arguments keyword only. (#5928)
- docstring update to lexicographical_topological_sort issue 5681 (#5930)
- Update pygraphviz (#5934)
- See matplotlb 3.6rc1 failure (#5937)

Contributors
------------

- Tanmay Aeron
- Ross Barnowski
- Kevin Brown
- Juanita Gomez
- Tigran Khachatryan
- Dhaval Kumar
- Lucas H. McCabe
- Jarrod Millman
- Sultan Orazbayev
- Dan Schult
- George Watkins
