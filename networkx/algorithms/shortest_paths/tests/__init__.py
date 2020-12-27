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
        "test_astar",
        "test_dense",
        "test_dense_numpy",
        "test_generic",
        "test_unweighted",
        "test_weighted",
    },
    submod_attrs={
        "test_astar": [
            "TestAStar",
        ],
        "test_dense": [
            "TestFloyd",
        ],
        "test_dense_numpy": [
            "TestFloydNumpy",
            "np",
        ],
        "test_generic": [
            "TestAverageShortestPathLength",
            "TestAverageShortestPathLengthNumpy",
            "TestGenericPath",
            "validate_grid_path",
        ],
        "test_unweighted": [
            "TestUnweightedPath",
            "validate_grid_path",
        ],
        "test_weighted": [
            "TestBellmanFordAndGoldbergRadzik",
            "TestDijkstraPathLength",
            "TestJohnsonAlgorithm",
            "TestMultiSourceDijkstra",
            "TestWeightedPath",
            "WeightedTestBase",
            "validate_length_path",
            "validate_path",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestAStar",
    "TestAverageShortestPathLength",
    "TestAverageShortestPathLengthNumpy",
    "TestBellmanFordAndGoldbergRadzik",
    "TestDijkstraPathLength",
    "TestFloyd",
    "TestFloydNumpy",
    "TestGenericPath",
    "TestJohnsonAlgorithm",
    "TestMultiSourceDijkstra",
    "TestUnweightedPath",
    "TestWeightedPath",
    "WeightedTestBase",
    "np",
    "test_astar",
    "test_dense",
    "test_dense_numpy",
    "test_generic",
    "test_unweighted",
    "test_weighted",
    "validate_grid_path",
    "validate_length_path",
    "validate_path",
]
