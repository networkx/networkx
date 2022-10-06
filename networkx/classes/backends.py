"""
Code to support various backends in a plugin dispatch architecture.

Create a Dispatcher
-------------------

To be a valid plugin, a package must register an entry_point
of `networkx.plugins` with a known key pointing to the handler.

For example,
```
entry_points={'networkx.plugins': 'sparse = networkx_plugin_sparse'}
```

The plugin must create a Graph-like object which contains an attribute
`__networkx_plugin__` with a value of the known key.

Continuing the example above:
```
class WrappedSparse:
    __networkx_plugin__ = "sparse"
    ...
```

When a dispatchable networkx algorithm encounters a Graph-like object
with a `__networkx_plugin__` attribute, it will look for the associated
dispatch object in the entry_points, load it, and dispatch the work ot it.


Testing
-------
To assist in validating the backend algorithm implementations, if an
environment variable `NETWORKX_GRAPH_CONVERT` is set to one of the known
plugin keys, the dispatch machinery will automatically convert regular
networkx Graphs and DiGraphs to the backend equivalent by calling
`<backend dispatcher>.convert(G, weight=weight)`.

By defining a `convert` method and setting the environment variable,
networkx will automatically route tests on dispatchable algorithms
to the backend, allowing the full networkx test suite to be run against
the backend implementation.

Example pytest invocation:
NETWORKX_GRAPH_CONVERT=sparse pytest --pyargs networkx

Any dispatchable algorithms which are not implemented by the backend
will cause a `pytest.xfail()`, giving some indication that not all
tests are working without causing an explicit failure.

A special `mark_nx_tests(items)` function may be defined by the backend.
It will be called with the list of NetworkX tests discovered. Each item
is a pytest.Node object. If the backend does not support the test, it
can be marked as xfail to indicate it is not being handled.
"""
import os
import sys
import inspect
from functools import wraps
from importlib.metadata import entry_points


__all__ = ["dispatch", "mark_tests"]


known_plugins = [
    "sparse",  # scipy.sparse
    "graphblas",  # python-graphblas
    "cugraph",  # cugraph
]


class PluginInfo:
    """Lazily loaded entry_points plugin information"""
    def __init__(self):
        self._items = None

    def __bool__(self):
        return len(self.items) > 0

    @property
    def items(self):
        if self._items is None:
            if sys.version_info < (3, 10):
                self._items = entry_points()["networkx.plugins"]
            else:
                self._items = entry_points(group="networkx.plugins")
        return self._items

    def __contains__(self, name):
        if sys.version_info < (3, 10):
            return len([ep for ep in self.items if ep.name == name]) > 0
        return name in self.items.names

    def __getitem__(self, name):
        if sys.version_info < (3, 10):
            return [ep for ep in self.items if ep.name == name][0]
        return self.items[name]


plugins = PluginInfo()


def dispatch(algo):
    def algorithm(func):
        @wraps(func)
        def wrapper(*args, **kwds):
            graph = args[0]
            if hasattr(graph, "__networkx_plugin__") and plugins:
                plugin_name = graph.__networkx_plugin__
                if plugin_name in plugins:
                    backend = plugins[plugin_name].load()
                    if hasattr(backend, algo):
                        return getattr(backend, algo).__call__(*args, **kwds)
            return func(*args, **kwds)

        return wrapper

    return algorithm


# Override `dispatch` for testing
if os.environ.get("NETWORKX_GRAPH_CONVERT"):
    plugin_name = os.environ["NETWORKX_GRAPH_CONVERT"]
    if plugin_name not in known_plugins:
        raise Exception(f"{plugin_name} is not a known plugin; must be one of {known_plugins}")
    if not plugins:
        raise Exception("No registered networkx.plugins entry_points")
    if plugin_name not in plugins:
        raise Exception(f"No registered networkx.plugins entry_point named {plugin_name}")

    try:
        import pytest
    except ImportError:
        raise ImportError(f"Missing pytest, which is required when using NETWORKX_GRAPH_CONVERT")

    def dispatch(algo):
        def algorithm(func):
            sig = inspect.signature(func)

            @wraps(func)
            def wrapper(*args, **kwds):
                backend = plugins[plugin_name].load()
                if not hasattr(backend, algo):
                    pytest.xfail(f"'{algo}' not implemented by {plugin_name}")
                bound = sig.bind(*args, **kwds)
                bound.apply_defaults()
                graph, *args = args
                # Convert graph into backend graph-like object
                #   Include the weight label, if provided to the algorithm
                weight = None
                if "weight" in bound.arguments:
                    weight = bound.arguments["weight"]
                elif "data" in bound.arguments and "default" in bound.arguments:
                    # This case exists for several MultiGraph edge algorithms
                    if bound.arguments["data"]:
                        weight = "weight"
                graph = backend.convert(graph, weight=weight)
                return getattr(backend, algo).__call__(graph, *args, **kwds)

            return wrapper

        return algorithm


def mark_tests(items):
    # Allow backend to mark tests (skip or xfail) if they aren't
    # able to correctly handle them
    if os.environ.get("NETWORKX_GRAPH_CONVERT"):
        plugin_name = os.environ["NETWORKX_GRAPH_CONVERT"]
        backend = plugins[plugin_name].load()
        if hasattr(backend, "mark_nx_tests"):
            getattr(backend, "mark_nx_tests")(items)
