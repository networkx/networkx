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
environment variable ``NETWORKX_TEST_BACKEND`` is set to a registered
plugin keys, the dispatch machinery will automatically convert regular
networkx Graphs and DiGraphs to the backend equivalent by calling
``<backend dispatcher>.convert_from_nx(G, edge_attrs=edge_attrs, name=name)``.
Set ``NETWORKX_TEST_FALLBACK_TO_NX`` environment variable to have tests
use networkx graphs for algorithms not implemented by the backend.

The arguments to ``convert_from_nx`` are:

- ``G`` : networkx Graph
- ``edge_attrs`` : dict, optional
    Dict that maps edge attributes to default values if missing in ``G``.
    If None, then no edge attributes will be converted and default may be 1.
- ``node_attrs``: dict, optional
    Dict that maps node attribute to default values if missing in ``G``.
    If None, then no node attributes will be converted.
- ``preserve_edge_attrs`` : bool
    Whether to preserve all edge attributes.
- ``preserve_node_attrs`` : bool
    Whether to preserve all node attributes.
- ``preserve_graph_attrs`` : bool
    Whether to preserve all graph attributes.
- ``preserve_all_attrs`` : bool
    Whether to preserve all graph, node, and edge attributes.
- ``name`` : str
    The name of the algorithm.
- ``graph_name`` : str
    The name of the graph argument being converted.
- ``is_testing`` : bool
    Whether the conversion is being done while running NetworkX tests.

The converted object is then passed to the backend implementation of
the algorithm. The result is then passed to
``<backend dispatcher>.convert_to_nx(result, name=name)`` to convert back
to a form expected by the NetworkX tests.

By defining ``convert_from_nx`` and ``convert_to_nx`` methods and setting
the environment variable, NetworkX will automatically route tests on
dispatchable algorithms to the backend, allowing the full networkx test
suite to be run against the backend implementation.

Example pytest invocation::

    NETWORKX_TEST_BACKEND=sparse pytest --pyargs networkx

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


