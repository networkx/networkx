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
        "test_ismags",
        "test_isomorphism",
        "test_isomorphvf2",
        "test_match_helpers",
        "test_temporalisomorphvf2",
        "test_tree_isomorphism",
        "test_vf2userfunc",
    },
    submod_attrs={
        "test_ismags": [
            "TestLargestCommonSubgraph",
            "TestSelfIsomorphism",
            "TestSubgraphIsomorphism",
            "TestWikipediaExample",
        ],
        "test_isomorphism": [
            "TestIsomorph",
        ],
        "test_isomorphvf2": [
            "TestAtlas",
            "TestVF2GraphDB",
            "TestWikipediaExample",
            "test_isomorphism_iter1",
            "test_isomorphism_iter2",
            "test_monomorphism_edge_match",
            "test_monomorphism_iter1",
            "test_multiedge",
            "test_multiple",
            "test_noncomparable_nodes",
            "test_selfloop",
            "test_selfloop_mono",
        ],
        "test_match_helpers": [
            "TestGenericMultiEdgeMatch",
            "test_categorical_node_match",
        ],
        "test_temporalisomorphvf2": [
            "TestDiTimeRespectingGraphMatcher",
            "TestTimeRespectingGraphMatcher",
            "provide_g1_edgelist",
            "put_same_datetime",
            "put_same_time",
            "put_sequence_time",
            "put_time_config_0",
            "put_time_config_1",
            "put_time_config_2",
        ],
        "test_tree_isomorphism": [
            "check_isomorphism",
            "positive_single_tree",
            "random_swap",
            "test_hardcoded",
            "test_negative",
            "test_positive",
            "test_trivial",
            "test_trivial_2",
        ],
        "test_vf2userfunc": [
            "TestEdgeMatch_DiGraph",
            "TestEdgeMatch_MultiDiGraph",
            "TestEdgeMatch_MultiGraph",
            "TestNodeMatch_Graph",
            "test_simple",
            "test_weightkey",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestAtlas",
    "TestDiTimeRespectingGraphMatcher",
    "TestEdgeMatch_DiGraph",
    "TestEdgeMatch_MultiDiGraph",
    "TestEdgeMatch_MultiGraph",
    "TestGenericMultiEdgeMatch",
    "TestIsomorph",
    "TestLargestCommonSubgraph",
    "TestNodeMatch_Graph",
    "TestSelfIsomorphism",
    "TestSubgraphIsomorphism",
    "TestTimeRespectingGraphMatcher",
    "TestVF2GraphDB",
    "TestWikipediaExample",
    "check_isomorphism",
    "positive_single_tree",
    "provide_g1_edgelist",
    "put_same_datetime",
    "put_same_time",
    "put_sequence_time",
    "put_time_config_0",
    "put_time_config_1",
    "put_time_config_2",
    "random_swap",
    "test_categorical_node_match",
    "test_hardcoded",
    "test_ismags",
    "test_isomorphism",
    "test_isomorphism_iter1",
    "test_isomorphism_iter2",
    "test_isomorphvf2",
    "test_match_helpers",
    "test_monomorphism_edge_match",
    "test_monomorphism_iter1",
    "test_multiedge",
    "test_multiple",
    "test_negative",
    "test_noncomparable_nodes",
    "test_positive",
    "test_selfloop",
    "test_selfloop_mono",
    "test_simple",
    "test_temporalisomorphvf2",
    "test_tree_isomorphism",
    "test_trivial",
    "test_trivial_2",
    "test_vf2userfunc",
    "test_weightkey",
]
