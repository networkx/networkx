__private__ = ['tests']


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
        "contextmanagers",
        "decorators",
        "heaps",
        "mapped_queue",
        "misc",
        "random_sequence",
        "rcm",
        "tests",
        "union_find",
    },
    submod_attrs={
        "contextmanagers": [
            "reversed",
        ],
        "decorators": [
            "nodes_or_number",
            "not_implemented_for",
            "np_random_state",
            "open_file",
            "preserve_random_state",
            "py_random_state",
            "random_state",
        ],
        "heaps": [
            "BinaryHeap",
            "MinHeap",
            "PairingHeap",
        ],
        "mapped_queue": [
            "MappedQueue",
        ],
        "misc": [
            "PythonRandomInterface",
            "arbitrary_element",
            "consume",
            "create_py_random_state",
            "create_random_state",
            "default_opener",
            "dict_to_numpy_array",
            "dict_to_numpy_array1",
            "dict_to_numpy_array2",
            "empty_generator",
            "flatten",
            "generate_unique_node",
            "groups",
            "is_iterator",
            "is_list_of_ints",
            "is_string_like",
            "iterable",
            "make_list_of_ints",
            "make_str",
            "pairwise",
            "to_tuple",
        ],
        "random_sequence": [
            "cumulative_distribution",
            "discrete_sequence",
            "powerlaw_sequence",
            "random_weighted_sample",
            "weighted_choice",
            "zipf_rv",
        ],
        "rcm": [
            "cuthill_mckee_ordering",
            "reverse_cuthill_mckee_ordering",
        ],
        "union_find": [
            "UnionFind",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "BinaryHeap",
    "MappedQueue",
    "MinHeap",
    "PairingHeap",
    "PythonRandomInterface",
    "UnionFind",
    "arbitrary_element",
    "consume",
    "contextmanagers",
    "create_py_random_state",
    "create_random_state",
    "cumulative_distribution",
    "cuthill_mckee_ordering",
    "decorators",
    "default_opener",
    "dict_to_numpy_array",
    "dict_to_numpy_array1",
    "dict_to_numpy_array2",
    "discrete_sequence",
    "empty_generator",
    "flatten",
    "generate_unique_node",
    "groups",
    "heaps",
    "is_iterator",
    "is_list_of_ints",
    "is_string_like",
    "iterable",
    "make_list_of_ints",
    "make_str",
    "mapped_queue",
    "misc",
    "nodes_or_number",
    "not_implemented_for",
    "np_random_state",
    "open_file",
    "pairwise",
    "powerlaw_sequence",
    "preserve_random_state",
    "py_random_state",
    "random_sequence",
    "random_state",
    "random_weighted_sample",
    "rcm",
    "reverse_cuthill_mckee_ordering",
    "reversed",
    "tests",
    "to_tuple",
    "union_find",
    "weighted_choice",
    "zipf_rv",
]
