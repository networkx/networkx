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
        "test_attracting",
        "test_biconnected",
        "test_connected",
        "test_semiconnected",
        "test_strongly_connected",
        "test_weakly_connected",
    },
    submod_attrs={
        "test_attracting": [
            "TestAttractingComponents",
        ],
        "test_biconnected": [
            "assert_components_edges_equal",
            "assert_components_equal",
            "test_articulation_points_cycle",
            "test_articulation_points_repetitions",
            "test_barbell",
            "test_biconnected_components1",
            "test_biconnected_components2",
            "test_biconnected_components_cycle",
            "test_biconnected_davis",
            "test_biconnected_eppstein",
            "test_biconnected_karate",
            "test_connected_raise",
            "test_empty_is_biconnected",
            "test_is_biconnected",
            "test_null_graph",
        ],
        "test_connected": [
            "TestConnected",
        ],
        "test_semiconnected": [
            "TestIsSemiconnected",
        ],
        "test_strongly_connected": [
            "TestStronglyConnected",
        ],
        "test_weakly_connected": [
            "TestWeaklyConnected",
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
]
