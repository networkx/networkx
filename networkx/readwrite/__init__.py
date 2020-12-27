"""
A package for reading and writing graphs in various formats.

"""


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
        "adjlist",
        "edgelist",
        "gexf",
        "gml",
        "gpickle",
        "graph6",
        "graphml",
        "json_graph",
        "leda",
        "multiline_adjlist",
        "nx_shp",
        "nx_yaml",
        "p2g",
        "pajek",
        "sparse6",
        "tests",
        "text",
    },
    submod_attrs={
        "adjlist": [
            "generate_adjlist",
            "parse_adjlist",
            "read_adjlist",
            "write_adjlist",
        ],
        "edgelist": [
            "generate_edgelist",
            "parse_edgelist",
            "read_edgelist",
            "read_weighted_edgelist",
            "write_edgelist",
            "write_weighted_edgelist",
        ],
        "gexf": [
            "generate_gexf",
            "read_gexf",
            "relabel_gexf_graph",
            "write_gexf",
        ],
        "gml": [
            "generate_gml",
            "parse_gml",
            "read_gml",
            "write_gml",
        ],
        "gpickle": [
            "read_gpickle",
            "write_gpickle",
        ],
        "graph6": [
            "from_graph6_bytes",
            "read_graph6",
            "to_graph6_bytes",
            "write_graph6",
        ],
        "graphml": [
            "GraphMLReader",
            "GraphMLWriter",
            "generate_graphml",
            "parse_graphml",
            "read_graphml",
            "write_graphml",
            "write_graphml_lxml",
            "write_graphml_xml",
        ],
        "json_graph": [
            "TestAdjacency",
            "TestCytoscape",
            "TestJIT",
            "TestNodeLink",
            "TestTree",
            "adjacency",
            "adjacency_data",
            "adjacency_graph",
            "cytoscape",
            "cytoscape_data",
            "cytoscape_graph",
            "jit",
            "jit_data",
            "jit_graph",
            "node_link",
            "node_link_data",
            "node_link_graph",
            "test_adjacency",
            "test_cytoscape",
            "test_futurewarning",
            "test_jit",
            "test_node_link",
            "test_tree",
            "tests",
            "tree",
            "tree_data",
            "tree_graph",
        ],
        "leda": [
            "parse_leda",
            "read_leda",
        ],
        "multiline_adjlist": [
            "generate_multiline_adjlist",
            "parse_multiline_adjlist",
            "read_multiline_adjlist",
            "write_multiline_adjlist",
        ],
        "nx_shp": [
            "read_shp",
            "write_shp",
        ],
        "nx_yaml": [
            "read_yaml",
            "write_yaml",
        ],
        "p2g": [
            "parse_p2g",
            "read_p2g",
            "write_p2g",
        ],
        "pajek": [
            "generate_pajek",
            "parse_pajek",
            "read_pajek",
            "write_pajek",
        ],
        "sparse6": [
            "from_sparse6_bytes",
            "read_sparse6",
            "to_sparse6_bytes",
            "write_sparse6",
        ],
        "tests": [
            "BaseGraphML",
            "TestAdjlist",
            "TestEdgelist",
            "TestFromGraph6Bytes",
            "TestGEXF",
            "TestGpickle",
            "TestGraph",
            "TestGraph6Utils",
            "TestLEDA",
            "TestMissingAttrWrite",
            "TestMissingGeometry",
            "TestMultilineAdjlist",
            "TestP2G",
            "TestPajek",
            "TestPropertyLists",
            "TestReadGraph6",
            "TestReadGraphML",
            "TestShp",
            "TestSparseGraph6",
            "TestWriteGraph6",
            "TestWriteGraphML",
            "TestWriteSparse6",
            "TestXMLGraphML",
            "TestYaml",
            "byte_file",
            "ogr",
            "test_adjlist",
            "test_directed_multi_tree_forest",
            "test_directed_tree_str",
            "test_edgelist",
            "test_empty_graph",
            "test_forest_str_errors",
            "test_gexf",
            "test_gml",
            "test_gpickle",
            "test_graph6",
            "test_graphml",
            "test_leda",
            "test_overspecified_sources",
            "test_p2g",
            "test_pajek",
            "test_parse_edgelist",
            "test_read_shp_nofile",
            "test_shp",
            "test_sparse6",
            "test_text",
            "test_undirected_multi_tree_forest",
            "test_undirected_tree_str",
            "test_yaml",
            "yaml",
        ],
        "text": [
            "forest_str",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "BaseGraphML",
    "GraphMLReader",
    "GraphMLWriter",
    "TestAdjacency",
    "TestAdjlist",
    "TestCytoscape",
    "TestEdgelist",
    "TestFromGraph6Bytes",
    "TestGEXF",
    "TestGpickle",
    "TestGraph",
    "TestGraph6Utils",
    "TestJIT",
    "TestLEDA",
    "TestMissingAttrWrite",
    "TestMissingGeometry",
    "TestMultilineAdjlist",
    "TestNodeLink",
    "TestP2G",
    "TestPajek",
    "TestPropertyLists",
    "TestReadGraph6",
    "TestReadGraphML",
    "TestShp",
    "TestSparseGraph6",
    "TestTree",
    "TestWriteGraph6",
    "TestWriteGraphML",
    "TestWriteSparse6",
    "TestXMLGraphML",
    "TestYaml",
    "adjacency",
    "adjacency_data",
    "adjacency_graph",
    "adjlist",
    "byte_file",
    "cytoscape",
    "cytoscape_data",
    "cytoscape_graph",
    "edgelist",
    "forest_str",
    "from_graph6_bytes",
    "from_sparse6_bytes",
    "generate_adjlist",
    "generate_edgelist",
    "generate_gexf",
    "generate_gml",
    "generate_graphml",
    "generate_multiline_adjlist",
    "generate_pajek",
    "gexf",
    "gml",
    "gpickle",
    "graph6",
    "graphml",
    "jit",
    "jit_data",
    "jit_graph",
    "json_graph",
    "leda",
    "multiline_adjlist",
    "node_link",
    "node_link_data",
    "node_link_graph",
    "nx_shp",
    "nx_yaml",
    "ogr",
    "p2g",
    "pajek",
    "parse_adjlist",
    "parse_edgelist",
    "parse_gml",
    "parse_graphml",
    "parse_leda",
    "parse_multiline_adjlist",
    "parse_p2g",
    "parse_pajek",
    "read_adjlist",
    "read_edgelist",
    "read_gexf",
    "read_gml",
    "read_gpickle",
    "read_graph6",
    "read_graphml",
    "read_leda",
    "read_multiline_adjlist",
    "read_p2g",
    "read_pajek",
    "read_shp",
    "read_sparse6",
    "read_weighted_edgelist",
    "read_yaml",
    "relabel_gexf_graph",
    "sparse6",
    "test_adjacency",
    "test_adjlist",
    "test_cytoscape",
    "test_directed_multi_tree_forest",
    "test_directed_tree_str",
    "test_edgelist",
    "test_empty_graph",
    "test_forest_str_errors",
    "test_futurewarning",
    "test_gexf",
    "test_gml",
    "test_gpickle",
    "test_graph6",
    "test_graphml",
    "test_jit",
    "test_leda",
    "test_node_link",
    "test_overspecified_sources",
    "test_p2g",
    "test_pajek",
    "test_parse_edgelist",
    "test_read_shp_nofile",
    "test_shp",
    "test_sparse6",
    "test_text",
    "test_tree",
    "test_undirected_multi_tree_forest",
    "test_undirected_tree_str",
    "test_yaml",
    "tests",
    "text",
    "to_graph6_bytes",
    "to_sparse6_bytes",
    "tree",
    "tree_data",
    "tree_graph",
    "write_adjlist",
    "write_edgelist",
    "write_gexf",
    "write_gml",
    "write_gpickle",
    "write_graph6",
    "write_graphml",
    "write_graphml_lxml",
    "write_graphml_xml",
    "write_multiline_adjlist",
    "write_p2g",
    "write_pajek",
    "write_shp",
    "write_sparse6",
    "write_weighted_edgelist",
    "write_yaml",
    "yaml",
]
