NetworkX 3.3
============

Release date: 6 April 2024

Supports Python 3.10, 3.11, and 3.12.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

API Changes
-----------

- Disallow negative number of nodes in ``complete_multipartite_graph`` (`#7057 <https://github.com/networkx/networkx/pull/7057>`_).
- DEP: Deprecate the all_triplets one-liner (`#7060 <https://github.com/networkx/networkx/pull/7060>`_).
- [A-star] Added expansion pruning via cutoff if cutoff is provided (`#7073 <https://github.com/networkx/networkx/pull/7073>`_).
- Make HITS raise exceptions consistent with power iterations (`#7084 <https://github.com/networkx/networkx/pull/7084>`_).
- DEP: Deprecate random_triad (`#7061 <https://github.com/networkx/networkx/pull/7061>`_).
- Added feature modular graph product (`#7227 <https://github.com/networkx/networkx/pull/7227>`_).
- ENH: Speed up common/non_neighbors by using _adj dict operations (`#7244 <https://github.com/networkx/networkx/pull/7244>`_).
- Deprecate the ``create`` argument of ``nonisomorphic_trees`` (`#7316 <https://github.com/networkx/networkx/pull/7316>`_).
- Improve total_spanning_tree_weight (`#7100 <https://github.com/networkx/networkx/pull/7100>`_).
- Update __init__.py (`#7320 <https://github.com/networkx/networkx/pull/7320>`_).
- add \*\*kwargs to traveling_salesman_problem (`#7371 <https://github.com/networkx/networkx/pull/7371>`_).

Enhancements
------------

