"""Functions for computing and measuring community structure.

The functions in this class are not imported into the top-level
:mod:`networkx` namespace. You can access these functions by importing
the :mod:`networkx.algorithms.community` module, then accessing the
functions as attributes of ``community``. For example::

    >>> from networkx.algorithms import community
    >>> G = nx.barbell_graph(5, 1)
    >>> communities_generator = community.girvan_newman(G)
    >>> top_level_communities = next(communities_generator)
    >>> next_level_communities = next(communities_generator)
    >>> sorted(map(sorted, next_level_communities))
    [[0, 1, 2, 3, 4], [5], [6, 7, 8, 9, 10]]

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
        "asyn_fluid",
        "centrality",
        "community_utils",
        "kclique",
        "kernighan_lin",
        "label_propagation",
        "lukes",
        "modularity_max",
        "quality",
        "tests",
    },
    submod_attrs={
        "asyn_fluid": [
            "asyn_fluidc",
        ],
        "centrality": [
            "girvan_newman",
        ],
        "community_utils": [
            "is_partition",
        ],
        "kclique": [
            "k_clique_communities",
        ],
        "kernighan_lin": [
            "kernighan_lin_bisection",
        ],
        "label_propagation": [
            "asyn_lpa_communities",
            "label_propagation_communities",
        ],
        "lukes": [
            "lukes_partitioning",
        ],
        "modularity_max": [
            "_naive_greedy_modularity_communities",
            "greedy_modularity_communities",
            "naive_greedy_modularity_communities",
        ],
        "quality": [
            "coverage",
            "modularity",
            "performance",
        ],
        "tests": [
            "EWL",
            "NWL",
            "TestAsynLpaCommunities",
            "TestCNM",
            "TestCoverage",
            "TestGirvanNewman",
            "TestNaive",
            "TestPerformance",
            "TestZacharyKarateClub",
            "assert_partition_equal",
            "paper_1_case",
            "paper_2_case",
            "set_of_sets",
            "test_asyn_fluid",
            "test_bad_k",
            "test_centrality",
            "test_connected_communities",
            "test_directed_not_supported",
            "test_exceptions",
            "test_five_clique_ring",
            "test_inter_community_edges_with_digraphs",
            "test_is_partition",
            "test_isolated_K5",
            "test_kclique",
            "test_kernighan_lin",
            "test_label_propagation",
            "test_lukes",
            "test_mandatory_integrality",
            "test_mandatory_tree",
            "test_modularity",
            "test_modularity_max",
            "test_multigraph",
            "test_non_disjoint_partition",
            "test_not_covering",
            "test_not_disjoint",
            "test_not_node",
            "test_one_node",
            "test_overlapping_K5",
            "test_paper_1_case",
            "test_paper_2_case",
            "test_partition",
            "test_partition_argument",
            "test_partition_argument_non_integer_nodes",
            "test_quality",
            "test_seed_argument",
            "test_single_node",
            "test_termination",
            "test_too_many_blocks",
            "test_two_clique_communities",
            "test_two_nodes",
            "test_unconnected_communities",
            "test_utils",
            "validate_communities",
            "validate_possible_communities",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "EWL",
    "NWL",
    "TestAsynLpaCommunities",
    "TestCNM",
    "TestCoverage",
    "TestGirvanNewman",
    "TestNaive",
    "TestPerformance",
    "TestZacharyKarateClub",
    "_naive_greedy_modularity_communities",
    "assert_partition_equal",
    "asyn_fluid",
    "asyn_fluidc",
    "asyn_lpa_communities",
    "centrality",
    "community_utils",
    "coverage",
    "girvan_newman",
    "greedy_modularity_communities",
    "is_partition",
    "k_clique_communities",
    "kclique",
    "kernighan_lin",
    "kernighan_lin_bisection",
    "label_propagation",
    "label_propagation_communities",
    "lukes",
    "lukes_partitioning",
    "modularity",
    "modularity_max",
    "naive_greedy_modularity_communities",
    "paper_1_case",
    "paper_2_case",
    "performance",
    "quality",
    "set_of_sets",
    "test_asyn_fluid",
    "test_bad_k",
    "test_centrality",
    "test_connected_communities",
    "test_directed_not_supported",
    "test_exceptions",
    "test_five_clique_ring",
    "test_inter_community_edges_with_digraphs",
    "test_is_partition",
    "test_isolated_K5",
    "test_kclique",
    "test_kernighan_lin",
    "test_label_propagation",
    "test_lukes",
    "test_mandatory_integrality",
    "test_mandatory_tree",
    "test_modularity",
    "test_modularity_max",
    "test_multigraph",
    "test_non_disjoint_partition",
    "test_not_covering",
    "test_not_disjoint",
    "test_not_node",
    "test_one_node",
    "test_overlapping_K5",
    "test_paper_1_case",
    "test_paper_2_case",
    "test_partition",
    "test_partition_argument",
    "test_partition_argument_non_integer_nodes",
    "test_quality",
    "test_seed_argument",
    "test_single_node",
    "test_termination",
    "test_too_many_blocks",
    "test_two_clique_communities",
    "test_two_nodes",
    "test_unconnected_communities",
    "test_utils",
    "tests",
    "validate_communities",
    "validate_possible_communities",
]
