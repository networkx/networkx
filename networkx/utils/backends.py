"""
Docs for backend users
~~~~~~~~~~~~~~~~~~~~~~

NetworkX utilizes a plugin-dispatch architecture, which means we can plug in and
out of backends with minimal code changes. A valid NetworkX backend specifies
`entry points <https://packaging.python.org/en/latest/specifications/entry-points>`_,
named ``networkx.backends`` and an optional ``networkx.backend_info`` when it is
installed (not imported). This allows NetworkX to dispatch (redirect) function calls
to the backend so the execution flows to the designated backend
implementation, similar to how plugging a charger into a socket redirects the
electricity to your phone. This design enhances flexibility and integration, making
NetworkX more adaptable and efficient.

There are three main ways to use a backend after the package is installed.
You can set environment variables and run the exact same code you run for
NetworkX. You can use a keyword argument ``backend=...`` with the NetworkX
function. Or, you can convert the NetworkX Graph to a backend graph type and
call a NetworkX function supported by that backend. Environment variables
and backend keywords automatically convert your NetworkX Graph to the
backend type. Manually converting it yourself allows you to use that same
backend graph for more than one function call, reducing conversion time.

For example, you can set an environment variable before starting python to request
all dispatchable functions automatically dispatch to the given backend::

    bash> NETWORKX_AUTOMATIC_BACKENDS=cugraph python my_networkx_script.py

or you can specify the backend as a kwarg::

    nx.betweenness_centrality(G, k=10, backend="parallel")

or you can convert the NetworkX Graph object ``G`` into a Graph-like
object specific to the backend and then pass that in the NetworkX function::

    H = nx_parallel.ParallelGraph(G)
    nx.betweenness_centrality(H, k=10)

The first approach is useful when you don't want to change your NetworkX code and just want
to run your code on different backend(s). The second approach comes in handy when you
need to pass additional backend-specific arguments, for example::

    nx.betweenness_centrality(G, k=10, backend="parallel", get_chunks=get_chunks)

Here, ``get_chunks`` is not a NetworkX argument, but a nx_parallel-specific argument.

How does this work?
-------------------

You might have seen the ``@nx._dispatchable`` decorator on
many of the NetworkX functions in the codebase. This decorator function works
by dispatching a NetworkX function to a specified backend if available, or running
it with NetworkX if no backend is specified or available. It checks if the specified
backend is valid and installed. If not, it raises an ``ImportError``. It also
resolves the graph arguments from the provided ``args`` and ``kwargs``, handling cases
where graphs are passed as positional arguments or keyword arguments. It then checks if
any of the resolved graphs are from a backend by checking if they have a
``__networkx_backend__`` attribute. The attribute ``__networkx_backend__`` holds a
string with the name of the ``entry_point`` (more on them later). If there are graphs
from a backend, it determines the priority of the backends based on the
``backend_priority`` configuration. If there are dispatchable graphs (i.e., graphs from
a backend), it checks if all graphs are from the same backend. If not, it raises a
``TypeError``. If a backend is specified and it matches the backend of the graphs, it
loads the backend and calls the corresponding function on the backend along with the
additional backend-specific ``backend_kwargs``. After calling the function the networkx
logger displays the ``DEBUG`` message, if the logging is enabled
(see :ref:`Introspection <introspect>` below). If no compatible
backend is found or the function is not implemented by the backend, it raises a
``NetworkXNotImplemented`` exception. And, if the function mutates the input graph or
returns a graph, graph generator or loader then it tries to convert and run the
function with a backend with automatic conversion. And it only convert and run if
``backend.should_run(...)`` returns ``True``. If no backend is used, it falls back to
running the original function with NetworkX. Refer the ``__call__`` method of the
``_dispatchable`` class for more details.

The NetworkX library does not need to know that a backend exists for it
to work. As long as the backend package creates the ``entry_point``, and
provides the correct interface, it will be called when the user requests
it using one of the three approaches described above. Some backends have
been working with the NetworkX developers to ensure smooth operation.
They are the following:

- `graphblas <https://github.com/python-graphblas/graphblas-algorithms>`_:
  OpenMP-enabled sparse linear algebra backend.
- `cugraph <https://github.com/rapidsai/cugraph/tree/branch-24.04/python/nx-cugraph>`_:
  GPU-accelerated backend.
- `parallel <https://github.com/networkx/nx-parallel>`_:
  Parallel backend for NetworkX algorithms.
- `loopback <https://github.com/networkx/networkx/blob/main/pyproject.toml#L53>`_:
  It's for testing purposes only and is not a real backend.

Note that the ``backend_name`` is e.g. ``parallel``, the package installed
is ``nx-parallel``, and we use ``nx_parallel`` while importing the package.

.. _introspect:

Introspection
-------------
Introspection techniques aim to demystify dispatching and backend graph conversion behaviors.

The primary way to see what the dispatch machinery is doing is by enabling logging.
This can help you verify that the backend you specified is being used.
You can enable NetworkX's backend logger to print to ``sys.stderr`` like this::

    import logging
    nxl = logging.getLogger("networkx")
    nxl.addHandler(logging.StreamHandler())
    nxl.setLevel(logging.DEBUG)

And you can disable it by running this::

    nxl.setLevel(logging.CRITICAL)

Refer to :external+python:mod:`logging` to learn more about the logging facilities in Python.

By looking at the ``.backends`` attribute, you can get the set of all currently
installed backends that implement a particular function. For example::

    >>> nx.betweenness_centrality.backends  # doctest: +SKIP
    {'parallel'}

The function docstring will also show which installed backends support it
along with any backend-specific notes and keyword arguments::

    >>> help(nx.betweenness_centrality)  # doctest: +SKIP
    ...
    Backends
    --------
    parallel : Parallel backend for NetworkX algorithms
      The parallel computation is implemented by dividing the nodes into chunks
      and computing betweenness centrality for each chunk concurrently.
    ...

The NetworkX documentation website also includes info about trusted backends of NetworkX in function references.
For example, see :func:`~networkx.algorithms.shortest_paths.weighted.all_pairs_bellman_ford_path_length`.

Introspection capabilities are currently limited, but we are working to improve them.
We plan to make it easier to answer questions such as:

- What happened (and why)?
- What *will* happen (and why)?
- Where was time spent (including conversions)?
- What is in the cache and how much memory is it using?

Transparency is essential to allow for greater understanding, debug-ability,
and customization. After all, NetworkX dispatching is extremely flexible and can
support advanced workflows with multiple backends and fine-tuned configuration,
but introspection is necessary to inform *when* and *how* to evolve your workflow
to meet your needs. If you have suggestions for how to improve introspection, please
`let us know <https://github.com/networkx/networkx/issues/new>`_!

Docs for backend developers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating a custom backend
-------------------------

1.  Defining a ``BackendInterface`` object:

    Note that the ``BackendInterface`` doesn't need to must be a class. It can be an
    instance of a class, or a module as well. You can define the following methods or
    functions in your backend's ``BackendInterface`` object.:

    1. ``convert_from_nx`` and ``convert_to_nx`` methods or functions are required for
       backend dispatching to work. The arguments to ``convert_from_nx`` are:

       - ``G`` : NetworkX Graph
       - ``edge_attrs`` : dict, optional
            Dictionary mapping edge attributes to default values if missing in ``G``.
            If None, then no edge attributes will be converted and default may be 1.
       - ``node_attrs``: dict, optional
            Dictionary mapping node attributes to default values if missing in ``G``.
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

    2. ``can_run`` (Optional):
          If your backend only partially implements an algorithm, you can define
          a ``can_run(name, args, kwargs)`` function in your ``BackendInterface`` object that
          returns True or False indicating whether the backend can run the algorithm with
          the given arguments or not. Instead of a boolean you can also return a string
          message to inform the user why that algorithm can't be run.

    3. ``should_run`` (Optional):
          A backend may also define ``should_run(name, args, kwargs)``
          that is similar to ``can_run``, but answers whether the backend *should* be run.
          ``should_run`` is only run when performing backend graph conversions. Like
          ``can_run``, it receives the original arguments so it can decide whether it
          should be run by inspecting the arguments. ``can_run`` runs before
          ``should_run``, so ``should_run`` may assume ``can_run`` is True. If not
          implemented by the backend, ``can_run``and ``should_run`` are assumed to
          always return True if the backend implements the algorithm.

    4. ``on_start_tests`` (Optional):
          A special ``on_start_tests(items)`` function may be defined by the backend.
          It will be called with the list of NetworkX tests discovered. Each item
          is a test object that can be marked as xfail if the backend does not support
          the test using ``item.add_marker(pytest.mark.xfail(reason=...))``.

2.  Adding entry points

    To be discoverable by NetworkX, your package must register an
    `entry-point <https://packaging.python.org/en/latest/specifications/entry-points>`_
    ``networkx.backends`` in the package's metadata, with a `key pointing to your
    dispatch object <https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata>`_ .
    For example, if you are using ``setuptools`` to manage your backend package,
    you can `add the following to your pyproject.toml file <https://setuptools.pypa.io/en/latest/userguide/entry_point.html>`_::

        [project.entry-points."networkx.backends"]
        backend_name = "your_backend_interface_object"

    You can also add the ``backend_info`` entry-point. It points towards the ``get_info``
    function that returns all the backend information, which is then used to build the
    "Additional Backend Implementation" box at the end of algorithm's documentation
    page. Note that the `get_info` function shouldn't import your backend package.::

        [project.entry-points."networkx.backend_info"]
        backend_name = "your_get_info_function"

    The ``get_info`` should return a dictionary with following key-value pairs:
        - ``backend_name`` : str or None
            It is the name passed in the ``backend`` kwarg.
        - ``project`` : str or None
            The name of your backend project.
        - ``package`` : str or None
            The name of your backend package.
        - ``url`` : str or None
            This is the url to either your backend's codebase or documentation, and
            will be displayed as a hyperlink to the ``backend_name``, in the
            "Additional backend implementations" section.
        - ``short_summary`` : str or None
            One line summary of your backend which will be displayed in the
            "Additional backend implementations" section.
        - ``default_config`` : dict
            A dictionary mapping the backend config parameter names to their default values.
            This is used to automatically initialize the default configs for all the
            installed backends at the time of networkx's import.

            .. seealso:: `~networkx.utils.configs.Config`

        - ``functions`` : dict or None
            A dictionary mapping function names to a dictionary of information
            about the function. The information can include the following keys:

            - ``url`` : str or None
              The url to ``function``'s source code or documentation.
            - ``additional_docs`` : str or None
              A short description or note about the backend function's
              implementation.
            - ``additional_parameters`` : dict or None
              A dictionary mapping additional parameters headers to their
              short descriptions. For example::

                  "additional_parameters": {
                      'param1 : str, function (default = "chunks")' : "...",
                      'param2 : int' : "...",
                  }

            If any of these keys are not present, the corresponding information
            will not be displayed in the "Additional backend implementations"
            section on NetworkX docs website.

        Note that your backend's docs would only appear on the official NetworkX docs only
        if your backend is a trusted backend of NetworkX, and is present in the
        `.circleci/config.yml` and `.github/workflows/deploy-docs.yml` files in the
        NetworkX repository.

3.  Defining a Backend Graph class

    The backend must create an object with an attribute ``__networkx_backend__`` that holds
    a string with the entry point name::

        class BackendGraph:
            __networkx_backend__ = "backend_name"
            ...

    A backend graph instance may have a ``G.__networkx_cache__`` dict to enable
    caching, and care should be taken to clear the cache when appropriate.

Testing the Custom backend
--------------------------

To test your custom backend, you can run the NetworkX test suite on your backend.
This also ensures that the custom backend is compatible with NetworkX's API.
The following steps will help you run the tests:

1. Setting Backend Environment Variables:
    - ``NETWORKX_TEST_BACKEND`` : Setting this to your backend's ``backend_name`` will
      let NetworkX's dispatch machinery to automatically convert a regular NetworkX
      ``Graph``, ``DiGraph``, ``MultiGraph``, etc. to their backend equivalents, using
      ``your_backend_interface_object.convert_from_nx(G, ...)`` function.
    - ``NETWORKX_FALLBACK_TO_NX`` (default=False) : Setting this variable to `True` will
      instruct tests to use a NetworkX ``Graph`` for algorithms not implemented by your
      custom backend. Setting this to `False` will only run the tests for algorithms
      implemented by your custom backend and tests for other algorithms will ``xfail``.

2. Running Tests:
    You can invoke NetworkX tests for your custom backend with the following commands::

        NETWORKX_TEST_BACKEND=<backend_name>
        NETWORKX_FALLBACK_TO_NX=True # or False
        pytest --pyargs networkx

How tests are run?
------------------

1. While dispatching to the backend implementation the ``_convert_and_call`` function
   is used and while testing the ``_convert_and_call_for_tests`` function is used.
   Other than testing it also checks for functions that return numpy scalars, and
   for functions that return graphs it runs the backend implementation and the
   networkx implementation and then converts the backend graph into a NetworkX graph
   and then compares them, and returns the networkx graph. This can be regarded as
   (pragmatic) technical debt. We may replace these checks in the future.

2. Conversions while running tests:
    - Convert NetworkX graphs using ``<your_backend_interface_object>.convert_from_nx(G, ...)`` into
      the backend graph.
    - Pass the backend graph objects to the backend implementation of the algorithm.
    - Convert the result back to a form expected by NetworkX tests using
      ``<your_backend_interface_object>.convert_to_nx(result, ...)``.
    - For nx_loopback, the graph is copied using the dispatchable metadata

3. Dispatchable algorithms that are not implemented by the backend
   will cause a ``pytest.xfail``, when the ``NETWORKX_FALLBACK_TO_NX``
   environment variable is set to ``False``, giving some indication that
   not all tests are running, while avoiding causing an explicit failure.
"""

