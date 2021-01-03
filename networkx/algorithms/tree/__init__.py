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
        "branchings",
        "coding",
        "decomposition",
        "mst",
        "operations",
        "recognition",
        "tests",
    },
    submod_attrs={
        "branchings": [
            "Edmonds",
            "branching_weight",
            "greedy_branching",
            "maximum_branching",
            "maximum_spanning_arborescence",
            "minimum_branching",
            "minimum_spanning_arborescence",
        ],
        "coding": [
            "NotATree",
            "from_nested_tuple",
            "from_prufer_sequence",
            "to_nested_tuple",
            "to_prufer_sequence",
        ],
        "decomposition": [
            "junction_tree",
        ],
        "mst": [
            "maximum_spanning_edges",
            "maximum_spanning_tree",
            "minimum_spanning_edges",
            "minimum_spanning_tree",
        ],
        "operations": [
            "join",
        ],
        "recognition": [
            "is_arborescence",
            "is_branching",
            "is_forest",
            "is_tree",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "Edmonds",
    "NotATree",
    "branching_weight",
    "branchings",
    "coding",
    "decomposition",
    "from_nested_tuple",
    "from_prufer_sequence",
    "greedy_branching",
    "is_arborescence",
    "is_branching",
    "is_forest",
    "is_tree",
    "join",
    "junction_tree",
    "maximum_branching",
    "maximum_spanning_arborescence",
    "maximum_spanning_edges",
    "maximum_spanning_tree",
    "minimum_branching",
    "minimum_spanning_arborescence",
    "minimum_spanning_edges",
    "minimum_spanning_tree",
    "mst",
    "operations",
    "recognition",
    "tests",
    "to_nested_tuple",
    "to_prufer_sequence",
]
