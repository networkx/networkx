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

The expectation is that each backend will pass all networkx tests
to be considered a fully compliant backend.
"""
import os
import sys
import inspect
from functools import wraps
from importlib.metadata import entry_points


__all__ = ["dispatch"]


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

    def dispatch(algo):
        def algorithm(func):
            sig = inspect.signature(func)

            @wraps(func)
            def wrapper(*args, **kwds):
                backend = plugins[plugin_name].load()
                bound = sig.bind(*args, **kwds)
                bound.apply_defaults()
                graph, *args = args
                # Convert graph into backend graph-like object
                #   Include the weight label, if provided to the algorithm
                graph = backend.convert(graph, bound.arguments.get("weight"))
                return getattr(backend, algo).__call__(graph, *args, **kwds)

            return wrapper

        return algorithm