- Add Tadpole graph (`#6999 <https://github.com/networkx/networkx/pull/6999>`_).
- [A-star] Added expansion pruning via cutoff if cutoff is provided (`#7073 <https://github.com/networkx/networkx/pull/7073>`_).
- Implementation of $S^1$ model (`#6858 <https://github.com/networkx/networkx/pull/6858>`_).
- [Feat] Random expanders utilities (`#6761 <https://github.com/networkx/networkx/pull/6761>`_).
- Compare graphs for generator functions when running tests with backend (`#7066 <https://github.com/networkx/networkx/pull/7066>`_).
- Add Kirchhoff index / Effective graph resistance (`#6926 <https://github.com/networkx/networkx/pull/6926>`_).
- Changed return types of shortest path methods to improve consistency (`#6584 <https://github.com/networkx/networkx/pull/6584>`_).
- New PR for Fixes minimal d-separator function failing to handle cases where no d-separators exist (`#7019 <https://github.com/networkx/networkx/pull/7019>`_).
- ENH : Provide non-normalized and normalized directed laplacian matrix calculation (`#7199 <https://github.com/networkx/networkx/pull/7199>`_).
- feat: drop the use of node attribute "first_nbr" in PlanarEmbedding (`#7202 <https://github.com/networkx/networkx/pull/7202>`_).
- Add functions to compute Schultz and Gutman Index (`#3709 <https://github.com/networkx/networkx/pull/3709>`_).
- Divisive community algorithms (`#5830 <https://github.com/networkx/networkx/pull/5830>`_).
- Added feature modular graph product (`#7227 <https://github.com/networkx/networkx/pull/7227>`_).
- ENH : added ``sort_neighbors`` to all functions in ``depth_first_search.py`` (`#7196 <https://github.com/networkx/networkx/pull/7196>`_).
- New graph generator for the Kneser graph (`#7146 <https://github.com/networkx/networkx/pull/7146>`_).
- Draw MultiDiGraph edges and labels qa7008 (`#7010 <https://github.com/networkx/networkx/pull/7010>`_).
- Use github actions to run a comparison benchmark (`#7268 <https://github.com/networkx/networkx/pull/7268>`_).
- BFS layout implementation (`#5179 <https://github.com/networkx/networkx/pull/5179>`_).
- Add ``max_level=`` argument to ``louvain_communities`` to limit macro-iterations (`#6909 <https://github.com/networkx/networkx/pull/6909>`_).
- Review and update ``@nx._dispatchable`` usage since 3.2.1 (`#7302 <https://github.com/networkx/networkx/pull/7302>`_).
- Transmogrify ``_dispatchable`` objects into functions (`#7298 <https://github.com/networkx/networkx/pull/7298>`_).
- fix: make ``PlanarEmbedding.copy()`` use ``add_edges_from()`` from parent (closes #7223) (`#7224 <https://github.com/networkx/networkx/pull/7224>`_).
- Allow seed of np.random instance to exactly produce arbitrarily large integers (`#6869 <https://github.com/networkx/networkx/pull/6869>`_).
- Improve total_spanning_tree_weight (`#7100 <https://github.com/networkx/networkx/pull/7100>`_).
- add seed to ``nx.generate_random_paths`` (`#7332 <https://github.com/networkx/networkx/pull/7332>`_).
- Allow backends to implement ``should_run`` (`#7257 <https://github.com/networkx/networkx/pull/7257>`_).
- Adding tree broadcasting algorithm in a new module (`#6928 <https://github.com/networkx/networkx/pull/6928>`_).
- Option to include initial labels in ``weisfeiler_lehman_subgraph_hashes`` (`#6601 <https://github.com/networkx/networkx/pull/6601>`_).
- Add better error message when trying to get edge that is not present (`#7245 <https://github.com/networkx/networkx/pull/7245>`_).
- Make ``is_negatively_weighted`` dispatchable (`#7352 <https://github.com/networkx/networkx/pull/7352>`_).
- Add option to hide or show tick labels (`#6018 <https://github.com/networkx/networkx/pull/6018>`_).
- ENH: Cache graphs objects when converting to a backend (`#7345 <https://github.com/networkx/networkx/pull/7345>`_).

Bug Fixes
---------

- Fix listing of release notes on Releases page (`#7030 <https://github.com/networkx/networkx/pull/7030>`_).
- Fix syntax warning from bad escape sequence (`#7034 <https://github.com/networkx/networkx/pull/7034>`_).
- Fix triangles to avoid using ``is`` to compare nodes (`#7041 <https://github.com/networkx/networkx/pull/7041>`_).
- Fix error message for ``nx.mycielski_graph(0)`` (`#7056 <https://github.com/networkx/networkx/pull/7056>`_).
- Disallow negative number of nodes in ``complete_multipartite_graph`` (`#7057 <https://github.com/networkx/networkx/pull/7057>`_).
- Handle edge cases for greedy_modularity_communities (`#6973 <https://github.com/networkx/networkx/pull/6973>`_).
- FIX: Match the doc description while copying over data (`#7092 <https://github.com/networkx/networkx/pull/7092>`_).
- fix: Include singleton/trivial paths in all_simple_paths & other functions (`#6694 <https://github.com/networkx/networkx/pull/6694>`_).
- Dinitz correction (`#6968 <https://github.com/networkx/networkx/pull/6968>`_).
- Modify GML test to fix invalid octal character warning (`#7159 <https://github.com/networkx/networkx/pull/7159>`_).
- Fix random_spanning_tree() for single node and empty graphs (`#7211 <https://github.com/networkx/networkx/pull/7211>`_).
- PlanarEmbedding.remove_edge() now updates removed edge's neighbors (`#6798 <https://github.com/networkx/networkx/pull/6798>`_).
- add seed to graph creation (`#7241 <https://github.com/networkx/networkx/pull/7241>`_).
- add seed to tests of fast_label_propatation_communities (`#7242 <https://github.com/networkx/networkx/pull/7242>`_).
- Fix rich_club_coefficient() for single node and empty graphs (`#7212 <https://github.com/networkx/networkx/pull/7212>`_).
- Fix minimum_spanning_arborescence regression (`#7280 <https://github.com/networkx/networkx/pull/7280>`_).
- Move arrowstyle input munging after intput validation (`#7293 <https://github.com/networkx/networkx/pull/7293>`_).
- Fix empty GraphML attribute is not parsed (`#7319 <https://github.com/networkx/networkx/pull/7319>`_).
- Add new test result to ``test_asadpour_tsp`` and change ``linprog`` method (`#7335 <https://github.com/networkx/networkx/pull/7335>`_).
- Fix custom weight attribute for Mehlhorn (`#6681 <https://github.com/networkx/networkx/pull/6681>`_).

Documentation
-------------

- Update release process (`#7029 <https://github.com/networkx/networkx/pull/7029>`_).
- Update convert_matrix.py (`#7018 <https://github.com/networkx/networkx/pull/7018>`_).
- fix extendability function name in bipartite.rst (`#7042 <https://github.com/networkx/networkx/pull/7042>`_).
- Minor doc cleanups to remove doc build warnings (`#7048 <https://github.com/networkx/networkx/pull/7048>`_).
- DOC: Add example to generic_bfs_edges to demonstrate the ``neighbors`` param (`#7072 <https://github.com/networkx/networkx/pull/7072>`_).
- Hierarchical clustering layout gallery example (`#7058 <https://github.com/networkx/networkx/pull/7058>`_).
- Fixed an error in the documentation of the katz centrality (`#6294 <https://github.com/networkx/networkx/pull/6294>`_).
- Create 3d_rotation_anime.py (`#7025 <https://github.com/networkx/networkx/pull/7025>`_).
- DOC: Add docstrings to filter view functions (`#7086 <https://github.com/networkx/networkx/pull/7086>`_).
- DOC: Add docstrings to Filter mapping views (`#7075 <https://github.com/networkx/networkx/pull/7075>`_).
- DOCS: Fix internal links to other functions in isomorphvf2 (`#6706 <https://github.com/networkx/networkx/pull/6706>`_).
- added note for the triangle inequality case in TSP (`#6995 <https://github.com/networkx/networkx/pull/6995>`_).
- Add note about importance of testing to contributor guide (`#7103 <https://github.com/networkx/networkx/pull/7103>`_).
- Proposal to add centrality overview to mentored projects (`#7104 <https://github.com/networkx/networkx/pull/7104>`_).
- Improve documentation of Component Algorithms (`#5473 <https://github.com/networkx/networkx/pull/5473>`_).
- Add dot io to readwrite (`#5061 <https://github.com/networkx/networkx/pull/5061>`_).
- Add Python versions to release notes (`#7113 <https://github.com/networkx/networkx/pull/7113>`_).
- DOC: Turn on inline plots in graph generators docstrings (`#6401 <https://github.com/networkx/networkx/pull/6401>`_).
- Fix duplicate numbering in contributor guide (`#7116 <https://github.com/networkx/networkx/pull/7116>`_).
- DOC: remove unnecessary 'or' in planted_partition_graph (`#7115 <https://github.com/networkx/networkx/pull/7115>`_).
- DOC: Link methods in functions to base Graph methods/properties (`#7125 <https://github.com/networkx/networkx/pull/7125>`_).
- Connect docs to doc_string for total_spanning_tree_weight (`#7098 <https://github.com/networkx/networkx/pull/7098>`_).
- Image (3D RGB data) segmentation by spectral clustering with 3D illustrations (`#7040 <https://github.com/networkx/networkx/pull/7040>`_).
- update triadic_census documentation for undirected graphs - issue 4386 (`#7141 <https://github.com/networkx/networkx/pull/7141>`_).
- added 3d and animation to plot_greedy_coloring.py (`#7090 <https://github.com/networkx/networkx/pull/7090>`_).
- DOC: fix URL econded links and doc references (`#7152 <https://github.com/networkx/networkx/pull/7152>`_).
- DOC: add reference to fast_label_propagation_communities (`#7167 <https://github.com/networkx/networkx/pull/7167>`_).
- updated See also sec of argmap class (`#7163 <https://github.com/networkx/networkx/pull/7163>`_).
- DOC : updated examples in mincost.py (`#7169 <https://github.com/networkx/networkx/pull/7169>`_).
- Document the walk_type argument default in directed_laplacian and similar functions (`#7171 <https://github.com/networkx/networkx/pull/7171>`_).
- DOC: Add plots to classic graph generators docs (`#7114 <https://github.com/networkx/networkx/pull/7114>`_).
- Fix a tiny typo in ``structuralholes.py::local_constraint`` docstring (`#7198 <https://github.com/networkx/networkx/pull/7198>`_).
- Added ``subgraph_is_monomorphic`` and ``subgraph_monomorphisms_iter`` in docs (`#7197 <https://github.com/networkx/networkx/pull/7197>`_).
- Fix online docs for ``_dispatch`` (`#7194 <https://github.com/networkx/networkx/pull/7194>`_).
- DOC : Updated docs for panther_similarity (`#7175 <https://github.com/networkx/networkx/pull/7175>`_).
- Fix warnings when building docs (`#7195 <https://github.com/networkx/networkx/pull/7195>`_).
- Improve docs for optimal_edit_paths (`#7130 <https://github.com/networkx/networkx/pull/7130>`_).
- DOC: build with nx-parallel extra documentation information (`#7220 <https://github.com/networkx/networkx/pull/7220>`_).
- Fixed typo in tensor product documentation (Fixes #7228) (`#7229 <https://github.com/networkx/networkx/pull/7229>`_).
- Add example for cycle detection (`#6560 <https://github.com/networkx/networkx/pull/6560>`_).
- Update general_k_edge_subgraphs docstring (`#7254 <https://github.com/networkx/networkx/pull/7254>`_).
- Update docstring of nonisomorphic_trees (`#7255 <https://github.com/networkx/networkx/pull/7255>`_).
- adding self loops related docs and tests for functions in ``cluster.py`` (`#7261 <https://github.com/networkx/networkx/pull/7261>`_).
- Add minimum_cycle_basis to cycle_basis See Also (`#7274 <https://github.com/networkx/networkx/pull/7274>`_).
- Update CONTRIBUTING.rst (`#7270 <https://github.com/networkx/networkx/pull/7270>`_).
- Fix all sphinx warnings during doc build (`#7289 <https://github.com/networkx/networkx/pull/7289>`_).
- Doc infrastructure: replace ``nb2plot`` with ``myst-nb`` (`#7237 <https://github.com/networkx/networkx/pull/7237>`_).
- Add explicit targets of missing modules for intersphinx (`#7313 <https://github.com/networkx/networkx/pull/7313>`_).
- DOC: add doc suggestions for arbitrarily large random integers tools (`#7322 <https://github.com/networkx/networkx/pull/7322>`_).
- Try/except intermittently failing basemaps in geospatial examples (`#7324 <https://github.com/networkx/networkx/pull/7324>`_).
- Update docstring example with future-proof pandas assignment (`#7323 <https://github.com/networkx/networkx/pull/7323>`_).
- Remove animation from spectral clustering example to improve performance (`#7328 <https://github.com/networkx/networkx/pull/7328>`_).
- Doc Improvements for Approximations Files (`#7338 <https://github.com/networkx/networkx/pull/7338>`_).
- Update ``LCF_graph`` docstring (`#7262 <https://github.com/networkx/networkx/pull/7262>`_).
- Option to include initial labels in ``weisfeiler_lehman_subgraph_hashes`` (`#6601 <https://github.com/networkx/networkx/pull/6601>`_).
- Add eriknw as contributor (`#7343 <https://github.com/networkx/networkx/pull/7343>`_).
- [DOC, DISPATCH] : updated and added ``backend.py``'s docs (`#7305 <https://github.com/networkx/networkx/pull/7305>`_).
- add \*\*kwargs to traveling_salesman_problem (`#7371 <https://github.com/networkx/networkx/pull/7371>`_).
- Move the backend docs and connect the config docs. Both in a single sidebar entry (`#7389 <https://github.com/networkx/networkx/pull/7389>`_).

Maintenance
-----------

- Drop Python 3.9 support (`#7028 <https://github.com/networkx/networkx/pull/7028>`_).
- fix: Explicitly check for None/False in edge_attr during import from np (`#6825 <https://github.com/networkx/networkx/pull/6825>`_).
- Add favicon (`#7043 <https://github.com/networkx/networkx/pull/7043>`_).
- Remove unused code resistance_distance (`#7053 <https://github.com/networkx/networkx/pull/7053>`_).
- Fix names of small graphs (`#7055 <https://github.com/networkx/networkx/pull/7055>`_).
- Improve error messages for misconfigured backend treatment (`#7062 <https://github.com/networkx/networkx/pull/7062>`_).
- MAINT: Fixup union exception message (`#7071 <https://github.com/networkx/networkx/pull/7071>`_).
- MAINT: Minor touchups to tadpole and lollipop graph (`#7049 <https://github.com/networkx/networkx/pull/7049>`_).
- Add ``@not_implemented_for("directed")`` to ``number_connected_components`` (`#7074 <https://github.com/networkx/networkx/pull/7074>`_).
- remove unused code (`#7076 <https://github.com/networkx/networkx/pull/7076>`_).
- Minor touchups to the beamsearch module (`#7059 <https://github.com/networkx/networkx/pull/7059>`_).
- Fix annoying split strings on same line (`#7079 <https://github.com/networkx/networkx/pull/7079>`_).
- Update dispatch decorator for ``hits`` to use ``"weight"`` edge weight (`#7081 <https://github.com/networkx/networkx/pull/7081>`_).
- Remove nbconvert upper pin (revert #6984) (`#7083 <https://github.com/networkx/networkx/pull/7083>`_).
- Add a step to CI to check for warnings at import time (`#7077 <https://github.com/networkx/networkx/pull/7077>`_).
- Added few tests for /generators/duplication.py and /generators/geomet… (`#6976 <https://github.com/networkx/networkx/pull/6976>`_).
- Test on Python 3.13-dev (`#7096 <https://github.com/networkx/networkx/pull/7096>`_).
- Changed arguments list of GraphMLWriterLxml.dump() (`#6261 <https://github.com/networkx/networkx/pull/6261>`_).
- ``write_graphml``: Small fix for object type description on ``TypeError`` exception (`#7109 <https://github.com/networkx/networkx/pull/7109>`_).
- updated functions in ``core.py`` (`#7027 <https://github.com/networkx/networkx/pull/7027>`_).
- label check on push and change check name (`#7111 <https://github.com/networkx/networkx/pull/7111>`_).
- DEP : adding ``not_implemented_for("multigraph”)`` to ``k_core``, ``k_shell``, ``k_crust`` and ``k_corona`` (`#7121 <https://github.com/networkx/networkx/pull/7121>`_).
- Add label check when pull request is edited instead of push (`#7134 <https://github.com/networkx/networkx/pull/7134>`_).
- Add label workflow pull_request type synchronize and echo message (`#7135 <https://github.com/networkx/networkx/pull/7135>`_).
- adding test coverage for isomorphism when using digraphs (`#6417 <https://github.com/networkx/networkx/pull/6417>`_).
- Remove usage of ``__networkx_plugin__`` (use ``__networkx_backend__`` instead) (`#7157 <https://github.com/networkx/networkx/pull/7157>`_).
- DOC: consistent spelling of neighbor and rename vars (`#7162 <https://github.com/networkx/networkx/pull/7162>`_).
- MAINT: use ruff format instead of black (`#7160 <https://github.com/networkx/networkx/pull/7160>`_).
- Ensure warnings related to changes in shortest_path returns are visible to users (`#7161 <https://github.com/networkx/networkx/pull/7161>`_).
- Sync up behavior of is_{type} for empty graphs (`#5849 <https://github.com/networkx/networkx/pull/5849>`_).
- Added ``NodeNotFound`` exceptions to ``_apply_prediction`` and ``simrank``, and ignored isolated nodes in ``panther_similarity`` (`#7110 <https://github.com/networkx/networkx/pull/7110>`_).
- Fix not_implemented_for decorator for is_regular and related functions (`#7182 <https://github.com/networkx/networkx/pull/7182>`_).
- Fix all_node_cuts output for complete graphs (`#6558 <https://github.com/networkx/networkx/pull/6558>`_).
- Remove ``"networkx.plugins"`` and ``"networkx.plugin_info"`` entry-points (`#7192 <https://github.com/networkx/networkx/pull/7192>`_).
- Bump actions/setup-python from 4 to 5 (`#7201 <https://github.com/networkx/networkx/pull/7201>`_).
- Update test suite for Pytest v8 (`#7203 <https://github.com/networkx/networkx/pull/7203>`_).
- Undeprecate ````nx_pydot```` now that pydot is actively maintained again (`#7204 <https://github.com/networkx/networkx/pull/7204>`_).
- Future-proofing and improve tests (`#7209 <https://github.com/networkx/networkx/pull/7209>`_).
- Drop old dependencies per SPEC 0 (`#7217 <https://github.com/networkx/networkx/pull/7217>`_).
- Update pygraphviz (`#7216 <https://github.com/networkx/networkx/pull/7216>`_).
- Refactor geometric_soft_configuration_model tests for performance (`#7210 <https://github.com/networkx/networkx/pull/7210>`_).
- Rename ``_dispatch`` to ``_dispatchable`` (`#7193 <https://github.com/networkx/networkx/pull/7193>`_).
- Replace tempfile with tmp_path fixture in test suite (`#7221 <https://github.com/networkx/networkx/pull/7221>`_).
- updated test_directed_edge_swap #5814 (`#6426 <https://github.com/networkx/networkx/pull/6426>`_).
- Bump copyright year for 2024 (`#7232 <https://github.com/networkx/networkx/pull/7232>`_).
- Improving test coverage for Small.py (`#7260 <https://github.com/networkx/networkx/pull/7260>`_).
- Test for symmetric edge flow betweenness partition (`#7251 <https://github.com/networkx/networkx/pull/7251>`_).
- MAINT : added ``seed`` to ``gnm_random_graph`` in ``community/tests/test_label_propagation.py`` (`#7264 <https://github.com/networkx/networkx/pull/7264>`_).
- Bump scientific-python/upload-nightly-action from 0.2.0 to 0.3.0 (`#7266 <https://github.com/networkx/networkx/pull/7266>`_).
- adding self loops related docs and tests for functions in ``cluster.py`` (`#7261 <https://github.com/networkx/networkx/pull/7261>`_).
- Improving test coverage for Mycielsky.py (`#7271 <https://github.com/networkx/networkx/pull/7271>`_).
- Use ruff's docstring formatting (`#7276 <https://github.com/networkx/networkx/pull/7276>`_).
- Add docstring formatting change to blame-ignore-revs (`#7281 <https://github.com/networkx/networkx/pull/7281>`_).
- Improve test coverage for random_clustered and update function names (`#7273 <https://github.com/networkx/networkx/pull/7273>`_).
- Doc infrastructure: replace ``nb2plot`` with ``myst-nb`` (`#7237 <https://github.com/networkx/networkx/pull/7237>`_).
- Temporarily rm geospatial examples to fix CI (`#7299 <https://github.com/networkx/networkx/pull/7299>`_).
- Improve test coverage for bipartite extendability (`#7306 <https://github.com/networkx/networkx/pull/7306>`_).
- CI: Update scientific-python/upload-nightly-action from 0.3.0 to 0.4.0 (`#7309 <https://github.com/networkx/networkx/pull/7309>`_).
- CI: Group dependabot updates (`#7308 <https://github.com/networkx/networkx/pull/7308>`_).
- CI: update upload-nightly-action to 0.5.0 (`#7311 <https://github.com/networkx/networkx/pull/7311>`_).
- renaming backend ``func_info`` dictionary's keys (`#7219 <https://github.com/networkx/networkx/pull/7219>`_).
- Add ``mutates_input=`` and ``returns_graph=`` to ``_dispatchable`` (`#7191 <https://github.com/networkx/networkx/pull/7191>`_).
- Avoid creating results with numpy scalars (re: NEP 51) (`#7282 <https://github.com/networkx/networkx/pull/7282>`_).
- Bump changelist from 0.4 to 0.5 (`#7325 <https://github.com/networkx/networkx/pull/7325>`_).
- Improve test coverage for bipartite matrix.py (`#7312 <https://github.com/networkx/networkx/pull/7312>`_).
- Un-dispatch coloring strategies (`#7329 <https://github.com/networkx/networkx/pull/7329>`_).
- Undo change in return type of ``single_target_shortest_path_length`` (`#7327 <https://github.com/networkx/networkx/pull/7327>`_).
- Remove animation from spectral clustering example to improve performance (`#7328 <https://github.com/networkx/networkx/pull/7328>`_).
- Expire steinertree mehlhorn futurewarning (`#7337 <https://github.com/networkx/networkx/pull/7337>`_).
- Update louvain test modularity comparison to leq (`#7336 <https://github.com/networkx/networkx/pull/7336>`_).
- Add aaronzo as contributor (`#7342 <https://github.com/networkx/networkx/pull/7342>`_).
- Fix #7339. ``shortest_path`` inconsisitent with warning (`#7341 <https://github.com/networkx/networkx/pull/7341>`_).
- Add ``nx.config`` dict for configuring dispatching and backends (`#7225 <https://github.com/networkx/networkx/pull/7225>`_).
- Improve test coverage for Steiner Tree & Docs (`#7348 <https://github.com/networkx/networkx/pull/7348>`_).
- added ``seed`` to ``test_richclub_normalized`` (`#7355 <https://github.com/networkx/networkx/pull/7355>`_).
- Add tests to link_prediction.py (`#7357 <https://github.com/networkx/networkx/pull/7357>`_).
- Fix pydot tests when testing backends (`#7356 <https://github.com/networkx/networkx/pull/7356>`_).
- Future proof xml parsing in graphml (`#7360 <https://github.com/networkx/networkx/pull/7360>`_).
- make doc_string examples order-independent by removing np.set_printoptions (`#7361 <https://github.com/networkx/networkx/pull/7361>`_).
- Close figures on test cleanup (`#7373 <https://github.com/networkx/networkx/pull/7373>`_).
- More numpy scalars cleanup for numpy 2.0 (`#7374 <https://github.com/networkx/networkx/pull/7374>`_).
- Update numpydoc (`#7364 <https://github.com/networkx/networkx/pull/7364>`_).
- Fix pygraphviz tests causing segmentation faults in backend test (`#7380 <https://github.com/networkx/networkx/pull/7380>`_).
- Add dispatching to broadcasting.py (`#7386 <https://github.com/networkx/networkx/pull/7386>`_).
- Update test suite to handle when scipy is not installed (`#7388 <https://github.com/networkx/networkx/pull/7388>`_).
- Rm deprecated np.row_stack in favor of vstack (`#7390 <https://github.com/networkx/networkx/pull/7390>`_).
- Fix exception for ``del config[key]`` (`#7391 <https://github.com/networkx/networkx/pull/7391>`_).
- Bump the GH actions with 3 updates (`#7310 <https://github.com/networkx/networkx/pull/7310>`_).

Contributors
------------

54 authors added to this release (alphabetically):

- `@BucketHeadP65 <https://github.com/BucketHeadP65>`_
- `@dependabot[bot] <https://github.com/apps/dependabot>`_
- `@nelsonaloysio <https://github.com/nelsonaloysio>`_
- `@YVWX <https://github.com/YVWX>`_
- Aaron Z. (`@aaronzo <https://github.com/aaronzo>`_)
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- AKSHAYA MADHURI (`@akshayamadhuri <https://github.com/akshayamadhuri>`_)
- Alex Markham (`@Alex-Markham <https://github.com/Alex-Markham>`_)
- Anders Rydbirk (`@anders-rydbirk <https://github.com/anders-rydbirk>`_)
- Andrew Knyazev (`@lobpcg <https://github.com/lobpcg>`_)
- Ayooluwa (`@Ay-slim <https://github.com/Ay-slim>`_)
- Baldo (`@BrunoBaldissera <https://github.com/BrunoBaldissera>`_)
- Benjamin Edwards (`@bjedwards <https://github.com/bjedwards>`_)
- Chiranjeevi Karthik Kuruganti (`@karthikchiru12 <https://github.com/karthikchiru12>`_)
- Chris Pryer (`@cnpryer <https://github.com/cnpryer>`_)
- d.grigonis (`@dgrigonis <https://github.com/dgrigonis>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Daniel V. Egdal (`@DanielEgdal <https://github.com/DanielEgdal>`_)
- Dilara Tekinoglu (`@dtekinoglu <https://github.com/dtekinoglu>`_)
- Dishie Vinchhi (`@Dishie2498 <https://github.com/Dishie2498>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Frédéric Crozatier (`@fcrozatier <https://github.com/fcrozatier>`_)
- Henrik Finsberg (`@finsberg <https://github.com/finsberg>`_)
- Jangwon Yie (`@jangwon-yie <https://github.com/jangwon-yie>`_)
- Jaron Lee (`@jaron-lee <https://github.com/jaron-lee>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Jon Crall (`@Erotemic <https://github.com/Erotemic>`_)
- Jonas Otto (`@ottojo <https://github.com/ottojo>`_)
- Jordan Matelsky (`@j6k4m8 <https://github.com/j6k4m8>`_)
- Koen van den Berk (`@kalkoen <https://github.com/kalkoen>`_)
- Luigi Sciarretta (`@LuigiSciar <https://github.com/LuigiSciar>`_)
- Luigi Sciarretta (`@LuigiSciarretta <https://github.com/LuigiSciarretta>`_)
- Matt Schwennesen (`@mjschwenne <https://github.com/mjschwenne>`_)
- Matthew Feickert (`@matthewfeickert <https://github.com/matthewfeickert>`_)
- Matthieu Gouel (`@matthieugouel <https://github.com/matthieugouel>`_)
- Mauricio Souza de Alencar (`@mdealencar <https://github.com/mdealencar>`_)
- Maximilian Seeliger (`@max-seeli <https://github.com/max-seeli>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Navya Agarwal (`@navyagarwal <https://github.com/navyagarwal>`_)
- Neil Botelho (`@NeilBotelho <https://github.com/NeilBotelho>`_)
- Nihal John George (`@nihalgeorge01 <https://github.com/nihalgeorge01>`_)
- Paolo Lammens (`@plammens <https://github.com/plammens>`_)
- Patrick Nicodemus (`@patrick-nicodemus <https://github.com/patrick-nicodemus>`_)
- Paula Pérez Bianchi (`@paulitapb <https://github.com/paulitapb>`_)
- Purvi Chaurasia (`@PurviChaurasia <https://github.com/PurviChaurasia>`_)
- Robert (`@ImHereForTheCookies <https://github.com/ImHereForTheCookies>`_)
- Robert Jankowski (`@robertjankowski <https://github.com/robertjankowski>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Sadra Barikbin (`@sadra-barikbin <https://github.com/sadra-barikbin>`_)
- Salim BELHADDAD (`@salym <https://github.com/salym>`_)
- Till Hoffmann (`@tillahoffmann <https://github.com/tillahoffmann>`_)
- Vanshika Mishra (`@vanshika230 <https://github.com/vanshika230>`_)
- William Black (`@smokestacklightnin <https://github.com/smokestacklightnin>`_)
- William Zijie Zhang (`@Transurgeon <https://github.com/Transurgeon>`_)

29 reviewers added to this release (alphabetically):

- `@YVWX <https://github.com/YVWX>`_
- Aaron Z. (`@aaronzo <https://github.com/aaronzo>`_)
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- AKSHAYA MADHURI (`@akshayamadhuri <https://github.com/akshayamadhuri>`_)
- Andrew Knyazev (`@lobpcg <https://github.com/lobpcg>`_)
- Ayooluwa (`@Ay-slim <https://github.com/Ay-slim>`_)
- Chiranjeevi Karthik Kuruganti (`@karthikchiru12 <https://github.com/karthikchiru12>`_)
- Chris Pryer (`@cnpryer <https://github.com/cnpryer>`_)
- d.grigonis (`@dgrigonis <https://github.com/dgrigonis>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Frédéric Crozatier (`@fcrozatier <https://github.com/fcrozatier>`_)
- Henrik Finsberg (`@finsberg <https://github.com/finsberg>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Kyle Sunden (`@ksunden <https://github.com/ksunden>`_)
- Matt Schwennesen (`@mjschwenne <https://github.com/mjschwenne>`_)
- Mauricio Souza de Alencar (`@mdealencar <https://github.com/mdealencar>`_)
- Maximilian Seeliger (`@max-seeli <https://github.com/max-seeli>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Nihal John George (`@nihalgeorge01 <https://github.com/nihalgeorge01>`_)
- Paolo Lammens (`@plammens <https://github.com/plammens>`_)
- Paula Pérez Bianchi (`@paulitapb <https://github.com/paulitapb>`_)
- Rick Ratzel (`@rlratzel <https://github.com/rlratzel>`_)
- Robert Jankowski (`@robertjankowski <https://github.com/robertjankowski>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Stefan van der Walt (`@stefanv <https://github.com/stefanv>`_)
- Vanshika Mishra (`@vanshika230 <https://github.com/vanshika230>`_)
- William Black (`@smokestacklightnin <https://github.com/smokestacklightnin>`_)
- William Zijie Zhang (`@Transurgeon <https://github.com/Transurgeon>`_)

_These lists are automatically generated, and may not be complete or may contain
duplicates._

