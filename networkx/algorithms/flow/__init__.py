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
        "boykovkolmogorov",
        "capacityscaling",
        "dinitz_alg",
        "edmondskarp",
        "gomory_hu",
        "maxflow",
        "mincost",
        "networksimplex",
        "preflowpush",
        "shortestaugmentingpath",
        "tests",
        "utils",
    },
    submod_attrs={
        "boykovkolmogorov": [
            "boykov_kolmogorov",
        ],
        "capacityscaling": [
            "capacity_scaling",
        ],
        "dinitz_alg": [
            "dinitz",
        ],
        "edmondskarp": [
            "edmonds_karp",
        ],
        "gomory_hu": [
            "gomory_hu_tree",
        ],
        "maxflow": [
            "maximum_flow",
            "maximum_flow_value",
            "minimum_cut",
            "minimum_cut_value",
        ],
        "mincost": [
            "cost_of_flow",
            "max_flow_min_cost",
            "min_cost_flow",
            "min_cost_flow_cost",
        ],
        "networksimplex": [
            "network_simplex",
        ],
        "preflowpush": [
            "preflow_push",
        ],
        "shortestaugmentingpath": [
            "shortest_augmenting_path",
        ],
        "utils": [
            "CurrentEdge",
            "GlobalRelabelThreshold",
            "Level",
            "build_flow_dict",
            "build_residual_network",
            "detect_unboundedness",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "CurrentEdge",
    "GlobalRelabelThreshold",
    "Level",
    "boykov_kolmogorov",
    "boykovkolmogorov",
    "build_flow_dict",
    "build_residual_network",
    "capacity_scaling",
    "capacityscaling",
    "cost_of_flow",
    "detect_unboundedness",
    "dinitz",
    "dinitz_alg",
    "edmonds_karp",
    "edmondskarp",
    "gomory_hu",
    "gomory_hu_tree",
    "max_flow_min_cost",
    "maxflow",
    "maximum_flow",
    "maximum_flow_value",
    "min_cost_flow",
    "min_cost_flow_cost",
    "mincost",
    "minimum_cut",
    "minimum_cut_value",
    "network_simplex",
    "networksimplex",
    "preflow_push",
    "preflowpush",
    "shortest_augmenting_path",
    "shortestaugmentingpath",
    "tests",
    "utils",
]
