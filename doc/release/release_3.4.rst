NetworkX 3.4
============

Release date: 10 October 2024

Supports Python 3.10, 3.11, 3.12, and 3.13.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

API Changes
-----------

- Expires the ``forest_str`` deprecation (`#7414 <https://github.com/networkx/networkx/pull/7414>`_).
- [ENH, BUG]: added ``colliders`` and ``v_structures`` and deprecated ``compute_v_structures`` in ``dag.py`` (`#7398 <https://github.com/networkx/networkx/pull/7398>`_).
- Expires the ``random_tree`` deprecation (`#7415 <https://github.com/networkx/networkx/pull/7415>`_).
- Expire deprecation for strongly_connected_components_recursive (`#7420 <https://github.com/networkx/networkx/pull/7420>`_).
- Expire deprecated ``sort_neighbors`` param in ``generic_bfs_edges`` (`#7417 <https://github.com/networkx/networkx/pull/7417>`_).
- Rm deprecated normalized param from s_metric (`#7418 <https://github.com/networkx/networkx/pull/7418>`_).
- Expire deprecated nx.join in favor of join_trees (`#7419 <https://github.com/networkx/networkx/pull/7419>`_).
- Remove depercated Edmonds class for 3.4 (`#7447 <https://github.com/networkx/networkx/pull/7447>`_).
- Remove deprecated MultiDiGraph_EdgeKey for 3.4 (`#7448 <https://github.com/networkx/networkx/pull/7448>`_).
- Add ``edges`` keyword/deprecate ``link`` keyword arguments in ``JSON`` input-output (`#7565 <https://github.com/networkx/networkx/pull/7565>`_).
- Revert breaking change to ``node_link_*`` link defaults (`#7652 <https://github.com/networkx/networkx/pull/7652>`_).

Enhancements
------------

- Add a ``nodelist`` feature to ``from_numpy_array`` (`#7412 <https://github.com/networkx/networkx/pull/7412>`_).
- Prioritize edgelist representations in ``to_networkx_graph`` (`#7424 <https://github.com/networkx/networkx/pull/7424>`_).
- Adds initial debug logging calls to _dispatchable (`#7300 <https://github.com/networkx/networkx/pull/7300>`_).
- add: nodes attribute is modifiable (`#7532 <https://github.com/networkx/networkx/pull/7532>`_).
- Enable config to be used as context manager (`#7363 <https://github.com/networkx/networkx/pull/7363>`_).
- Added code to handle multi-graph in mst (`#7454 <https://github.com/networkx/networkx/pull/7454>`_).
- Enable caching by default (`#7498 <https://github.com/networkx/networkx/pull/7498>`_).
- #7546 More detail error message for pydot (`#7558 <https://github.com/networkx/networkx/pull/7558>`_).
- Fix weakly_connected_components() performance on graph view (`#7586 <https://github.com/networkx/networkx/pull/7586>`_).
- Forceatlas2 (`#7543 <https://github.com/networkx/networkx/pull/7543>`_).
- avoid iteration and use boolean indexing (`#7591 <https://github.com/networkx/networkx/pull/7591>`_).
- Hide edges with a weight of None in simple_paths (`#7583 <https://github.com/networkx/networkx/pull/7583>`_).
- Improved running time for harmonic centrality (`#7595 <https://github.com/networkx/networkx/pull/7595>`_).
- Add remove attribute functions (`#7569 <https://github.com/networkx/networkx/pull/7569>`_).
- Log "can/should run" and caching in dispatch machinery (`#7568 <https://github.com/networkx/networkx/pull/7568>`_).
- Individualize drawing attributes (`#7570 <https://github.com/networkx/networkx/pull/7570>`_).
- added nx-parallel gsoc project (`#7620 <https://github.com/networkx/networkx/pull/7620>`_).
- Harmonic diameter (`#5251 <https://github.com/networkx/networkx/pull/5251>`_).
- Allow dispatch machinery to fall back to networkx (`#7585 <https://github.com/networkx/networkx/pull/7585>`_).
- Add ``create_using`` parameter for random graphs (`#5672 <https://github.com/networkx/networkx/pull/5672>`_).
- Add config option to disable warning when using cached value (`#7497 <https://github.com/networkx/networkx/pull/7497>`_).

