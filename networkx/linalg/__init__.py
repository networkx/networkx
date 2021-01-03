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
        "algebraicconnectivity",
        "attrmatrix",
        "bethehessianmatrix",
        "graphmatrix",
        "laplacianmatrix",
        "modularitymatrix",
        "spectrum",
        "tests",
    },
    submod_attrs={
        "algebraicconnectivity": [
            "algebraic_connectivity",
            "fiedler_vector",
            "spectral_ordering",
        ],
        "attrmatrix": [
            "attr_matrix",
            "attr_sparse_matrix",
        ],
        "bethehessianmatrix": [
            "bethe_hessian_matrix",
        ],
        "graphmatrix": [
            "adj_matrix",
            "adjacency_matrix",
            "incidence_matrix",
        ],
        "laplacianmatrix": [
            "directed_combinatorial_laplacian_matrix",
            "directed_laplacian_matrix",
            "laplacian_matrix",
            "normalized_laplacian_matrix",
        ],
        "modularitymatrix": [
            "directed_modularity_matrix",
            "modularity_matrix",
        ],
        "spectrum": [
            "adjacency_spectrum",
            "bethe_hessian_spectrum",
            "laplacian_spectrum",
            "modularity_spectrum",
            "normalized_laplacian_spectrum",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "adj_matrix",
    "adjacency_matrix",
    "adjacency_spectrum",
    "algebraic_connectivity",
    "algebraicconnectivity",
    "attr_matrix",
    "attr_sparse_matrix",
    "attrmatrix",
    "bethe_hessian_matrix",
    "bethe_hessian_spectrum",
    "bethehessianmatrix",
    "directed_combinatorial_laplacian_matrix",
    "directed_laplacian_matrix",
    "directed_modularity_matrix",
    "fiedler_vector",
    "graphmatrix",
    "incidence_matrix",
    "laplacian_matrix",
    "laplacian_spectrum",
    "laplacianmatrix",
    "modularity_matrix",
    "modularity_spectrum",
    "modularitymatrix",
    "normalized_laplacian_matrix",
    "normalized_laplacian_spectrum",
    "spectral_ordering",
    "spectrum",
    "tests",
]
