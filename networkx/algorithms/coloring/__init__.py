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
        "equitable_coloring",
        "greedy_coloring",
        "greedy_coloring_with_interchange",
        "tests",
    },
    submod_attrs={
        "equitable_coloring": [
            "equitable_color",
        ],
        "greedy_coloring": [
            "greedy_color",
            "strategy_connected_sequential",
            "strategy_connected_sequential_bfs",
            "strategy_connected_sequential_dfs",
            "strategy_independent_set",
            "strategy_largest_first",
            "strategy_random_sequential",
            "strategy_saturation_largest_first",
            "strategy_smallest_last",
        ],
        "greedy_coloring_with_interchange": [
            "greedy_coloring_with_interchange",
        ],
        "tests": [
            "ALL_STRATEGIES",
            "BASIC_TEST_CASES",
            "INTERCHANGE_INVALID",
            "SPECIAL_TEST_CASES",
            "TestColoring",
            "check_state",
            "cs_shc",
            "dict_to_sets",
            "disconnected",
            "empty_graph",
            "gis_hc",
            "gis_shc",
            "is_coloring",
            "is_equitable",
            "lf_hc",
            "lf_shc",
            "lfi_hc",
            "lfi_shc",
            "make_params_from_graph",
            "max_degree",
            "one_node_graph",
            "rs_shc",
            "rsi_shc",
            "sl_hc",
            "sl_shc",
            "slf_hc",
            "slf_shc",
            "sli_hc",
            "sli_shc",
            "test_coloring",
            "three_node_clique",
            "two_node_graph",
            "verify_coloring",
            "verify_length",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "ALL_STRATEGIES",
    "BASIC_TEST_CASES",
    "INTERCHANGE_INVALID",
    "SPECIAL_TEST_CASES",
    "TestColoring",
    "check_state",
    "cs_shc",
    "dict_to_sets",
    "disconnected",
    "empty_graph",
    "equitable_color",
    "equitable_coloring",
    "gis_hc",
    "gis_shc",
    "greedy_color",
    "greedy_coloring",
    "greedy_coloring_with_interchange",
    "is_coloring",
    "is_equitable",
    "lf_hc",
    "lf_shc",
    "lfi_hc",
    "lfi_shc",
    "make_params_from_graph",
    "max_degree",
    "one_node_graph",
    "rs_shc",
    "rsi_shc",
    "sl_hc",
    "sl_shc",
    "slf_hc",
    "slf_shc",
    "sli_hc",
    "sli_shc",
    "strategy_connected_sequential",
    "strategy_connected_sequential_bfs",
    "strategy_connected_sequential_dfs",
    "strategy_independent_set",
    "strategy_largest_first",
    "strategy_random_sequential",
    "strategy_saturation_largest_first",
    "strategy_smallest_last",
    "test_coloring",
    "tests",
    "three_node_clique",
    "two_node_graph",
    "verify_coloring",
    "verify_length",
]