Bug Fixes
---------

- Fix graph name attribute for ``complete_bipartite_graph`` (`#7399 <https://github.com/networkx/networkx/pull/7399>`_).
- Remove import warnings during to_networkx_graph conversion (`#7426 <https://github.com/networkx/networkx/pull/7426>`_).
- Fix nx.from_pandas_edgelist so edge keys are not added as edge attributes and edge keys (`#7445 <https://github.com/networkx/networkx/pull/7445>`_).
- Fix ``from_pandas_edgelist`` for MultiGraph given edge_key (`#7466 <https://github.com/networkx/networkx/pull/7466>`_).
- Fix dispatch tests when using numpy 2 (`#7506 <https://github.com/networkx/networkx/pull/7506>`_).
- [ENH, BUG]: added ``colliders`` and ``v_structures`` and deprecated ``compute_v_structures`` in ``dag.py`` (`#7398 <https://github.com/networkx/networkx/pull/7398>`_).
- Fix reading edgelist when delimiter is whitespace, e.g. tab (`#7465 <https://github.com/networkx/networkx/pull/7465>`_).
- Ensure we always raise for unknown backend in ``backend=`` (`#7494 <https://github.com/networkx/networkx/pull/7494>`_).
- Prevent ``to_agraph`` from modifying graph argument (`#7610 <https://github.com/networkx/networkx/pull/7610>`_).
- Implementing iterative removal of non_terminal_leaves in Steiner Tree approximation (`#7422 <https://github.com/networkx/networkx/pull/7422>`_).
- Only allow connected graphs in ``eigenvector_centrality_numpy`` (`#7549 <https://github.com/networkx/networkx/pull/7549>`_).
- CI: Fix typo in nightly run pip install (`#7625 <https://github.com/networkx/networkx/pull/7625>`_).

Documentation
-------------

