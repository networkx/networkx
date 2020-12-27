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
        "correlation",
        "mixing",
        "neighbor_degree",
        "pairs",
        "tests",
    },
    submod_attrs={
        "connectivity": [
            "average_degree_connectivity",
            "k_nearest_neighbors",
        ],
        "correlation": [
            "attribute_assortativity_coefficient",
            "degree_assortativity_coefficient",
            "degree_pearson_correlation_coefficient",
            "numeric_assortativity_coefficient",
        ],
        "mixing": [
            "attribute_mixing_dict",
            "attribute_mixing_matrix",
            "degree_mixing_dict",
            "degree_mixing_matrix",
            "mixing_dict",
            "numeric_mixing_matrix",
        ],
        "neighbor_degree": [
            "average_neighbor_degree",
        ],
        "pairs": [
            "node_attribute_xy",
            "node_degree_xy",
        ],
        "tests": [
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
    "attribute_assortativity_coefficient",
    "attribute_mixing_dict",
    "attribute_mixing_matrix",
    "average_degree_connectivity",
    "average_neighbor_degree",
    "base_test",
    "connectivity",
    "correlation",
    "degree_assortativity_coefficient",
    "degree_mixing_dict",
    "degree_mixing_matrix",
    "degree_pearson_correlation_coefficient",
    "k_nearest_neighbors",
    "mixing",
    "mixing_dict",
    "neighbor_degree",
    "node_attribute_xy",
    "node_degree_xy",
    "np",
    "numeric_assortativity_coefficient",
    "numeric_mixing_matrix",
    "pairs",
    "test_connectivity",
    "test_correlation",
    "test_mixing",
    "test_neighbor_degree",
    "test_pairs",
    "tests",
]
