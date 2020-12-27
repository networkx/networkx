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
        "coreviews",
        "digraph",
        "filters",
        "function",
        "graph",
        "graphviews",
        "multidigraph",
        "multigraph",
        "ordered",
        "reportviews",
        "tests",
    },
    submod_attrs={
        "coreviews": [
            "AdjacencyView",
            "AtlasView",
            "FilterAdjacency",
            "FilterAtlas",
            "FilterMultiAdjacency",
            "FilterMultiInner",
            "MultiAdjacencyView",
            "UnionAdjacency",
            "UnionAtlas",
            "UnionMultiAdjacency",
            "UnionMultiInner",
        ],
        "digraph": [
            "DiGraph",
        ],
        "filters": [
            "hide_diedges",
            "hide_edges",
            "hide_multidiedges",
            "hide_multiedges",
            "hide_nodes",
            "no_filter",
            "show_diedges",
            "show_edges",
            "show_multidiedges",
            "show_multiedges",
            "show_nodes",
        ],
        "function": [
            "add_cycle",
            "add_path",
            "add_star",
            "all_neighbors",
            "common_neighbors",
            "create_empty_copy",
            "degree",
            "degree_histogram",
            "density",
            "edge_subgraph",
            "edges",
            "freeze",
            "get_edge_attributes",
            "get_node_attributes",
            "induced_subgraph",
            "info",
            "is_directed",
            "is_empty",
            "is_frozen",
            "is_negatively_weighted",
            "is_path",
            "is_weighted",
            "neighbors",
            "nodes",
            "nodes_with_selfloops",
            "non_edges",
            "non_neighbors",
            "number_of_edges",
            "number_of_nodes",
            "number_of_selfloops",
            "path_weight",
            "restricted_view",
            "reverse_view",
            "selfloop_edges",
            "set_edge_attributes",
            "set_node_attributes",
            "subgraph",
            "subgraph_view",
            "to_directed",
            "to_undirected",
        ],
        "graph": [
            "Graph",
        ],
        "graphviews": [
            "generic_graph_view",
            "reverse_view",
            "subgraph_view",
        ],
        "multidigraph": [
            "MultiDiGraph",
        ],
        "multigraph": [
            "MultiGraph",
        ],
        "ordered": [
            "OrderedDiGraph",
            "OrderedGraph",
            "OrderedMultiDiGraph",
            "OrderedMultiGraph",
        ],
        "reportviews": [
            "DegreeView",
            "DiDegreeView",
            "DiMultiDegreeView",
            "EdgeDataView",
            "EdgeView",
            "InDegreeView",
            "InEdgeDataView",
            "InEdgeView",
            "InMultiDegreeView",
            "InMultiEdgeDataView",
            "InMultiEdgeView",
            "MultiDegreeView",
            "MultiEdgeDataView",
            "MultiEdgeView",
            "NodeDataView",
            "NodeView",
            "OutDegreeView",
            "OutEdgeDataView",
            "OutEdgeView",
            "OutMultiDegreeView",
            "OutMultiEdgeDataView",
            "OutMultiEdgeView",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "AdjacencyView",
    "AtlasView",
    "DegreeView",
    "DiDegreeView",
    "DiGraph",
    "DiMultiDegreeView",
    "EdgeDataView",
    "EdgeView",
    "FilterAdjacency",
    "FilterAtlas",
    "FilterMultiAdjacency",
    "FilterMultiInner",
    "Graph",
    "InDegreeView",
    "InEdgeDataView",
    "InEdgeView",
    "InMultiDegreeView",
    "InMultiEdgeDataView",
    "InMultiEdgeView",
    "MultiAdjacencyView",
    "MultiDegreeView",
    "MultiDiGraph",
    "MultiEdgeDataView",
    "MultiEdgeView",
    "MultiGraph",
    "NodeDataView",
    "NodeView",
    "OrderedDiGraph",
    "OrderedGraph",
    "OrderedMultiDiGraph",
    "OrderedMultiGraph",
    "OutDegreeView",
    "OutEdgeDataView",
    "OutEdgeView",
    "OutMultiDegreeView",
    "OutMultiEdgeDataView",
    "OutMultiEdgeView",
    "UnionAdjacency",
    "UnionAtlas",
    "UnionMultiAdjacency",
    "UnionMultiInner",
    "add_cycle",
    "add_path",
    "add_star",
    "all_neighbors",
    "common_neighbors",
    "coreviews",
    "create_empty_copy",
    "degree",
    "degree_histogram",
    "density",
    "digraph",
    "edge_subgraph",
    "edges",
    "filters",
    "freeze",
    "function",
    "generic_graph_view",
    "get_edge_attributes",
    "get_node_attributes",
    "graph",
    "graphviews",
    "hide_diedges",
    "hide_edges",
    "hide_multidiedges",
    "hide_multiedges",
    "hide_nodes",
    "induced_subgraph",
    "info",
    "is_directed",
    "is_empty",
    "is_frozen",
    "is_negatively_weighted",
    "is_path",
    "is_weighted",
    "multidigraph",
    "multigraph",
    "neighbors",
    "no_filter",
    "nodes",
    "nodes_with_selfloops",
    "non_edges",
    "non_neighbors",
    "number_of_edges",
    "number_of_nodes",
    "number_of_selfloops",
    "ordered",
    "path_weight",
    "reportviews",
    "restricted_view",
    "reverse_view",
    "selfloop_edges",
    "set_edge_attributes",
    "set_node_attributes",
    "show_diedges",
    "show_edges",
    "show_multidiedges",
    "show_multiedges",
    "show_nodes",
    "subgraph",
    "subgraph_view",
    "tests",
    "to_directed",
    "to_undirected",
]
