networkx 3.5
============

We're happy to announce the release of networkx 3.5!

API Changes
-----------

- Save Layouts on Graphs (`#7571 <https://github.com/networkx/networkx/pull/7571>`_).
- Expire d_separated and minimum_d_separator functions (`#7830 <https://github.com/networkx/networkx/pull/7830>`_).
- Expire all_triplets deprecation (`#7828 <https://github.com/networkx/networkx/pull/7828>`_).
- Expire random_triad deprecation (`#7829 <https://github.com/networkx/networkx/pull/7829>`_).
- DEP: Raise an exception for k_core functions with multigraphs (`#7831 <https://github.com/networkx/networkx/pull/7831>`_).
- Deprecate graph_could_be_isomorphic (`#7826 <https://github.com/networkx/networkx/pull/7826>`_).
- Expire total_spanning_tree_weight deprecation (`#7843 <https://github.com/networkx/networkx/pull/7843>`_).
- Expire deprecation of create kwarg in nonisomorphic_trees (`#7847 <https://github.com/networkx/networkx/pull/7847>`_).
- New draw API (`#7589 <https://github.com/networkx/networkx/pull/7589>`_).

Enhancements
------------

- perf: optimise ``random_k_out_graph`` (`#7702 <https://github.com/networkx/networkx/pull/7702>`_).
- Clausets local community detection algorithm (`#7691 <https://github.com/networkx/networkx/pull/7691>`_).
- ``find_asteroidal_triple`` improvement (`#7736 <https://github.com/networkx/networkx/pull/7736>`_).
- Add ``weight`` to harmonic_diameter (`#7636 <https://github.com/networkx/networkx/pull/7636>`_).
- Densest Subgraph Problem: Greedy Peeling and Greedy++ Implementations (`#7731 <https://github.com/networkx/networkx/pull/7731>`_).
- single_source_all_shortest_paths: don't loop over all nodes (`#7762 <https://github.com/networkx/networkx/pull/7762>`_).
- Error message improvement for nbunch_iter ( NetworkXError raised with specific message on TypeError with "iter" in msg ) (`#7790 <https://github.com/networkx/networkx/pull/7790>`_).
- Faster computation of energy in Laplacian centrality (`#7793 <https://github.com/networkx/networkx/pull/7793>`_).
- Make ``forceatlas2_layout`` dispatchable (`#7794 <https://github.com/networkx/networkx/pull/7794>`_).
- Update dispatchable for ``forceatlas2_layout`` (`#7798 <https://github.com/networkx/networkx/pull/7798>`_).
- Enable backend-only functions where NetworkX is just an API (`#7690 <https://github.com/networkx/networkx/pull/7690>`_).
- Steinertree kou enhancement in response to issue 5889 type:Enhancements (`#7767 <https://github.com/networkx/networkx/pull/7767>`_).
- Add Leiden as a backend-only algorithm (`#7743 <https://github.com/networkx/networkx/pull/7743>`_).
- Bipartite layout nodes optional (`#7756 <https://github.com/networkx/networkx/pull/7756>`_).
- Densest Subgraph Problem: FISTA based algorithm + Large scale tests (`#7770 <https://github.com/networkx/networkx/pull/7770>`_).
- Dispatch ``get_node_attributes`` and a few more from ``nx.classes.function`` (`#7824 <https://github.com/networkx/networkx/pull/7824>`_).
- Faster ``could_be_isomorphic`` and ``number_of_cliques`` (`#7855 <https://github.com/networkx/networkx/pull/7855>`_).
- Add square_clustering to algorithm benchmarks (`#7857 <https://github.com/networkx/networkx/pull/7857>`_).
- Faster Implementation of Structural Holes (`#7249 <https://github.com/networkx/networkx/pull/7249>`_).
- Improve runtime of number_of_nonisomorphic_trees() (`#7917 <https://github.com/networkx/networkx/pull/7917>`_).
- Fix write_gexf timeformat for dynamic Graphs (`#7914 <https://github.com/networkx/networkx/pull/7914>`_).
- Consolidate could_be_isomorphic (`#7852 <https://github.com/networkx/networkx/pull/7852>`_).
- Improving rooted_tree_isomorphism for deep trees (`#7945 <https://github.com/networkx/networkx/pull/7945>`_).
- Fixing nx.diameter inconsistent results with usebounds=True (`#7954 <https://github.com/networkx/networkx/pull/7954>`_).
- Faster ``square_clustering`` (`#7810 <https://github.com/networkx/networkx/pull/7810>`_).
- Avoid repeated cache conversion failures for backends (`#7768 <https://github.com/networkx/networkx/pull/7768>`_).
- Improve _sparse_fruchterman_reingold with L-BFGS (`#7889 <https://github.com/networkx/networkx/pull/7889>`_).
- Improve Performance of Tree Isomorphism and Center Calculation (`#7946 <https://github.com/networkx/networkx/pull/7946>`_).
- Add option for ``biadjacency_matrix`` to be returned as a dense NumPy array (`#7973 <https://github.com/networkx/networkx/pull/7973>`_).
- Add Functions for Finding Connected Dominating Sets (`#7774 <https://github.com/networkx/networkx/pull/7774>`_).
- Add feature to make storing node contraction data optional (`#7902 <https://github.com/networkx/networkx/pull/7902>`_).
- Added "initial_node" param to generate_random_paths() to allow a starting node to be specified for generated walks (`#8002 <https://github.com/networkx/networkx/pull/8002>`_).
- Fix behavior for iterable ``sources`` argument in ``bfs_layers`` (`#8013 <https://github.com/networkx/networkx/pull/8013>`_).
- Speed up ``connected_components`` and ``weakly_connected_components`` (`#7971 <https://github.com/networkx/networkx/pull/7971>`_).
- BiRank Algorithm Implementation (`#7978 <https://github.com/networkx/networkx/pull/7978>`_).
- Enforce correct graph types for graph matchers (`#8043 <https://github.com/networkx/networkx/pull/8043>`_).

