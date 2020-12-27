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
        "astar",
        "dense",
        "generic",
        "tests",
        "unweighted",
        "weighted",
    },
    submod_attrs={
        "astar": [
            "astar_path",
            "astar_path_length",
        ],
        "dense": [
            "floyd_warshall",
            "floyd_warshall_numpy",
            "floyd_warshall_predecessor_and_distance",
            "reconstruct_path",
        ],
        "generic": [
            "all_shortest_paths",
            "average_shortest_path_length",
            "has_path",
            "shortest_path",
            "shortest_path_length",
        ],
        "unweighted": [
            "all_pairs_shortest_path",
            "all_pairs_shortest_path_length",
            "bidirectional_shortest_path",
            "predecessor",
            "single_source_shortest_path",
            "single_source_shortest_path_length",
            "single_target_shortest_path",
            "single_target_shortest_path_length",
        ],
        "weighted": [
            "all_pairs_bellman_ford_path",
            "all_pairs_bellman_ford_path_length",
            "all_pairs_dijkstra",
            "all_pairs_dijkstra_path",
            "all_pairs_dijkstra_path_length",
            "bellman_ford_path",
            "bellman_ford_path_length",
            "bellman_ford_predecessor_and_distance",
            "bidirectional_dijkstra",
            "dijkstra_path",
            "dijkstra_path_length",
            "dijkstra_predecessor_and_distance",
            "goldberg_radzik",
            "johnson",
            "multi_source_dijkstra",
            "multi_source_dijkstra_path",
            "multi_source_dijkstra_path_length",
            "negative_edge_cycle",
            "single_source_bellman_ford",
            "single_source_bellman_ford_path",
            "single_source_bellman_ford_path_length",
            "single_source_dijkstra",
            "single_source_dijkstra_path",
            "single_source_dijkstra_path_length",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "all_pairs_bellman_ford_path",
    "all_pairs_bellman_ford_path_length",
    "all_pairs_dijkstra",
    "all_pairs_dijkstra_path",
    "all_pairs_dijkstra_path_length",
    "all_pairs_shortest_path",
    "all_pairs_shortest_path_length",
    "all_shortest_paths",
    "astar",
    "astar_path",
    "astar_path_length",
    "average_shortest_path_length",
    "bellman_ford_path",
    "bellman_ford_path_length",
    "bellman_ford_predecessor_and_distance",
    "bidirectional_dijkstra",
    "bidirectional_shortest_path",
    "dense",
    "dijkstra_path",
    "dijkstra_path_length",
    "dijkstra_predecessor_and_distance",
    "floyd_warshall",
    "floyd_warshall_numpy",
    "floyd_warshall_predecessor_and_distance",
    "generic",
    "goldberg_radzik",
    "has_path",
    "johnson",
    "multi_source_dijkstra",
    "multi_source_dijkstra_path",
    "multi_source_dijkstra_path_length",
    "negative_edge_cycle",
    "predecessor",
    "reconstruct_path",
    "shortest_path",
    "shortest_path_length",
    "single_source_bellman_ford",
    "single_source_bellman_ford_path",
    "single_source_bellman_ford_path_length",
    "single_source_dijkstra",
    "single_source_dijkstra_path",
    "single_source_dijkstra_path_length",
    "single_source_shortest_path",
    "single_source_shortest_path_length",
    "single_target_shortest_path",
    "single_target_shortest_path_length",
    "tests",
    "unweighted",
    "weighted",
]