import inspect
import itertools
import logging
import os
import warnings
from functools import partial
from importlib.metadata import entry_points

import networkx as nx

from .decorators import argmap

__all__ = ["_dispatchable"]

_logger = logging.getLogger(__name__)


def _do_nothing():
    """This does nothing at all, yet it helps turn `_dispatchable` into functions."""


def _get_backends(group, *, load_and_call=False):
    """
    Retrieve NetworkX ``backends`` and ``backend_info`` from the entry points.

    Parameters
    -----------
    group : str
        The entry_point to be retrieved.
    load_and_call : bool, optional
        If True, load and call the backend. Defaults to False.

    Returns
    --------
    dict
        A dictionary mapping backend names to their respective backend objects.

    Notes
    ------
    If a backend is defined more than once, a warning is issued.
    The `nx_loopback` backend is removed if it exists, as it is only available during testing.
    A warning is displayed if an error occurs while loading a backend.
    """
    items = entry_points(group=group)
    rv = {}
    for ep in items:
        if ep.name in rv:
            warnings.warn(
                f"networkx backend defined more than once: {ep.name}",
                RuntimeWarning,
                stacklevel=2,
            )
        elif load_and_call:
            try:
                rv[ep.name] = ep.load()()
            except Exception as exc:
                warnings.warn(
                    f"Error encountered when loading info for backend {ep.name}: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )
        else:
            rv[ep.name] = ep
    rv.pop("nx_loopback", None)
    return rv


backends = _get_backends("networkx.backends")
backend_info = _get_backends("networkx.backend_info", load_and_call=True)

# We must import from config after defining `backends` above
from .configs import Config, config

# Get default configuration from environment variables at import time
config.backend_priority = [
    x.strip()
    for x in os.environ.get(
        "NETWORKX_BACKEND_PRIORITY",
        os.environ.get("NETWORKX_AUTOMATIC_BACKENDS", ""),
    ).split(",")
    if x.strip()
]
# Initialize default configuration for backends
config.backends = Config(
    **{
        backend: (
            cfg if isinstance(cfg := info["default_config"], Config) else Config(**cfg)
        )
        if "default_config" in info
        else Config()
        for backend, info in backend_info.items()
    }
)
type(config.backends).__doc__ = "All installed NetworkX backends and their configs."

# Load and cache backends on-demand
_loaded_backends = {}  # type: ignore[var-annotated]


def _always_run(name, args, kwargs):
    return True


def _load_backend(backend_name):
    if backend_name in _loaded_backends:
        return _loaded_backends[backend_name]
    rv = _loaded_backends[backend_name] = backends[backend_name].load()
    if not hasattr(rv, "can_run"):
        rv.can_run = _always_run
    if not hasattr(rv, "should_run"):
        rv.should_run = _always_run
    return rv


_registered_algorithms = {}


class _dispatchable:
    _is_testing = False
    _fallback_to_nx = (
        os.environ.get("NETWORKX_FALLBACK_TO_NX", "true").strip().lower() == "true"
    )

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
        mutates_input=False,
        returns_graph=False,
    ):
        """A decorator function that is used to redirect the execution of ``func``
        function to its backend implementation.

        This decorator function dispatches to
        a different backend implementation based on the input graph types, and it also
        manages all the ``backend_kwargs``. Usage can be any of the following decorator
        forms:

        - ``@_dispatchable``
        - ``@_dispatchable()``
        - ``@_dispatchable(name="override_name")``
        - ``@_dispatchable(graphs="graph_var_name")``
        - ``@_dispatchable(edge_attrs="weight")``
        - ``@_dispatchable(graphs={"G": 0, "H": 1}, edge_attrs={"weight": "default"})``
            with 0 and 1 giving the position in the signature function for graph
            objects. When ``edge_attrs`` is a dict, keys are keyword names and values
            are defaults.

        Parameters
        ----------
        func : callable, optional
            The function to be decorated. If ``func`` is not provided, returns a
            partial object that can be used to decorate a function later. If ``func``
            is provided, returns a new callable object that dispatches to a backend
            algorithm based on input graph types.

        name : str, optional
            The name of the algorithm to use for dispatching. If not provided,
            the name of ``func`` will be used. ``name`` is useful to avoid name
            conflicts, as all dispatched algorithms live in a single namespace.
            For example, ``tournament.is_strongly_connected`` had a name conflict
            with the standard ``nx.is_strongly_connected``, so we used
            ``@_dispatchable(name="tournament_is_strongly_connected")``.

        graphs : str or dict or None, default "G"
            If a string, the parameter name of the graph, which must be the first
            argument of the wrapped function. If more than one graph is required
            for the algorithm (or if the graph is not the first argument), provide
            a dict keyed to argument names with argument position as values for each
            graph argument. For example, ``@_dispatchable(graphs={"G": 0, "auxiliary?": 4})``
            indicates the 0th parameter ``G`` of the function is a required graph,
            and the 4th parameter ``auxiliary?`` is an optional graph.
            To indicate that an argument is a list of graphs, do ``"[graphs]"``.
            Use ``graphs=None``, if *no* arguments are NetworkX graphs such as for
            graph generators, readers, and conversion functions.

        edge_attrs : str or dict, optional
            ``edge_attrs`` holds information about edge attribute arguments
            and default values for those edge attributes.
            If a string, ``edge_attrs`` holds the function argument name that
            indicates a single edge attribute to include in the converted graph.
            The default value for this attribute is 1. To indicate that an argument
            is a list of attributes (all with default value 1), use e.g. ``"[attrs]"``.
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

        mutates_input : bool or dict, default False
            For bool, whether the function mutates an input graph argument.
            For dict of ``{arg_name: arg_pos}``, arguments that indicate whether an
            input graph will be mutated, and ``arg_name`` may begin with ``"not "``
            to negate the logic (for example, this is used by ``copy=`` arguments).
            By default, dispatching doesn't convert input graphs to a different
            backend for functions that mutate input graphs.

        returns_graph : bool, default False
            Whether the function can return or yield a graph object. By default,
            dispatching doesn't convert input graphs to a different backend for
            functions that return graphs.
        """
        if func is None:
            return partial(
                _dispatchable,
                name=name,
                graphs=graphs,
                edge_attrs=edge_attrs,
                node_attrs=node_attrs,
                preserve_edge_attrs=preserve_edge_attrs,
                preserve_node_attrs=preserve_node_attrs,
                preserve_graph_attrs=preserve_graph_attrs,
                preserve_all_attrs=preserve_all_attrs,
                mutates_input=mutates_input,
                returns_graph=returns_graph,
            )
        if isinstance(func, str):
            raise TypeError("'name' and 'graphs' must be passed by keyword") from None
        # If name not provided, use the name of the function
        if name is None:
            name = func.__name__

        self = object.__new__(cls)

        # standard function-wrapping stuff
        # __annotations__ not used
        self.__name__ = func.__name__
        # self.__doc__ = func.__doc__  # __doc__ handled as cached property
        self.__defaults__ = func.__defaults__
        # We "magically" add `backend=` keyword argument to allow backend to be specified
        if func.__kwdefaults__:
            self.__kwdefaults__ = {**func.__kwdefaults__, "backend": None}
        else:
            self.__kwdefaults__ = {"backend": None}
        self.__module__ = func.__module__
        self.__qualname__ = func.__qualname__
        self.__dict__.update(func.__dict__)
        self.__wrapped__ = func

        # Supplement docstring with backend info; compute and cache when needed
        self._orig_doc = func.__doc__
        self._cached_doc = None

        self.orig_func = func
        self.name = name
        self.edge_attrs = edge_attrs
        self.node_attrs = node_attrs
        self.preserve_edge_attrs = preserve_edge_attrs or preserve_all_attrs
        self.preserve_node_attrs = preserve_node_attrs or preserve_all_attrs
        self.preserve_graph_attrs = preserve_graph_attrs or preserve_all_attrs
        self.mutates_input = mutates_input
        # Keep `returns_graph` private for now, b/c we may extend info on return types
        self._returns_graph = returns_graph

        if edge_attrs is not None and not isinstance(edge_attrs, str | dict):
            raise TypeError(
                f"Bad type for edge_attrs: {type(edge_attrs)}. Expected str or dict."
            ) from None
        if node_attrs is not None and not isinstance(node_attrs, str | dict):
            raise TypeError(
                f"Bad type for node_attrs: {type(node_attrs)}. Expected str or dict."
            ) from None
        if not isinstance(self.preserve_edge_attrs, bool | str | dict):
            raise TypeError(
                f"Bad type for preserve_edge_attrs: {type(self.preserve_edge_attrs)}."
                " Expected bool, str, or dict."
            ) from None
        if not isinstance(self.preserve_node_attrs, bool | str | dict):
            raise TypeError(
                f"Bad type for preserve_node_attrs: {type(self.preserve_node_attrs)}."
                " Expected bool, str, or dict."
            ) from None
        if not isinstance(self.preserve_graph_attrs, bool | set):
            raise TypeError(
                f"Bad type for preserve_graph_attrs: {type(self.preserve_graph_attrs)}."
                " Expected bool or set."
            ) from None
        if not isinstance(self.mutates_input, bool | dict):
            raise TypeError(
                f"Bad type for mutates_input: {type(self.mutates_input)}."
                " Expected bool or dict."
            ) from None
        if not isinstance(self._returns_graph, bool):
            raise TypeError(
                f"Bad type for returns_graph: {type(self._returns_graph)}."
                " Expected bool."
            ) from None

        if isinstance(graphs, str):
            graphs = {graphs: 0}
        elif graphs is None:
            pass
        elif not isinstance(graphs, dict):
            raise TypeError(
                f"Bad type for graphs: {type(graphs)}. Expected str or dict."
            ) from None
        elif len(graphs) == 0:
            raise KeyError("'graphs' must contain at least one variable name") from None

        # This dict comprehension is complicated for better performance; equivalent shown below.
        self.optional_graphs = set()
        self.list_graphs = set()
        if graphs is None:
            self.graphs = {}
        else:
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

        # Compute and cache the signature on-demand
        self._sig = None

        # Which backends implement this function?
        self.backends = {
            backend
            for backend, info in backend_info.items()
            if "functions" in info and name in info["functions"]
        }

        if name in _registered_algorithms:
            raise KeyError(
                f"Algorithm already exists in dispatch registry: {name}"
            ) from None
        # Use the magic of `argmap` to turn `self` into a function. This does result
        # in small additional overhead compared to calling `_dispatchable` directly,
        # but `argmap` has the magical property that it can stack with other `argmap`
        # decorators "for free". Being a function is better for REPRs and type-checkers.
        self = argmap(_do_nothing)(self)
        _registered_algorithms[name] = self
        return self

    @property
    def __doc__(self):
        """If the cached documentation exists, it is returned.
        Otherwise, the documentation is generated using _make_doc() method,
        cached, and then returned."""

        if (rv := self._cached_doc) is not None:
            return rv
        rv = self._cached_doc = self._make_doc()
        return rv

    @__doc__.setter
    def __doc__(self, val):
        """Sets the original documentation to the given value and resets the
        cached documentation."""

        self._orig_doc = val
        self._cached_doc = None

    @property
    def __signature__(self):
        """Return the signature of the original function, with the addition of
        the `backend` and `backend_kwargs` parameters."""

        if self._sig is None:
            sig = inspect.signature(self.orig_func)
            # `backend` is now a reserved argument used by dispatching.
            # assert "backend" not in sig.parameters
            if not any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            ):
                sig = sig.replace(
                    parameters=[
                        *sig.parameters.values(),
                        inspect.Parameter(
                            "backend", inspect.Parameter.KEYWORD_ONLY, default=None
                        ),
                        inspect.Parameter(
                            "backend_kwargs", inspect.Parameter.VAR_KEYWORD
                        ),
                    ]
                )
            else:
                *parameters, var_keyword = sig.parameters.values()
                sig = sig.replace(
                    parameters=[
                        *parameters,
                        inspect.Parameter(
                            "backend", inspect.Parameter.KEYWORD_ONLY, default=None
                        ),
                        var_keyword,
                    ]
                )
            self._sig = sig
        return self._sig

    def __call__(self, /, *args, backend=None, **kwargs):
        """Returns the result of the original function, or the backend function if
        the backend is specified and that backend implements `func`."""

        if not backends:
            # Fast path if no backends are installed
            if backend is not None:
                raise ImportError(f"'{backend}' backend is not installed")
            return self.orig_func(*args, **kwargs)

        # Use `backend_name` in this function instead of `backend`
        backend_name = backend
        if backend_name is not None and backend_name not in backends:
            raise ImportError(f"'{backend_name}' backend is not installed")

        graphs_resolved = {}
        for gname, pos in self.graphs.items():
            if pos < len(args):
                if gname in kwargs:
                    raise TypeError(f"{self.name}() got multiple values for {gname!r}")
                val = args[pos]
            elif gname in kwargs:
                val = kwargs[gname]
            elif gname not in self.optional_graphs:
                raise TypeError(
                    f"{self.name}() missing required graph argument: {gname}"
                )
            else:
                continue
            if val is None:
                if gname not in self.optional_graphs:
                    raise TypeError(
                        f"{self.name}() required graph argument {gname!r} is None; must be a graph"
                    )
            else:
                graphs_resolved[gname] = val

        # Alternative to the above that does not check duplicated args or missing required graphs.
        # graphs_resolved = {
        #     val
        #     for gname, pos in self.graphs.items()
        #     if (val := args[pos] if pos < len(args) else kwargs.get(gname)) is not None
        # }

        # Check if any graph comes from a backend
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

            has_backends = any(
                hasattr(g, "__networkx_backend__")
                if gname not in self.list_graphs
                else any(hasattr(g2, "__networkx_backend__") for g2 in g)
                for gname, g in graphs_resolved.items()
            )
            if has_backends:
                graph_backend_names = {
                    getattr(g, "__networkx_backend__", "networkx")
                    for gname, g in graphs_resolved.items()
                    if gname not in self.list_graphs
                }
                for gname in self.list_graphs & graphs_resolved.keys():
                    graph_backend_names.update(
                        getattr(g, "__networkx_backend__", "networkx")
                        for g in graphs_resolved[gname]
                    )
        else:
            has_backends = any(
                hasattr(g, "__networkx_backend__") for g in graphs_resolved.values()
            )
            if has_backends:
                graph_backend_names = {
                    getattr(g, "__networkx_backend__", "networkx")
                    for g in graphs_resolved.values()
                }

        backend_priority = config.backend_priority
        if self._is_testing and backend_priority and backend_name is None:
            # Special path if we are running networkx tests with a backend.
            # This even runs for (and handles) functions that mutate input graphs.
            return self._convert_and_call_for_tests(
                backend_priority[0],
                args,
                kwargs,
                fallback_to_nx=self._fallback_to_nx,
            )

        if has_backends:
            # Dispatchable graphs found! Dispatch to backend function.
            # We don't handle calls with different backend graphs yet,
            # but we may be able to convert additional networkx graphs.
            backend_names = graph_backend_names - {"networkx"}
            if len(backend_names) != 1:
                # Future work: convert between backends and run if multiple backends found
                raise TypeError(
                    f"{self.name}() graphs must all be from the same backend, found {backend_names}"
                )
            [graph_backend_name] = backend_names
            if backend_name is not None and backend_name != graph_backend_name:
                # Future work: convert between backends to `backend_name` backend
                raise TypeError(
                    f"{self.name}() is unable to convert graph from backend {graph_backend_name!r} "
                    f"to the specified backend {backend_name!r}."
                )
            if graph_backend_name not in backends:
                raise ImportError(f"'{graph_backend_name}' backend is not installed")
            if (
                "networkx" in graph_backend_names
                and graph_backend_name not in backend_priority
            ):
                # Not configured to convert networkx graphs to this backend
                raise TypeError(
                    f"Unable to convert inputs and run {self.name}. "
                    f"{self.name}() has networkx and {graph_backend_name} graphs, but NetworkX is not "
                    f"configured to automatically convert graphs from networkx to {graph_backend_name}."
                )
            backend = _load_backend(graph_backend_name)
            if hasattr(backend, self.name):
                if "networkx" in graph_backend_names:
                    # We need to convert networkx graphs to backend graphs.
                    # There is currently no need to check `self.mutates_input` here.
                    return self._convert_and_call(
                        graph_backend_name,
                        args,
                        kwargs,
                        fallback_to_nx=self._fallback_to_nx,
                    )
                # All graphs are backend graphs--no need to convert!
                _logger.debug(
                    "Using backend '%s' for call to `%s' with args: %s, kwargs: %s",
                    graph_backend_name,
                    self.name,
                    args,
                    kwargs,
                )
                return getattr(backend, self.name)(*args, **kwargs)
            # Future work: try to convert and run with other backends in backend_priority
            raise nx.NetworkXNotImplemented(
                f"'{self.name}' not implemented by {graph_backend_name}"
            )

        # If backend was explicitly given by the user, so we need to use it no matter what
        if backend_name is not None:
            return self._convert_and_call(
                backend_name, args, kwargs, fallback_to_nx=False
            )

        # Only networkx graphs; try to convert and run with a backend with automatic
        # conversion, but don't do this by default for graph generators or loaders,
        # or if the functions mutates an input graph or returns a graph.
        # Only convert and run if `backend.should_run(...)` returns True.
        if (
            not self._returns_graph
            and (
                not self.mutates_input
                or isinstance(self.mutates_input, dict)
                # If `mutates_input` begins with "not ", then assume the argument is boolean,
                # otherwise treat it as a node or edge attribute if it's not None.
                and any(
                    not (
                        args[arg_pos]
                        if len(args) > arg_pos
                        else kwargs.get(arg_name[4:], True)
                    )
                    if arg_name.startswith("not ")
                    else (
                        args[arg_pos] if len(args) > arg_pos else kwargs.get(arg_name)
                    )
                    is not None
                    for arg_name, arg_pos in self.mutates_input.items()
                )
            )
        ):
            # Should we warn or log if we don't convert b/c the input will be mutated?
            for backend_name in backend_priority:
                if self._should_backend_run(backend_name, args, kwargs):
                    return self._convert_and_call(
                        backend_name,
                        args,
                        kwargs,
                        fallback_to_nx=self._fallback_to_nx,
                    )
        # Default: run with networkx on networkx inputs
        return self.orig_func(*args, **kwargs)

    def _can_backend_run(self, backend_name, args, kwargs, *, log=True):
        """Can the specified backend run this algorithm with these arguments?"""
        backend = _load_backend(backend_name)
        # `backend.can_run` and `backend.should_run` may return strings that describe
        # why they can't or shouldn't be run.
        if not hasattr(backend, self.name):
            if log:
                _logger.debug(
                    "Backend '%s' does not implement `%s'", backend_name, self.name
                )
            return False
        can_run = backend.can_run(self.name, args, kwargs)
        if isinstance(can_run, str) or not can_run:
            if log:
                reason = f", because: {can_run}" if isinstance(can_run, str) else ""
                _logger.debug(
                    "Backend '%s' can't run `%s` with args: %s, kwargs: %s%s",
                    backend_name,
                    self.name,
                    args,
                    kwargs,
                    reason,
                )
            return False
        return True

    def _should_backend_run(self, backend_name, args, kwargs):
        """Can/should the specified backend run this algorithm with these arguments?"""
        # `backend.can_run` and `backend.should_run` may return strings that describe
        # why they can't or shouldn't be run.
        if not self._can_backend_run(backend_name, args, kwargs):
            return False
        backend = _load_backend(backend_name)
        should_run = backend.should_run(self.name, args, kwargs)
        if isinstance(should_run, str) or not should_run:
            reason = f", because: {should_run}" if isinstance(should_run, str) else ""
            _logger.debug(
                "Backend '%s' shouldn't run `%s` with args: %s, kwargs: %s%s",
                backend_name,
                self.name,
                args,
                kwargs,
                reason,
            )
            return False
        return True

    def _convert_arguments(self, backend_name, args, kwargs, *, use_cache):
        """Convert graph arguments to the specified backend.

        Returns
        -------
        args tuple and kwargs dict
        """
        bound = self.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        if not self.graphs:
            bound_kwargs = bound.kwargs
            del bound_kwargs["backend"]
            return bound.args, bound_kwargs
        # Convert graphs into backend graph-like object
        # Include the edge and/or node labels if provided to the algorithm
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
        # Else: e.g. `preserve_edge_attrs={"G": {"weight": 1}}`

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
        else:
            # e.g. `edge_attrs={"attr": "default"}` and `func(attr="foo", default=7)`
            # e.g. `edge_attrs={"attr": 0}` and `func(attr="foo")`
            edge_attrs = {
                edge_attr: bound.arguments.get(val, 1) if isinstance(val, str) else val
                for key, val in edge_attrs.items()
                if (edge_attr := bound.arguments[key]) is not None
            }

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
        # Else: e.g. `preserve_node_attrs={"G": {"pos": None}}`

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
        else:
            # e.g. `node_attrs={"attr": "default"}` and `func(attr="foo", default=7)`
            # e.g. `node_attrs={"attr": 0}` and `func(attr="foo")`
            node_attrs = {
                node_attr: bound.arguments.get(val) if isinstance(val, str) else val
                for key, val in node_attrs.items()
                if (node_attr := bound.arguments[key]) is not None
            }

        preserve_graph_attrs = self.preserve_graph_attrs

        # It should be safe to assume that we either have networkx graphs or backend graphs.
        # Future work: allow conversions between backends.
        for gname in self.graphs:
            if gname in self.list_graphs:
                bound.arguments[gname] = [
                    self._convert_graph(
                        backend_name,
                        g,
                        edge_attrs=edge_attrs,
                        node_attrs=node_attrs,
                        preserve_edge_attrs=preserve_edge_attrs,
                        preserve_node_attrs=preserve_node_attrs,
                        preserve_graph_attrs=preserve_graph_attrs,
                        graph_name=gname,
                        use_cache=use_cache,
                    )
                    if getattr(g, "__networkx_backend__", "networkx") == "networkx"
                    else g
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
                if getattr(graph, "__networkx_backend__", "networkx") == "networkx":
                    bound.arguments[gname] = self._convert_graph(
                        backend_name,
                        graph,
                        edge_attrs=edges,
                        node_attrs=nodes,
                        preserve_edge_attrs=preserve_edges,
                        preserve_node_attrs=preserve_nodes,
                        preserve_graph_attrs=preserve_graph,
                        graph_name=gname,
                        use_cache=use_cache,
                    )
        bound_kwargs = bound.kwargs
        del bound_kwargs["backend"]
        return bound.args, bound_kwargs

    def _convert_graph(
        self,
        backend_name,
        graph,
        *,
        edge_attrs,
        node_attrs,
        preserve_edge_attrs,
        preserve_node_attrs,
        preserve_graph_attrs,
        graph_name,
        use_cache,
    ):
        if (
            use_cache
            and (nx_cache := getattr(graph, "__networkx_cache__", None)) is not None
        ):
            cache = nx_cache.setdefault("backends", {}).setdefault(backend_name, {})
            # edge_attrs: dict | None
            # node_attrs: dict | None
            # preserve_edge_attrs: bool (False if edge_attrs is not None)
            # preserve_node_attrs: bool (False if node_attrs is not None)
            key = edge_key, node_key = (
                frozenset(edge_attrs.items())
                if edge_attrs is not None
                else preserve_edge_attrs,
                frozenset(node_attrs.items())
                if node_attrs is not None
                else preserve_node_attrs,
            )
            if cache:
                warning_message = (
                    f"Using cached graph for {backend_name!r} backend in "
                    f"call to {self.name}.\n\nFor the cache to be consistent "
                    "(i.e., correct), the input graph must not have been "
                    "manually mutated since the cached graph was created. "
                    "Examples of manually mutating the graph data structures "
                    "resulting in an inconsistent cache include:\n\n"
                    "    >>> G[u][v][key] = val\n\n"
                    "and\n\n"
                    "    >>> for u, v, d in G.edges(data=True):\n"
                    "    ...     d[key] = val\n\n"
                    "Using methods such as `G.add_edge(u, v, weight=val)` "
                    "will correctly clear the cache to keep it consistent. "
                    "You may also use `G.__networkx_cache__.clear()` to "
                    "manually clear the cache, or set `G.__networkx_cache__` "
                    "to None to disable caching for G. Enable or disable caching "
                    "globally via `nx.config.cache_converted_graphs` config."
                )
                # Do a simple search for a cached graph with compatible data.
                # For example, if we need a single attribute, then it's okay
                # to use a cached graph that preserved all attributes.
                # This looks for an exact match first.
                for compat_key in itertools.product(
                    (edge_key, True) if edge_key is not True else (True,),
                    (node_key, True) if node_key is not True else (True,),
                ):
                    if (rv := cache.get(compat_key)) is not None:
                        warnings.warn(warning_message)
                        _logger.debug(
                            "Using cached converted graph (from 'networkx' to '%s' backend) "
                            "in call to `%s' for '%s' argument",
                            backend_name,
                            self.name,
                            graph_name,
                        )
                        return rv
                if edge_key is not True and node_key is not True:
                    # Iterate over the items in `cache` to see if any are compatible.
                    # For example, if no edge attributes are needed, then a graph
                    # with any edge attribute will suffice. We use the same logic
                    # below (but switched) to clear unnecessary items from the cache.
                    # Use `list(cache.items())` to be thread-safe.
                    for (ekey, nkey), val in list(cache.items()):
                        if edge_key is False or ekey is True:
                            pass  # Cache works for edge data!
                        elif (
                            edge_key is True
                            or ekey is False
                            or not edge_key.issubset(ekey)
                        ):
                            continue  # Cache missing required edge data; does not work
                        if node_key is False or nkey is True:
                            pass  # Cache works for node data!
                        elif (
                            node_key is True
                            or nkey is False
                            or not node_key.issubset(nkey)
                        ):
                            continue  # Cache missing required node data; does not work
                        warnings.warn(warning_message)
                        _logger.debug(
                            "Using cached converted graph (from 'networkx' to '%s' backend) "
                            "in call to `%s' for '%s' argument",
                            backend_name,
                            self.name,
                            graph_name,
                        )
                        return val

        backend = _load_backend(backend_name)
        rv = backend.convert_from_nx(
            graph,
            edge_attrs=edge_attrs,
            node_attrs=node_attrs,
            preserve_edge_attrs=preserve_edge_attrs,
            preserve_node_attrs=preserve_node_attrs,
            # Always preserve graph attrs when we are caching b/c this should be
            # cheap and may help prevent extra (unnecessary) conversions. Because
            # we do this, we don't need `preserve_graph_attrs` in the cache key.
            preserve_graph_attrs=preserve_graph_attrs or use_cache,
            name=self.name,
            graph_name=graph_name,
        )
        if use_cache and nx_cache is not None:
            # Remove old cached items that are no longer necessary since they
            # are dominated/subsumed/outdated by what was just calculated.
            # This uses the same logic as above, but with keys switched.
            cache[key] = rv  # Set at beginning to be thread-safe
            for cur_key in list(cache):
                if cur_key == key:
                    continue
                ekey, nkey = cur_key
                if ekey is False or edge_key is True:
                    pass
                elif ekey is True or edge_key is False or not ekey.issubset(edge_key):
                    continue
                if nkey is False or node_key is True:
                    pass
                elif nkey is True or node_key is False or not nkey.issubset(node_key):
                    continue
                cache.pop(cur_key, None)  # Use pop instead of del to be thread-safe
            _logger.debug(
                "Caching converted graph (from 'networkx' to '%s' backend) "
                "in call to `%s' for '%s' argument",
                backend_name,
                self.name,
                graph_name,
            )

        return rv

    def _convert_and_call(self, backend_name, args, kwargs, *, fallback_to_nx=False):
        """Call this dispatchable function with a backend, converting graphs if necessary."""
        backend = _load_backend(backend_name)
        # Don't log in `_can_backend_run` here to avoid duplicating info in the exception
        if not self._can_backend_run(backend_name, args, kwargs, log=fallback_to_nx):
            if fallback_to_nx:
                _logger.debug(
                    "Falling back to use 'networkx' instead of '%s' backend "
                    "for call to `%s' with args: %s, kwargs: %s",
                    backend_name,
                    self.name,
                    args,
                    kwargs,
                )
                return self.orig_func(*args, **kwargs)
            msg = f"'{self.name}' not implemented by {backend_name}"
            if hasattr(backend, self.name):
                msg += " with the given arguments"
            raise RuntimeError(msg)

        try:
            converted_args, converted_kwargs = self._convert_arguments(
                backend_name, args, kwargs, use_cache=config.cache_converted_graphs
            )
            _logger.debug(
                "Using backend '%s' for call to `%s' with args: %s, kwargs: %s",
                backend_name,
                self.name,
                converted_args,
                converted_kwargs,
            )
            result = getattr(backend, self.name)(*converted_args, **converted_kwargs)
        except (NotImplementedError, nx.NetworkXNotImplemented) as exc:
            if fallback_to_nx:
                _logger.debug(
                    "Graph conversion failed; falling back to use 'networkx' instead "
                    "of '%s' backend for call to `%s'",
                    backend_name,
                    self.name,
                )
                return self.orig_func(*args, **kwargs)
            raise

        return result

    def _convert_and_call_for_tests(
        self, backend_name, args, kwargs, *, fallback_to_nx=False
    ):
        """Call this dispatchable function with a backend; for use with testing."""
        backend = _load_backend(backend_name)
        if not self._can_backend_run(backend_name, args, kwargs):
            if fallback_to_nx or not self.graphs:
                if fallback_to_nx:
                    _logger.debug(
                        "Falling back to use 'networkx' instead of '%s' backend "
                        "for call to `%s' with args: %s, kwargs: %s",
                        backend_name,
                        self.name,
                        args,
                        kwargs,
                    )
                return self.orig_func(*args, **kwargs)

            import pytest

            msg = f"'{self.name}' not implemented by {backend_name}"
            if hasattr(backend, self.name):
                msg += " with the given arguments"
            pytest.xfail(msg)

        from collections.abc import Iterable, Iterator, Mapping
        from copy import copy, deepcopy
        from io import BufferedReader, BytesIO, StringIO, TextIOWrapper
        from itertools import tee
        from random import Random

        import numpy as np
        from numpy.random import Generator, RandomState
        from scipy.sparse import sparray

        # We sometimes compare the backend result to the original result,
        # so we need two sets of arguments. We tee iterators and copy
        # random state so that they may be used twice.
        if not args:
            args1 = args2 = args
        else:
            args1, args2 = zip(
                *(
                    (arg, deepcopy(arg))
                    if isinstance(arg, RandomState)
                    else (arg, copy(arg))
                    if isinstance(arg, BytesIO | StringIO | Random | Generator)
                    else tee(arg)
                    if isinstance(arg, Iterator)
                    and not isinstance(arg, BufferedReader | TextIOWrapper)
                    else (arg, arg)
                    for arg in args
                )
            )
        if not kwargs:
            kwargs1 = kwargs2 = kwargs
        else:
            kwargs1, kwargs2 = zip(
                *(
                    ((k, v), (k, deepcopy(v)))
                    if isinstance(v, RandomState)
                    else ((k, v), (k, copy(v)))
                    if isinstance(v, BytesIO | StringIO | Random | Generator)
                    else ((k, (teed := tee(v))[0]), (k, teed[1]))
                    if isinstance(v, Iterator)
                    and not isinstance(v, BufferedReader | TextIOWrapper)
                    else ((k, v), (k, v))
                    for k, v in kwargs.items()
                )
            )
            kwargs1 = dict(kwargs1)
            kwargs2 = dict(kwargs2)
        try:
            converted_args, converted_kwargs = self._convert_arguments(
                backend_name, args1, kwargs1, use_cache=False
            )
            _logger.debug(
                "Using backend '%s' for call to `%s' with args: %s, kwargs: %s",
                backend_name,
                self.name,
                converted_args,
                converted_kwargs,
            )
            result = getattr(backend, self.name)(*converted_args, **converted_kwargs)
        except (NotImplementedError, nx.NetworkXNotImplemented) as exc:
            if fallback_to_nx:
                _logger.debug(
                    "Graph conversion failed; falling back to use 'networkx' instead "
                    "of '%s' backend for call to `%s'",
                    backend_name,
                    self.name,
                )
                return self.orig_func(*args2, **kwargs2)
            import pytest

            pytest.xfail(
                exc.args[0] if exc.args else f"{self.name} raised {type(exc).__name__}"
            )
        # Verify that `self._returns_graph` is correct. This compares the return type
        # to the type expected from `self._returns_graph`. This handles tuple and list
        # return types, but *does not* catch functions that yield graphs.
        if (
            self._returns_graph
            != (
                isinstance(result, nx.Graph)
                or hasattr(result, "__networkx_backend__")
                or isinstance(result, tuple | list)
                and any(
                    isinstance(x, nx.Graph) or hasattr(x, "__networkx_backend__")
                    for x in result
                )
            )
            and not (
                # May return Graph or None
                self.name in {"check_planarity", "check_planarity_recursive"}
                and any(x is None for x in result)
            )
            and not (
                # May return Graph or dict
                self.name in {"held_karp_ascent"}
                and any(isinstance(x, dict) for x in result)
            )
            and self.name
            not in {
                # yields graphs
                "all_triads",
                "general_k_edge_subgraphs",
                # yields graphs or arrays
                "nonisomorphic_trees",
            }
        ):
            raise RuntimeError(f"`returns_graph` is incorrect for {self.name}")

        def check_result(val, depth=0):
            if isinstance(val, np.number):
                raise RuntimeError(
                    f"{self.name} returned a numpy scalar {val} ({type(val)}, depth={depth})"
                )
            if isinstance(val, np.ndarray | sparray):
                return
            if isinstance(val, nx.Graph):
                check_result(val._node, depth=depth + 1)
                check_result(val._adj, depth=depth + 1)
                return
            if isinstance(val, Iterator):
                raise NotImplementedError
            if isinstance(val, Iterable) and not isinstance(val, str):
                for x in val:
                    check_result(x, depth=depth + 1)
            if isinstance(val, Mapping):
                for x in val.values():
                    check_result(x, depth=depth + 1)

        def check_iterator(it):
            for val in it:
                try:
                    check_result(val)
                except RuntimeError as exc:
                    raise RuntimeError(
                        f"{self.name} returned a numpy scalar {val} ({type(val)})"
                    ) from exc
                yield val

        if self.name in {"from_edgelist"}:
            # numpy scalars are explicitly given as values in some tests
            pass
        elif isinstance(result, Iterator):
            result = check_iterator(result)
        else:
            try:
                check_result(result)
            except RuntimeError as exc:
                raise RuntimeError(
                    f"{self.name} returned a numpy scalar {result} ({type(result)})"
                ) from exc
            check_result(result)

        if self.name in {
            "edmonds_karp",
            "barycenter",
            "contracted_edge",
            "contracted_nodes",
            "stochastic_graph",
            "relabel_nodes",
            "maximum_branching",
            "incremental_closeness_centrality",
            "minimal_branching",
            "minimum_spanning_arborescence",
            "recursive_simple_cycles",
            "connected_double_edge_swap",
        }:
            # Special-case algorithms that mutate input graphs
            bound = self.__signature__.bind(*converted_args, **converted_kwargs)
            bound.apply_defaults()
            bound2 = self.__signature__.bind(*args2, **kwargs2)
            bound2.apply_defaults()
            if self.name in {
                "minimal_branching",
                "minimum_spanning_arborescence",
                "recursive_simple_cycles",
                "connected_double_edge_swap",
            }:
                G1 = backend.convert_to_nx(bound.arguments["G"])
                G2 = bound2.arguments["G"]
                G2._adj = G1._adj
                if G2.is_directed():
                    G2._pred = G1._pred
                nx._clear_cache(G2)
            elif self.name == "edmonds_karp":
                R1 = backend.convert_to_nx(bound.arguments["residual"])
                R2 = bound2.arguments["residual"]
                if R1 is not None and R2 is not None:
                    for k, v in R1.edges.items():
                        R2.edges[k]["flow"] = v["flow"]
                    R2.graph.update(R1.graph)
                    nx._clear_cache(R2)
            elif self.name == "barycenter" and bound.arguments["attr"] is not None:
                G1 = backend.convert_to_nx(bound.arguments["G"])
                G2 = bound2.arguments["G"]
                attr = bound.arguments["attr"]
                for k, v in G1.nodes.items():
                    G2.nodes[k][attr] = v[attr]
                nx._clear_cache(G2)
            elif (
                self.name in {"contracted_nodes", "contracted_edge"}
                and not bound.arguments["copy"]
            ):
                # Edges and nodes changed; node "contraction" and edge "weight" attrs
                G1 = backend.convert_to_nx(bound.arguments["G"])
                G2 = bound2.arguments["G"]
                G2.__dict__.update(G1.__dict__)
                nx._clear_cache(G2)
            elif self.name == "stochastic_graph" and not bound.arguments["copy"]:
                G1 = backend.convert_to_nx(bound.arguments["G"])
                G2 = bound2.arguments["G"]
                for k, v in G1.edges.items():
                    G2.edges[k]["weight"] = v["weight"]
                nx._clear_cache(G2)
            elif (
                self.name == "relabel_nodes"
                and not bound.arguments["copy"]
                or self.name in {"incremental_closeness_centrality"}
            ):
                G1 = backend.convert_to_nx(bound.arguments["G"])
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
                nx._clear_cache(G2)
                if self.name == "relabel_nodes":
                    return G2
            return backend.convert_to_nx(result)

        converted_result = backend.convert_to_nx(result)
        if isinstance(converted_result, nx.Graph) and self.name not in {
            "boykov_kolmogorov",
            "preflow_push",
            "quotient_graph",
            "shortest_augmenting_path",
            "spectral_graph_forge",
            # We don't handle tempfile.NamedTemporaryFile arguments
            "read_gml",
            "read_graph6",
            "read_sparse6",
            # We don't handle io.BufferedReader or io.TextIOWrapper arguments
            "bipartite_read_edgelist",
            "read_adjlist",
            "read_edgelist",
            "read_graphml",
            "read_multiline_adjlist",
            "read_pajek",
            "from_pydot",
            "pydot_read_dot",
            "agraph_read_dot",
            # graph comparison fails b/c of nan values
            "read_gexf",
        }:
            # For graph return types (e.g. generators), we compare that results are
            # the same between the backend and networkx, then return the original
            # networkx result so the iteration order will be consistent in tests.
            G = self.orig_func(*args2, **kwargs2)
            if not nx.utils.graphs_equal(G, converted_result):
                assert G.number_of_nodes() == converted_result.number_of_nodes()
                assert G.number_of_edges() == converted_result.number_of_edges()
                assert G.graph == converted_result.graph
                assert G.nodes == converted_result.nodes
                assert G.adj == converted_result.adj
                assert type(G) is type(converted_result)
                raise AssertionError("Graphs are not equal")
            return G
        return converted_result

    def _make_doc(self):
        """Generate the backends section at the end for functions having an alternate
        backend implementation(s) using the `backend_info` entry-point."""

        if not self.backends:
            return self._orig_doc
        lines = [
            "Backends",
            "--------",
        ]
        for backend in sorted(self.backends):
            info = backend_info[backend]
            if "short_summary" in info:
                lines.append(f"{backend} : {info['short_summary']}")
            else:
                lines.append(backend)
            if "functions" not in info or self.name not in info["functions"]:
                lines.append("")
                continue

            func_info = info["functions"][self.name]

            # Renaming extra_docstring to additional_docs
            if func_docs := (
                func_info.get("additional_docs") or func_info.get("extra_docstring")
            ):
                lines.extend(
                    f"  {line}" if line else line for line in func_docs.split("\n")
                )
                add_gap = True
            else:
                add_gap = False

            # Renaming extra_parameters to additional_parameters
            if extra_parameters := (
                func_info.get("extra_parameters")
                or func_info.get("additional_parameters")
            ):
                if add_gap:
                    lines.append("")
                lines.append("  Additional parameters:")
                for param in sorted(extra_parameters):
                    lines.append(f"    {param}")
                    if desc := extra_parameters[param]:
                        lines.append(f"      {desc}")
                    lines.append("")
            else:
                lines.append("")

            if func_url := func_info.get("url"):
                lines.append(f"[`Source <{func_url}>`_]")
                lines.append("")

        lines.pop()  # Remove last empty line
        to_add = "\n    ".join(lines)
        return f"{self._orig_doc.rstrip()}\n\n    {to_add}"

    def __reduce__(self):
        """Allow this object to be serialized with pickle.

        This uses the global registry `_registered_algorithms` to deserialize.
        """
        return _restore_dispatchable, (self.name,)


def _restore_dispatchable(name):
    return _registered_algorithms[name]


if os.environ.get("_NETWORKX_BUILDING_DOCS_"):
    # When building docs with Sphinx, use the original function with the
    # dispatched __doc__, b/c Sphinx renders normal Python functions better.
    # This doesn't show e.g. `*, backend=None, **backend_kwargs` in the
    # signatures, which is probably okay. It does allow the docstring to be
    # updated based on the installed backends.
    _orig_dispatchable = _dispatchable

    def _dispatchable(func=None, **kwargs):  # type: ignore[no-redef]
        if func is None:
            return partial(_dispatchable, **kwargs)
        dispatched_func = _orig_dispatchable(func, **kwargs)
        func.__doc__ = dispatched_func.__doc__
        return func

    _dispatchable.__doc__ = _orig_dispatchable.__new__.__doc__  # type: ignore[method-assign,assignment]
    _sig = inspect.signature(_orig_dispatchable.__new__)
    _dispatchable.__signature__ = _sig.replace(  # type: ignore[method-assign,assignment]
        parameters=[v for k, v in _sig.parameters.items() if k != "cls"]
    )
