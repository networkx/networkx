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
        "base_test",
        "test_connectivity",
        "test_correlation",
        "test_mixing",
        "test_neighbor_degree",
        "test_pairs",
    },
    submod_attrs={
        "base_test": [
            "BaseTestAttributeMixing",
            "BaseTestDegreeMixing",
        ],
        "test_connectivity": [
            "TestNeighborConnectivity",
        ],
        "test_correlation": [
            "TestAttributeMixingCorrelation",
            "TestDegreeMixingCorrelation",
            "np",
        ],
        "test_mixing": [
            "TestAttributeMixingDict",
            "TestAttributeMixingMatrix",
            "TestDegreeMixingDict",
            "TestDegreeMixingMatrix",
            "np",
        ],
        "test_neighbor_degree": [
            "TestAverageNeighbor",
        ],
        "test_pairs": [
            "TestAttributeMixingXY",
            "TestDegreeMixingXY",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "BaseTestAttributeMixing",
    "BaseTestDegreeMixing",
    "TestAttributeMixingCorrelation",
    "TestAttributeMixingDict",
    "TestAttributeMixingMatrix",
    "TestAttributeMixingXY",
    "TestAverageNeighbor",
    "TestDegreeMixingCorrelation",
    "TestDegreeMixingDict",
    "TestDegreeMixingMatrix",
    "TestDegreeMixingXY",
    "TestNeighborConnectivity",
    "base_test",
    "np",
    "test_connectivity",
    "test_correlation",
    "test_mixing",
    "test_neighbor_degree",
    "test_pairs",
]
