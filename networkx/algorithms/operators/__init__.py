__private__ = ['tests']


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
        "all",
        "binary",
        "product",
        "tests",
        "unary",
    },
    submod_attrs={
        "all": [
            "compose_all",
            "disjoint_union_all",
            "intersection_all",
            "union_all",
        ],
        "binary": [
            "compose",
            "difference",
            "disjoint_union",
            "full_join",
            "intersection",
            "symmetric_difference",
            "union",
        ],
        "product": [
            "cartesian_product",
            "lexicographic_product",
            "power",
            "rooted_product",
            "strong_product",
            "tensor_product",
        ],
        "unary": [
            "complement",
            "reverse",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "all",
    "binary",
    "cartesian_product",
    "complement",
    "compose",
    "compose_all",
    "difference",
    "disjoint_union",
    "disjoint_union_all",
    "full_join",
    "intersection",
    "intersection_all",
    "lexicographic_product",
    "power",
    "product",
    "reverse",
    "rooted_product",
    "strong_product",
    "symmetric_difference",
    "tensor_product",
    "tests",
    "unary",
    "union",
    "union_all",
]
