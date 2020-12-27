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
        "test_approx_clust_coeff",
        "test_clique",
        "test_connectivity",
        "test_dominating_set",
        "test_independent_set",
        "test_kcomponents",
        "test_matching",
        "test_maxcut",
        "test_ramsey",
        "test_steinertree",
        "test_treewidth",
        "test_vertex_cover",
    },
    submod_attrs={
        "test_approx_clust_coeff": [
            "test_complete",
            "test_dodecahedral",
            "test_empty",
            "test_petersen",
            "test_petersen_seed",
            "test_tetrahedral",
        ],
        "test_clique": [
            "TestCliqueRemoval",
            "TestMaxClique",
            "is_clique",
            "is_independent_set",
            "test_large_clique_size",
        ],
        "test_connectivity": [
            "TestAllPairsNodeConnectivityApprox",
            "test_complete_graphs",
            "test_directed_node_connectivity",
            "test_dodecahedral",
            "test_empty_graphs",
            "test_global_node_connectivity",
            "test_missing_source",
            "test_missing_target",
            "test_octahedral",
            "test_only_source",
            "test_only_target",
            "test_petersen",
            "test_source_equals_target",
            "test_white_harary1",
        ],
        "test_dominating_set": [
            "TestMinWeightDominatingSet",
        ],
        "test_independent_set": [
            "test_independent_set",
        ],
        "test_kcomponents": [
            "TestAntiGraph",
            "build_k_number_dict",
            "graph_example_1",
            "test_directed",
            "test_example_1",
            "test_example_1_detail_3_and_4",
            "test_karate_0",
            "test_karate_1",
            "test_same",
            "test_torrents_and_ferraro_graph",
            "torrents_and_ferraro_graph",
        ],
        "test_matching": [
            "test_min_maximal_matching",
        ],
        "test_maxcut": [
            "test_negative_weights",
            "test_one_exchange_basic",
            "test_one_exchange_optimal",
            "test_random_partitioning",
            "test_random_partitioning_all_to_one",
        ],
        "test_ramsey": [
            "test_ramsey",
        ],
        "test_steinertree": [
            "TestSteinerTree",
        ],
        "test_treewidth": [
            "TestTreewidthMinDegree",
            "TestTreewidthMinFillIn",
            "is_tree_decomp",
        ],
        "test_vertex_cover": [
            "TestMWVC",
            "is_cover",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestAllPairsNodeConnectivityApprox",
    "TestAntiGraph",
    "TestCliqueRemoval",
    "TestMWVC",
    "TestMaxClique",
    "TestMinWeightDominatingSet",
    "TestSteinerTree",
    "TestTreewidthMinDegree",
    "TestTreewidthMinFillIn",
    "build_k_number_dict",
    "graph_example_1",
    "is_clique",
    "is_cover",
    "is_independent_set",
    "is_tree_decomp",
    "test_approx_clust_coeff",
    "test_clique",
    "test_complete",
    "test_complete_graphs",
    "test_connectivity",
    "test_directed",
    "test_directed_node_connectivity",
    "test_dodecahedral",
    "test_dominating_set",
    "test_empty",
    "test_empty_graphs",
    "test_example_1",
    "test_example_1_detail_3_and_4",
    "test_global_node_connectivity",
    "test_independent_set",
    "test_karate_0",
    "test_karate_1",
    "test_kcomponents",
    "test_large_clique_size",
    "test_matching",
    "test_maxcut",
    "test_min_maximal_matching",
    "test_missing_source",
    "test_missing_target",
    "test_negative_weights",
    "test_octahedral",
    "test_one_exchange_basic",
    "test_one_exchange_optimal",
    "test_only_source",
    "test_only_target",
    "test_petersen",
    "test_petersen_seed",
    "test_ramsey",
    "test_random_partitioning",
    "test_random_partitioning_all_to_one",
    "test_same",
    "test_source_equals_target",
    "test_steinertree",
    "test_tetrahedral",
    "test_torrents_and_ferraro_graph",
    "test_treewidth",
    "test_vertex_cover",
    "test_white_harary1",
    "torrents_and_ferraro_graph",
]
