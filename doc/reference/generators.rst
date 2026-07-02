.. _generators:


Graph generators
****************

.. currentmodule:: networkx


Atlas
-----
.. automodule:: networkx.generators.atlas
.. autosummary::
   :toctree: generated/

   graph_atlas
   graph_atlas_g


Classic
-------
.. automodule:: networkx.generators.classic
.. autosummary::
   :toctree: generated/

   balanced_tree
   barbell_graph
   binomial_tree
   complete_graph
   complete_multipartite_graph
   circular_ladder_graph
   circulant_graph
   cycle_graph
   dorogovtsev_goltsev_mendes_graph
   empty_graph
   full_rary_tree
   kneser_graph
   ladder_graph
   lollipop_graph
   null_graph
   path_graph
   star_graph
   tadpole_graph
   trivial_graph
   turan_graph
   wheel_graph


Expanders
---------
.. automodule:: networkx.generators.expanders
.. autosummary::
   :toctree: generated/

   margulis_gabber_galil_graph
   chordal_cycle_graph
   paley_graph
   maybe_regular_expander
   is_regular_expander
   random_regular_expander_graph

Lattice
-------
.. automodule:: networkx.generators.lattice
.. autosummary::
   :toctree: generated/

   grid_2d_graph
   grid_graph
   hexagonal_lattice_graph
   hypercube_graph
   triangular_lattice_graph


Small
-----
.. automodule:: networkx.generators.small
.. autosummary::
   :toctree: generated/

   LCF_graph
   bull_graph
   chvatal_graph
   cubical_graph
   desargues_graph
   diamond_graph
   dodecahedral_graph
   frucht_graph
   generalized_petersen_graph
   heawood_graph
   hoffman_singleton_graph
   house_graph
   house_x_graph
   icosahedral_graph
   krackhardt_kite_graph
   moebius_kantor_graph
   octahedral_graph
   pappus_graph
   petersen_graph
   sedgewick_maze_graph
   tetrahedral_graph
   truncated_cube_graph
   truncated_tetrahedron_graph
   tutte_graph


Random Graphs
-------------
.. automodule:: networkx.generators.random_graphs
.. autosummary::
   :toctree: generated/

   fast_gnp_random_graph
   gnp_random_graph
   dense_gnm_random_graph
   gnm_random_graph
   erdos_renyi_graph
   binomial_graph
   newman_watts_strogatz_graph
   watts_strogatz_graph
   connected_watts_strogatz_graph
   random_regular_graph
   barabasi_albert_graph
   dual_barabasi_albert_graph
   extended_barabasi_albert_graph
   powerlaw_cluster_graph
   random_kernel_graph
   random_k_lift
   random_lobster_graph
   random_shell_graph
   random_powerlaw_tree
   random_powerlaw_tree_sequence


Duplication Divergence
----------------------
.. automodule:: networkx.generators.duplication
.. autosummary::
   :toctree: generated/

   duplication_divergence_graph
   partial_duplication_graph


Degree Sequence
---------------
.. automodule:: networkx.generators.degree_seq

.. autosummary::
   :toctree: generated/

   configuration_model
   directed_configuration_model
   expected_degree_graph
   havel_hakimi_graph
   directed_havel_hakimi_graph
   degree_sequence_tree
   random_degree_sequence_graph


Random Clustered
----------------
.. automodule:: networkx.generators.random_clustered

.. autosummary::
   :toctree: generated/

   random_clustered_graph


Directed
--------
.. automodule:: networkx.generators.directed
.. autosummary::
   :toctree: generated/

   gn_graph
   gnr_graph
   gnc_graph
   random_k_out_graph
   scale_free_graph


Geometric
---------
.. automodule:: networkx.generators.geometric
.. autosummary::
   :toctree: generated/

   geometric_edges
   geographical_threshold_graph
   navigable_small_world_graph
   random_geometric_graph
   soft_random_geometric_graph
   thresholded_random_geometric_graph
   waxman_graph
   geometric_soft_configuration_graph

Line Graph
----------
.. automodule:: networkx.generators.line
.. autosummary::
   :toctree: generated/

   line_graph
   inverse_line_graph


Ego Graph
---------
.. automodule:: networkx.generators.ego
.. autosummary::
   :toctree: generated/

   ego_graph


Stochastic
----------
.. automodule:: networkx.generators.stochastic
.. autosummary::
   :toctree: generated/

   stochastic_graph


AS graph
--------
.. automodule:: networkx.generators.internet_as_graphs
.. autosummary::
   :toctree: generated/

   random_internet_as_graph


Intersection
------------
.. automodule:: networkx.generators.intersection
.. autosummary::
   :toctree: generated/

   uniform_random_intersection_graph
   k_random_intersection_graph
   general_random_intersection_graph


Social Networks
---------------
.. automodule:: networkx.generators.social
.. autosummary::
   :toctree: generated/

   karate_club_graph
   davis_southern_women_graph
   florentine_families_graph
   les_miserables_graph


Community
---------
.. automodule:: networkx.generators.community
.. autosummary::
   :toctree: generated/

   caveman_graph
   connected_caveman_graph
   gaussian_random_partition_graph
   LFR_benchmark_graph
   planted_partition_graph
   random_partition_graph
   relaxed_caveman_graph
   ring_of_cliques
   stochastic_block_model
   windmill_graph


Spectral
--------
.. automodule:: networkx.generators.spectral_graph_forge
.. autosummary::
   :toctree: generated/

   spectral_graph_forge


Trees
-----
.. automodule:: networkx.generators.trees
.. autosummary::
   :toctree: generated/

   prefix_tree
   random_labeled_tree
   random_labeled_rooted_tree
   random_labeled_rooted_forest
   random_unlabeled_tree
   random_unlabeled_rooted_tree
   random_unlabeled_rooted_forest


Non Isomorphic Trees
--------------------
.. automodule:: networkx.generators.nonisomorphic_trees
.. autosummary::
   :toctree: generated/

   nonisomorphic_trees
   number_of_nonisomorphic_trees


Triads
------
.. automodule:: networkx.generators.triads
.. autosummary::
   :toctree: generated/

   triad_graph


Joint Degree Sequence
---------------------
.. automodule:: networkx.generators.joint_degree_seq
.. autosummary::
   :toctree: generated/

   is_valid_joint_degree
   joint_degree_graph
   is_valid_directed_joint_degree
   directed_joint_degree_graph


Mycielski
---------
.. automodule:: networkx.generators.mycielski
.. autosummary::
   :toctree: generated/

   mycielskian
   mycielski_graph


Harary Graph
------------
.. automodule:: networkx.generators.harary_graph
.. autosummary::
   :toctree: generated/

   hnm_harary_graph
   hkn_harary_graph

Cographs
------------
.. automodule:: networkx.generators.cographs
.. autosummary::
   :toctree: generated/

   random_cograph

Interval Graph
---------------
.. automodule:: networkx.generators.interval_graph
.. autosummary::
   :toctree: generated/

   interval_graph

Sudoku
------
.. automodule:: networkx.generators.sudoku
.. autosummary::
   :toctree: generated/

   sudoku_graph

Time Series
-----------
.. automodule:: networkx.generators.time_series
.. autosummary::
   :toctree: generated/

   visibility_graph
