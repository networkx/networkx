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
        "branchings",
        "coding",
        "decomposition",
        "mst",
        "operations",
        "recognition",
        "tests",
    },
    submod_attrs={
        "branchings": [
            "Edmonds",
            "branching_weight",
            "greedy_branching",
            "maximum_branching",
            "maximum_spanning_arborescence",
            "minimum_branching",
            "minimum_spanning_arborescence",
        ],
        "coding": [
            "NotATree",
            "from_nested_tuple",
            "from_prufer_sequence",
            "to_nested_tuple",
            "to_prufer_sequence",
        ],
        "decomposition": [
            "junction_tree",
        ],
        "mst": [
            "maximum_spanning_edges",
            "maximum_spanning_tree",
            "minimum_spanning_edges",
            "minimum_spanning_tree",
        ],
        "operations": [
            "join",
        ],
        "recognition": [
            "is_arborescence",
            "is_branching",
            "is_forest",
            "is_tree",
        ],
        "tests": [
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
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "Edmonds",
    "G1",
    "G2",
    "G_array",
    "MinimumSpanningTreeTestBase",
    "MultigraphMSTTestBase",
    "NotATree",
    "TestBoruvka",
    "TestDirectedTreeRecognition",
    "TestJoin",
    "TestKruskal",
    "TestNestedTuple",
    "TestPrim",
    "TestPruferSequence",
    "TestTreeRecognition",
    "assert_equal_branchings",
    "branching_weight",
    "branchings",
    "build_branching",
    "coding",
    "decomposition",
    "from_nested_tuple",
    "from_prufer_sequence",
    "greedy_branching",
    "greedy_subopt_branching_1a",
    "greedy_subopt_branching_1b",
    "is_arborescence",
    "is_branching",
    "is_forest",
    "is_tree",
    "join",
    "junction_tree",
    "maximum_branching",
    "maximum_spanning_arborescence",
    "maximum_spanning_edges",
    "maximum_spanning_tree",
    "minimum_branching",
    "minimum_spanning_arborescence",
    "minimum_spanning_edges",
    "minimum_spanning_tree",
    "mst",
    "np",
    "operations",
    "optimal_arborescence_1",
    "optimal_arborescence_2",
    "optimal_branching_2a",
    "optimal_branching_2b",
    "recognition",
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
    "tests",
    "to_nested_tuple",
    "to_prufer_sequence",
]
