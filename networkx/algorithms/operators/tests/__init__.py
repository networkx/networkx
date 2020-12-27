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
        "test_all",
        "test_binary",
        "test_product",
        "test_unary",
    },
    submod_attrs={
        "test_all": [
            "test_empty_compose_all",
            "test_empty_disjoint_union",
            "test_empty_intersection_all",
            "test_empty_union",
            "test_input_output",
            "test_intersection_all",
            "test_intersection_all_attributes",
            "test_intersection_all_multigraph_attributes",
            "test_mixed_type_compose",
            "test_mixed_type_disjoint_union",
            "test_mixed_type_intersection",
            "test_mixed_type_union",
            "test_union_all_and_compose_all",
            "test_union_all_attributes",
            "test_union_all_multigraph",
        ],
        "test_binary": [
            "test_compose_multigraph",
            "test_difference",
            "test_difference2",
            "test_difference_attributes",
            "test_difference_multigraph_attributes",
            "test_difference_raise",
            "test_disjoint_union_multigraph",
            "test_full_join_graph",
            "test_full_join_multigraph",
            "test_intersection",
            "test_intersection_attributes",
            "test_intersection_multigraph_attributes",
            "test_mixed_type_union",
            "test_symmetric_difference_multigraph",
            "test_union_and_compose",
            "test_union_attributes",
            "test_union_multigraph",
        ],
        "test_product": [
            "test_cartesian_product_classic",
            "test_cartesian_product_multigraph",
            "test_cartesian_product_null",
            "test_cartesian_product_raises",
            "test_cartesian_product_random",
            "test_cartesian_product_size",
            "test_graph_power",
            "test_graph_power_negative",
            "test_graph_power_raises",
            "test_lexicographic_product_combinations",
            "test_lexicographic_product_null",
            "test_lexicographic_product_raises",
            "test_lexicographic_product_random",
            "test_lexicographic_product_size",
            "test_rooted_product",
            "test_rooted_product_raises",
            "test_strong_product_combinations",
            "test_strong_product_null",
            "test_strong_product_raises",
            "test_strong_product_random",
            "test_strong_product_size",
            "test_tensor_product_classic_result",
            "test_tensor_product_combinations",
            "test_tensor_product_null",
            "test_tensor_product_raises",
            "test_tensor_product_random",
            "test_tensor_product_size",
        ],
        "test_unary": [
            "test_complement",
            "test_complement_2",
            "test_reverse1",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "test_all",
    "test_binary",
    "test_cartesian_product_classic",
    "test_cartesian_product_multigraph",
    "test_cartesian_product_null",
    "test_cartesian_product_raises",
    "test_cartesian_product_random",
    "test_cartesian_product_size",
    "test_complement",
    "test_complement_2",
    "test_compose_multigraph",
    "test_difference",
    "test_difference2",
    "test_difference_attributes",
    "test_difference_multigraph_attributes",
    "test_difference_raise",
    "test_disjoint_union_multigraph",
    "test_empty_compose_all",
    "test_empty_disjoint_union",
    "test_empty_intersection_all",
    "test_empty_union",
    "test_full_join_graph",
    "test_full_join_multigraph",
    "test_graph_power",
    "test_graph_power_negative",
    "test_graph_power_raises",
    "test_input_output",
    "test_intersection",
    "test_intersection_all",
    "test_intersection_all_attributes",
    "test_intersection_all_multigraph_attributes",
    "test_intersection_attributes",
    "test_intersection_multigraph_attributes",
    "test_lexicographic_product_combinations",
    "test_lexicographic_product_null",
    "test_lexicographic_product_raises",
    "test_lexicographic_product_random",
    "test_lexicographic_product_size",
    "test_mixed_type_compose",
    "test_mixed_type_disjoint_union",
    "test_mixed_type_intersection",
    "test_mixed_type_union",
    "test_product",
    "test_reverse1",
    "test_rooted_product",
    "test_rooted_product_raises",
    "test_strong_product_combinations",
    "test_strong_product_null",
    "test_strong_product_raises",
    "test_strong_product_random",
    "test_strong_product_size",
    "test_symmetric_difference_multigraph",
    "test_tensor_product_classic_result",
    "test_tensor_product_combinations",
    "test_tensor_product_null",
    "test_tensor_product_raises",
    "test_tensor_product_random",
    "test_tensor_product_size",
    "test_unary",
    "test_union_all_and_compose_all",
    "test_union_all_attributes",
    "test_union_all_multigraph",
    "test_union_and_compose",
    "test_union_attributes",
    "test_union_multigraph",
]
