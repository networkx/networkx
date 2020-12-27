"""Functions for computing and measuring community structure.

The functions in this class are not imported into the top-level
:mod:`networkx` namespace. You can access these functions by importing
the :mod:`networkx.algorithms.community` module, then accessing the
functions as attributes of ``community``. For example::

    >>> from networkx.algorithms import community
    >>> G = nx.barbell_graph(5, 1)
    >>> communities_generator = community.girvan_newman(G)
    >>> top_level_communities = next(communities_generator)
    >>> next_level_communities = next(communities_generator)
    >>> sorted(map(sorted, next_level_communities))
    [[0, 1, 2, 3, 4], [5], [6, 7, 8, 9, 10]]

"""
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
        "asyn_fluid",
        "centrality",
        "community_utils",
        "kclique",
        "kernighan_lin",
        "label_propagation",
        "lukes",
        "modularity_max",
        "quality",
        "tests",
    },
    submod_attrs={
        "asyn_fluid": [
            "asyn_fluidc",
        ],
        "centrality": [
            "girvan_newman",
        ],
        "community_utils": [
            "is_partition",
        ],
        "kclique": [
            "k_clique_communities",
        ],
        "kernighan_lin": [
            "kernighan_lin_bisection",
        ],
        "label_propagation": [
            "asyn_lpa_communities",
            "label_propagation_communities",
        ],
        "lukes": [
            "lukes_partitioning",
        ],
        "modularity_max": [
            "_naive_greedy_modularity_communities",
            "greedy_modularity_communities",
            "naive_greedy_modularity_communities",
        ],
        "quality": [
            "coverage",
            "modularity",
            "performance",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "_naive_greedy_modularity_communities",
    "asyn_fluid",
    "asyn_fluidc",
    "asyn_lpa_communities",
    "centrality",
    "community_utils",
    "coverage",
    "girvan_newman",
    "greedy_modularity_communities",
    "is_partition",
    "k_clique_communities",
    "kclique",
    "kernighan_lin",
    "kernighan_lin_bisection",
    "label_propagation",
    "label_propagation_communities",
    "lukes",
    "lukes_partitioning",
    "modularity",
    "modularity_max",
    "naive_greedy_modularity_communities",
    "performance",
    "quality",
    "tests",
]
