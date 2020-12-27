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
        "test_basic",
        "test_centrality",
        "test_cluster",
        "test_covering",
        "test_edgelist",
        "test_generators",
        "test_matching",
        "test_matrix",
        "test_project",
        "test_redundancy",
        "test_spectral_bipartivity",
    },
    submod_attrs={
        "test_basic": [
            "TestBipartiteBasic",
        ],
        "test_centrality": [
            "TestBipartiteCentrality",
        ],
        "test_cluster": [
            "test_average_path_graph",
            "test_bad_mode",
            "test_not_bipartite",
            "test_pairwise_bipartite_cc_functions",
            "test_path_graph",
            "test_ra_clustering_davis",
            "test_ra_clustering_square",
            "test_ra_clustering_zero",
            "test_star_graph",
        ],
        "test_covering": [
            "TestMinEdgeCover",
        ],
        "test_edgelist": [
            "TestEdgelist",
        ],
        "test_generators": [
            "TestGeneratorsBipartite",
        ],
        "test_matching": [
            "TestMatching",
            "TestMinimumWeightFullMatching",
            "test_eppstein_matching",
        ],
        "test_matrix": [
            "TestBiadjacencyMatrix",
            "np",
            "sp",
            "sparse",
        ],
        "test_project": [
            "TestBipartiteProject",
            "TestBipartiteWeightedProjection",
        ],
        "test_redundancy": [
            "test_no_redundant_nodes",
            "test_not_enough_neighbors",
            "test_redundant_nodes",
        ],
        "test_spectral_bipartivity": [
            "TestSpectralBipartivity",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestBiadjacencyMatrix",
    "TestBipartiteBasic",
    "TestBipartiteCentrality",
    "TestBipartiteProject",
    "TestBipartiteWeightedProjection",
    "TestEdgelist",
    "TestGeneratorsBipartite",
    "TestMatching",
    "TestMinEdgeCover",
    "TestMinimumWeightFullMatching",
    "TestSpectralBipartivity",
    "np",
    "sp",
    "sparse",
    "test_average_path_graph",
    "test_bad_mode",
    "test_basic",
    "test_centrality",
    "test_cluster",
    "test_covering",
    "test_edgelist",
    "test_eppstein_matching",
    "test_generators",
    "test_matching",
    "test_matrix",
    "test_no_redundant_nodes",
    "test_not_bipartite",
    "test_not_enough_neighbors",
    "test_pairwise_bipartite_cc_functions",
    "test_path_graph",
    "test_project",
    "test_ra_clustering_davis",
    "test_ra_clustering_square",
    "test_ra_clustering_zero",
    "test_redundancy",
    "test_redundant_nodes",
    "test_spectral_bipartivity",
    "test_star_graph",
]
