"""
*********
JSON data
*********
Generate and parse JSON serializable data for NetworkX graphs.

These formats are suitable for use with the d3.js examples https://d3js.org/

The three formats that you can generate with NetworkX are:

 - node-link like in the d3.js example https://bl.ocks.org/mbostock/4062045
 - tree like in the d3.js example https://bl.ocks.org/mbostock/4063550
 - adjacency like in the d3.js example https://bost.ocks.org/mike/miserables/
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
        "adjacency",
        "cytoscape",
        "jit",
        "node_link",
        "tests",
        "tree",
    },
    submod_attrs={
        "adjacency": [
            "adjacency_data",
            "adjacency_graph",
        ],
        "cytoscape": [
            "cytoscape_data",
            "cytoscape_graph",
        ],
        "jit": [
            "jit_data",
            "jit_graph",
        ],
        "node_link": [
            "node_link_data",
            "node_link_graph",
        ],
        "tests": [
            "TestAdjacency",
            "TestCytoscape",
            "TestJIT",
            "TestNodeLink",
            "TestTree",
            "test_adjacency",
            "test_cytoscape",
            "test_futurewarning",
            "test_jit",
            "test_node_link",
            "test_tree",
        ],
        "tree": [
            "tree_data",
            "tree_graph",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
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
]
