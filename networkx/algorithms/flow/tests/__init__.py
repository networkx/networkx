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
        "test_gomory_hu",
        "test_maxflow",
        "test_maxflow_large_graph",
        "test_mincost",
    },
    submod_attrs={
        "test_gomory_hu": [
            "TestGomoryHuTree",
            "flow_funcs",
        ],
        "test_maxflow": [
            "TestCutoff",
            "TestMaxFlowMinCutInterface",
            "TestMaxflowMinCutCommon",
            "all_funcs",
            "compare_flows_and_cuts",
            "compute_cutset",
            "flow_funcs",
            "flow_value_funcs",
            "interface_funcs",
            "max_min_funcs",
            "test_preflow_push_global_relabel_freq",
            "test_preflow_push_makes_enough_space",
            "test_shortest_augmenting_path_two_phase",
            "validate_cuts",
            "validate_flows",
        ],
        "test_maxflow_large_graph": [
            "TestMaxflowLargeGraph",
            "flow_funcs",
            "gen_pyramid",
            "read_graph",
            "validate_flows",
        ],
        "test_mincost": [
            "TestMinCostFlow",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestCutoff",
    "TestGomoryHuTree",
    "TestMaxFlowMinCutInterface",
    "TestMaxflowLargeGraph",
    "TestMaxflowMinCutCommon",
    "TestMinCostFlow",
    "all_funcs",
    "compare_flows_and_cuts",
    "compute_cutset",
    "flow_funcs",
    "flow_value_funcs",
    "gen_pyramid",
    "interface_funcs",
    "max_min_funcs",
    "read_graph",
    "test_gomory_hu",
    "test_maxflow",
    "test_maxflow_large_graph",
    "test_mincost",
    "test_preflow_push_global_relabel_freq",
    "test_preflow_push_makes_enough_space",
    "test_shortest_augmenting_path_two_phase",
    "validate_cuts",
    "validate_flows",
]