class _dispatch:
    """Dispatches to a backend algorithm based on input graph types.

    Parameters
    ----------
    func : function

    name : str, optional
        The name of the algorithm to use for dispatching. If not provided,
        the name of ``func`` will be used. ``name`` is useful to avoid name
        conflicts, as all dispatched algorithms live in a single namespace.

    graphs : str or dict, default "G"
        If a string, the parameter name of the graph, which must be the first
        argument of the wrapped function. If more than one graph is required
        for the algorithm (or if the graph is not the first argument), provide
        a dict of parameter name to argument position for each graph argument.
        For example, ``@_dispatch(graphs={"G": 0, "auxiliary?": 4})``
        indicates the 0th parameter ``G`` of the function is a required graph,
        and the 4th parameter ``auxiliary`` is an optional graph.
        To indicate an argument is a list of graphs, do e.g. ``"[graphs]"``.

    edge_attrs : str or dict, optional
        ``edge_attrs`` holds information about edge attribute arguments
        and default values for those edge attributes.
        If a string, ``edge_attrs`` holds the function argument name that
        indicates a single edge attribute to include in the converted graph.
        The default value for this attribute is 1. To indicate that an argument
        is a list of attributes (all with deafult value 1), use e.g. ``"[attrs]"``.
        If a dict, ``edge_attrs`` holds a dict keyed by argument names, with
        values that are either the default value or, if a string, the argument
        name that indicates the default value.

    node_attrs : str or dict, optional
        Like ``edge_attrs``, but for node attributes.

    preserve_edge_attrs : bool or str or dict, optional
        For bool, whether to preserve all edge attributes.
        For str, the parameter name that may indicate (with ``True`` or a
        callable argument) whether all edge attributes should be preserved
        when converting.
        For dict of ``{graph_name: {attr: default}}``, indicate pre-determined
        edge attributes (and defaults) to preserve for input graphs.

    preserve_node_attrs : bool or str or dict, optional
        Like ``preserve_edge_attrs``, but for node attributes.

    preserve_graph_attrs : bool or set
        For bool, whether to preserve all graph attributes.
        For set, which input graph arguments to preserve graph attributes.

    preserve_all_attrs : bool
        Whether to preserve all edge, node and graph attributes.
        This overrides all the other preserve_*_attrs.

    """

    # Allow any of the following decorator forms:
    #  - @_dispatch
    #  - @_dispatch()
    #  - @_dispatch(name="override_name")
    #  - @_dispatch(graphs="graph")
    #  - @_dispatch(edge_attrs="weight")
    #  - @_dispatch(graphs={"G": 0, "H": 1}, edge_attrs={"weight": "default"})

    # These class attributes are currently used to allow backends to run networkx tests.
    # For example: `PYTHONPATH=. pytest --backend graphblas --fallback-to-nx`
    _is_testing = False
    _fallback_to_nx = False
    _plugin_name = None

    def __new__(
        cls,
        func=None,
        *,
        name=None,
        graphs="G",
        edge_attrs=None,
        node_attrs=None,
        preserve_edge_attrs=False,
        preserve_node_attrs=False,
        preserve_graph_attrs=False,
        preserve_all_attrs=False,
    ):
        if func is None:
            return functools.partial(
                _dispatch,
                name=name,
                graphs=graphs,
                edge_attrs=edge_attrs,
                node_attrs=node_attrs,
                preserve_edge_attrs=preserve_edge_attrs,
                preserve_node_attrs=preserve_node_attrs,
                preserve_graph_attrs=preserve_graph_attrs,
                preserve_all_attrs=preserve_all_attrs,
            )
        if isinstance(func, str):
            raise TypeError("'name' and 'graphs' must be passed by keyword") from None
        # If name not provided, use the name of the function
        if name is None:
            name = func.__name__

        self = object.__new__(cls)

        # Make it look like the original function
        functools.update_wrapper(self, func)
        self.__defaults__ = func.__defaults__
        self.__kwdefaults__ = func.__kwdefaults__

        self.orig_func = func
        self.name = name
        self.edge_attrs = edge_attrs
        self.node_attrs = node_attrs
        self.preserve_edge_attrs = preserve_edge_attrs or preserve_all_attrs
        self.preserve_node_attrs = preserve_node_attrs or preserve_all_attrs
        self.preserve_graph_attrs = preserve_graph_attrs or preserve_all_attrs

        if isinstance(graphs, str):
            graphs = {graphs: 0}
        elif len(graphs) == 0:
            raise KeyError("'graphs' must contain at least one variable name") from None

        # This dict comprehension is complicated for better performance; equivalent shown below.
        self.optional_graphs = set()
        self.list_graphs = set()
        self.graphs = {
            self.optional_graphs.add(val := k[:-1]) or val
            if (last := k[-1]) == "?"
            else self.list_graphs.add(val := k[1:-1]) or val
            if last == "]"
            else k: v
            for k, v in graphs.items()
        }
        # The above is equivalent to:
        # self.optional_graphs = {k[:-1] for k in graphs if k[-1] == "?"}
        # self.list_graphs = {k[1:-1] for k in graphs if k[-1] == "]"}
        # self.graphs = {k[:-1] if k[-1] == "?" else k: v for k, v in graphs.items()}

        sig = inspect.signature(func)
        if not any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        ):
            sig = sig.replace(
                parameters=[
                    *sig.parameters.values(),
                    inspect.Parameter("backend_kwargs", inspect.Parameter.VAR_KEYWORD),
                ]
            )
        self.__signature__ = sig

        if name in _registered_algorithms:
            raise KeyError(f"Algorithm already exists in dispatch registry: {name}")
        _registered_algorithms[name] = self
        return self

    def __call__(self, *args, **kwargs):
        graphs_resolved = {}
        for gname, pos in self.graphs.items():
            if pos < len(args):
                if gname in kwargs:
                    raise TypeError(
                        f"{self.name}() got multiple values for {gname!r}"
                    ) from None
                val = args[pos]
            elif gname in kwargs:
                val = kwargs[gname]
            elif gname not in self.optional_graphs:
                raise TypeError(
                    f"{self.name}() missing required graph argument: {gname}"
                ) from None
            else:
                continue
            if val is None:
                if gname not in self.optional_graphs:
                    raise TypeError(
                        f"{self.name}() required graph argument {gname!r} is None; must be a graph"
                    ) from None
            else:
                graphs_resolved[gname] = val

        # Alternative to the above that does not check duplicated args or missing required graphs.
        # graphs_resolved = {
        #     val
        #     for gname, pos in self.graphs.items()
        #     if (val := args[pos] if pos < len(args) else kwargs.get(gname)) is not None
        # }

        if self._is_testing and self._plugin_name is not None:
            # Can we use graphs_resolved here?
            return self._convert_and_call(
                self._plugin_name,
                args,
                kwargs,
                is_testing=True,
                fallback_to_nx=self._fallback_to_nx,
            )

        # Check if any graph comes from a plugin
        if self.list_graphs:
            # Make sure we don't lose values by consuming an iterator
            args = list(args)
            for gname in self.list_graphs & graphs_resolved.keys():
                val = list(graphs_resolved[gname])
                graphs_resolved[gname] = val
                if gname in kwargs:
                    kwargs[gname] = val
                else:
                    args[self.graphs[gname]] = val

            has_plugins = any(
                hasattr(g, "__networkx_plugin__")
                if gname not in self.list_graphs
                else any(hasattr(g2, "__networkx_plugin__") for g2 in g)
                for gname, g in graphs_resolved.items()
            )
            if has_plugins:
                plugin_names = {
                    getattr(g, "__networkx_plugin__", "networkx")
                    for gname, g in graphs_resolved.items()
                    if gname not in self.list_graphs
                }
                for gname in self.list_graphs & graphs_resolved.keys():
                    plugin_names.update(
                        getattr(g, "__networkx_plugin__", "networkx")
                        for g in graphs_resolved[gname]
                    )
        else:
            has_plugins = any(
                hasattr(g, "__networkx_plugin__") for g in graphs_resolved.values()
            )
            plugin_names = {
                getattr(g, "__networkx_plugin__", "networkx")
                for g in graphs_resolved.values()
            }
        if has_plugins:
            if len(plugin_names) != 1:
                raise TypeError(
                    f"{self.name}() graphs must all be from the same plugin, found {plugin_names}"
                ) from None
            [plugin_name] = plugin_names
            if plugin_name not in plugins:
                raise ImportError(f"Unable to load plugin: {plugin_name}") from None
            backend = plugins[plugin_name].load()
            if hasattr(backend, self.name):
                return getattr(backend, self.name)(*args, **kwargs)
            raise NetworkXNotImplemented(
                f"'{self.name}' not implemented by {plugin_name}"
            )
        return self.orig_func(*args, **kwargs)

    def _convert_and_call(
        self, plugin_name, args, kwargs, *, is_testing=False, fallback_to_nx=False
    ):
        """Call this dispatchable function with a plugin."""
        backend = plugins[plugin_name].load()
        if not hasattr(backend, self.name):
            if fallback_to_nx:
                return self.orig_func(*args, **kwargs)
            msg = f"'{self.name}' not implemented by {plugin_name}"
            if is_testing:
                import pytest

                pytest.xfail(msg)
            raise RuntimeError(msg)

        bound = self.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        # Check that graph names are actually in the signature
        if set(self.graphs) - set(bound.arguments):
            raise KeyError(
                f"Invalid graph names: {set(self.graphs) - set(bound.arguments)}"
            )
        # Convert graphs into backend graph-like object
        #   Include the edge and/or node labels if provided to the algorithm
        preserve_edge_attrs = self.preserve_edge_attrs
        edge_attrs = self.edge_attrs
        if preserve_edge_attrs is False:
            # e.g. `preserve_edge_attrs=False`
            pass
        elif preserve_edge_attrs is True:
            # e.g. `preserve_edge_attrs=True`
            edge_attrs = None
        elif isinstance(preserve_edge_attrs, str):
            if bound.arguments[preserve_edge_attrs] is True or callable(
                bound.arguments[preserve_edge_attrs]
            ):
                # e.g. `preserve_edge_attrs="attr"` and `func(attr=True)`
                # e.g. `preserve_edge_attrs="attr"` and `func(attr=myfunc)`
                preserve_edge_attrs = True
                edge_attrs = None
            elif bound.arguments[preserve_edge_attrs] is False and (
                isinstance(edge_attrs, str)
                and edge_attrs == preserve_edge_attrs
                or isinstance(edge_attrs, dict)
                and preserve_edge_attrs in edge_attrs
            ):
                # e.g. `preserve_edge_attrs="attr"` and `func(attr=False)`
                # Treat `False` argument as meaning "preserve_edge_data=False"
                # and not `False` as the edge attribute to use.
                preserve_edge_attrs = False
                edge_attrs = None
            else:
                # e.g. `preserve_edge_attrs="attr"` and `func(attr="weight")`
                preserve_edge_attrs = False
        elif not isinstance(preserve_edge_attrs, dict):
            raise TypeError(
                f"Bad type for preserve_edge_attrs: {type(self.preserve_edge_attrs)}"
            )
            # e.g. `preserve_edge_attrs={"G": {"weight": 1}}`

        if edge_attrs is None:
            # May have been set to None above b/c all attributes are preserved
            pass
        elif isinstance(edge_attrs, str):
            if edge_attrs[0] == "[":
                # e.g. `edge_attrs="[edge_attributes]"` (argument of list of attributes)
                # e.g. `func(edge_attributes=["foo", "bar"])`
                edge_attrs = {
                    edge_attr: 1 for edge_attr in bound.arguments[edge_attrs[1:-1]]
                }
            elif callable(bound.arguments[edge_attrs]):
                # e.g. `edge_attrs="weight"` and `func(weight=myfunc)`
                preserve_edge_attrs = True
                edge_attrs = None
            elif bound.arguments[edge_attrs] is not None:
                # e.g. `edge_attrs="weight"` and `func(weight="foo")` (default of 1)
                edge_attrs = {bound.arguments[edge_attrs]: 1}
            elif self.name == "to_numpy_array" and hasattr(
                bound.arguments["dtype"], "names"
            ):
                # Custom handling: attributes may be obtained from `dtype`
                edge_attrs = {
                    edge_attr: 1 for edge_attr in bound.arguments["dtype"].names
                }
            else:
                # e.g. `edge_attrs="weight"` and `func(weight=None)`
                edge_attrs = None
        elif isinstance(edge_attrs, dict):
            # e.g. `edge_attrs={"attr": "default"}` and `func(attr="foo", default=7)`
            # e.g. `edge_attrs={"attr": 0}` and `func(attr="foo")`
            edge_attrs = {
                edge_attr: bound.arguments.get(val, 1) if isinstance(val, str) else val
                for key, val in edge_attrs.items()
                if (edge_attr := bound.arguments[key]) is not None
            }
        else:
            raise TypeError(f"Bad type for edge_attrs: {type(self.edge_attrs)}")

        preserve_node_attrs = self.preserve_node_attrs
        node_attrs = self.node_attrs
        if preserve_node_attrs is False:
            # e.g. `preserve_node_attrs=False`
            pass
        elif preserve_node_attrs is True:
            # e.g. `preserve_node_attrs=True`
            node_attrs = None
        elif isinstance(preserve_node_attrs, str):
            if bound.arguments[preserve_node_attrs] is True or callable(
                bound.arguments[preserve_node_attrs]
            ):
                # e.g. `preserve_node_attrs="attr"` and `func(attr=True)`
                # e.g. `preserve_node_attrs="attr"` and `func(attr=myfunc)`
                preserve_node_attrs = True
                node_attrs = None
            elif bound.arguments[preserve_node_attrs] is False and (
                isinstance(node_attrs, str)
                and node_attrs == preserve_node_attrs
                or isinstance(node_attrs, dict)
                and preserve_node_attrs in node_attrs
            ):
                # e.g. `preserve_node_attrs="attr"` and `func(attr=False)`
                # Treat `False` argument as meaning "preserve_node_data=False"
                # and not `False` as the node attribute to use. Is this used?
                preserve_node_attrs = False
                node_attrs = None
            else:
                # e.g. `preserve_node_attrs="attr"` and `func(attr="weight")`
                preserve_node_attrs = False
        elif not isinstance(preserve_node_attrs, dict):
            raise TypeError(
                f"Bad type for preserve_node_attrs: {type(self.preserve_node_attrs)}"
            )
            # e.g. `preserve_node_attrs={"G": {"pos": None}}`

        if node_attrs is None:
            # May have been set to None above b/c all attributes are preserved
            pass
        elif isinstance(node_attrs, str):
            if node_attrs[0] == "[":
                # e.g. `node_attrs="[node_attributes]"` (argument of list of attributes)
                # e.g. `func(node_attributes=["foo", "bar"])`
                node_attrs = {
                    node_attr: None for node_attr in bound.arguments[node_attrs[1:-1]]
                }
            elif callable(bound.arguments[node_attrs]):
                # e.g. `node_attrs="weight"` and `func(weight=myfunc)`
                preserve_node_attrs = True
                node_attrs = None
            elif bound.arguments[node_attrs] is not None:
                # e.g. `node_attrs="weight"` and `func(weight="foo")`
                node_attrs = {bound.arguments[node_attrs]: None}
            else:
                # e.g. `node_attrs="weight"` and `func(weight=None)`
                node_attrs = None
        elif isinstance(node_attrs, dict):
            # e.g. `node_attrs={"attr": "default"}` and `func(attr="foo", default=7)`
            # e.g. `node_attrs={"attr": 0}` and `func(attr="foo")`
            node_attrs = {
                node_attr: bound.arguments.get(val) if isinstance(val, str) else val
                for key, val in node_attrs.items()
                if (node_attr := bound.arguments[key]) is not None
            }
        else:
            raise TypeError(f"Bad type for node_attrs: {type(self.node_attrs)}")

        preserve_graph_attrs = self.preserve_graph_attrs
        if not isinstance(preserve_graph_attrs, (bool, set)):
            raise TypeError(
                f"Bad type for preserve_graph_attrs: {type(self.preserve_graph_attrs)}"
            )

        for gname in self.graphs:
            if gname in self.list_graphs:
                bound.arguments[gname] = [
                    backend.convert_from_nx(
                        g,
                        edge_attrs=edge_attrs,
                        node_attrs=node_attrs,
                        preserve_edge_attrs=preserve_edge_attrs,
                        preserve_node_attrs=preserve_node_attrs,
                        preserve_graph_attrs=preserve_graph_attrs,
                        name=self.name,
                        graph_name=gname,
                        is_testing=is_testing,
                    )
                    for g in bound.arguments[gname]
                ]
            else:
                graph = bound.arguments[gname]
                if graph is None:
                    if gname in self.optional_graphs:
                        continue
                    raise TypeError(
                        f"Missing required graph argument `{gname}` in {self.name} function"
                    )
                if isinstance(preserve_edge_attrs, dict):
                    preserve_edges = False
                    edges = preserve_edge_attrs.get(gname, edge_attrs)
                else:
                    preserve_edges = preserve_edge_attrs
                    edges = edge_attrs
                if isinstance(preserve_node_attrs, dict):
                    preserve_nodes = False
                    nodes = preserve_node_attrs.get(gname, node_attrs)
                else:
                    preserve_nodes = preserve_node_attrs
                    nodes = node_attrs
                if isinstance(preserve_graph_attrs, set):
                    preserve_graph = gname in preserve_graph_attrs
                else:
                    preserve_graph = preserve_graph_attrs
                bound.arguments[gname] = backend.convert_from_nx(
                    graph,
                    edge_attrs=edges,
                    node_attrs=nodes,
                    preserve_edge_attrs=preserve_edges,
                    preserve_node_attrs=preserve_nodes,
                    preserve_graph_attrs=preserve_graph,
                    name=self.name,
                    graph_name=gname,
                    is_testing=is_testing,
                )

        try:
            result = getattr(backend, self.name)(*bound.args, **bound.kwargs)
        except (NotImplementedError, NetworkXNotImplemented) as exc:
            if fallback_to_nx:
                return self.orig_func(*args, **kwargs)
            if is_testing:
                import pytest

                pytest.xfail(
                    exc.args[0] if exc.args else f"{name} raised {type(exc).__name__}"
                )
            raise

        if is_testing and self.name in {
            "edmonds_karp_core",
            "barycenter",
            "contracted_nodes",
            "stochastic_graph",
            "relabel_nodes",
        }:
            # For testing, special-case algorithms that mutate input graphs
            if self.name == "edmonds_karp_core":
                R1 = backend.convert_to_nx(bound.arguments["R"])
                bound2 = self.__signature__.bind(*args, **kwargs)
                bound2.apply_defaults()
                R2 = bound2.arguments["R"]
                for k, v in R1.edges.items():
                    R2.edges[k]["flow"] = v["flow"]
            elif self.name == "barycenter" and bound.arguments["attr"] is not None:
                G1 = backend.convert_to_nx(bound.arguments["G"])
                bound2 = self.__signature__.bind(*args, **kwargs)
                bound2.apply_defaults()
                G2 = bound2.arguments["G"]
                attr = bound.arguments["attr"]
                for k, v in G1.nodes.items():
                    G2.nodes[k][attr] = v[attr]
            elif self.name == "contracted_nodes" and not bound.arguments["copy"]:
                # Edges and nodes changed; node "contraction" and edge "weight" attrs
                G1 = backend.convert_to_nx(bound.arguments["G"])
                bound2 = self.__signature__.bind(*args, **kwargs)
                bound2.apply_defaults()
                G2 = bound2.arguments["G"]
                G2.__dict__.update(G1.__dict__)
            elif self.name == "stochastic_graph" and not bound.arguments["copy"]:
                G1 = backend.convert_to_nx(bound.arguments["G"])
                bound2 = self.__signature__.bind(*args, **kwargs)
                bound2.apply_defaults()
                G2 = bound2.arguments["G"]
                for k, v in G1.edges.items():
                    G2.edges[k]["weight"] = v["weight"]
            elif self.name == "relabel_nodes" and not bound.arguments["copy"]:
                G1 = backend.convert_to_nx(bound.arguments["G"])
                bound2 = self.__signature__.bind(*args, **kwargs)
                bound2.apply_defaults()
                G2 = bound2.arguments["G"]
                if G1 is G2:
                    return G2
                G2._node.clear()
                G2._node.update(G1._node)
                G2._adj.clear()
                G2._adj.update(G1._adj)
                if hasattr(G1, "_pred") and hasattr(G2, "_pred"):
                    G2._pred.clear()
                    G2._pred.update(G1._pred)
                if hasattr(G1, "_succ") and hasattr(G2, "_succ"):
                    G2._succ.clear()
                    G2._succ.update(G1._succ)
                return G2

        if is_testing:
            return backend.convert_to_nx(result, name=self.name)
        return result
