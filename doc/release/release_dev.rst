networkx 3.6rc0
===============

We're happy to announce the release of networkx 3.6rc0!

API Changes
-----------

- Replace ``random_lobster`` with ``random_lobster_graph`` (`#8067 <https://github.com/networkx/networkx/pull/8067>`_).
- Replace ``maybe_regular_expander`` with ``maybe_regular_expander_graph`` (`#8050 <https://github.com/networkx/networkx/pull/8050>`_).
- Rm networkx.algorithms.threshold.swap_d (`#8213 <https://github.com/networkx/networkx/pull/8213>`_).
- Expire deprecation of compute_v_structures (`#8281 <https://github.com/networkx/networkx/pull/8281>`_).
- Rm unused dissuade_hubs kwarg from forceatlas2 (`#8293 <https://github.com/networkx/networkx/pull/8293>`_).
- Expire deprecation of link kwarg in node_link fns (`#8282 <https://github.com/networkx/networkx/pull/8282>`_).
- DEP: Deprecate metric_closure (`#8304 <https://github.com/networkx/networkx/pull/8304>`_).

Enhancements
------------

- Improve error message for removed ``random_tree`` function (`#8105 <https://github.com/networkx/networkx/pull/8105>`_).
- Update approx current_flow betweenness to use k directly (`#8007 <https://github.com/networkx/networkx/pull/8007>`_).
- Proposal: update semantics for nonisomorphic trees with order 0 or 1 (`#8083 <https://github.com/networkx/networkx/pull/8083>`_).
- SCC benchmarks and use of ``G._adj`` in Tarjan algorithm (`#8064 <https://github.com/networkx/networkx/pull/8064>`_).
- Performance improvement and tests for ``edges_equal`` (`#8077 <https://github.com/networkx/networkx/pull/8077>`_).
- optimise ``is_reachable()`` (`#8112 <https://github.com/networkx/networkx/pull/8112>`_).
- Optimise harmonic centrality (`#8158 <https://github.com/networkx/networkx/pull/8158>`_).
- feat(drawing): add missing connection styles in ``draw_networkx_edge_labels`` and ``display`` (`#8108 <https://github.com/networkx/networkx/pull/8108>`_).
- Optimizing Dijkstra's paths to target (~50x faster for graphs with multiple-hops shortest path) (`#8023 <https://github.com/networkx/networkx/pull/8023>`_).
- Add ``all_triangles`` generator yielding all unique triangles in a graph (`#8135 <https://github.com/networkx/networkx/pull/8135>`_).
- refactor: simplify ``k_factor`` (`#8139 <https://github.com/networkx/networkx/pull/8139>`_).
- feat: add directed star graph (`#8151 <https://github.com/networkx/networkx/pull/8151>`_).
- Faster ``intersection_array`` computation for checking distance-regularity (`#7181 <https://github.com/networkx/networkx/pull/7181>`_).
- enh: short-circuit in ``is_regular`` for directed graphs (`#8138 <https://github.com/networkx/networkx/pull/8138>`_).
- Avoid re-exploring nodes in Kosaraju's SCC algorithm (`#8056 <https://github.com/networkx/networkx/pull/8056>`_).
- trust rank implementation and testing (`#8165 <https://github.com/networkx/networkx/pull/8165>`_).
- Add hyper_wiener_index function (`#8184 <https://github.com/networkx/networkx/pull/8184>`_).
- Bidirectional dijkstra optimization: from 1.1x to 25x faster (`#8206 <https://github.com/networkx/networkx/pull/8206>`_).
- Implement the algorithm to find the centroid(s) of a tree (`#8089 <https://github.com/networkx/networkx/pull/8089>`_).
- Set length threshold in FR and use np.clip (`#8145 <https://github.com/networkx/networkx/pull/8145>`_).
- Add panther++ (`#4400 <https://github.com/networkx/networkx/pull/4400>`_).
- maint: use ``nx.circulant_graph`` to generate Harary graphs (`#8189 <https://github.com/networkx/networkx/pull/8189>`_).
- ENH: add ``directed`` kwarg to ``edges_equal`` (`#8192 <https://github.com/networkx/networkx/pull/8192>`_).
- Optimizing Dijkstra's path construction for all targets case (`#8218 <https://github.com/networkx/networkx/pull/8218>`_).
- ENH: adds ISMAGS support for directed and multigraph with tests and refactor (`#8274 <https://github.com/networkx/networkx/pull/8274>`_).
- Dispatch classes such as ``nx.Graph(backend=...)`` (`#7760 <https://github.com/networkx/networkx/pull/7760>`_).
- ENH: Add is_perfect_graph using SPGT (follow-up to #8111) (`#8318 <https://github.com/networkx/networkx/pull/8318>`_).
- Add benchmark suite for shortest path algorithms on weighted graphs (`#8059 <https://github.com/networkx/networkx/pull/8059>`_).

Bug Fixes
---------

- Add Python 3.14 to testing matrix (`#8096 <https://github.com/networkx/networkx/pull/8096>`_).
- Fix round-trip to and from pygraphviz.AGraph setting spurious graph attributes (`#8121 <https://github.com/networkx/networkx/pull/8121>`_).
- Add input validation to ``non_randomness()`` and clarify its behavior (`#8057 <https://github.com/networkx/networkx/pull/8057>`_).
- Ensure that backend names are valid Python identifiers (`#8160 <https://github.com/networkx/networkx/pull/8160>`_).
- fix: resolve failure to pickle.loads(pickle.dumps(PlanarEmbedding())) (`#8186 <https://github.com/networkx/networkx/pull/8186>`_).
- Add GEXF 1.3 to the recognized GEXF versions (`#8196 <https://github.com/networkx/networkx/pull/8196>`_).
- BUG: Raise on directed graphs in ``nx.find_cliques_recursive`` (`#8211 <https://github.com/networkx/networkx/pull/8211>`_).
- fix ``optimize_edit_paths`` handling of self-loops (`#8207 <https://github.com/networkx/networkx/pull/8207>`_).
- BUG: add check for isolated nodes in ``degree_sequence_tree`` (`#8235 <https://github.com/networkx/networkx/pull/8235>`_).
- Mehlorn Steiner Tree (`#8052 <https://github.com/networkx/networkx/pull/8052>`_).
- BUG/MAINT: fix edge betweenness centrality scaling when ``k<N`` and merge all b.c. rescale helper functions (`#8256 <https://github.com/networkx/networkx/pull/8256>`_).
- Fix node attributes on lattice graphs (`#8311 <https://github.com/networkx/networkx/pull/8311>`_).
- BUG: allow graphs with nonstandard node labels in FISTA (`#8332 <https://github.com/networkx/networkx/pull/8332>`_).
- Make dominance functions consistent with definitions (`#8061 <https://github.com/networkx/networkx/pull/8061>`_).

Documentation
-------------

- Fix ``min_weight_matching`` (`#8062 <https://github.com/networkx/networkx/pull/8062>`_).
- Update deploy-docs yml to use Python 3.12 when deploying the docs (`#8102 <https://github.com/networkx/networkx/pull/8102>`_).
- DOC: Add missing params to bfs_layout docstring (`#8086 <https://github.com/networkx/networkx/pull/8086>`_).
- Add input validation to ``non_randomness()`` and clarify its behavior (`#8057 <https://github.com/networkx/networkx/pull/8057>`_).
- doc: improve docstring for hypercube_graph (`#8012 <https://github.com/networkx/networkx/pull/8012>`_).
- Improved documentation for boundary_expansion function (`#7905 <https://github.com/networkx/networkx/pull/7905>`_).
- DOC: Add docstring example count number of unique triangles (`#8144 <https://github.com/networkx/networkx/pull/8144>`_).
- Add function bfs_labeled_edges to docs (`#8149 <https://github.com/networkx/networkx/pull/8149>`_).
- Fix issues with urls in HITS reference docs (`#8156 <https://github.com/networkx/networkx/pull/8156>`_).
- Correct the docs for ``display()`` keyword ``node_pos`` (`#8153 <https://github.com/networkx/networkx/pull/8153>`_).
- Adding Notes on Multi-Target Shortest Path Queries (`#8169 <https://github.com/networkx/networkx/pull/8169>`_).
- 3d facebook plot example (`#6893 <https://github.com/networkx/networkx/pull/6893>`_).
- trust rank implementation and testing (`#8165 <https://github.com/networkx/networkx/pull/8165>`_).
- Improve docs for ``all_neighbors()`` (`#8166 <https://github.com/networkx/networkx/pull/8166>`_).
- Adding shortest-paths documentation (`#8187 <https://github.com/networkx/networkx/pull/8187>`_).
- Add Linux Foundation health score badge to README (`#8219 <https://github.com/networkx/networkx/pull/8219>`_).
- DOC: Add docstring for ``number_of_cliques`` (`#8216 <https://github.com/networkx/networkx/pull/8216>`_).
- DOC: add docstring for ``degree_sequence_tree`` (`#8236 <https://github.com/networkx/networkx/pull/8236>`_).
- DOC: Add examples to contracted_nodes (`#7856 <https://github.com/networkx/networkx/pull/7856>`_).
- DOC: fix wrong reference in ``leiden`` docs (`#8277 <https://github.com/networkx/networkx/pull/8277>`_).
- Fix over-indentation of list in chordless_cycles docstring (`#8288 <https://github.com/networkx/networkx/pull/8288>`_).
- Add iplotx to network drawing documentation (`#8289 <https://github.com/networkx/networkx/pull/8289>`_).
- Fix sphinx build errors (`#8303 <https://github.com/networkx/networkx/pull/8303>`_).
- DOC: Move deprecation procedure from contributing->dev guide (`#8308 <https://github.com/networkx/networkx/pull/8308>`_).
- DOC: add gallery example for metric_closure (`#8306 <https://github.com/networkx/networkx/pull/8306>`_).
- Cross-link Platonic graphs in See Also section (`#8307 <https://github.com/networkx/networkx/pull/8307>`_).
- Add seealso crosslinks between lattice graphs (`#8310 <https://github.com/networkx/networkx/pull/8310>`_).
- CI,DOC: Only run one parallel betweenness example (`#8305 <https://github.com/networkx/networkx/pull/8305>`_).
- DOC: rework betweenness centrality docstrings (`#8264 <https://github.com/networkx/networkx/pull/8264>`_).
- Rm 3D layout and animation from greedy_color example (`#8315 <https://github.com/networkx/networkx/pull/8315>`_).
- DOC: Clarify node and edge removal behavior in tutorial (`#8321 <https://github.com/networkx/networkx/pull/8321>`_).
- Improving connected module docs (`#8267 <https://github.com/networkx/networkx/pull/8267>`_).
- Docs: add nx-neptune backend documentation (`#8258 <https://github.com/networkx/networkx/pull/8258>`_).
- Improving shortest paths docs when there is no path between source and target (`#8327 <https://github.com/networkx/networkx/pull/8327>`_).
- Adding floating point considerations to tutorial (`#8324 <https://github.com/networkx/networkx/pull/8324>`_).
- Adding Dijkstra's algo specific doc (`#8286 <https://github.com/networkx/networkx/pull/8286>`_).
- Minor documentation build improvements (`#8329 <https://github.com/networkx/networkx/pull/8329>`_).
- Clarify the meaning of the cutoff parameter in some path-finding functions (`#7487 <https://github.com/networkx/networkx/pull/7487>`_).
- Switch to the NumFOCUS Code of Conduct (`#8320 <https://github.com/networkx/networkx/pull/8320>`_).

Maintenance
-----------

- Rm extraneous print from nx.display (`#8084 <https://github.com/networkx/networkx/pull/8084>`_).
- Remove structuralholes.py from ``needs_(num|sci)py`` (`#8088 <https://github.com/networkx/networkx/pull/8088>`_).
- Refactor image comparison tests (`#8097 <https://github.com/networkx/networkx/pull/8097>`_).
- Update deploy-docs yml to use Python 3.12 when deploying the docs (`#8102 <https://github.com/networkx/networkx/pull/8102>`_).
- Fix typo in extra name (`#8103 <https://github.com/networkx/networkx/pull/8103>`_).
- MAINT: Support PEP 639 for license metadata (`#8100 <https://github.com/networkx/networkx/pull/8100>`_).
- Use ``scipy.sparse`` array versions where applicable (`#8080 <https://github.com/networkx/networkx/pull/8080>`_).
- pass numpy seed by value not index (`#8116 <https://github.com/networkx/networkx/pull/8116>`_).
- Maintenance for broadcasting.py (`#8082 <https://github.com/networkx/networkx/pull/8082>`_).
- Bump the actions group across 1 directory with 6 updates (`#8085 <https://github.com/networkx/networkx/pull/8085>`_).
- Revert dict comprehensions -> dict.fromkeys accidentally introduced in #8017 (`#8018 <https://github.com/networkx/networkx/pull/8018>`_).
- refactor: improve ``generate_adjlist`` (`#8146 <https://github.com/networkx/networkx/pull/8146>`_).
- MAINT: Weekly cron job to run dispatch test with an extensive matrix (`#8154 <https://github.com/networkx/networkx/pull/8154>`_).
- Add benchmarks for multisrc_dijkstra over many small graphs (`#8164 <https://github.com/networkx/networkx/pull/8164>`_).
- test: clean up ``k_factor`` tests (`#8140 <https://github.com/networkx/networkx/pull/8140>`_).
- Use ``pytest.raises`` as a context (`#8170 <https://github.com/networkx/networkx/pull/8170>`_).
- Testing sentinel-node trick (`#8171 <https://github.com/networkx/networkx/pull/8171>`_).
- chore: make benchmarking and release requirements extras in ``pyproject.toml`` (`#8172 <https://github.com/networkx/networkx/pull/8172>`_).
- Add benchmarks for is_regular (`#8173 <https://github.com/networkx/networkx/pull/8173>`_).
- MAINT: use ``matrix_power`` from ``scipy.sparse`` in ``number_of_walks`` (`#8197 <https://github.com/networkx/networkx/pull/8197>`_).
- MAINT: remove ``try except`` for ``tomllib`` in ``generate_requirements`` (`#8198 <https://github.com/networkx/networkx/pull/8198>`_).
- MAINT: Ignore graph hashing warnings in tests (`#8205 <https://github.com/networkx/networkx/pull/8205>`_).
- STY: Variable rename proposal in bidirectional_dijkstra (`#8210 <https://github.com/networkx/networkx/pull/8210>`_).
- MAINT: Rm print from threshold_graph (`#8212 <https://github.com/networkx/networkx/pull/8212>`_).
- feat(api): update non-tree check in ``_tree_center``  and move to ``tree`` subpackage (`#8174 <https://github.com/networkx/networkx/pull/8174>`_).
- TST: add seed for ``random_cograph`` test (`#8228 <https://github.com/networkx/networkx/pull/8228>`_).
- Update links for broken testing badge in README (`#8234 <https://github.com/networkx/networkx/pull/8234>`_).
- Clarifying ``@_dispatchable(name=`` (`#8168 <https://github.com/networkx/networkx/pull/8168>`_).
- MAINT/TST: increase non-``slow`` coverage in ``k_components`` (`#8239 <https://github.com/networkx/networkx/pull/8239>`_).
- MAINT/TST: clean up tests for ``degree_seq`` (`#8257 <https://github.com/networkx/networkx/pull/8257>`_).
- Use CircleCI for coverage workflow (`#8178 <https://github.com/networkx/networkx/pull/8178>`_).
- Bump the actions group across 1 directory with 5 updates (`#8261 <https://github.com/networkx/networkx/pull/8261>`_).
- BUG/MAINT: fix edge betweenness centrality scaling when ``k<N`` and merge all b.c. rescale helper functions (`#8256 <https://github.com/networkx/networkx/pull/8256>`_).
- DOC/MAINT: Use ``itertools.pairwise`` in ``pairwise`` and add docstring (`#8201 <https://github.com/networkx/networkx/pull/8201>`_).
- Optimizing is_connected (`#8266 <https://github.com/networkx/networkx/pull/8266>`_).
- Rm outdated codecov badge from README (`#8272 <https://github.com/networkx/networkx/pull/8272>`_).
- CI: Move slow tests from coverage to dedicated run (`#8273 <https://github.com/networkx/networkx/pull/8273>`_).
- Move coverage configuration to pyproject.toml (`#8287 <https://github.com/networkx/networkx/pull/8287>`_).
- Making weakly connected logic consistent with connected logic (`#8285 <https://github.com/networkx/networkx/pull/8285>`_).
- Bump scientific-python/circleci-artifacts-redirector-action from 1.2.0 to 1.3.1 in the actions group (`#8309 <https://github.com/networkx/networkx/pull/8309>`_).
- CI: Add nicer rendering of env contents (`#8301 <https://github.com/networkx/networkx/pull/8301>`_).
- CI: Install ffmpeg in circleci docs pipeline (`#8291 <https://github.com/networkx/networkx/pull/8291>`_).
- Add/bump Python 3.14 to testing matrices (`#8319 <https://github.com/networkx/networkx/pull/8319>`_).
- Rm 3D layout and animation from greedy_color example (`#8315 <https://github.com/networkx/networkx/pull/8315>`_).
- MAINT: Remove unused sphinx extensions from conf.py (`#8314 <https://github.com/networkx/networkx/pull/8314>`_).
- optimize _single_shortest_path function (`#6337 <https://github.com/networkx/networkx/pull/6337>`_).
- Add autoflake and pyupgrade as manual pre-commit hooks (`#7870 <https://github.com/networkx/networkx/pull/7870>`_).
- ignore autoflake and pyupgrade changes (`#8333 <https://github.com/networkx/networkx/pull/8333>`_).
- Revert "ignore autoflake and pyupgrade changes" (`#8334 <https://github.com/networkx/networkx/pull/8334>`_).

Other
-----

- TST: improve coverage for ``generators/deg_seq.py`` (`#8226 <https://github.com/networkx/networkx/pull/8226>`_).
- TST: test ``max_iter`` in ``asyn_fluidc`` (`#8224 <https://github.com/networkx/networkx/pull/8224>`_).
- MAINT: clean up tests for ``steiner_tree`` (`#8259 <https://github.com/networkx/networkx/pull/8259>`_).
- TST: add non-``slow`` coverage for random graph generators (`#8252 <https://github.com/networkx/networkx/pull/8252>`_).
- TST: Add a nonslow test for ``all_node_cuts`` with shortest augmenting path flow function (`#8230 <https://github.com/networkx/networkx/pull/8230>`_).
- TST/MAINT: add non-slow coverage for random generators (`#8233 <https://github.com/networkx/networkx/pull/8233>`_).
- TST: add coverage for ``isomorphvf2`` (`#8251 <https://github.com/networkx/networkx/pull/8251>`_).
- TST: ensure determinism in ``nx_pylab`` drawing tests (`#8232 <https://github.com/networkx/networkx/pull/8232>`_).
- TST: add ``random_k_out_graph`` to tests to hit ``try except`` path (`#8231 <https://github.com/networkx/networkx/pull/8231>`_).
- TST: add coverage for some branches in ``internet_as_graphs.py`` (`#8225 <https://github.com/networkx/networkx/pull/8225>`_).
- TST: test ``topo_sort`` skips visited nodes in ``goldberg_radzik`` (`#8279 <https://github.com/networkx/networkx/pull/8279>`_).

Contributors
------------

38 authors added to this release (alphabetically):

- `@Aka2210 <https://github.com/Aka2210>`_
- `@dean985 <https://github.com/dean985>`_
- `@georako <https://github.com/georako>`_
- `@georakom <https://github.com/georakom>`_
- `@ishrathtahaseen-9 <https://github.com/ishrathtahaseen-9>`_
- `@sourabh-sudesh-paradeshi <https://github.com/sourabh-sudesh-paradeshi>`_
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- Adriano Meligrana (`@Tortar <https://github.com/Tortar>`_)
- akshita  (`@akshitasure12 <https://github.com/akshitasure12>`_)
- Albert Koppelmaa (`@albastardoto <https://github.com/albastardoto>`_)
- Alejandro Candioti (`@amcandio <https://github.com/amcandio>`_)
- Andrew Carbonetto (`@acarbonetto <https://github.com/acarbonetto>`_)
- Anthony Labarre (`@alabarre <https://github.com/alabarre>`_)
- Casper van Elteren (`@cvanelteren <https://github.com/cvanelteren>`_)
- Colman Bouton (`@LorentzFactor <https://github.com/LorentzFactor>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- dgpb (`@dg-pb <https://github.com/dg-pb>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Fabio Zanini (`@iosonofabio <https://github.com/iosonofabio>`_)
- Fei Pan (`@fei0319 <https://github.com/fei0319>`_)
- Florian2Richter (`@Florian2Richter <https://github.com/Florian2Richter>`_)
- Gilles Peiffer (`@Peiffap <https://github.com/Peiffap>`_)
- Gustavo Ataide (`@gustavo-ataide <https://github.com/gustavo-ataide>`_)
- Hadrien Crassous (`@Hadrien-Cr <https://github.com/Hadrien-Cr>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Jeff Bradberry (`@jbradberry <https://github.com/jbradberry>`_)
- Jonathan Reimer (`@jonathimer <https://github.com/jonathimer>`_)
- Maninder Dhanauta (`@Maninder-sd <https://github.com/Maninder-sd>`_)
- Marcus Fedarko (`@fedarko <https://github.com/fedarko>`_)
- Mauricio Souza de Alencar (`@mdealencar <https://github.com/mdealencar>`_)
- Michael Recachinas (`@mrecachinas <https://github.com/mrecachinas>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Peter Cock (`@peterjc <https://github.com/peterjc>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Stefano Vallodoro (`@ilvallod <https://github.com/ilvallod>`_)
- Supreeth Mysore Venkatesh (`@supreethmv <https://github.com/supreethmv>`_)
- Yasser El Haddar (`@Yasserelhaddar <https://github.com/Yasserelhaddar>`_)
- Yasser El Haddar (`@YasserElHaddar16 <https://github.com/YasserElHaddar16>`_)

24 reviewers added to this release (alphabetically):

- `@Aka2210 <https://github.com/Aka2210>`_
- `@dean985 <https://github.com/dean985>`_
- `@georakom <https://github.com/georakom>`_
- `@ishrathtahaseen-9 <https://github.com/ishrathtahaseen-9>`_
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- akshita  (`@akshitasure12 <https://github.com/akshitasure12>`_)
- Alejandro Candioti (`@amcandio <https://github.com/amcandio>`_)
- Anthony Labarre (`@alabarre <https://github.com/alabarre>`_)
- Christian Clauss (`@cclauss <https://github.com/cclauss>`_)
- Colman Bouton (`@LorentzFactor <https://github.com/LorentzFactor>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- dgpb (`@dg-pb <https://github.com/dg-pb>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Fei Pan (`@fei0319 <https://github.com/fei0319>`_)
- Gilles Peiffer (`@Peiffap <https://github.com/Peiffap>`_)
- Hiroki Hamaguchi (`@HirokiHamaguchi <https://github.com/HirokiHamaguchi>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Jeff Bradberry (`@jbradberry <https://github.com/jbradberry>`_)
- Marcus Fedarko (`@fedarko <https://github.com/fedarko>`_)
- Michael Recachinas (`@mrecachinas <https://github.com/mrecachinas>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Supreeth Mysore Venkatesh (`@supreethmv <https://github.com/supreethmv>`_)
- Yasser El Haddar (`@YasserElHaddar16 <https://github.com/YasserElHaddar16>`_)

_These lists are automatically generated, and may not be complete or may contain
duplicates._

