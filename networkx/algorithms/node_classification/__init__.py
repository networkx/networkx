""" This module provides the functions for node classification problem.

The functions in this module are not imported
into the top level `networkx` namespace.
You can access these functions by importing
the `networkx.algorithms.node_classification` modules,
then accessing the functions as attributes of `node_classification`.
For example:

  >>> from networkx.algorithms import node_classification
  >>> G = nx.path_graph(4)
  >>> G.edges()
  EdgeView([(0, 1), (1, 2), (2, 3)])
  >>> G.nodes[0]["label"] = "A"
  >>> G.nodes[3]["label"] = "B"
  >>> node_classification.harmonic_function(G)
  ['A', 'A', 'B', 'B']

"""


def __getattr__(name):
    if name in ("hmn", "lgc"):
        import warnings
        import importlib

        fn_name = (
            "harmonic_function" if name == "hmn" else "local_and_global_consistency"
        )
        msg = (
            f"The {name}  module is deprecated and will be removed in version 3.0.\n"
            f"Access `{fn_name}` directly from `node_classification`:\n\n"
            "    from networkx.algorithms import node_classification\n"
            f"    node_classification.{fn_name}\n"
        )
        warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
        return importlib.import_module(
            f".{name}", "networkx.algorithms.node_classification"
        )
    if name == "harmonic_function":
        from .hmn import harmonic_function

        return harmonic_function
    if name == "local_and_global_consistency":
        from .lgc import local_and_global_consistency

        return local_and_global_consistency
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    return ["harmonic_function", "local_and_global_consistency"]
