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
        "test_betweenness_centrality",
        "test_betweenness_centrality_subset",
        "test_closeness_centrality",
        "test_current_flow_betweenness_centrality",
        "test_current_flow_betweenness_centrality_subset",
        "test_current_flow_closeness",
        "test_degree_centrality",
        "test_dispersion",
        "test_eigenvector_centrality",
        "test_group",
        "test_harmonic_centrality",
        "test_katz_centrality",
        "test_load_centrality",
        "test_percolation_centrality",
        "test_reaching",
        "test_second_order_centrality",
        "test_subgraph",
        "test_trophic",
        "test_voterank",
    },
    submod_attrs={
        "test_betweenness_centrality": [
            "TestBetweennessCentrality",
            "TestEdgeBetweennessCentrality",
            "TestWeightedBetweennessCentrality",
            "TestWeightedEdgeBetweennessCentrality",
            "weighted_G",
        ],
        "test_betweenness_centrality_subset": [
            "TestBetweennessCentralitySources",
            "TestEdgeSubsetBetweennessCentrality",
            "TestSubsetBetweennessCentrality",
        ],
        "test_closeness_centrality": [
            "TestClosenessCentrality",
        ],
        "test_current_flow_betweenness_centrality": [
            "TestApproximateFlowBetweennessCentrality",
            "TestEdgeFlowBetweennessCentrality",
            "TestFlowBetweennessCentrality",
            "TestWeightedFlowBetweennessCentrality",
            "np",
        ],
        "test_current_flow_betweenness_centrality_subset": [
            "TestEdgeFlowBetweennessCentrality",
            "TestFlowBetweennessCentrality",
        ],
        "test_current_flow_closeness": [
            "TestFlowClosenessCentrality",
            "TestWeightedFlowClosenessCentrality",
        ],
        "test_degree_centrality": [
            "TestDegreeCentrality",
        ],
        "test_dispersion": [
            "TestDispersion",
            "small_ego_G",
        ],
        "test_eigenvector_centrality": [
            "TestEigenvectorCentrality",
            "TestEigenvectorCentralityDirected",
            "TestEigenvectorCentralityExceptions",
            "np",
        ],
        "test_group": [
            "TestGroupBetweennessCentrality",
            "TestGroupClosenessCentrality",
            "TestGroupDegreeCentrality",
        ],
        "test_harmonic_centrality": [
            "TestClosenessCentrality",
        ],
        "test_katz_centrality": [
            "TestKatzCentrality",
            "TestKatzCentralityDirected",
            "TestKatzCentralityDirectedNumpy",
            "TestKatzCentralityNumpy",
            "TestKatzEigenvectorVKatz",
        ],
        "test_load_centrality": [
            "TestLoadCentrality",
        ],
        "test_percolation_centrality": [
            "TestPercolationCentrality",
            "example1a_G",
            "example1b_G",
        ],
        "test_reaching": [
            "TestGlobalReachingCentrality",
            "TestLocalReachingCentrality",
        ],
        "test_second_order_centrality": [
            "TestSecondOrderCentrality",
        ],
        "test_subgraph": [
            "TestSubgraph",
        ],
        "test_trophic": [
            "np",
            "test_trophic_differences",
            "test_trophic_incoherence_parameter_cannibalism",
            "test_trophic_incoherence_parameter_no_cannibalism",
            "test_trophic_levels",
            "test_trophic_levels_even_more_complex",
            "test_trophic_levels_levine",
            "test_trophic_levels_more_complex",
            "test_trophic_levels_simple",
            "test_trophic_levels_singular_matrix",
            "test_trophic_levels_singular_with_basal",
        ],
        "test_voterank": [
            "TestVoteRankCentrality",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestApproximateFlowBetweennessCentrality",
    "TestBetweennessCentrality",
    "TestBetweennessCentralitySources",
    "TestClosenessCentrality",
    "TestDegreeCentrality",
    "TestDispersion",
    "TestEdgeBetweennessCentrality",
    "TestEdgeFlowBetweennessCentrality",
    "TestEdgeSubsetBetweennessCentrality",
    "TestEigenvectorCentrality",
    "TestEigenvectorCentralityDirected",
    "TestEigenvectorCentralityExceptions",
    "TestFlowBetweennessCentrality",
    "TestFlowClosenessCentrality",
    "TestGlobalReachingCentrality",
    "TestGroupBetweennessCentrality",
    "TestGroupClosenessCentrality",
    "TestGroupDegreeCentrality",
    "TestKatzCentrality",
    "TestKatzCentralityDirected",
    "TestKatzCentralityDirectedNumpy",
    "TestKatzCentralityNumpy",
    "TestKatzEigenvectorVKatz",
    "TestLoadCentrality",
    "TestLocalReachingCentrality",
    "TestPercolationCentrality",
    "TestSecondOrderCentrality",
    "TestSubgraph",
    "TestSubsetBetweennessCentrality",
    "TestVoteRankCentrality",
    "TestWeightedBetweennessCentrality",
    "TestWeightedEdgeBetweennessCentrality",
    "TestWeightedFlowBetweennessCentrality",
    "TestWeightedFlowClosenessCentrality",
    "example1a_G",
    "example1b_G",
    "np",
    "small_ego_G",
    "test_betweenness_centrality",
    "test_betweenness_centrality_subset",
    "test_closeness_centrality",
    "test_current_flow_betweenness_centrality",
    "test_current_flow_betweenness_centrality_subset",
    "test_current_flow_closeness",
    "test_degree_centrality",
    "test_dispersion",
    "test_eigenvector_centrality",
    "test_group",
    "test_harmonic_centrality",
    "test_katz_centrality",
    "test_load_centrality",
    "test_percolation_centrality",
    "test_reaching",
    "test_second_order_centrality",
    "test_subgraph",
    "test_trophic",
    "test_trophic_differences",
    "test_trophic_incoherence_parameter_cannibalism",
    "test_trophic_incoherence_parameter_no_cannibalism",
    "test_trophic_levels",
    "test_trophic_levels_even_more_complex",
    "test_trophic_levels_levine",
    "test_trophic_levels_more_complex",
    "test_trophic_levels_simple",
    "test_trophic_levels_singular_matrix",
    "test_trophic_levels_singular_with_basal",
    "test_voterank",
    "weighted_G",
]
