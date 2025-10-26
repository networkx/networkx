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

- Add random_spanning_tree to documentation (#5810)
- DOC: Switch to enumerated list in quotient_graph docstring (#5837)
- Add warning to nx_agraph about layout nondeterminism. (#5832)
- Update docs to include description of the `return_seen` kwarg (#5891)
- Add cache reset for when G._node is changed (#5894)
- Allow classes to relabel nodes -- casting (#5903)
- Update lattice.py (#5914)
- Add to about_us.rst (#5919)
- Update precommit hooks (#5923)
- Remove old Appveyor cruft (#5924)
- signature change for `node_link` functions: for issue #5787 (#5899)
- Allow unsortable nodes in approximation.treewidth functions (#5921)
- Fix Louvain_partitions by yielding a copy of the sets in the partition gh-5901 (#5902)
- Adds ```nx.bfs_layers``` method (#5879)
- Add function bfs_layers to docs (#5932)
- Propose to make new node_link arguments keyword only. (#5928)
- Bump nodelink args deprecation expiration to v3.2 (#5933)
- Add examples to lowest common ancestors algorithms (#5531)
- Naive lowest common ancestor implementation (#5736)
- Add examples for the condensation function (#5452)
- Minor doc fixups (#5868)
- update all_pairs_lca docstrings (#5876)
- Improve LCA input validation (#5877)
- Replace LCA with naive implementations (#5883)
- Update release notes
- docstring update to lexicographical_topological_sort issue 5681 (#5930)
- Support matplotlib 3.6rc1 failure (#5937)

Improvements
------------

- [`#5883 <https://github.com/networkx/networkx/pull/5883>`_]
  Replace the implementation of ``lowest_common_ancestor`` and
  ``all_pairs_lowest_common_ancestor`` with a "naive" algorithm to fix
  several bugs and improve performance.

Contributors
------------

- Tanmay Aeron
- Ross Barnowski
- Kevin Brown
- Matthias Bussonnier
- Tigran Khachatryan
- Dhaval Kumar
- Jarrod Millman
- Sultan Orazbayev
- Dan Schult
- Matt Schwennesen
- Dilara Tekinoglu
- kpetridis
