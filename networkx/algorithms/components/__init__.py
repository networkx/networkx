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
        "attracting",
        "biconnected",
        "connected",
        "semiconnected",
        "strongly_connected",
        "tests",
        "weakly_connected",
    },
    submod_attrs={
        "attracting": [
            "attracting_components",
            "is_attracting_component",
            "number_attracting_components",
        ],
        "biconnected": [
            "articulation_points",
            "biconnected_component_edges",
            "biconnected_components",
            "is_biconnected",
        ],
        "connected": [
            "connected_components",
            "is_connected",
            "node_connected_component",
            "number_connected_components",
        ],
        "semiconnected": [
            "is_semiconnected",
        ],
        "strongly_connected": [
            "condensation",
            "is_strongly_connected",
            "kosaraju_strongly_connected_components",
            "number_strongly_connected_components",
            "strongly_connected_components",
            "strongly_connected_components_recursive",
        ],
        "tests": [
            "TestAttractingComponents",
            "TestConnected",
            "TestIsSemiconnected",
            "TestStronglyConnected",
            "TestWeaklyConnected",
            "assert_components_edges_equal",
            "assert_components_equal",
            "test_articulation_points_cycle",
            "test_articulation_points_repetitions",
            "test_attracting",
            "test_barbell",
            "test_biconnected",
            "test_biconnected_components1",
            "test_biconnected_components2",
            "test_biconnected_components_cycle",
            "test_biconnected_davis",
            "test_biconnected_eppstein",
            "test_biconnected_karate",
            "test_connected",
            "test_connected_raise",
            "test_empty_is_biconnected",
            "test_is_biconnected",
            "test_null_graph",
            "test_semiconnected",
            "test_strongly_connected",
            "test_weakly_connected",
        ],
        "weakly_connected": [
            "is_weakly_connected",
            "number_weakly_connected_components",
            "weakly_connected_components",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestAttractingComponents",
    "TestConnected",
    "TestIsSemiconnected",
    "TestStronglyConnected",
    "TestWeaklyConnected",
    "articulation_points",
    "assert_components_edges_equal",
    "assert_components_equal",
    "attracting",
    "attracting_components",
    "biconnected",
    "biconnected_component_edges",
    "biconnected_components",
    "condensation",
    "connected",
    "connected_components",
    "is_attracting_component",
    "is_biconnected",
    "is_connected",
    "is_semiconnected",
    "is_strongly_connected",
    "is_weakly_connected",
    "kosaraju_strongly_connected_components",
    "node_connected_component",
    "number_attracting_components",
    "number_connected_components",
    "number_strongly_connected_components",
    "number_weakly_connected_components",
    "semiconnected",
    "strongly_connected",
    "strongly_connected_components",
    "strongly_connected_components_recursive",
    "test_articulation_points_cycle",
    "test_articulation_points_repetitions",
    "test_attracting",
    "test_barbell",
    "test_biconnected",
    "test_biconnected_components1",
    "test_biconnected_components2",
    "test_biconnected_components_cycle",
    "test_biconnected_davis",
    "test_biconnected_eppstein",
    "test_biconnected_karate",
    "test_connected",
    "test_connected_raise",
    "test_empty_is_biconnected",
    "test_is_biconnected",
    "test_null_graph",
    "test_semiconnected",
    "test_strongly_connected",
    "test_weakly_connected",
    "tests",
    "weakly_connected",
    "weakly_connected_components",
]
