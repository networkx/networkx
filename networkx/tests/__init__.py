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
        "test_all_random_functions",
        "test_convert",
        "test_convert_numpy",
        "test_convert_pandas",
        "test_convert_scipy",
        "test_exceptions",
        "test_relabel",
    },
    submod_attrs={
        "test_all_random_functions": [
            "np",
            "np_rv",
            "progress",
            "py_rv",
            "run_all_random_functions",
            "t",
            "test_rng_interface",
        ],
        "test_convert": [
            "TestConvert",
            "test_to_dict_of_dicts_with_edgedata_and_nodelist",
            "test_to_dict_of_dicts_with_edgedata_multigraph",
            "test_to_dict_of_dicts_with_edgedata_param",
            "test_to_networkx_graph_non_edgelist",
        ],
        "test_convert_numpy": [
            "TestConvertNumpyArray",
            "TestConvertNumpyMatrix",
            "multigraph_test_graph",
            "np",
            "recarray_nodelist_test_graph",
            "recarray_test_graph",
            "test_from_numpy_matrix_deprecation",
            "test_numpy_multigraph",
            "test_to_numpy_array_multigraph_nodelist",
            "test_to_numpy_array_multigraph_weight",
            "test_to_numpy_matrix_deprecation",
            "test_to_numpy_recarray",
            "test_to_numpy_recarray_bad_nodelist",
            "test_to_numpy_recarray_default_dtype",
            "test_to_numpy_recarray_default_dtype_no_weight",
            "test_to_numpy_recarray_directed",
            "test_to_numpy_recarray_nodelist",
        ],
        "test_convert_pandas": [
            "TestConvertPandas",
            "np",
            "pd",
            "test_to_pandas_adjacency_with_nodelist",
            "test_to_pandas_edgelist_with_nodelist",
        ],
        "test_convert_scipy": [
            "TestConvertScipy",
            "np",
            "sp",
            "test_from_scipy_sparse_matrix_formats",
        ],
        "test_exceptions": [
            "test_raises_networkx_no_path",
            "test_raises_networkx_pointless_concept",
            "test_raises_networkx_unbounded",
            "test_raises_networkx_unfeasible",
            "test_raises_networkxalgorithmerr",
            "test_raises_networkxerr",
            "test_raises_networkxexception",
        ],
        "test_relabel": [
            "TestRelabel",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "TestConvert",
    "TestConvertNumpyArray",
    "TestConvertNumpyMatrix",
    "TestConvertPandas",
    "TestConvertScipy",
    "TestRelabel",
    "multigraph_test_graph",
    "np",
    "np_rv",
    "pd",
    "progress",
    "py_rv",
    "recarray_nodelist_test_graph",
    "recarray_test_graph",
    "run_all_random_functions",
    "sp",
    "t",
    "test_all_random_functions",
    "test_convert",
    "test_convert_numpy",
    "test_convert_pandas",
    "test_convert_scipy",
    "test_exceptions",
    "test_from_numpy_matrix_deprecation",
    "test_from_scipy_sparse_matrix_formats",
    "test_numpy_multigraph",
    "test_raises_networkx_no_path",
    "test_raises_networkx_pointless_concept",
    "test_raises_networkx_unbounded",
    "test_raises_networkx_unfeasible",
    "test_raises_networkxalgorithmerr",
    "test_raises_networkxerr",
    "test_raises_networkxexception",
    "test_relabel",
    "test_rng_interface",
    "test_to_dict_of_dicts_with_edgedata_and_nodelist",
    "test_to_dict_of_dicts_with_edgedata_multigraph",
    "test_to_dict_of_dicts_with_edgedata_param",
    "test_to_networkx_graph_non_edgelist",
    "test_to_numpy_array_multigraph_nodelist",
    "test_to_numpy_array_multigraph_weight",
    "test_to_numpy_matrix_deprecation",
    "test_to_numpy_recarray",
    "test_to_numpy_recarray_bad_nodelist",
    "test_to_numpy_recarray_default_dtype",
    "test_to_numpy_recarray_default_dtype_no_weight",
    "test_to_numpy_recarray_directed",
    "test_to_numpy_recarray_nodelist",
    "test_to_pandas_adjacency_with_nodelist",
    "test_to_pandas_edgelist_with_nodelist",
]
