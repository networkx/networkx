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
        "historical_tests",
        "test_coreviews",
        "test_digraph",
        "test_digraph_historical",
        "test_filters",
        "test_function",
        "test_graph",
        "test_graph_historical",
        "test_graphviews",
        "test_multidigraph",
        "test_multigraph",
        "test_ordered",
        "test_reportviews",
        "test_special",
        "test_subgraphviews",
    },
    submod_attrs={
        "historical_tests": [
            "HistoricalTests",
        ],
        "test_coreviews": [
            "TestAdjacencyView",
            "TestAtlasView",
            "TestFilteredGraphs",
            "TestMultiAdjacencyView",
            "TestUnionAdjacency",
            "TestUnionAtlas",
            "TestUnionMultiAdjacency",
            "TestUnionMultiInner",
        ],
        "test_digraph": [
            "BaseAttrDiGraphTester",
            "BaseDiGraphTester",
            "TestDiGraph",
            "TestEdgeSubgraph",
        ],
        "test_digraph_historical": [
            "TestDiGraphHistorical",
        ],
        "test_filters": [
            "TestFilterFactory",
        ],
        "test_function": [
            "TestCommonNeighbors",
            "TestFunction",
            "test_get_edge_attributes",
            "test_get_node_attributes",
            "test_is_empty",
            "test_ispath",
            "test_pathweight",
            "test_restricted_view",
            "test_restricted_view_multi",
            "test_selfloop_edges_attr",
            "test_selfloop_edges_multi_with_data_and_keys",
            "test_selfloops",
            "test_selfloops_removal",
            "test_selfloops_removal_multi",
            "test_set_edge_attributes",
            "test_set_edge_attributes_ignores_extra_edges",
            "test_set_edge_attributes_multi",
            "test_set_edge_attributes_multi_ignores_extra_edges",
            "test_set_node_attributes",
            "test_set_node_attributes_ignores_extra_nodes",
        ],
        "test_graph": [
            "BaseAttrGraphTester",
            "BaseGraphTester",
            "TestEdgeSubgraph",
            "TestGraph",
        ],
        "test_graph_historical": [
            "TestGraphHistorical",
        ],
        "test_graphviews": [
            "TestChainsOfViews",
            "TestMultiReverseView",
            "TestReverseView",
            "TestToDirected",
            "TestToUndirected",
            "test_generic_multitype",
        ],
        "test_multidigraph": [
            "BaseMultiDiGraphTester",
            "TestEdgeSubgraph",
            "TestMultiDiGraph",
        ],
        "test_multigraph": [
            "BaseMultiGraphTester",
            "TestEdgeSubgraph",
            "TestMultiGraph",
            "test_multigraph_add_edges_from_four_tuple_misordered",
        ],
        "test_ordered": [
            "TestOrdered",
            "TestOrderedFeatures",
        ],
        "test_reportviews": [
            "TestDegreeView",
            "TestDiDegreeView",
            "TestDiMultiDegreeView",
            "TestEdgeDataView",
            "TestEdgeView",
            "TestInDegreeView",
            "TestInEdgeDataView",
            "TestInEdgeView",
            "TestInMultiDegreeView",
            "TestInMultiEdgeDataView",
            "TestInMultiEdgeView",
            "TestMultiDegreeView",
            "TestMultiEdgeDataView",
            "TestMultiEdgeView",
            "TestNodeDataView",
            "TestNodeDataViewDefaultSetOps",
            "TestNodeDataViewSetOps",
            "TestNodeView",
            "TestNodeViewSetOps",
            "TestOutDegreeView",
            "TestOutEdgeDataView",
            "TestOutEdgeView",
            "TestOutMultiDegreeView",
            "TestOutMultiEdgeDataView",
            "TestOutMultiEdgeView",
            "test_nodedataview_unhashable",
            "test_slicing_reportviews",
        ],
        "test_special": [
            "TestOrderedDiGraph",
            "TestOrderedGraph",
            "TestOrderedMultiDiGraph",
            "TestOrderedMultiGraph",
            "TestSpecialDiGraph",
            "TestSpecialGraph",
            "TestSpecialMultiDiGraph",
            "TestSpecialMultiGraph",
            "TestThinDiGraph",
            "TestThinGraph",
            "test_factories",
        ],
        "test_subgraphviews": [
            "TestEdgeSubGraph",
            "TestInducedSubGraph",
            "TestMultiDiGraphView",
            "TestMultiGraphView",
            "TestSubDiGraphView",
            "TestSubGraphView",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "BaseAttrDiGraphTester",
    "BaseAttrGraphTester",
    "BaseDiGraphTester",
    "BaseGraphTester",
    "BaseMultiDiGraphTester",
    "BaseMultiGraphTester",
    "HistoricalTests",
    "TestAdjacencyView",
    "TestAtlasView",
    "TestChainsOfViews",
    "TestCommonNeighbors",
    "TestDegreeView",
    "TestDiDegreeView",
    "TestDiGraph",
    "TestDiGraphHistorical",
    "TestDiMultiDegreeView",
    "TestEdgeDataView",
    "TestEdgeSubGraph",
    "TestEdgeSubgraph",
    "TestEdgeView",
    "TestFilterFactory",
    "TestFilteredGraphs",
    "TestFunction",
    "TestGraph",
    "TestGraphHistorical",
    "TestInDegreeView",
    "TestInEdgeDataView",
    "TestInEdgeView",
    "TestInMultiDegreeView",
    "TestInMultiEdgeDataView",
    "TestInMultiEdgeView",
    "TestInducedSubGraph",
    "TestMultiAdjacencyView",
    "TestMultiDegreeView",
    "TestMultiDiGraph",
    "TestMultiDiGraphView",
    "TestMultiEdgeDataView",
    "TestMultiEdgeView",
    "TestMultiGraph",
    "TestMultiGraphView",
    "TestMultiReverseView",
    "TestNodeDataView",
    "TestNodeDataViewDefaultSetOps",
    "TestNodeDataViewSetOps",
    "TestNodeView",
    "TestNodeViewSetOps",
    "TestOrdered",
    "TestOrderedDiGraph",
    "TestOrderedFeatures",
    "TestOrderedGraph",
    "TestOrderedMultiDiGraph",
    "TestOrderedMultiGraph",
    "TestOutDegreeView",
    "TestOutEdgeDataView",
    "TestOutEdgeView",
    "TestOutMultiDegreeView",
    "TestOutMultiEdgeDataView",
    "TestOutMultiEdgeView",
    "TestReverseView",
    "TestSpecialDiGraph",
    "TestSpecialGraph",
    "TestSpecialMultiDiGraph",
    "TestSpecialMultiGraph",
    "TestSubDiGraphView",
    "TestSubGraphView",
    "TestThinDiGraph",
    "TestThinGraph",
    "TestToDirected",
    "TestToUndirected",
    "TestUnionAdjacency",
    "TestUnionAtlas",
    "TestUnionMultiAdjacency",
    "TestUnionMultiInner",
    "historical_tests",
    "test_coreviews",
    "test_digraph",
    "test_digraph_historical",
    "test_factories",
    "test_filters",
    "test_function",
    "test_generic_multitype",
    "test_get_edge_attributes",
    "test_get_node_attributes",
    "test_graph",
    "test_graph_historical",
    "test_graphviews",
    "test_is_empty",
    "test_ispath",
    "test_multidigraph",
    "test_multigraph",
    "test_multigraph_add_edges_from_four_tuple_misordered",
    "test_nodedataview_unhashable",
    "test_ordered",
    "test_pathweight",
    "test_reportviews",
    "test_restricted_view",
    "test_restricted_view_multi",
    "test_selfloop_edges_attr",
    "test_selfloop_edges_multi_with_data_and_keys",
    "test_selfloops",
    "test_selfloops_removal",
    "test_selfloops_removal_multi",
    "test_set_edge_attributes",
    "test_set_edge_attributes_ignores_extra_edges",
    "test_set_edge_attributes_multi",
    "test_set_edge_attributes_multi_ignores_extra_edges",
    "test_set_node_attributes",
    "test_set_node_attributes_ignores_extra_nodes",
    "test_slicing_reportviews",
    "test_special",
    "test_subgraphviews",
]
