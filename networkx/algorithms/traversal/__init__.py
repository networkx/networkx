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
        "beamsearch",
        "breadth_first_search",
        "depth_first_search",
        "edgebfs",
        "edgedfs",
        "tests",
    },
    submod_attrs={
        "beamsearch": [
            "bfs_beam_edges",
        ],
        "breadth_first_search": [
            "bfs_edges",
            "bfs_predecessors",
            "bfs_successors",
            "bfs_tree",
            "descendants_at_distance",
        ],
        "depth_first_search": [
            "dfs_edges",
            "dfs_labeled_edges",
            "dfs_postorder_nodes",
            "dfs_predecessors",
            "dfs_preorder_nodes",
            "dfs_successors",
            "dfs_tree",
        ],
        "edgebfs": [
            "edge_bfs",
        ],
        "edgedfs": [
            "edge_dfs",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "beamsearch",
    "bfs_beam_edges",
    "bfs_edges",
    "bfs_predecessors",
    "bfs_successors",
    "bfs_tree",
    "breadth_first_search",
    "depth_first_search",
    "descendants_at_distance",
    "dfs_edges",
    "dfs_labeled_edges",
    "dfs_postorder_nodes",
    "dfs_predecessors",
    "dfs_preorder_nodes",
    "dfs_successors",
    "dfs_tree",
    "edge_bfs",
    "edge_dfs",
    "edgebfs",
    "edgedfs",
    "tests",
]
