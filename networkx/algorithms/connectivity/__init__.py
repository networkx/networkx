"""Connectivity and cut algorithms
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
        "connectivity",
        "cuts",
        "disjoint_paths",
        "edge_augmentation",
        "edge_kcomponents",
        "kcomponents",
        "kcutsets",
        "stoerwagner",
        "tests",
        "utils",
    },
    submod_attrs={
        "connectivity": [
            "all_pairs_node_connectivity",
            "average_node_connectivity",
            "edge_connectivity",
            "local_edge_connectivity",
            "local_node_connectivity",
            "node_connectivity",
        ],
        "cuts": [
            "minimum_edge_cut",
            "minimum_node_cut",
            "minimum_st_edge_cut",
            "minimum_st_node_cut",
        ],
        "disjoint_paths": [
            "edge_disjoint_paths",
            "node_disjoint_paths",
        ],
        "edge_augmentation": [
            "is_k_edge_connected",
            "is_locally_k_edge_connected",
            "k_edge_augmentation",
        ],
        "edge_kcomponents": [
            "EdgeComponentAuxGraph",
            "bridge_components",
            "k_edge_components",
            "k_edge_subgraphs",
        ],
        "kcomponents": [
            "k_components",
        ],
        "kcutsets": [
            "all_node_cuts",
        ],
        "stoerwagner": [
            "stoer_wagner",
        ],
        "utils": [
            "build_auxiliary_edge_connectivity",
            "build_auxiliary_node_connectivity",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "EdgeComponentAuxGraph",
    "all_node_cuts",
    "all_pairs_node_connectivity",
    "average_node_connectivity",
    "bridge_components",
    "build_auxiliary_edge_connectivity",
    "build_auxiliary_node_connectivity",
    "connectivity",
    "cuts",
    "disjoint_paths",
    "edge_augmentation",
    "edge_connectivity",
    "edge_disjoint_paths",
    "edge_kcomponents",
    "is_k_edge_connected",
    "is_locally_k_edge_connected",
    "k_components",
    "k_edge_augmentation",
    "k_edge_components",
    "k_edge_subgraphs",
    "kcomponents",
    "kcutsets",
    "local_edge_connectivity",
    "local_node_connectivity",
    "minimum_edge_cut",
    "minimum_node_cut",
    "minimum_st_edge_cut",
    "minimum_st_node_cut",
    "node_connectivity",
    "node_disjoint_paths",
    "stoer_wagner",
    "stoerwagner",
    "tests",
    "utils",
]
