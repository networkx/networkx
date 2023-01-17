"""
Code to support various backends in a plugin dispatch architecture.

Create a Dispatcher
-------------------

To be a valid plugin, a package must register an entry_point
of `networkx.plugins` with a key pointing to the handler.

For example:

```
entry_points={'networkx.plugins': 'sparse = networkx_plugin_sparse'}
```

The plugin must create a Graph-like object which contains an attribute
`__networkx_plugin__` with a value of the entry point name.

Continuing the example above:

```
class WrappedSparse:
    __networkx_plugin__ = "sparse"
    ...
```

When a dispatchable NetworkX algorithm encounters a Graph-like object
with a `__networkx_plugin__` attribute, it will look for the associated
dispatch object in the entry_points, load it, and dispatch the work to it.


Testing
-------
To assist in validating the backend algorithm implementations, if an
environment variable `NETWORKX_GRAPH_CONVERT` is set to a registered
plugin keys, the dispatch machinery will automatically convert regular
networkx Graphs and DiGraphs to the backend equivalent by calling
`<backend dispatcher>.convert_from_nx(G, weight=weight, name=name)`.

The converted object is then passed to the backend implementation of
the algorithm. The result is then passed to
`<backend dispatcher>.convert_to_nx(result, name=name)` to convert back
to a form expected by the NetworkX tests.

By defining `convert_from_nx` and `convert_to_nx` methods and setting
the environment variable, NetworkX will automatically route tests on
dispatchable algorithms to the backend, allowing the full networkx test
suite to be run against the backend implementation.

Example pytest invocation:
NETWORKX_GRAPH_CONVERT=sparse pytest --pyargs networkx

Dispatchable algorithms which are not implemented by the backend
will cause a `pytest.xfail()`, giving some indication that not all
tests are working, while avoiding causing an explicit failure.

A special `on_start_tests(items)` function may be defined by the backend.
It will be called with the list of NetworkX tests discovered. Each item
is a pytest.Node object. If the backend does not support the test, that
test can be marked as xfail.
"""
import functools
import inspect
import os
import sys
from importlib.metadata import entry_points

from ..exception import NetworkXNotImplemented

__all__ = ["_dispatch", "_mark_tests"]


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
_registered_algorithms = {}


def _register_algo(name, wrapped_func):
    if name in _registered_algorithms:
        raise KeyError(f"Algorithm already exists in dispatch registry: {name}")
    _registered_algorithms[name] = wrapped_func
    wrapped_func.dispatchname = name


def _dispatch(func=None, *, name=None):
    """Dispatches to a backend algorithm
    when the first argument is a backend graph-like object.
    """
    # Allow any of the following decorator forms:
    #  - @_dispatch
    #  - @_dispatch()
    #  - @_dispatch("override_name")
    #  - @_dispatch(name="override_name")
    if func is None:
        if name is None:
            return _dispatch
        return functools.partial(_dispatch, name=name)
    if isinstance(func, str):
        return functools.partial(_dispatch, name=func)
    # If name not provided, use the name of the function
    if name is None:
        name = func.__name__

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        graph = args[0]
        if hasattr(graph, "__networkx_plugin__") and plugins:
            plugin_name = graph.__networkx_plugin__
            if plugin_name in plugins:
                backend = plugins[plugin_name].load()
                if hasattr(backend, name):
                    return getattr(backend, name).__call__(*args, **kwds)
                else:
                    raise NetworkXNotImplemented(
                        f"'{name}' not implemented by {plugin_name}"
                    )
        return func(*args, **kwds)

    _register_algo(name, wrapper)
    return wrapper


def test_override_dispatch(func=None, *, name=None):
    """Auto-converts the first argument into the backend equivalent,
    causing the dispatching mechanism to trigger for every
    decorated algorithm."""
    if func is None:
        if name is None:
            return test_override_dispatch
        return functools.partial(test_override_dispatch, name=name)
    if isinstance(func, str):
        return functools.partial(test_override_dispatch, name=func)
    # If name not provided, use the name of the function
    if name is None:
        name = func.__name__

    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        backend = plugins[plugin_name].load()
        if not hasattr(backend, name):
            pytest.xfail(f"'{name}' not implemented by {plugin_name}")
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
            if isinstance(bound.arguments["data"], str):
                weight = bound.arguments["data"]
            elif bound.arguments["data"]:
                weight = "weight"
        graph = backend.convert_from_nx(graph, weight=weight, name=name)
        result = getattr(backend, name).__call__(graph, *args, **kwds)
        return backend.convert_to_nx(result, name=name)

    _register_algo(name, wrapper)
    return wrapper


# Check for auto-convert testing
# This allows existing NetworkX tests to be run against a backend
# implementation without any changes to the testing code. The only
# required change is to set an environment variable prior to running
# pytest.
if os.environ.get("NETWORKX_GRAPH_CONVERT"):
    plugin_name = os.environ["NETWORKX_GRAPH_CONVERT"]
    if not plugins:
        raise Exception("No registered networkx.plugins entry_points")
    if plugin_name not in plugins:
        raise Exception(
            f"No registered networkx.plugins entry_point named {plugin_name}"
        )

    try:
        import pytest
    except ImportError:
        raise ImportError(
            f"Missing pytest, which is required when using NETWORKX_GRAPH_CONVERT"
        )

    # Override `dispatch` for testing
    _dispatch = test_override_dispatch


def _mark_tests(items):
    """Allow backend to mark tests (skip or xfail) if they aren't able to correctly handle them"""
    if os.environ.get("NETWORKX_GRAPH_CONVERT"):
        plugin_name = os.environ["NETWORKX_GRAPH_CONVERT"]
        backend = plugins[plugin_name].load()
        if hasattr(backend, "on_start_tests"):
            getattr(backend, "on_start_tests")(items)
