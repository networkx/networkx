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
        "test_algebraic_connectivity",
        "test_attrmatrix",
        "test_bethehessian",
        "test_graphmatrix",
        "test_laplacian",
        "test_modularity",
        "test_spectrum",
    },
    submod_attrs={
        "test_algebraic_connectivity": [
            "TestAlgebraicConnectivity",
            "TestSpectralOrdering",
            "check_eigenvector",
            "methods",
            "np",
            "test_algebraic_connectivity_tracemin_chol",
            "test_fiedler_vector_tracemin_chol",
            "test_fiedler_vector_tracemin_unknown",
            "test_spectral_ordering_tracemin_chol",
        ],
        "test_attrmatrix": [
            "np",
            "test_attr_matrix",
            "test_attr_matrix_directed",
            "test_attr_matrix_multigraph",
            "test_attr_sparse_matrix",
            "test_attr_sparse_matrix_directed",
        ],
        "test_bethehessian": [
            "TestBetheHessian",
            "np",
        ],
        "test_graphmatrix": [
            "TestGraphMatrix",
            "np",
            "test_incidence_matrix_simple",
        ],
        "test_laplacian": [
            "TestLaplacian",
            "np",
        ],
        "test_modularity": [
            "TestModularity",
            "np",
        ],
        "test_spectrum": [
            "TestSpectrum",
            "np",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestAlgebraicConnectivity",
    "TestBetheHessian",
    "TestGraphMatrix",
    "TestLaplacian",
    "TestModularity",
    "TestSpectralOrdering",
    "TestSpectrum",
    "check_eigenvector",
    "methods",
    "np",
    "test_algebraic_connectivity",
    "test_algebraic_connectivity_tracemin_chol",
    "test_attr_matrix",
    "test_attr_matrix_directed",
    "test_attr_matrix_multigraph",
    "test_attr_sparse_matrix",
    "test_attr_sparse_matrix_directed",
    "test_attrmatrix",
    "test_bethehessian",
    "test_fiedler_vector_tracemin_chol",
    "test_fiedler_vector_tracemin_unknown",
    "test_graphmatrix",
    "test_incidence_matrix_simple",
    "test_laplacian",
    "test_modularity",
    "test_spectral_ordering_tracemin_chol",
    "test_spectrum",
]
