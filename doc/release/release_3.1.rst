NetworkX 3.1
============

Release date: 4 April 2023

Supports Python 3.8, 3.9, 3.10, and 3.11.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of 3 months of work with over 85 pull requests by
26 contributors. Highlights include:

- Minor bug-fixes and speed-ups
- Improvements to plugin based backend infrastructure
- Minor documentation improvements
- Improved test coverage
- Last release supporting Python 3.8
- Stopped building PDF version of docs
- Use Ruff for linting

Improvements
------------

- [`#6461 <https://github.com/networkx/networkx/pull/6461>`_]
  Add simple cycle enumerator for undirected class
- [`#6404 <https://github.com/networkx/networkx/pull/6404>`_]
  Add spectral bisection for graphs using fiedler vector
- [`#6244 <https://github.com/networkx/networkx/pull/6244>`_]
  Improve handling of create_using to allow Mixins of type Protocol
- [`#5399 <https://github.com/networkx/networkx/pull/5399>`_]
  Add Laplace centrality measure

Deprecations
------------

- [`#6564 <https://github.com/networkx/networkx/pull/6564>`_]
  Deprecate ``single_target_shortest_path_length`` to change return value to a dict in v3.3.
  Deprecate ``shortest_path`` in case of all_pairs to change return value to a iterator in v3.3.
- [`#5602 <https://github.com/networkx/networkx/pull/5602>`_]
  Deprecate ``forest_str`` function (use ``write_network_text`` instead).

Merged PRs
----------

- Designate 3.0 release
- Fix docs
- Bump release version
- Fix link in isomorphvf2.py (#6347)
- Add dev release notes template
- Update precommit hooks (#6348)
- Add clique examples and deprecate helper functions (#6186)
- Laplace centrality for issue 4973 (#5399)
- doc:improve doc of possible values of nodes and expected behaviour (#6333)
- add OrderedGraph removal as an API change in release_3.0.rst (#6354)
- Update release_3.0 authors (add Jim and Erik) (#6356)
- Fix broken link nx guide (#6361)
- Add nx-guide link in the tutorial (#6353)
- DOC: Minor formatting fixups to get rid of doc build warnings. (#6363)
- Fix equation in clustering documentation (#6369)
- Add reference to paper in vf2pp (#6373)
- provide tikz with degrees, not radians (#6360)
- Improve handling of create_using to allow Mixins of type Protocol (#6244)
- Remove an instance of random.sample from a set (deprecated in Python 3.9) (#6380)
- DOC: Add banner for user survey announcement (#6375)
- bump pre-commit hooks (and fix CI) (#6396)
- Add generate / write "network text" (formerly graph_str) (#5602)
- Improve doc regular graphs (#6397)
- Fix link vonoroi (#6398)
- Document PageRank algo convergence condition  (#6212)
- Fix pre-commit on Python 3.10 (#6407)
- DOC: list pred method for MultiDiGraphs (#6409)
- Delete warning in approximation documentation (#6221)
- Comment out unused unlayered dict construction. (#6411)
- Update installation test instructions (#6303)
- Added new tests in test_clique.py (#6142)
- Improve testing of bipartite projection. (#6196)
- Add dispatching to more shortest path algorithms (#6415)
- Add Plausible Analytics to our docs (#6413)
- Fix docstring heading title. (#6424)
- Added tests to test_directed.py. (#6208)
- Gallery example for Maximum Independent Set (#5563)
- spectral bisection for graphs using fiedler vector (#6404)
- Update developer requirements (#6429)
- Fix reference in line.py-inverse_line_graph (#6434)
- Add project desc for visualization and ISMAGs (#6432)
- Lint using Ruff (#6371)
- add ruff commit to git-blame-ignore (#6440)
- NXEP 0 and NXEP 1 - change status to Accepted (#5343)
- Bump gh-pages deploy bot version. (#6446)
- Start using ruff for pyupgrade and isort (#6441)
- Add documentation building to contributor guide (#6437)
- Reset deploy-action param names for latest version. (#6451)
- Doc upgrade paley graph (#6399)
- Added two tests for convert_numpy (#6455)
- Clean up similarity.py and use dataclasses for storing state (#5831)
- Remove pdf latex builds of docs (#5572)
- Add docstring for dorogovtsev_goltsev_mendes generator (#6450)
- Allow first argument to be passed as kwarg in dispatcher (#6471)
- Fix negative edge cycle function raising exception for empty graph (#6473)
- Dispatch more BFS-based algorithms (#6467)
- Ignore weakrefs when testing for memory leak (#6466)
- Fix reference formatting in generator docstring. (#6493)
- tweak `test_override_dispatch` to allow G keyword (#6499)
- Improve test coverage for astar.py (#6504)
- Add docstring example to weighted.py (#6497)
- Fix len operation of UnionAtlas (#6478)
- Improve test coverage for edgelist.py (#6507)
- Improve test coverage for mst.py and bug fix in prim_mst_edges() (#6486)
- Add examples clarifying ambiguity of nbunch (#6513)
- Updating removing explicit import for communities (#6459)
- Use generator to limit memory footprint of read_graph6. (#6519)
- Update docstring of paley graph  (#6529)
- Fixed bug k_truss doesn't raise exception for self loops (#6521)
- Update pre-commit (#6545)
- Update sphinx (#6544)
- Add docstring examples to dag.py (#6491)
- Add example script for mst (#6525)
- Add docstring examples to boundary.py (#6487)
- improve test coverage for branchings.py (#6523)
- Improve test coverage for redundancy.py (#6551)
- Fixed return type inconsistencies in shortest path methods documentation (#6528)
- Optimize _single_shortest_path_length function (#6299)
- Deprecate shortest_path functions to have consistent return values in v3.3 (#6567)
- Add community detection example to Gallery (#6526)
- add simple cycle enumerator for undirected class (#6461)
- Fix survey URL (#6548)
- Test dispatching via nx-loopback backend (#6536)
- Fixed return type inconsistencies in weighted.py (#6568)
- Update team galleries (#6569)
- Added Docstring Example for Bidirectional Shortest Path (#6570)
- Update release requirements (#6587)
- Designate 3.1rc0 release
- Bump release version
- corrections to docstring of `weisfeiler_lehman_subgraph_hashes` (#6598)
- Fixed method description in ismags.py (#6600)
- Minor docs/test maintenance (#6614)
- Better default alpha value for viz attributes in gexf writer (#6612)
- Fix module docstring format for ismags reference article. (#6611)
- Resolve NXEP4 with justification for not implementing it. (#6617)
- Fix typos (#6620)
- Draft release notes (#6621)
- Prep 3.1 release

Contributors
------------

- Navya Agarwal
- Lukong Anne
- Ross Barnowski
- Gabor Berei
- Paula Pérez Bianchi
- Kelly Boothby
- Purvi Chaurasia
- Jon Crall
- Michael Holtz
- Jim Kitchen
- Claudia Madrid
- Jarrod Millman
- Vanshika Mishra
- Harri Nieminen
- Tina Oberoi
- Omkaar
- Dima Pasechnik
- Alimi Qudirah
- Dan Schult
- Mridul Seth
- Eric Sims
- Tortar
- Erik Welch
- Aaron Z
- danieleades
- stanyas
