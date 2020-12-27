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
        "test_adjlist",
        "test_edgelist",
        "test_gexf",
        "test_gml",
        "test_gpickle",
        "test_graph6",
        "test_graphml",
        "test_leda",
        "test_p2g",
        "test_pajek",
        "test_shp",
        "test_sparse6",
        "test_text",
        "test_yaml",
    },
    submod_attrs={
        "test_adjlist": [
            "TestAdjlist",
            "TestMultilineAdjlist",
        ],
        "test_edgelist": [
            "TestEdgelist",
            "test_parse_edgelist",
        ],
        "test_gexf": [
            "TestGEXF",
        ],
        "test_gml": [
            "TestGraph",
            "TestPropertyLists",
            "byte_file",
        ],
        "test_gpickle": [
            "TestGpickle",
        ],
        "test_graph6": [
            "TestFromGraph6Bytes",
            "TestGraph6Utils",
            "TestReadGraph6",
            "TestWriteGraph6",
        ],
        "test_graphml": [
            "BaseGraphML",
            "TestReadGraphML",
            "TestWriteGraphML",
            "TestXMLGraphML",
        ],
        "test_leda": [
            "TestLEDA",
        ],
        "test_p2g": [
            "TestP2G",
        ],
        "test_pajek": [
            "TestPajek",
        ],
        "test_shp": [
            "TestMissingAttrWrite",
            "TestMissingGeometry",
            "TestShp",
            "ogr",
            "test_read_shp_nofile",
        ],
        "test_sparse6": [
            "TestSparseGraph6",
            "TestWriteSparse6",
        ],
        "test_text": [
            "test_directed_multi_tree_forest",
            "test_directed_tree_str",
            "test_empty_graph",
            "test_forest_str_errors",
            "test_overspecified_sources",
            "test_undirected_multi_tree_forest",
            "test_undirected_tree_str",
        ],
        "test_yaml": [
            "TestYaml",
            "yaml",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
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
]
