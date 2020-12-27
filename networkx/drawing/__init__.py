# graph drawing and interface to graphviz


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
        "layout",
        "nx_agraph",
        "nx_pydot",
        "nx_pylab",
        "tests",
    },
    submod_attrs={
        "layout": [
            "bipartite_layout",
            "circular_layout",
            "fruchterman_reingold_layout",
            "kamada_kawai_layout",
            "multipartite_layout",
            "planar_layout",
            "random_layout",
            "rescale_layout",
            "rescale_layout_dict",
            "shell_layout",
            "spectral_layout",
            "spiral_layout",
            "spring_layout",
        ],
        "nx_agraph": [
            "from_agraph",
            "graphviz_layout",
            "pygraphviz_layout",
            "read_dot",
            "to_agraph",
            "view_pygraphviz",
            "write_dot",
        ],
        "nx_pydot": [
            "from_pydot",
            "graphviz_layout",
            "pydot_layout",
            "read_dot",
            "to_pydot",
            "write_dot",
        ],
        "nx_pylab": [
            "draw",
            "draw_circular",
            "draw_kamada_kawai",
            "draw_networkx",
            "draw_networkx_edge_labels",
            "draw_networkx_edges",
            "draw_networkx_labels",
            "draw_networkx_nodes",
            "draw_planar",
            "draw_random",
            "draw_shell",
            "draw_spectral",
            "draw_spring",
        ],
        "tests": [
            "TestAGraph",
            "TestLayout",
            "TestPydot",
            "TestPylab",
            "mpl",
            "np",
            "plt",
            "pydot",
            "pygraphviz",
            "test_agraph",
            "test_apply_alpha",
            "test_draw_edges_min_source_target_margins",
            "test_draw_edges_warns_on_arrow_and_arrowstyle",
            "test_draw_edges_with_nodelist",
            "test_draw_nodes_missing_node_from_position",
            "test_layout",
            "test_nonzero_selfloop_with_single_edge_in_edgelist",
            "test_nonzero_selfloop_with_single_node",
            "test_pydot",
            "test_pylab",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestAGraph",
    "TestLayout",
    "TestPydot",
    "TestPylab",
    "bipartite_layout",
    "circular_layout",
    "draw",
    "draw_circular",
    "draw_kamada_kawai",
    "draw_networkx",
    "draw_networkx_edge_labels",
    "draw_networkx_edges",
    "draw_networkx_labels",
    "draw_networkx_nodes",
    "draw_planar",
    "draw_random",
    "draw_shell",
    "draw_spectral",
    "draw_spring",
    "from_agraph",
    "from_pydot",
    "fruchterman_reingold_layout",
    "graphviz_layout",
    "kamada_kawai_layout",
    "layout",
    "mpl",
    "multipartite_layout",
    "np",
    "nx_agraph",
    "nx_pydot",
    "nx_pylab",
    "planar_layout",
    "plt",
    "pydot",
    "pydot_layout",
    "pygraphviz",
    "pygraphviz_layout",
    "random_layout",
    "read_dot",
    "rescale_layout",
    "rescale_layout_dict",
    "shell_layout",
    "spectral_layout",
    "spiral_layout",
    "spring_layout",
    "test_agraph",
    "test_apply_alpha",
    "test_draw_edges_min_source_target_margins",
    "test_draw_edges_warns_on_arrow_and_arrowstyle",
    "test_draw_edges_with_nodelist",
    "test_draw_nodes_missing_node_from_position",
    "test_layout",
    "test_nonzero_selfloop_with_single_edge_in_edgelist",
    "test_nonzero_selfloop_with_single_node",
    "test_pydot",
    "test_pylab",
    "tests",
    "to_agraph",
    "to_pydot",
    "view_pygraphviz",
    "write_dot",
]
