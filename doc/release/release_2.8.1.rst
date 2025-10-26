NetworkX 2.8.1
==============

Release date: 18 May 2022

Supports Python 3.8, 3.9, and 3.10

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

Minor documentation and bug fixes.


Improvements
------------

- Changed the treatment of directed graphs for `has_eulerian_path` which
  used to allow graphs with isolated nodes, i.e. nodes with zero degree to have
  an eulerian path. For undirected graphs, on the other hand, `has_eulerian_path`
  does not allow isolated nodes. For example:

      >>> G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])
      >>> G.add_node(3)
      >>> nx.has_eulerian_path(G)

  The above snippet used to produce `True` whereas the below one used to produce `False`.

      >>> G = nx.Graph([(0, 1), (1, 2), (2, 0)])
      >>> G.add_node(3)
      >>> nx.has_eulerian_path(G)

  The change makes the method consistent for both undirected and directed graph types so
  that it does not allow isolated nodes. (Both examples produce `False` now.)

- `is_bipartite_node_set` now raises an exception when the tested nodes are
  not distinct (previously this would not affect the outcome).
  This is to avoid surprising behaviour when using node sets in other bipartite
  algorithms, for example it yields incorrect results for `weighted_projected_graph`.

Merged PRs
----------

A total of 52 changes have been committed.

- Fix release notes
- Bump release version
- Change default value of arrowstyle for undirected graphs (#5514)
- added edge labels in weighted graph (#5521)
- Added examples in is_forest() and is_tree() (#5524)
- a hack to force self edges to be ignored on the first node inspected (#5516)
- De-Regression: eagerly evaluate not_implemented_for in decorated generators (#5537)
- Improve documentation of PlanarEmbedding class (#5523)
- PlanarEmbedding in autosummary instead of autoclass. (#5548)
- Added examples in tournament and tree functions (#5536)
- Fixup PlanarEmbedding See Also (#5556)
- Fix min_edge_cover in special cases (#5538)  and correct documentation (#5549)
- Add is_planar function.  Solves issue #5109 (#5544)
- Improve bridges documentation (#5519)
- fix greedy_modularity when multiple components exist. (#5550)
-  Fix issue probably-meant-fstring found at https://codereview.doctor (#5574)
- MAINT: Fix sphinx build errors and warnings (#5571)
- replace induced_subgraph example with directly relevant example (#5576)
- Add examples to compose operation (#5583)
- Fix reference in label_propagation_communities docstring (#5588)
- Use sets instead of lists for collecting flowfuncs in tests. (#5589)
- Update .degree() docs: outdated return type (#5529)
- Update numpydoc (#5580)
- Add a space in an error (#5601)
- improve docstring for read_doc, see issue #5604 (#5605)
- Cache `nodes` property on Graph (#5600)
- Fixes #5403: Errors on non-distinct bipartite node sets (#5442)
- Added documentation for branching_weight() solving issue #5553 (#5558)
- Distance measures example (#5608)
- Corrected the documentation of find_negative_cycle() solving issue #5610 (#5613)
- Added examples in connected and strongly connected functions (#5559)
- Update GH actions (#5622)
- Remove `_mat_spect_approx` in favor of simpler procedure (#5624)
- Replace np.flip with indexing in layouts. (#5623)
- Cache edges, degree, adj properties of Graph classes (#5614)
- Disallow isolated nodes for Eulerian Path (#5616)
- Fix triadic census (#5575)
- Adjust the usage of nodes_or_number decorator (#5599)
- Use new ubuntu LTS release (#5630)
- Build docs with Py 3.9 (#5632)
- added example on moral graph (#5633)
- Added examples in weakly_connected.py (#5593)
- Designate 2.8.1rc1 release
- Bump release version
- Rm unnecessary input validation from moral_graph. (#5638)
- DOC: fix up links, remove references to directed graphs, add proper cites (#5635)
- Added example under unary operators (#5625)
- Added docstring examples to matching functions (#5617)
- doc: fix typos in docstring and comment (#5647)
- DOC: remove note re: nonexistent param (#5648)
- added examples to covering.py (#5646)
- added examples on chain decomposition (#5641)
- Fix typo (#5652)


Contributors
------------

- William Allen
- Ross Barnowski
- Kelly Boothby
- Brit
- Guillem Francès
- Brian A. Heckman
- Horst JENS
- Lukong123
- Jarrod Millman
- Omkaar
- Dan Schult
- Mridul Seth
- Nikita Sharma
- Tatsuya Shimoda
- Dilara Tekinoglu
- Stefan van der Walt
- Aaron Z
- code-review-doctor
- danielolsen
- sheldonkhall
