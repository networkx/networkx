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
    submodules={
        "test_atlas",
        "test_classic",
        "test_cographs",
        "test_community",
        "test_degree_seq",
        "test_directed",
        "test_duplication",
        "test_ego",
        "test_expanders",
        "test_geometric",
        "test_harary_graph",
        "test_internet_as_graphs",
        "test_intersection",
        "test_interval_graph",
        "test_joint_degree_seq",
        "test_lattice",
        "test_line",
        "test_mycielski",
        "test_nonisomorphic_trees",
        "test_random_clustered",
        "test_random_graphs",
        "test_small",
        "test_spectral_graph_forge",
        "test_stochastic",
        "test_sudoku",
        "test_trees",
        "test_triads",
    },
    submod_attrs={
        "test_atlas": [
            "TestAtlasGraph",
            "TestAtlasGraphG",
        ],
        "test_classic": [
            "TestGeneratorClassic",
            "is_isomorphic",
        ],
        "test_cographs": [
            "test_random_cograph",
        ],
        "test_community": [
            "test_both_degrees_none",
            "test_caveman_graph",
            "test_connected_caveman_graph",
            "test_gaussian_random_partition_graph",
            "test_generator",
            "test_invalid_tau1",
            "test_invalid_tau2",
            "test_mu_too_large",
            "test_mu_too_small",
            "test_neither_degrees_none",
            "test_planted_partition_graph",
            "test_random_partition_graph",
            "test_relaxed_caveman_graph",
            "test_ring_of_cliques",
            "test_stochastic_block_model",
            "test_windmill_graph",
        ],
        "test_degree_seq": [
            "TestConfigurationModel",
            "test_degree_sequence_tree",
            "test_directed_configuation_model",
            "test_directed_configuation_raise_unequal",
            "test_directed_havel_hakimi",
            "test_expected_degree_graph",
            "test_expected_degree_graph_empty",
            "test_expected_degree_graph_selfloops",
            "test_expected_degree_graph_skew",
            "test_havel_hakimi_construction",
            "test_random_degree_sequence_graph",
            "test_random_degree_sequence_graph_raise",
            "test_random_degree_sequence_large",
            "test_simple_directed_configuation_model",
        ],
        "test_directed": [
            "TestGeneratorsDirected",
            "TestRandomKOutGraph",
            "TestUniformRandomKOutGraph",
        ],
        "test_duplication": [
            "TestDuplicationDivergenceGraph",
            "TestPartialDuplicationGraph",
        ],
        "test_ego": [
            "TestGeneratorEgo",
        ],
        "test_expanders": [
            "test_chordal_cycle_graph",
            "test_margulis_gabber_galil_graph",
            "test_margulis_gabber_galil_graph_badinput",
            "test_paley_graph",
        ],
        "test_geometric": [
            "TestGeographicalThresholdGraph",
            "TestNavigableSmallWorldGraph",
            "TestRandomGeometricGraph",
            "TestSoftRandomGeometricGraph",
            "TestThresholdedRandomGeometricGraph",
            "TestWaxmanGraph",
            "join",
            "l1dist",
        ],
        "test_harary_graph": [
            "TestHararyGraph",
        ],
        "test_internet_as_graphs": [
            "TestInternetASTopology",
        ],
        "test_intersection": [
            "TestIntersectionGraph",
        ],
        "test_interval_graph": [
            "TestIntervalGraph",
        ],
        "test_joint_degree_seq": [
            "test_directed_joint_degree_graph",
            "test_is_valid_directed_joint_degree",
            "test_is_valid_joint_degree",
            "test_joint_degree_graph",
        ],
        "test_lattice": [
            "TestGrid2DGraph",
            "TestGridGraph",
            "TestHexagonalLatticeGraph",
            "TestHypercubeGraph",
            "TestTriangularLatticeGraph",
        ],
        "test_line": [
            "TestGeneratorInverseLine",
            "TestGeneratorLine",
            "test_edge_func",
            "test_node_func",
            "test_sorted_edge",
        ],
        "test_mycielski": [
            "TestMycielski",
        ],
        "test_nonisomorphic_trees": [
            "TestGeneratorNonIsomorphicTrees",
        ],
        "test_random_clustered": [
            "TestRandomClusteredGraph",
        ],
        "test_random_graphs": [
            "TestGeneratorsRandom",
        ],
        "test_small": [
            "TestGeneratorsSmall",
            "is_isomorphic",
            "null",
        ],
        "test_spectral_graph_forge": [
            "test_spectral_graph_forge",
        ],
        "test_stochastic": [
            "TestStochasticGraph",
        ],
        "test_sudoku": [
            "test_sudoku_generator",
            "test_sudoku_negative",
        ],
        "test_trees": [
            "TestPrefixTree",
            "test_random_tree",
        ],
        "test_triads": [
            "test_invalid_name",
            "test_triad_graph",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestAtlasGraph",
    "TestAtlasGraphG",
    "TestConfigurationModel",
    "TestDuplicationDivergenceGraph",
    "TestGeneratorClassic",
    "TestGeneratorEgo",
    "TestGeneratorInverseLine",
    "TestGeneratorLine",
    "TestGeneratorNonIsomorphicTrees",
    "TestGeneratorsDirected",
    "TestGeneratorsRandom",
    "TestGeneratorsSmall",
    "TestGeographicalThresholdGraph",
    "TestGrid2DGraph",
    "TestGridGraph",
    "TestHararyGraph",
    "TestHexagonalLatticeGraph",
    "TestHypercubeGraph",
    "TestInternetASTopology",
    "TestIntersectionGraph",
    "TestIntervalGraph",
    "TestMycielski",
    "TestNavigableSmallWorldGraph",
    "TestPartialDuplicationGraph",
    "TestPrefixTree",
    "TestRandomClusteredGraph",
    "TestRandomGeometricGraph",
    "TestRandomKOutGraph",
    "TestSoftRandomGeometricGraph",
    "TestStochasticGraph",
    "TestThresholdedRandomGeometricGraph",
    "TestTriangularLatticeGraph",
    "TestUniformRandomKOutGraph",
    "TestWaxmanGraph",
    "is_isomorphic",
    "join",
    "l1dist",
    "null",
    "test_atlas",
    "test_both_degrees_none",
    "test_caveman_graph",
    "test_chordal_cycle_graph",
    "test_classic",
    "test_cographs",
    "test_community",
    "test_connected_caveman_graph",
    "test_degree_seq",
    "test_degree_sequence_tree",
    "test_directed",
    "test_directed_configuation_model",
    "test_directed_configuation_raise_unequal",
    "test_directed_havel_hakimi",
    "test_directed_joint_degree_graph",
    "test_duplication",
    "test_edge_func",
    "test_ego",
    "test_expanders",
    "test_expected_degree_graph",
    "test_expected_degree_graph_empty",
    "test_expected_degree_graph_selfloops",
    "test_expected_degree_graph_skew",
    "test_gaussian_random_partition_graph",
    "test_generator",
    "test_geometric",
    "test_harary_graph",
    "test_havel_hakimi_construction",
    "test_internet_as_graphs",
    "test_intersection",
    "test_interval_graph",
    "test_invalid_name",
    "test_invalid_tau1",
    "test_invalid_tau2",
    "test_is_valid_directed_joint_degree",
    "test_is_valid_joint_degree",
    "test_joint_degree_graph",
    "test_joint_degree_seq",
    "test_lattice",
    "test_line",
    "test_margulis_gabber_galil_graph",
    "test_margulis_gabber_galil_graph_badinput",
    "test_mu_too_large",
    "test_mu_too_small",
    "test_mycielski",
    "test_neither_degrees_none",
    "test_node_func",
    "test_nonisomorphic_trees",
    "test_paley_graph",
    "test_planted_partition_graph",
    "test_random_clustered",
    "test_random_cograph",
    "test_random_degree_sequence_graph",
    "test_random_degree_sequence_graph_raise",
    "test_random_degree_sequence_large",
    "test_random_graphs",
    "test_random_partition_graph",
    "test_random_tree",
    "test_relaxed_caveman_graph",
    "test_ring_of_cliques",
    "test_simple_directed_configuation_model",
    "test_small",
    "test_sorted_edge",
    "test_spectral_graph_forge",
    "test_stochastic",
    "test_stochastic_block_model",
    "test_sudoku",
    "test_sudoku_generator",
    "test_sudoku_negative",
    "test_trees",
    "test_triad_graph",
    "test_triads",
    "test_windmill_graph",
]
