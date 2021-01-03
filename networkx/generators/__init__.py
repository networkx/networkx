"""
A package for generating various graphs in networkx.

mkinit --black --lazy --nomods ~/code/networkx/networkx/generators/__init__.py -w
"""

__private__ = [
    "tests"
    "interval_graph",
    "spectral_graph_forge",
    "nonisomorphic_trees"
]


def lazy_import(module_name, submodules, submod_attrs):
    import sys
    import importlib
    import importlib.util

    all_funcs = []
    for mod, funcs in submod_attrs.items():
        all_funcs.extend(funcs)
    name_to_submod = {
        func: mod for mod, funcs in submod_attrs.items() for func in funcs
    }

    def require(fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        spec = importlib.util.find_spec(fullname)
        try:
            module = importlib.util.module_from_spec(spec)
        except Exception:
            raise ImportError(
                "Could not lazy import module {fullname}".format(fullname=fullname)
            ) from None
        loader = importlib.util.LazyLoader(spec.loader)
        sys.modules[fullname] = module
        loader.exec_module(module)
        return module

    def __getattr__(name):
        if name in submodules:
            fullname = "{module_name}.{name}".format(module_name=module_name, name=name)
            attr = require(fullname)
        elif name in name_to_submod:
            modname = name_to_submod[name]
            module = importlib.import_module(
                "{module_name}.{modname}".format(
                    module_name=module_name, modname=modname
                )
            )
            attr = getattr(module, name)
        else:
            raise AttributeError(
                "No {module_name} attribute {name}".format(
                    module_name=module_name, name=name
                )
            )
        globals()[name] = attr
        return attr

    return __getattr__


__getattr__ = lazy_import(
    __name__,
    submodules={},
    submod_attrs={
        "atlas": [
            "graph_atlas",
            "graph_atlas_g",
        ],
        "classic": [
            "balanced_tree",
            "barbell_graph",
            "binomial_tree",
            "circulant_graph",
            "circular_ladder_graph",
            "complete_graph",
            "complete_multipartite_graph",
            "cycle_graph",
            "dorogovtsev_goltsev_mendes_graph",
            "empty_graph",
            "full_rary_tree",
            "ladder_graph",
            "lollipop_graph",
            "null_graph",
            "path_graph",
            "star_graph",
            "trivial_graph",
            "turan_graph",
            "wheel_graph",
        ],
        "cographs": [
            "random_cograph",
        ],
        "community": [
            "LFR_benchmark_graph",
            "caveman_graph",
            "connected_caveman_graph",
            "gaussian_random_partition_graph",
            "planted_partition_graph",
            "random_partition_graph",
            "relaxed_caveman_graph",
            "ring_of_cliques",
            "stochastic_block_model",
            "windmill_graph",
        ],
        "degree_seq": [
            "configuration_model",
            "degree_sequence_tree",
            "directed_configuration_model",
            "directed_havel_hakimi_graph",
            "expected_degree_graph",
            "havel_hakimi_graph",
            "random_degree_sequence_graph",
        ],
        "directed": [
            "gn_graph",
            "gnc_graph",
            "gnr_graph",
            "random_k_out_graph",
            "scale_free_graph",
        ],
        "duplication": [
            "duplication_divergence_graph",
            "partial_duplication_graph",
        ],
        "ego": [
            "ego_graph",
        ],
        "expanders": [
            "chordal_cycle_graph",
            "margulis_gabber_galil_graph",
            "paley_graph",
        ],
        "geometric": [
            "geographical_threshold_graph",
            "navigable_small_world_graph",
            "random_geometric_graph",
            "soft_random_geometric_graph",
            "thresholded_random_geometric_graph",
            "waxman_graph",
        ],
        "harary_graph": [
            "hkn_harary_graph",
            "hnm_harary_graph",
        ],
        "internet_as_graphs": [
            "random_internet_as_graph",
        ],
        "intersection": [
            "general_random_intersection_graph",
            "k_random_intersection_graph",
            "uniform_random_intersection_graph",
        ],
        "interval_graph": [
            "interval_graph",
        ],
        "joint_degree_seq": [
            "directed_joint_degree_graph",
            "is_valid_directed_joint_degree",
            "is_valid_joint_degree",
            "joint_degree_graph",
        ],
        "lattice": [
            "grid_2d_graph",
            "grid_graph",
            "hexagonal_lattice_graph",
            "hypercube_graph",
            "triangular_lattice_graph",
        ],
        "line": [
            "inverse_line_graph",
            "line_graph",
        ],
        "mycielski": [
            "mycielski_graph",
            "mycielskian",
        ],
        "random_clustered": [
            "random_clustered_graph",
        ],
        "random_graphs": [
            "barabasi_albert_graph",
            "binomial_graph",
            "connected_watts_strogatz_graph",
            "dense_gnm_random_graph",
            "dual_barabasi_albert_graph",
            "erdos_renyi_graph",
            "extended_barabasi_albert_graph",
            "fast_gnp_random_graph",
            "gnm_random_graph",
            "gnp_random_graph",
            "newman_watts_strogatz_graph",
            "powerlaw_cluster_graph",
            "random_kernel_graph",
            "random_lobster",
            "random_powerlaw_tree",
            "random_powerlaw_tree_sequence",
            "random_regular_graph",
            "random_shell_graph",
            "watts_strogatz_graph",
        ],
        "small": [
            "LCF_graph",
            "bull_graph",
            "chvatal_graph",
            "cubical_graph",
            "desargues_graph",
            "diamond_graph",
            "dodecahedral_graph",
            "frucht_graph",
            "heawood_graph",
            "hoffman_singleton_graph",
            "house_graph",
            "house_x_graph",
            "icosahedral_graph",
            "krackhardt_kite_graph",
            "make_small_graph",
            "moebius_kantor_graph",
            "octahedral_graph",
            "pappus_graph",
            "petersen_graph",
            "sedgewick_maze_graph",
            "tetrahedral_graph",
            "truncated_cube_graph",
            "truncated_tetrahedron_graph",
            "tutte_graph",
        ],
        "social": [
            "davis_southern_women_graph",
            "florentine_families_graph",
            "karate_club_graph",
            "les_miserables_graph",
        ],
        "stochastic": [
            "stochastic_graph",
        ],
        "sudoku": [
            "sudoku_graph",
        ],
        "trees": [
            "prefix_tree",
            "random_tree",
        ],
        "triads": [
            "triad_graph",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "LCF_graph",
    "LFR_benchmark_graph",
    "balanced_tree",
    "barabasi_albert_graph",
    "barbell_graph",
    "binomial_graph",
    "binomial_tree",
    "bull_graph",
    "caveman_graph",
    "chordal_cycle_graph",
    "chvatal_graph",
    "circulant_graph",
    "circular_ladder_graph",
    "complete_graph",
    "complete_multipartite_graph",
    "configuration_model",
    "connected_caveman_graph",
    "connected_watts_strogatz_graph",
    "cubical_graph",
    "cycle_graph",
    "davis_southern_women_graph",
    "degree_sequence_tree",
    "dense_gnm_random_graph",
    "desargues_graph",
    "diamond_graph",
    "directed_configuration_model",
    "directed_havel_hakimi_graph",
    "directed_joint_degree_graph",
    "dodecahedral_graph",
    "dorogovtsev_goltsev_mendes_graph",
    "dual_barabasi_albert_graph",
    "duplication_divergence_graph",
    "ego_graph",
    "empty_graph",
    "erdos_renyi_graph",
    "expected_degree_graph",
    "extended_barabasi_albert_graph",
    "fast_gnp_random_graph",
    "florentine_families_graph",
    "frucht_graph",
    "full_rary_tree",
    "gaussian_random_partition_graph",
    "general_random_intersection_graph",
    "geographical_threshold_graph",
    "gn_graph",
    "gnc_graph",
    "gnm_random_graph",
    "gnp_random_graph",
    "gnr_graph",
    "graph_atlas",
    "graph_atlas_g",
    "grid_2d_graph",
    "grid_graph",
    "havel_hakimi_graph",
    "heawood_graph",
    "hexagonal_lattice_graph",
    "hkn_harary_graph",
    "hnm_harary_graph",
    "hoffman_singleton_graph",
    "house_graph",
    "house_x_graph",
    "hypercube_graph",
    "icosahedral_graph",
    "interval_graph",
    "inverse_line_graph",
    "is_valid_directed_joint_degree",
    "is_valid_joint_degree",
    "joint_degree_graph",
    "k_random_intersection_graph",
    "karate_club_graph",
    "krackhardt_kite_graph",
    "ladder_graph",
    "les_miserables_graph",
    "line_graph",
    "lollipop_graph",
    "make_small_graph",
    "margulis_gabber_galil_graph",
    "moebius_kantor_graph",
    "mycielski_graph",
    "mycielskian",
    "navigable_small_world_graph",
    "newman_watts_strogatz_graph",
    "null_graph",
    "octahedral_graph",
    "paley_graph",
    "pappus_graph",
    "partial_duplication_graph",
    "path_graph",
    "petersen_graph",
    "planted_partition_graph",
    "powerlaw_cluster_graph",
    "prefix_tree",
    "random_clustered_graph",
    "random_cograph",
    "random_degree_sequence_graph",
    "random_geometric_graph",
    "random_internet_as_graph",
    "random_k_out_graph",
    "random_kernel_graph",
    "random_lobster",
    "random_partition_graph",
    "random_powerlaw_tree",
    "random_powerlaw_tree_sequence",
    "random_regular_graph",
    "random_shell_graph",
    "random_tree",
    "relaxed_caveman_graph",
    "ring_of_cliques",
    "scale_free_graph",
    "sedgewick_maze_graph",
    "soft_random_geometric_graph",
    "star_graph",
    "stochastic_block_model",
    "stochastic_graph",
    "sudoku_graph",
    "tetrahedral_graph",
    "thresholded_random_geometric_graph",
    "triad_graph",
    "triangular_lattice_graph",
    "trivial_graph",
    "truncated_cube_graph",
    "truncated_tetrahedron_graph",
    "turan_graph",
    "tutte_graph",
    "uniform_random_intersection_graph",
    "watts_strogatz_graph",
    "waxman_graph",
    "wheel_graph",
    "windmill_graph",
]
