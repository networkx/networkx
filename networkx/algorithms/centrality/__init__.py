__private__ = ["tests"]


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
        "betweenness",
        "betweenness_subset",
        "closeness",
        "current_flow_betweenness",
        "current_flow_betweenness_subset",
        "current_flow_closeness",
        "degree_alg",
        "dispersion",
        "eigenvector",
        "flow_matrix",
        "group",
        "harmonic",
        "katz",
        "load",
        "percolation",
        "reaching",
        "second_order",
        "subgraph_alg",
        "tests",
        "trophic",
        "voterank_alg",
    },
    submod_attrs={
        "betweenness": [
            "betweenness_centrality",
            "edge_betweenness",
            "edge_betweenness_centrality",
        ],
        "betweenness_subset": [
            "betweenness_centrality_source",
            "betweenness_centrality_subset",
            "edge_betweenness_centrality_subset",
        ],
        "closeness": [
            "closeness_centrality",
            "incremental_closeness_centrality",
        ],
        "current_flow_betweenness": [
            "approximate_current_flow_betweenness_centrality",
            "current_flow_betweenness_centrality",
            "edge_current_flow_betweenness_centrality",
        ],
        "current_flow_betweenness_subset": [
            "current_flow_betweenness_centrality_subset",
            "edge_current_flow_betweenness_centrality_subset",
        ],
        "current_flow_closeness": [
            "current_flow_closeness_centrality",
            "information_centrality",
        ],
        "degree_alg": [
            "degree_centrality",
            "in_degree_centrality",
            "out_degree_centrality",
        ],
        "dispersion": [
            "dispersion",
        ],
        "eigenvector": [
            "eigenvector_centrality",
            "eigenvector_centrality_numpy",
        ],
        "flow_matrix": [
            "CGInverseLaplacian",
            "FullInverseLaplacian",
            "InverseLaplacian",
            "SuperLUInverseLaplacian",
            "flow_matrix_row",
            "laplacian_sparse_matrix",
        ],
        "group": [
            "group_betweenness_centrality",
            "group_closeness_centrality",
            "group_degree_centrality",
            "group_in_degree_centrality",
            "group_out_degree_centrality",
        ],
        "harmonic": [
            "harmonic_centrality",
        ],
        "katz": [
            "katz_centrality",
            "katz_centrality_numpy",
        ],
        "load": [
            "edge_load_centrality",
            "load_centrality",
        ],
        "percolation": [
            "percolation_centrality",
        ],
        "reaching": [
            "global_reaching_centrality",
            "local_reaching_centrality",
        ],
        "second_order": [
            "second_order_centrality",
        ],
        "subgraph_alg": [
            "communicability_betweenness_centrality",
            "estrada_index",
            "subgraph_centrality",
            "subgraph_centrality_exp",
        ],
        "trophic": [
            "trophic_differences",
            "trophic_incoherence_parameter",
            "trophic_levels",
        ],
        "voterank_alg": [
            "voterank",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "CGInverseLaplacian",
    "FullInverseLaplacian",
    "InverseLaplacian",
    "SuperLUInverseLaplacian",
    "approximate_current_flow_betweenness_centrality",
    "betweenness",
    "betweenness_centrality",
    "betweenness_centrality_source",
    "betweenness_centrality_subset",
    "betweenness_subset",
    "closeness",
    "closeness_centrality",
    "communicability_betweenness_centrality",
    "current_flow_betweenness",
    "current_flow_betweenness_centrality",
    "current_flow_betweenness_centrality_subset",
    "current_flow_betweenness_subset",
    "current_flow_closeness",
    "current_flow_closeness_centrality",
    "degree_alg",
    "degree_centrality",
    "dispersion",
    "edge_betweenness",
    "edge_betweenness_centrality",
    "edge_betweenness_centrality_subset",
    "edge_current_flow_betweenness_centrality",
    "edge_current_flow_betweenness_centrality_subset",
    "edge_load_centrality",
    "eigenvector",
    "eigenvector_centrality",
    "eigenvector_centrality_numpy",
    "estrada_index",
    "flow_matrix",
    "flow_matrix_row",
    "global_reaching_centrality",
    "group",
    "group_betweenness_centrality",
    "group_closeness_centrality",
    "group_degree_centrality",
    "group_in_degree_centrality",
    "group_out_degree_centrality",
    "harmonic",
    "harmonic_centrality",
    "in_degree_centrality",
    "incremental_closeness_centrality",
    "information_centrality",
    "katz",
    "katz_centrality",
    "katz_centrality_numpy",
    "laplacian_sparse_matrix",
    "load",
    "load_centrality",
    "local_reaching_centrality",
    "out_degree_centrality",
    "percolation",
    "percolation_centrality",
    "reaching",
    "second_order",
    "second_order_centrality",
    "subgraph_alg",
    "subgraph_centrality",
    "subgraph_centrality_exp",
    "tests",
    "trophic",
    "trophic_differences",
    "trophic_incoherence_parameter",
    "trophic_levels",
    "voterank",
    "voterank_alg",
]
