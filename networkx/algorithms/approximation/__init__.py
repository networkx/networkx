"""Approximations of graph properties and Heuristic functions for optimization
problems.

    .. warning:: The approximation submodule is not imported in the top-level
        ``networkx``.

    These functions can be imported with
    ``from networkx.algorithms import approximation``.

"""

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
        "clique",
        "clustering_coefficient",
        "connectivity",
        "dominating_set",
        "independent_set",
        "kcomponents",
        "matching",
        "maxcut",
        "ramsey",
        "steinertree",
        "tests",
        "treewidth",
        "vertex_cover",
    },
    submod_attrs={
        "clique": [
            "clique_removal",
            "large_clique_size",
            "max_clique",
        ],
        "clustering_coefficient": [
            "average_clustering",
        ],
        "connectivity": [
            "all_pairs_node_connectivity",
            "local_node_connectivity",
            "node_connectivity",
        ],
        "dominating_set": [
            "min_edge_dominating_set",
            "min_weighted_dominating_set",
        ],
        "independent_set": [
            "maximum_independent_set",
        ],
        "kcomponents": [
            "k_components",
        ],
        "matching": [
            "min_maximal_matching",
        ],
        "maxcut": [
            "one_exchange",
            "randomized_partitioning",
        ],
        "ramsey": [
            "ramsey_R2",
        ],
        "steinertree": [
            "metric_closure",
            "steiner_tree",
        ],
        "treewidth": [
            "treewidth_min_degree",
            "treewidth_min_fill_in",
        ],
        "vertex_cover": [
            "min_weighted_vertex_cover",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "all_pairs_node_connectivity",
    "average_clustering",
    "clique",
    "clique_removal",
    "clustering_coefficient",
    "connectivity",
    "dominating_set",
    "independent_set",
    "k_components",
    "kcomponents",
    "large_clique_size",
    "local_node_connectivity",
    "matching",
    "max_clique",
    "maxcut",
    "maximum_independent_set",
    "metric_closure",
    "min_edge_dominating_set",
    "min_maximal_matching",
    "min_weighted_dominating_set",
    "min_weighted_vertex_cover",
    "node_connectivity",
    "one_exchange",
    "ramsey",
    "ramsey_R2",
    "randomized_partitioning",
    "steiner_tree",
    "steinertree",
    "tests",
    "treewidth",
    "treewidth_min_degree",
    "treewidth_min_fill_in",
    "vertex_cover",
]