- Document missing shortest_path functions (`#7394 <https://github.com/networkx/networkx/pull/7394>`_).
- Optimal Edit Paths Return Section Improved (`#7375 <https://github.com/networkx/networkx/pull/7375>`_).
- Minor updates to simple_cycles docstring (`#7421 <https://github.com/networkx/networkx/pull/7421>`_).
- DOC: Clarifying ``NetworkXPointlessConcept`` exception (`#7434 <https://github.com/networkx/networkx/pull/7434>`_).
- DOC: updated ``pairs.py`` (`#7416 <https://github.com/networkx/networkx/pull/7416>`_).
- Add docstring example for directed tree (`#7449 <https://github.com/networkx/networkx/pull/7449>`_).
- Change docs of ``shortest_path_length`` so return is number instead of int (`#7477 <https://github.com/networkx/networkx/pull/7477>`_).
- Use intersphinx_registry to manage intersphinx mapping (`#7481 <https://github.com/networkx/networkx/pull/7481>`_).
- Ma: fix some spelling errors in docs (`#7480 <https://github.com/networkx/networkx/pull/7480>`_).
- Update NetworkX reference links in doc index (`#7500 <https://github.com/networkx/networkx/pull/7500>`_).
- strong product docs update (`#7511 <https://github.com/networkx/networkx/pull/7511>`_).
- Refactoring and enhancing user-facing ``Backend and Configs`` docs (`#7404 <https://github.com/networkx/networkx/pull/7404>`_).
- Fixed the citation in ``dominance.py`` [Issue #7522] (`#7524 <https://github.com/networkx/networkx/pull/7524>`_).
- Clarify generation number in ``dorogovtsev_goltsev_mendes_graph()`` (`#7473 <https://github.com/networkx/networkx/pull/7473>`_).
- Add ``Introspection`` section to backends docs (`#7556 <https://github.com/networkx/networkx/pull/7556>`_).
- DOC: Added ``default_config`` in ``get_info``'s description (`#7567 <https://github.com/networkx/networkx/pull/7567>`_).
- Prettify ``README.rst`` (`#7514 <https://github.com/networkx/networkx/pull/7514>`_).
- DOC: Fix typo in the code snippet provided in the docstring of nx_pydot.pydot_layout() (`#7572 <https://github.com/networkx/networkx/pull/7572>`_).
- Fix installation instructions for ``default`` extras in README (`#7574 <https://github.com/networkx/networkx/pull/7574>`_).
- Add missing metadata to v3.3 release notes (`#7592 <https://github.com/networkx/networkx/pull/7592>`_).
- Correct the members of steering council (`#7604 <https://github.com/networkx/networkx/pull/7604>`_).
- Fix dispatch docs formatting (`#7619 <https://github.com/networkx/networkx/pull/7619>`_).
- Add to Contributor List (`#7621 <https://github.com/networkx/networkx/pull/7621>`_).
- Example fix for issue 7633 (`#7634 <https://github.com/networkx/networkx/pull/7634>`_).
- Fix: Correct community color assignment in Girvan-Newman community detection (`#7644 <https://github.com/networkx/networkx/pull/7644>`_).
- Updated docstring for generators/karate_club_graph() (`#7626 <https://github.com/networkx/networkx/pull/7626>`_).
- Updates documentation to include details about using NetworkX with backends (`#7611 <https://github.com/networkx/networkx/pull/7611>`_).
- Add examples section to ``to_scipy_sparse_array`` (`#7627 <https://github.com/networkx/networkx/pull/7627>`_).
- Add examples to docstrings of subgraph_(iso/monomorphism) methods (`#7622 <https://github.com/networkx/networkx/pull/7622>`_).

Maintenance
-----------

- Simplify flow func augmentation logic in ``connectivity`` module (`#7367 <https://github.com/networkx/networkx/pull/7367>`_).
- A few more doctest skips for mpl/np dependencies (`#7403 <https://github.com/networkx/networkx/pull/7403>`_).
- Remove repetitive words (`#7406 <https://github.com/networkx/networkx/pull/7406>`_).
- FilterAdjacency: __len__ is recalculated unnecessarily #7377 (`#7378 <https://github.com/networkx/networkx/pull/7378>`_).
- Add check for empty graphs in ``flow_hierarchy`` (`#7393 <https://github.com/networkx/networkx/pull/7393>`_).
- Use nodelist feature of from_numpy_array (`#7425 <https://github.com/networkx/networkx/pull/7425>`_).
- Cleanup remaining usages of deprecated ``random_tree`` in package (`#7411 <https://github.com/networkx/networkx/pull/7411>`_).
- Add check for empty graphs in ``non_randomness`` (`#7395 <https://github.com/networkx/networkx/pull/7395>`_).
- Update tests for macOS Sonoma v14 (`#7437 <https://github.com/networkx/networkx/pull/7437>`_).
- Update doc requirements (`#7435 <https://github.com/networkx/networkx/pull/7435>`_).
- Update pygraphviz (`#7441 <https://github.com/networkx/networkx/pull/7441>`_).
- Always cache graph attrs for better cache behavior (`#7455 <https://github.com/networkx/networkx/pull/7455>`_).
- retain adjacency order in nx-loopback copy of networkx graph (`#7432 <https://github.com/networkx/networkx/pull/7432>`_).
- DEV: Add files generated by benchmarking to .gitignore (`#7461 <https://github.com/networkx/networkx/pull/7461>`_).
- Remove redundant graph copy in ``algorithms.bridges.bridges()`` (`#7471 <https://github.com/networkx/networkx/pull/7471>`_).
- CI: Add GitHub artifact attestations to package distribution (`#7459 <https://github.com/networkx/networkx/pull/7459>`_).
- Add ``polynomials.py`` to ``needs_numpy`` (`#7493 <https://github.com/networkx/networkx/pull/7493>`_).
- MAINT: Rename ``LoopbackDispatcher`` to ``LoopbackBackendInterface`` and ``dispatcher`` to ``backend_interface`` (`#7492 <https://github.com/networkx/networkx/pull/7492>`_).
- CI: update action that got moved org (`#7503 <https://github.com/networkx/networkx/pull/7503>`_).
- Update momepy (`#7507 <https://github.com/networkx/networkx/pull/7507>`_).
- Fix pygraphviz install on Windows (`#7512 <https://github.com/networkx/networkx/pull/7512>`_).
- MAINT: Made ``plot_image_segmentation_spectral_graph_partition`` example compatible with scipy 1.14.0 (`#7518 <https://github.com/networkx/networkx/pull/7518>`_).
- Fix CI installation of nx-cugraph in docs workflow (`#7538 <https://github.com/networkx/networkx/pull/7538>`_).
- Minor doc/test tweaks for dorogovtsev_goltsev_mendes (`#7535 <https://github.com/networkx/networkx/pull/7535>`_).
- CI: Add timeout limit to coverage job (`#7542 <https://github.com/networkx/networkx/pull/7542>`_).
- Update images used in docs build workflow (`#7537 <https://github.com/networkx/networkx/pull/7537>`_).
- Remove parallelization related TODO comments (`#7226 <https://github.com/networkx/networkx/pull/7226>`_).
- FIX: scipy 1d indexing tripped up numpy? (`#7541 <https://github.com/networkx/networkx/pull/7541>`_).
- Minor touchups to node_link functions (`#7540 <https://github.com/networkx/networkx/pull/7540>`_).
- Minor updates to colliders v_structures tests (`#7539 <https://github.com/networkx/networkx/pull/7539>`_).
- Update sphinx gallery config to enable sphinx build caching (`#7548 <https://github.com/networkx/networkx/pull/7548>`_).
- Update geospatial gallery dependencies (`#7508 <https://github.com/networkx/networkx/pull/7508>`_).
- Update ruff pre-commit and config (`#7547 <https://github.com/networkx/networkx/pull/7547>`_).
- More accurate NodeNotFound error message (`#7545 <https://github.com/networkx/networkx/pull/7545>`_).
- Update ruff config (`#7552 <https://github.com/networkx/networkx/pull/7552>`_).
- Add changelist config (`#7551 <https://github.com/networkx/networkx/pull/7551>`_).
- Fix installing nx-cugraph in deploy docs CI (`#7561 <https://github.com/networkx/networkx/pull/7561>`_).
- Fix ``nx_pydot.graphviz_layout`` for nodes with quoted/escaped chars (`#7588 <https://github.com/networkx/networkx/pull/7588>`_).
- DOC: Rm redundant module from autosummary (`#7599 <https://github.com/networkx/networkx/pull/7599>`_).
- Update numpydoc (1.8) (`#7573 <https://github.com/networkx/networkx/pull/7573>`_).
- Bump minimum pydot version to 3.0 (`#7596 <https://github.com/networkx/networkx/pull/7596>`_).
- CI: Include Python 3.13 in nightly wheel tests (`#7594 <https://github.com/networkx/networkx/pull/7594>`_).
- pydot - Remove Colon Check on Strings (`#7606 <https://github.com/networkx/networkx/pull/7606>`_).
- MAINT: Do not use requirements files in circle CI (`#7553 <https://github.com/networkx/networkx/pull/7553>`_).
- Do not use requirements file in github workflow (`#7495 <https://github.com/networkx/networkx/pull/7495>`_).
- ``weisfeiler_lehman_graph_hash``: add ``not_implemented_for("multigraph")`` decorator (`#7614 <https://github.com/networkx/networkx/pull/7614>`_).
- Update teams doc by running ``tools/team_list.py`` (`#7616 <https://github.com/networkx/networkx/pull/7616>`_).
- Add single node with self loop check to local and global reaching centrality (`#7350 <https://github.com/networkx/networkx/pull/7350>`_).
- Full test coverage for maxflow in issue #6029 (`#6355 <https://github.com/networkx/networkx/pull/6355>`_).
- CI: Fix typo in nightly run pip install (`#7625 <https://github.com/networkx/networkx/pull/7625>`_).
- DOC: Bring back plausible for docs (`#7639 <https://github.com/networkx/networkx/pull/7639>`_).
- Update minimum dependencies (SPEC 0) (`#7631 <https://github.com/networkx/networkx/pull/7631>`_).
- Update pygraphviz (1.14) (`#7654 <https://github.com/networkx/networkx/pull/7654>`_).
- modified product.py to raise NodeNotFound when 'root is not in H' (`#7635 <https://github.com/networkx/networkx/pull/7635>`_).
- Support Python 3.13 (`#7661 <https://github.com/networkx/networkx/pull/7661>`_).
- Use official Python 3.13 release (`#7667 <https://github.com/networkx/networkx/pull/7667>`_).

Other
-----

- chore: fix some typos in comments (`#7427 <https://github.com/networkx/networkx/pull/7427>`_).

Contributors
------------

53 authors added to this release (alphabetically):

- `@finaltrip <https://github.com/finaltrip>`_
- `@goodactive <https://github.com/goodactive>`_
- `@inbalh1 <https://github.com/inbalh1>`_
- `@johnthagen <https://github.com/johnthagen>`_
- `@jrdnh <https://github.com/jrdnh>`_
- `@lejansenGitHub <https://github.com/lejansenGitHub>`_
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- Alexander Bakhtin (`@bakhtos <https://github.com/bakhtos>`_)
- Ashwin Nayak (`@ashwin-nayak <https://github.com/ashwin-nayak>`_)
- Brigitta Sipőcz (`@bsipocz <https://github.com/bsipocz>`_)
- Casper van Elteren (`@cvanelteren <https://github.com/cvanelteren>`_)
- Charitha Buddhika Heendeniya (`@buddih09 <https://github.com/buddih09>`_)
- chrizzftd (`@chrizzFTD <https://github.com/chrizzFTD>`_)
- Cora Schneck (`@cyschneck <https://github.com/cyschneck>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Ewout ter Hoeven (`@EwoutH <https://github.com/EwoutH>`_)
- Fabian Spaeh (`@285714 <https://github.com/285714>`_)
- Gilles Peiffer (`@Peiffap <https://github.com/Peiffap>`_)
- Gregory Shklover (`@gregory-shklover <https://github.com/gregory-shklover>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Jim Hull (`@jmhull <https://github.com/jmhull>`_)
- Joye Mang (`@joyemang33 <https://github.com/joyemang33>`_)
- Kelvin Chung (`@KelvinChung2000 <https://github.com/KelvinChung2000>`_)
- Koushik_Nekkanti (`@KoushikNekkanti <https://github.com/KoushikNekkanti>`_)
- M Bussonnier (`@Carreau <https://github.com/Carreau>`_)
- Marc-Alexandre Côté (`@MarcCote <https://github.com/MarcCote>`_)
- Matt Schwennesen (`@mjschwenne <https://github.com/mjschwenne>`_)
- Matthew Feickert (`@matthewfeickert <https://github.com/matthewfeickert>`_)
- Maverick18 (`@Aditya-Shandilya1182 <https://github.com/Aditya-Shandilya1182>`_)
- Michael Bolger (`@mbbolger <https://github.com/mbbolger>`_)
- Miguel Cárdenas (`@miguelcsx <https://github.com/miguelcsx>`_)
- Mohamed Rezk (`@mohamedrezk122 <https://github.com/mohamedrezk122>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Mudassir Chapra (`@muddi900 <https://github.com/muddi900>`_)
- Orion Sehn (`@OrionSehn <https://github.com/OrionSehn>`_)
- Orion Sehn (`@OrionSehn-personal <https://github.com/OrionSehn-personal>`_)
- Peter Cock (`@peterjc <https://github.com/peterjc>`_)
- Philipp van Kempen (`@PhilippvK <https://github.com/PhilippvK>`_)
- prathamesh shinde (`@prathamesh901 <https://github.com/prathamesh901>`_)
- Raj Pawar (`@Raj3110 <https://github.com/Raj3110>`_)
- Rick Ratzel (`@rlratzel <https://github.com/rlratzel>`_)
- Rike-Benjamin Schuppner (`@Debilski <https://github.com/Debilski>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Sanchit Ram Arvind (`@sanchitram1 <https://github.com/sanchitram1>`_)
- Sebastiano Vigna (`@vigna <https://github.com/vigna>`_)
- STEVEN  ADAMS (`@hugehope <https://github.com/hugehope>`_)
- Thomas J. Fan (`@thomasjpfan <https://github.com/thomasjpfan>`_)
- Till Hoffmann (`@tillahoffmann <https://github.com/tillahoffmann>`_)
- Vanshika Mishra (`@vanshika230 <https://github.com/vanshika230>`_)
- Woojin Jung (`@WoojinJung-04 <https://github.com/WoojinJung-04>`_)
- Yury Fedotov (`@yury-fedotov <https://github.com/yury-fedotov>`_)
- Łukasz (`@lkk7 <https://github.com/lkk7>`_)

28 reviewers added to this release (alphabetically):

- `@finaltrip <https://github.com/finaltrip>`_
- `@inbalh1 <https://github.com/inbalh1>`_
- `@jrdnh <https://github.com/jrdnh>`_
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- Bhuvneshwar Chouksey (`@gbhuvneshwar <https://github.com/gbhuvneshwar>`_)
- Casper van Elteren (`@cvanelteren <https://github.com/cvanelteren>`_)
- chrizzftd (`@chrizzFTD <https://github.com/chrizzFTD>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Fabian Spaeh (`@285714 <https://github.com/285714>`_)
- Gilles Peiffer (`@Peiffap <https://github.com/Peiffap>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- M Bussonnier (`@Carreau <https://github.com/Carreau>`_)
- Matt Schwennesen (`@mjschwenne <https://github.com/mjschwenne>`_)
- Maverick18 (`@Aditya-Shandilya1182 <https://github.com/Aditya-Shandilya1182>`_)
- Michael Bolger (`@mbbolger <https://github.com/mbbolger>`_)
- Miguel Cárdenas (`@miguelcsx <https://github.com/miguelcsx>`_)
- Mohamed Rezk (`@mohamedrezk122 <https://github.com/mohamedrezk122>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Orion Sehn (`@OrionSehn <https://github.com/OrionSehn>`_)
- Orion Sehn (`@OrionSehn-personal <https://github.com/OrionSehn-personal>`_)
- Raj Pawar (`@Raj3110 <https://github.com/Raj3110>`_)
- Rick Ratzel (`@rlratzel <https://github.com/rlratzel>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Sanchit Ram Arvind (`@sanchitram1 <https://github.com/sanchitram1>`_)
- Sebastiano Vigna (`@vigna <https://github.com/vigna>`_)
- Till Hoffmann (`@tillahoffmann <https://github.com/tillahoffmann>`_)
- Woojin Jung (`@WoojinJung-04 <https://github.com/WoojinJung-04>`_)

_These lists are automatically generated, and may not be complete or may contain
duplicates._