Bug Fixes
---------

- Update ``_raise_on_directed`` to work with ``create_using`` pos arg (`#7695 <https://github.com/networkx/networkx/pull/7695>`_).
- trophic_levels now checks for paths from each node to a basal node (`#7453 <https://github.com/networkx/networkx/pull/7453>`_).
- Fix TSP weight parameter issues (`#7721 <https://github.com/networkx/networkx/pull/7721>`_).
- Fix for filtered MultiGraph views from ``edge_subgraph`` (#7724) (`#7729 <https://github.com/networkx/networkx/pull/7729>`_).
- BUG: fixed the ``if`` condition in ``asadpour_atsp`` (`#7753 <https://github.com/networkx/networkx/pull/7753>`_).
- Implement Bar ConnectionStyle for labels (`#7739 <https://github.com/networkx/networkx/pull/7739>`_).
- Fixed a divide by zero error in forceatlas2 (`#7791 <https://github.com/networkx/networkx/pull/7791>`_).
- Fix for issue #7645: Do not preserve 'cw' and 'ccw' attributes in PlanarEmbedding.to_undirected() (`#7750 <https://github.com/networkx/networkx/pull/7750>`_).
- fix typo in ramanujan branch (`#7804 <https://github.com/networkx/networkx/pull/7804>`_).
- Fix ``with nx.config(backend_priority=backends):`` (`#7814 <https://github.com/networkx/networkx/pull/7814>`_).
- Fix handling of faux_infinite values in network_simplex (`#7796 <https://github.com/networkx/networkx/pull/7796>`_).
- Fixed the return type from an empty dict to an empty set (`#7910 <https://github.com/networkx/networkx/pull/7910>`_).
- Add ``edge_attrs="weight"`` to ``forceatlas2_layout`` dispatch decorator (`#7918 <https://github.com/networkx/networkx/pull/7918>`_).
- Fix graph_hash iteration counts and DiGraph handling (`#7834 <https://github.com/networkx/networkx/pull/7834>`_).
- Refactored the working of chordless_cycles to handle self loops (`#7901 <https://github.com/networkx/networkx/pull/7901>`_).
- Fix bc scale with k endpoints (`#7908 <https://github.com/networkx/networkx/pull/7908>`_).
- Fix BC scaling for source nodes with k and endpoints=False (`#7949 <https://github.com/networkx/networkx/pull/7949>`_).
- BUG: graph6 format invariant to trailing newline (`#7941 <https://github.com/networkx/networkx/pull/7941>`_).
- Fix ``random_degree_sequence_graph`` when input is an iterator (`#7979 <https://github.com/networkx/networkx/pull/7979>`_).
- Improve special cases in dispatch testing (paying off tech debt) (`#7982 <https://github.com/networkx/networkx/pull/7982>`_).
- Fix bug when assigning list to ``nx.config.backend_priority`` (`#8034 <https://github.com/networkx/networkx/pull/8034>`_).
- A minimal fix for ``is_aperiodic`` (`#8029 <https://github.com/networkx/networkx/pull/8029>`_).
- fix bug of _sparse_fruchterman_reingold and remove try/except idiom (`#8041 <https://github.com/networkx/networkx/pull/8041>`_).
- Fix edge case in ISMAGS symmetry detection (`#8055 <https://github.com/networkx/networkx/pull/8055>`_).

Documentation
-------------

- set nx-arangodb link to github (`#7694 <https://github.com/networkx/networkx/pull/7694>`_).
- Re-submission of gh-7087 with better file provenance (`#7681 <https://github.com/networkx/networkx/pull/7681>`_).
- Fix code formatting of some examples (`#7730 <https://github.com/networkx/networkx/pull/7730>`_).
- Add examples for custom graph in the doc of ``soft_random_geometric_graph`` and ``thresholded_random_geometric_graph`` (`#7749 <https://github.com/networkx/networkx/pull/7749>`_).
- Gallery example: bipartite a/b-core motif (`#7757 <https://github.com/networkx/networkx/pull/7757>`_).
- Add blurb about pytest-mpl dependency to contributing guide (`#7741 <https://github.com/networkx/networkx/pull/7741>`_).
- Minor updates to ``single_source_shortest_path_length`` docstring (`#7637 <https://github.com/networkx/networkx/pull/7637>`_).
- Added a note to the contributor guideline to avoid numpy scalars as a… (`#7773 <https://github.com/networkx/networkx/pull/7773>`_).
- Correcting the example given under subgraph_is_monomorphic.py (`#7779 <https://github.com/networkx/networkx/pull/7779>`_).
- [easy] Add to Contributor List (`#7801 <https://github.com/networkx/networkx/pull/7801>`_).
- doc: mention the second major update (`#7782 <https://github.com/networkx/networkx/pull/7782>`_).
- DOC: Add details about more grants (`#7823 <https://github.com/networkx/networkx/pull/7823>`_).
- Refactor: Moving backend docs from ``backends.py`` to ``backends.rst`` (`#7776 <https://github.com/networkx/networkx/pull/7776>`_).
- Update readwrite docstrings for the ``path`` parameter (`#7835 <https://github.com/networkx/networkx/pull/7835>`_).
- Fix docstring example of ``nx.generate_random_paths(index_map=...)`` (`#7832 <https://github.com/networkx/networkx/pull/7832>`_).
- Adds NVIDIA Corporation to list of supporters (`#7846 <https://github.com/networkx/networkx/pull/7846>`_).
- Fix use of triple backticks in docstrings (`#7845 <https://github.com/networkx/networkx/pull/7845>`_).
- Add paragraph about university classes to mentored projects (`#7838 <https://github.com/networkx/networkx/pull/7838>`_).
- Fix pygraphviz_layout example (`#7849 <https://github.com/networkx/networkx/pull/7849>`_).
- Add test-extras to optional dependencies (`#7854 <https://github.com/networkx/networkx/pull/7854>`_).
- doc: hash size are in bytes (`#7866 <https://github.com/networkx/networkx/pull/7866>`_).
- DOC: Clean up mentored projects page: move visualization project to completed section (`#7881 <https://github.com/networkx/networkx/pull/7881>`_).
- added 2 projects for GSoC 2025 (`#7880 <https://github.com/networkx/networkx/pull/7880>`_).
- Add missing usebounds param descr to distance docstrings (`#7703 <https://github.com/networkx/networkx/pull/7703>`_).
- Add examples to graph_atlas_g docstring (`#7900 <https://github.com/networkx/networkx/pull/7900>`_).
- Add missing ``weight`` and ``gravity`` attribute to ``forceatlas2_layout`` docstring (`#7915 <https://github.com/networkx/networkx/pull/7915>`_).
- DOC: Update first docstring example and add a serialization example (`#7928 <https://github.com/networkx/networkx/pull/7928>`_).
- DOC: Remove myself from the mentor list for projects (`#7943 <https://github.com/networkx/networkx/pull/7943>`_).
- Fix typo in forceatlas2_layout (`#7966 <https://github.com/networkx/networkx/pull/7966>`_).
- Add ``tournament_matrix`` to docs (`#7968 <https://github.com/networkx/networkx/pull/7968>`_).
- Add function descriptions in the threshold.py file (`#7906 <https://github.com/networkx/networkx/pull/7906>`_).
- bugfix: use supergraph to compute superpos in plot_clusters example (`#7997 <https://github.com/networkx/networkx/pull/7997>`_).
- More ``random_paths`` docstring improvements (`#7841 <https://github.com/networkx/networkx/pull/7841>`_).
- Add nx-guides link to navbar without dropdown (`#8015 <https://github.com/networkx/networkx/pull/8015>`_).
- Clarifying backend graph class interface is_directed+is_multigraph (`#8032 <https://github.com/networkx/networkx/pull/8032>`_).
- Fix all sphinx build warnings (`#8047 <https://github.com/networkx/networkx/pull/8047>`_).
- Add a new gallery spring layout (`#8042 <https://github.com/networkx/networkx/pull/8042>`_).
- Add note about cycles in ``maximum_flow()`` (`#8058 <https://github.com/networkx/networkx/pull/8058>`_).
- Clarify subgraph node/edge order is not preserved (`#8069 <https://github.com/networkx/networkx/pull/8069>`_).
- Fix typo in ``min_edge_cover`` docstring (`#8075 <https://github.com/networkx/networkx/pull/8075>`_).

Maintenance
-----------

- MAINT: wrapping ``partial`` with ``staticmethod()`` in ``test_link_prediction.py`` (`#7673 <https://github.com/networkx/networkx/pull/7673>`_).
- Updating ``pip install`` in benchmarking workflow (`#7647 <https://github.com/networkx/networkx/pull/7647>`_).
- Mv changelist to release deps (`#7708 <https://github.com/networkx/networkx/pull/7708>`_).
- Drop support for Python 3.10 (`#7668 <https://github.com/networkx/networkx/pull/7668>`_).
- Update minimum dependencies (SPEC 0) (`#7711 <https://github.com/networkx/networkx/pull/7711>`_).
- Remove print statements and comments from test suite (`#7715 <https://github.com/networkx/networkx/pull/7715>`_).
- Refactor closeness centrality tests (`#7712 <https://github.com/networkx/networkx/pull/7712>`_).
- Add Python fallback to random_k_out_graph + document dependencies (`#7718 <https://github.com/networkx/networkx/pull/7718>`_).
- Fix sphinx warnings from numpydoc parsing (`#7742 <https://github.com/networkx/networkx/pull/7742>`_).
- MAINT: Updating geospatial example to be compatible with ``osmnx=2.0.0`` (`#7746 <https://github.com/networkx/networkx/pull/7746>`_).
- Add more tests for ``nx.lowest_common_ancestor`` (`#7726 <https://github.com/networkx/networkx/pull/7726>`_).
- Update ``shortest_path`` and ``single_target_shortest_path_length`` for 3.5 (`#7754 <https://github.com/networkx/networkx/pull/7754>`_).
- Parametrize edge_subgraph multigraph test (`#7737 <https://github.com/networkx/networkx/pull/7737>`_).
- Add filters for LOBPCG convergence warnings (`#7778 <https://github.com/networkx/networkx/pull/7778>`_).
- MAINT: Close mpl figures in tests to clear up test env (`#7783 <https://github.com/networkx/networkx/pull/7783>`_).
- Update pre-commit linting (`#7797 <https://github.com/networkx/networkx/pull/7797>`_).
- Small dispatching refactor: simple ``__call__`` when no backends (`#7761 <https://github.com/networkx/networkx/pull/7761>`_).
- Benchmarking: graph atlas (`#7766 <https://github.com/networkx/networkx/pull/7766>`_).
- Improve square clustering test derived from Zhang paper (reference 2) (`#7811 <https://github.com/networkx/networkx/pull/7811>`_).
- Fix exception for backend-only functions (`#7812 <https://github.com/networkx/networkx/pull/7812>`_).
- Add a subplot fixture to automate test cleanup (`#7799 <https://github.com/networkx/networkx/pull/7799>`_).
- MAINT: use nx.layout instead of importing layouts (`#7819 <https://github.com/networkx/networkx/pull/7819>`_).
- MAINT: Move stub func in the correct scope for pickle test (`#7818 <https://github.com/networkx/networkx/pull/7818>`_).
- Ensure standard import conventions are used (`#7821 <https://github.com/networkx/networkx/pull/7821>`_).
- Clean up pygrep pre-commit for import convention checks (`#7822 <https://github.com/networkx/networkx/pull/7822>`_).
- Add a few more square clustering test cases (`#7825 <https://github.com/networkx/networkx/pull/7825>`_).
- Don't use ``assert`` when using ``pytest.raises`` (`#7833 <https://github.com/networkx/networkx/pull/7833>`_).
- Update doc requirements (`#7837 <https://github.com/networkx/networkx/pull/7837>`_).
- Update developer requirements (`#7839 <https://github.com/networkx/networkx/pull/7839>`_).
- MAINT: Minus not underscore in the dep package name (`#7840 <https://github.com/networkx/networkx/pull/7840>`_).
- Update readwrite docstrings for the ``path`` parameter (`#7835 <https://github.com/networkx/networkx/pull/7835>`_).
- Fix docstring example of ``nx.generate_random_paths(index_map=...)`` (`#7832 <https://github.com/networkx/networkx/pull/7832>`_).
- Fix use of triple backticks in docstrings (`#7845 <https://github.com/networkx/networkx/pull/7845>`_).
- Add .mailmap file to consilidate contributors (`#7853 <https://github.com/networkx/networkx/pull/7853>`_).
- TST: Refactor example test case generation functions (`#7844 <https://github.com/networkx/networkx/pull/7844>`_).
- Refactor network_simplex test of faux_infinity (`#7858 <https://github.com/networkx/networkx/pull/7858>`_).
- Change CRLF format of two files (`#7861 <https://github.com/networkx/networkx/pull/7861>`_).
- Fix some typos (`#7863 <https://github.com/networkx/networkx/pull/7863>`_).
- Pre commit hooks to check line endings and trailing whitespace (`#7862 <https://github.com/networkx/networkx/pull/7862>`_).
- MAINT: replace the SHAs for blame and move the changes within pre-commit (`#7869 <https://github.com/networkx/networkx/pull/7869>`_).
- Rm stray instances of sparse matrices from test suite (`#7860 <https://github.com/networkx/networkx/pull/7860>`_).
- Remove unused imports (`#7864 <https://github.com/networkx/networkx/pull/7864>`_).
- Remove unnecessary ``dict(...)`` for SSSP algos that return dicts (`#7878 <https://github.com/networkx/networkx/pull/7878>`_).
- Change function calls to address pandas linting (`#7885 <https://github.com/networkx/networkx/pull/7885>`_).
- Activate pycodestyle in linting pre-commit (`#7859 <https://github.com/networkx/networkx/pull/7859>`_).
- Correct sphinx warnings from doc build (`#7888 <https://github.com/networkx/networkx/pull/7888>`_).
- ``effective_size`` of nodes with only self-loop edges is undefined (`#7347 <https://github.com/networkx/networkx/pull/7347>`_).
- DOC: docstring changes to ``to_dict_of_dicts`` and ``attr_matrix`` and input name change in ``min_fill_in_heuristic`` (`#7883 <https://github.com/networkx/networkx/pull/7883>`_).
- Update layout.py (`#7939 <https://github.com/networkx/networkx/pull/7939>`_).
- Tree isomorphism input validation (`#7920 <https://github.com/networkx/networkx/pull/7920>`_).
- Tweaks and notes from a dive into backends.py (`#7884 <https://github.com/networkx/networkx/pull/7884>`_).
- MAINT: Follow-up to 7945 - rm helper function (`#7952 <https://github.com/networkx/networkx/pull/7952>`_).
- Some light refactoring to make the tree isomorphism tests more readable (`#7924 <https://github.com/networkx/networkx/pull/7924>`_).
- new try at will_call_mutate_inputs (`#7959 <https://github.com/networkx/networkx/pull/7959>`_).
- MAINT: rm debug print from similarity module (`#7937 <https://github.com/networkx/networkx/pull/7937>`_).
- Improve special cases in dispatch testing (paying off tech debt) (`#7982 <https://github.com/networkx/networkx/pull/7982>`_).
- Remove unused import in convert_matrix.py (networkx.utils.not_implemented_for) (`#7983 <https://github.com/networkx/networkx/pull/7983>`_).
- Use ``-n auto`` from pytest-xdist for dispatch and coverage CI jobs (`#7987 <https://github.com/networkx/networkx/pull/7987>`_).
- Make test file names unique to be threadsafe (`#7998 <https://github.com/networkx/networkx/pull/7998>`_).
- Update pre-commit repos (`#8017 <https://github.com/networkx/networkx/pull/8017>`_).
- Minor follow-up to gh-8002 tests (`#8016 <https://github.com/networkx/networkx/pull/8016>`_).
- Add linting for line length in docstrings and comments (`#7938 <https://github.com/networkx/networkx/pull/7938>`_).
- Add sg_execution_times.rst to gitignore (`#8025 <https://github.com/networkx/networkx/pull/8025>`_).
- Support both pydot v3 and pydot v4 (`#8027 <https://github.com/networkx/networkx/pull/8027>`_).
- Update copyright license years (`#8038 <https://github.com/networkx/networkx/pull/8038>`_).
- Fix all sphinx build warnings (`#8047 <https://github.com/networkx/networkx/pull/8047>`_).
- Fix intermittent test failures in expander graph generator tests (`#8048 <https://github.com/networkx/networkx/pull/8048>`_).
- Refactor tree_isomorphism to improve code reuse and readability (`#7929 <https://github.com/networkx/networkx/pull/7929>`_).
- STY: Rm local variable remapping of heappush and heappop (`#8051 <https://github.com/networkx/networkx/pull/8051>`_).
- TST: Minor improvements to layout test suite (`#8049 <https://github.com/networkx/networkx/pull/8049>`_).
- Minor refactor to cleanup/improve matching test suite (`#8068 <https://github.com/networkx/networkx/pull/8068>`_).

Contributors
------------

56 authors added to this release (alphabetically):

- `@Bigstool <https://github.com/Bigstool>`_
- `@Celelibi <https://github.com/Celelibi>`_
- `@Frankwii <https://github.com/Frankwii>`_
- `@lmeNaN <https://github.com/lmeNaN>`_
- `@nelsonaloysio <https://github.com/nelsonaloysio>`_
- `@Schwarf <https://github.com/Schwarf>`_
- `@vtrifonov-altos <https://github.com/vtrifonov-altos>`_
- `@vttrifonov <https://github.com/vttrifonov>`_
- `@xavieronassis <https://github.com/xavieronassis>`_
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- akshita  (`@akshitasure12 <https://github.com/akshitasure12>`_)
- Alejandro Candioti (`@amcandio <https://github.com/amcandio>`_)
- Andrew Knyazev, Professor Emeritus (`@lobpcg <https://github.com/lobpcg>`_)
- Anthony Labarre (`@alabarre <https://github.com/alabarre>`_)
- Anthony Mahanna (`@aMahanna <https://github.com/aMahanna>`_)
- Christian Clauss (`@cclauss <https://github.com/cclauss>`_)
- Colman Bouton (`@LorentzFactor <https://github.com/LorentzFactor>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- dgpb (`@dg-pb <https://github.com/dg-pb>`_)
- Elfarouk Harb (`@FaroukY <https://github.com/FaroukY>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Fei Pan (`@fei0319 <https://github.com/fei0319>`_)
- Fernando Pérez (`@fperez <https://github.com/fperez>`_)
- Gilles Peiffer (`@Peiffap <https://github.com/Peiffap>`_)
- gmichaeli (`@GalMichaeli <https://github.com/GalMichaeli>`_)
- Hesam Sheikh (`@hesamsheikh <https://github.com/hesamsheikh>`_)
- Hiroki Hamaguchi (`@HirokiHamaguchi <https://github.com/HirokiHamaguchi>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Jason Mitchell (`@oestej <https://github.com/oestej>`_)
- Juanita Gomez (`@juanis2112 <https://github.com/juanis2112>`_)
- Keith Hughitt (`@khughitt <https://github.com/khughitt>`_)
- Matt Schwennesen (`@mjschwenne <https://github.com/mjschwenne>`_)
- Matt Thorne (`@MattThorne <https://github.com/MattThorne>`_)
- Maverick18 (`@Aditya-Shandilya1182 <https://github.com/Aditya-Shandilya1182>`_)
- Michael Weinold (`@michaelweinold <https://github.com/michaelweinold>`_)
- Morteza24 (`@Morteza-24 <https://github.com/Morteza-24>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Nikolaos Chatzikonstantinou (`@createyourpersonalaccount <https://github.com/createyourpersonalaccount>`_)
- Peter C Kroon (`@pckroon <https://github.com/pckroon>`_)
- Po-Lin Cho (`@berlincho <https://github.com/berlincho>`_)
- Qian Zhang (`@QianZhang19 <https://github.com/QianZhang19>`_)
- Raj Pawar (`@Raj3110 <https://github.com/Raj3110>`_)
- Ralph Liu (`@nv-rliu <https://github.com/nv-rliu>`_)
- Ratan Kulshreshtha (`@RatanShreshtha <https://github.com/RatanShreshtha>`_)
- Ricardo Bittencourt (`@ricbit <https://github.com/ricbit>`_)
- Rick Ratzel (`@rlratzel <https://github.com/rlratzel>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Shiyun(Arthur) Hu (`@Shiyun-Hu <https://github.com/Shiyun-Hu>`_)
- Shunyang Li (`@ShunyangLi <https://github.com/ShunyangLi>`_)
- Thomas Louf (`@TLouf <https://github.com/TLouf>`_)
- Théo Cavignac (`@Lattay <https://github.com/Lattay>`_)
- TL Vromen (`@ThijsVromen <https://github.com/ThijsVromen>`_)
- Woojin Jung (`@WoojinJung-04 <https://github.com/WoojinJung-04>`_)
- Xiao Yuan (`@yuanx749 <https://github.com/yuanx749>`_)
- Zhige Xin (`@xinzhige <https://github.com/xinzhige>`_)
- 大王白小甫 (`@dawangbaixiaofu <https://github.com/dawangbaixiaofu>`_)

32 reviewers added to this release (alphabetically):

- `@Celelibi <https://github.com/Celelibi>`_
- `@Schwarf <https://github.com/Schwarf>`_
- `@vttrifonov <https://github.com/vttrifonov>`_
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- Alejandro Candioti (`@amcandio <https://github.com/amcandio>`_)
- Anthony Mahanna (`@aMahanna <https://github.com/aMahanna>`_)
- Chuck Hastings (`@ChuckHastings <https://github.com/ChuckHastings>`_)
- Colman Bouton (`@LorentzFactor <https://github.com/LorentzFactor>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Elfarouk Harb (`@FaroukY <https://github.com/FaroukY>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Fei Pan (`@fei0319 <https://github.com/fei0319>`_)
- Gilles Peiffer (`@Peiffap <https://github.com/Peiffap>`_)
- gmichaeli (`@GalMichaeli <https://github.com/GalMichaeli>`_)
- Hiroki Hamaguchi (`@HirokiHamaguchi <https://github.com/HirokiHamaguchi>`_)
- Jarrod Millman (`@jarrodmillman <https://github.com/jarrodmillman>`_)
- Keith Hughitt (`@khughitt <https://github.com/khughitt>`_)
- Matt Schwennesen (`@mjschwenne <https://github.com/mjschwenne>`_)
- Matt Thorne (`@MattThorne <https://github.com/MattThorne>`_)
- Michael Martini (`@MichaelMartini-Celonis <https://github.com/MichaelMartini-Celonis>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Qian Zhang (`@QianZhang19 <https://github.com/QianZhang19>`_)
- Raj Pawar (`@Raj3110 <https://github.com/Raj3110>`_)
- Ricardo Bittencourt (`@ricbit <https://github.com/ricbit>`_)
- Rick Ratzel (`@rlratzel <https://github.com/rlratzel>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)
- Ruida Zeng (`@ruidazeng <https://github.com/ruidazeng>`_)
- Shiyun(Arthur) Hu (`@Shiyun-Hu <https://github.com/Shiyun-Hu>`_)
- Thomas Louf (`@TLouf <https://github.com/TLouf>`_)
- TL Vromen (`@ThijsVromen <https://github.com/ThijsVromen>`_)
- Woojin Jung (`@WoojinJung-04 <https://github.com/WoojinJung-04>`_)
- Xiao Yuan (`@yuanx749 <https://github.com/yuanx749>`_)

_These lists are automatically generated, and may not be complete or may contain
duplicates._

