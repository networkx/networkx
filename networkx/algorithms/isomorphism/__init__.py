__private__ = ["tests"]

# FIXME: tree_isomorphism module with an attribute with the same name
# mkinit needs to fix that tree_isomorphism


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
        "ismags",
        "isomorph",
        "isomorphvf2",
        "matchhelpers",
        "temporalisomorphvf2",
        "tests",
        # "tree_isomorphism",
        "vf2userfunc",
    },
    submod_attrs={
        "ismags": [
            "ISMAGS",
        ],
        "isomorph": [
            "could_be_isomorphic",
            "fast_could_be_isomorphic",
            "faster_could_be_isomorphic",
            "is_isomorphic",
        ],
        "isomorphvf2": [
            "DiGraphMatcher",
            "GraphMatcher",
        ],
        "matchhelpers": [
            "categorical_edge_match",
            "categorical_multiedge_match",
            "categorical_node_match",
            "generic_edge_match",
            "generic_multiedge_match",
            "generic_node_match",
            "numerical_edge_match",
            "numerical_multiedge_match",
            "numerical_node_match",
        ],
        "temporalisomorphvf2": [
            "TimeRespectingDiGraphMatcher",
            "TimeRespectingGraphMatcher",
        ],
        "tree_isomorphism": [
            "rooted_tree_isomorphism",
            "tree_isomorphism",
        ],
        "vf2userfunc": [
            "DiGraphMatcher",
            "GraphMatcher",
            "MultiDiGraphMatcher",
            "MultiGraphMatcher",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "DiGraphMatcher",
    "GraphMatcher",
    "ISMAGS",
    "MultiDiGraphMatcher",
    "MultiGraphMatcher",
    "TimeRespectingDiGraphMatcher",
    "TimeRespectingGraphMatcher",
    "categorical_edge_match",
    "categorical_multiedge_match",
    "categorical_node_match",
    "could_be_isomorphic",
    "fast_could_be_isomorphic",
    "faster_could_be_isomorphic",
    "generic_edge_match",
    "generic_multiedge_match",
    "generic_node_match",
    "is_isomorphic",
    "ismags",
    "isomorph",
    "isomorphvf2",
    "matchhelpers",
    "numerical_edge_match",
    "numerical_multiedge_match",
    "numerical_node_match",
    "rooted_tree_isomorphism",
    "temporalisomorphvf2",
    "tests",
    "tree_isomorphism",
    "vf2userfunc",
]
