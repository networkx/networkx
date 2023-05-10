"""
Code to support various backends in a plugin dispatch architecture.

Create a Dispatcher
-------------------

To be a valid plugin, a package must register an entry_point
of `networkx.plugins` with a key pointing to the handler.

For example::

    entry_points={'networkx.plugins': 'sparse = networkx_plugin_sparse'}

The plugin must create a Graph-like object which contains an attribute
``__networkx_plugin__`` with a value of the entry point name.

Continuing the example above::

    class WrappedSparse:
        __networkx_plugin__ = "sparse"
        ...

When a dispatchable NetworkX algorithm encounters a Graph-like object
with a ``__networkx_plugin__`` attribute, it will look for the associated
dispatch object in the entry_points, load it, and dispatch the work to it.


Testing
-------
To assist in validating the backend algorithm implementations, if an
environment variable ``NETWORKX_GRAPH_CONVERT`` is set to a registered
plugin keys, the dispatch machinery will automatically convert regular
networkx Graphs and DiGraphs to the backend equivalent by calling
``<backend dispatcher>.convert_from_nx(G, weight=weight, name=name)``.

The converted object is then passed to the backend implementation of
the algorithm. The result is then passed to
``<backend dispatcher>.convert_to_nx(result, name=name)`` to convert back
to a form expected by the NetworkX tests.

By defining ``convert_from_nx`` and ``convert_to_nx`` methods and setting
the environment variable, NetworkX will automatically route tests on
dispatchable algorithms to the backend, allowing the full networkx test
suite to be run against the backend implementation.

Example pytest invocation::

    NETWORKX_GRAPH_CONVERT=sparse pytest --pyargs networkx

Dispatchable algorithms which are not implemented by the backend
will cause a ``pytest.xfail()``, giving some indication that not all
tests are working, while avoiding causing an explicit failure.

A special ``on_start_tests(items)`` function may be defined by the backend.
It will be called with the list of NetworkX tests discovered. Each item
is a test object that can be marked as xfail if the backend does not support
the test using `item.add_marker(pytest.mark.xfail(reason=...))`.
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


def _dispatch(func=None, *, name=None, graphs="G"):
    """Dispatches to a backend algorithm
    when the first argument is a backend graph-like object.

    The algorithm name is assumed to be the name of the wrapped function unless
    `name` is provided. This is useful to avoid name conflicts, as all
    dispatched algorithms live in a single namespace.

    If more than one graph is required for the algorithm, provide a comma-separated
    string of variable names as `graphs`. These must be the same order and name
    as the variables passed to the algorithm. Dispatching does not support graphs
    which are not the first argument(s) to an algorithm.
    """
    # Allow any of the following decorator forms:
    #  - @_dispatch
    #  - @_dispatch()
    #  - @_dispatch(name="override_name")
    #  - @_dispatch(graphs="G,H")
    #  - @_dispatch(name="override_name", graphs="G,H")
    if func is None:
        if name is None and graphs == "G":
            return _dispatch
        return functools.partial(_dispatch, name=name, graphs=graphs)
    if isinstance(func, str):
        raise TypeError("'name' and 'graphs' must be passed by keyword") from None
    # If name not provided, use the name of the function
    if name is None:
        name = func.__name__

    graph_list = [g.strip() for g in graphs.split(",")]
    if len(graph_list) <= 0:
        raise KeyError("'graphs' must contain at least one variable name") from None

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        # Select overlap of args and graph_list
        graphs_resolved = dict(zip(graph_list, args))
        # Check for duplicates from kwds
        dups = set(kwds) & set(graphs_resolved)
        if dups:
            raise KeyError(f"{name}() got multiple values for {dups}") from None
        # Add items from kwds
        for gname in graph_list[len(graphs_resolved) :]:
            if gname not in kwds:
                raise TypeError(
                    f"{name}() missing required graph argument: {gname}"
                ) from None
            graphs_resolved[gname] = kwds[gname]
        # Check if any graph comes from a plugin
        if any(hasattr(g, "__networkx_plugin__") for g in graphs_resolved.values()):
            # Find common plugin name
            plugin_names = {
                getattr(g, "__networkx_plugin__", "networkx")
                for g in graphs_resolved.values()
            }
            if len(plugin_names) != 1:
                raise TypeError(
                    f"{name}() graphs must all be from the same plugin, found {plugin_names}"
                ) from None
            plugin_name = plugin_names.pop()
            if plugin_name not in plugins:
                raise ImportError(f"Unable to load plugin: {plugin_name}") from None
            backend = plugins[plugin_name].load()
            if hasattr(backend, name):
                return getattr(backend, name).__call__(*args, **kwds)
            else:
                raise NetworkXNotImplemented(
                    f"'{name}' not implemented by {plugin_name}"
                )
        return func(*args, **kwds)

    # Keep a handle to the original function to use when testing
    # the dispatch mechanism internally
    wrapper._orig_func = func

    _register_algo(name, wrapper)
    return wrapper


def test_override_dispatch(func=None, *, name=None, graphs="G"):
    """Auto-converts graph arguments into the backend equivalent,
    causing the dispatching mechanism to trigger for every
    decorated algorithm."""
    if func is None:
        if name is None and graphs == "G":
            return _dispatch
        return functools.partial(_dispatch, name=name, graphs=graphs)
    if isinstance(func, str):
        raise TypeError("'name' and 'graphs' must be passed by keyword") from None
    # If name not provided, use the name of the function
    if name is None:
        name = func.__name__

    graph_list = [g.strip() for g in graphs.split(",")]
    if len(graph_list) <= 0:
        raise ValueError("'graphs' must contain at least one variable name") from None

    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        backend = plugins[plugin_name].load()
        if not hasattr(backend, name):
            if plugin_name == "nx-loopback":
                raise NetworkXNotImplemented(
                    f"'{name}' not found in {backend.__class__.__name__}"
                )
            pytest.xfail(f"'{name}' not implemented by {plugin_name}")
        bound = sig.bind(*args, **kwds)
        bound.apply_defaults()
        # Check that graph names are actually in the signature
        if set(graph_list) - set(bound.arguments):
            raise KeyError(
                f"Invalid graph names: {set(graph_list) - set(bound.arguments)}"
            )
        # Convert graphs into backend graph-like object
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
        for gname in graph_list:
            bound.arguments[gname] = backend.convert_from_nx(
                bound.arguments[gname], weight=weight, name=name
            )
        result = getattr(backend, name).__call__(**bound.arguments)
        return backend.convert_to_nx(result, name=name)

    wrapper._orig_func = func
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
