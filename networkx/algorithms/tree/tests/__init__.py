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
        "test_branchings",
        "test_coding",
        "test_decomposition",
        "test_mst",
        "test_operations",
        "test_recognition",
    },
    submod_attrs={
        "test_branchings": [
            "G1",
            "G2",
            "G_array",
            "assert_equal_branchings",
            "build_branching",
            "greedy_subopt_branching_1a",
            "greedy_subopt_branching_1b",
            "np",
            "optimal_arborescence_1",
            "optimal_arborescence_2",
            "optimal_branching_2a",
            "optimal_branching_2b",
            "sorted_edges",
            "test_edge_attribute_discard",
            "test_edge_attribute_preservation_multigraph",
            "test_edge_attribute_preservation_normal_graph",
            "test_edmonds1_maxarbor",
            "test_edmonds1_maxbranch",
            "test_edmonds1_minbranch",
            "test_edmonds2_maxarbor",
            "test_edmonds2_maxbranch",
            "test_edmonds2_minarbor",
            "test_edmonds3_minbranch1",
            "test_edmonds3_minbranch2",
            "test_greedy_max1",
            "test_greedy_max2",
            "test_greedy_max3",
            "test_greedy_min",
            "test_greedy_suboptimal_branching1a",
            "test_greedy_suboptimal_branching1b",
            "test_mixed_nodetypes",
            "test_mst",
            "test_optimal_arborescence2",
            "test_optimal_branching1",
            "test_optimal_branching2a",
            "test_optimal_branching2b",
        ],
        "test_coding": [
            "TestNestedTuple",
            "TestPruferSequence",
        ],
        "test_decomposition": [
            "test_junction_tree_directed_cascade",
            "test_junction_tree_directed_confounders",
            "test_junction_tree_directed_unconnected_edges",
            "test_junction_tree_directed_unconnected_nodes",
            "test_junction_tree_undirected",
        ],
        "test_mst": [
            "MinimumSpanningTreeTestBase",
            "MultigraphMSTTestBase",
            "TestBoruvka",
            "TestKruskal",
            "TestPrim",
            "test_unknown_algorithm",
        ],
        "test_operations": [
            "TestJoin",
        ],
        "test_recognition": [
            "TestDirectedTreeRecognition",
            "TestTreeRecognition",
            "test_dag_nontree",
            "test_disconnected_graph",
            "test_emptybranch",
            "test_multicycle",
            "test_notarborescence1",
            "test_notarborescence2",
            "test_notbranching1",
            "test_notbranching2",
            "test_path",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "G1",
    "G2",
    "G_array",
    "MinimumSpanningTreeTestBase",
    "MultigraphMSTTestBase",
    "TestBoruvka",
    "TestDirectedTreeRecognition",
    "TestJoin",
    "TestKruskal",
    "TestNestedTuple",
    "TestPrim",
    "TestPruferSequence",
    "TestTreeRecognition",
    "assert_equal_branchings",
    "build_branching",
    "greedy_subopt_branching_1a",
    "greedy_subopt_branching_1b",
    "np",
    "optimal_arborescence_1",
    "optimal_arborescence_2",
    "optimal_branching_2a",
    "optimal_branching_2b",
    "sorted_edges",
    "test_branchings",
    "test_coding",
    "test_dag_nontree",
    "test_decomposition",
    "test_disconnected_graph",
    "test_edge_attribute_discard",
    "test_edge_attribute_preservation_multigraph",
    "test_edge_attribute_preservation_normal_graph",
    "test_edmonds1_maxarbor",
    "test_edmonds1_maxbranch",
    "test_edmonds1_minbranch",
    "test_edmonds2_maxarbor",
    "test_edmonds2_maxbranch",
    "test_edmonds2_minarbor",
    "test_edmonds3_minbranch1",
    "test_edmonds3_minbranch2",
    "test_emptybranch",
    "test_greedy_max1",
    "test_greedy_max2",
    "test_greedy_max3",
    "test_greedy_min",
    "test_greedy_suboptimal_branching1a",
    "test_greedy_suboptimal_branching1b",
    "test_junction_tree_directed_cascade",
    "test_junction_tree_directed_confounders",
    "test_junction_tree_directed_unconnected_edges",
    "test_junction_tree_directed_unconnected_nodes",
    "test_junction_tree_undirected",
    "test_mixed_nodetypes",
    "test_mst",
    "test_multicycle",
    "test_notarborescence1",
    "test_notarborescence2",
    "test_notbranching1",
    "test_notbranching2",
    "test_operations",
    "test_optimal_arborescence2",
    "test_optimal_branching1",
    "test_optimal_branching2a",
    "test_optimal_branching2b",
    "test_path",
    "test_recognition",
    "test_unknown_algorithm",
]
