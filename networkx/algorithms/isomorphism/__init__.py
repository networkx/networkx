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
        "ismags",
        "isomorph",
        "isomorphvf2",
        "matchhelpers",
        "temporalisomorphvf2",
        "tests",
        "tree_isomorphism",
        "vf2userfunc",
    },
    submod_attrs={
        "ismags": [
            "ISMAGS",
        ],
        "isomorph": [
            "could_be_isomorphic",
            "fast_could_be_isomorphic",
            "faster_could_be_isomorphic",
            "is_isomorphic",
        ],
        "isomorphvf2": [
            "DiGraphMatcher",
            "GraphMatcher",
        ],
        "matchhelpers": [
            "categorical_edge_match",
            "categorical_multiedge_match",
            "categorical_node_match",
            "generic_edge_match",
            "generic_multiedge_match",
            "generic_node_match",
            "numerical_edge_match",
            "numerical_multiedge_match",
            "numerical_node_match",
        ],
        "temporalisomorphvf2": [
            "TimeRespectingDiGraphMatcher",
            "TimeRespectingGraphMatcher",
        ],
        "tests": [
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
        ],
        "tree_isomorphism": [
            "rooted_tree_isomorphism",
            "tree_isomorphism",
        ],
        "vf2userfunc": [
            "DiGraphMatcher",
            "GraphMatcher",
            "MultiDiGraphMatcher",
            "MultiGraphMatcher",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "DiGraphMatcher",
    "GraphMatcher",
    "ISMAGS",
    "MultiDiGraphMatcher",
    "MultiGraphMatcher",
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
    "TimeRespectingDiGraphMatcher",
    "TimeRespectingGraphMatcher",
    "categorical_edge_match",
    "categorical_multiedge_match",
    "categorical_node_match",
    "check_isomorphism",
    "could_be_isomorphic",
    "fast_could_be_isomorphic",
    "faster_could_be_isomorphic",
    "generic_edge_match",
    "generic_multiedge_match",
    "generic_node_match",
    "is_isomorphic",
    "ismags",
    "isomorph",
    "isomorphvf2",
    "matchhelpers",
    "numerical_edge_match",
    "numerical_multiedge_match",
    "numerical_node_match",
    "positive_single_tree",
    "provide_g1_edgelist",
    "put_same_datetime",
    "put_same_time",
    "put_sequence_time",
    "put_time_config_0",
    "put_time_config_1",
    "put_time_config_2",
    "random_swap",
    "rooted_tree_isomorphism",
    "temporalisomorphvf2",
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
    "tests",
    "tree_isomorphism",
    "vf2userfunc",
]
