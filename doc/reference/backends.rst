********
Backends
********

NetworkX can be configured to use separate thrid-party backends to improve
performance and add functionality. Backends are optional, installed separately,
and can be enabled either directly in the user's code or through environment
variables.

.. note:: The interface used by developers creating custom NetworkX backends is
   receiving frequent updates and improvements. Participating in weekly
   `NetworkX dispatch meetings
   <https://scientific-python.org/calendars/networkx.ics>`_ is an excellent way
   to stay updated and contribute to the ongoing discussions.

Docs for backend users
~~~~~~~~~~~~~~~~~~~~~~
NetworkX utilizes a plugin-dispatch architecture. A valid NetworkX backend
specifies `entry points
<https://packaging.python.org/en/latest/specifications/entry-points>`_, named
``networkx.backends`` and an optional ``networkx.backend_info`` when it is
installed (not imported). This allows NetworkX to dispatch (redirect) function
calls to the backend so the execution flows to the designated backend
implementation. This design enhances flexibility and integration, making
NetworkX more adaptable and efficient.

NetworkX can dispatch to backends **explicitly** (this requires changing code)
or **automatically** (this requires setting configuration or environment
variables). The best way to use a backend depends on the backend, your use
case, and whether you want to automatically convert to or from backend
graphs. Automatic conversions of graphs is always opt-in.

To explicitly dispatch to a backend, use the ``backend=`` keyword argument in a
dispatchable function. This will convert (and cache by default) input NetworkX
graphs to backend graphs and call the backend implementation.

Another explicit way to use a backend is to create a backend graph directly.
Graph classes support the ``backend=`` keyword argument to create a backend
graph such as ``nx.Graph(backend=...)``, and backends may have their own
functions for loading data and creating graphs that you can use. Passing a
backend graph to a dispatchable function will call the backend implementation
without converting.

Using automatic dispatch requires setting configuration options. Every NetworkX
configuration may also be set from an environment variable and are processed at
the time networkx is imported.  The following configuration variables are
supported:

* ``nx.config.backend_priority`` (``NETWORKX_BACKEND_PRIORITY`` env var), a
  list of backends, controls dispatchable functions that don't return graphs
  such as e.g. ``nx.pagerank``. When one of these functions is called with
  NetworkX graphs as input, the dispatcher iterates over the backends listed in
  this backend_priority config and will use the first backend that implements
  this function. The input NetworkX graphs are converted (and cached by
  default) to backend graphs. Using this configuration can allow you to use the
  full flexibility of NetworkX graphs and the performance of backend
  implementations, but possible downsides are that creating NetworkX graphs,
  converting to backend graphs, and caching backend graphs may all be
  expensive.

* ``nx.config.backend_priority.algos`` (``NETWORKX_BACKEND_PRIORITY_ALGOS`` env
  var), can be used instead of ``nx.config.backend_priority``
  (``NETWORKX_BACKEND_PRIORITY`` env var) to emphasize that the setting only
  affects the dispatching of algorithm functions as described above.

* ``nx.config.backend_priority.generators``
  (``NETWORKX_BACKEND_PRIORITY_GENERATORS`` env var), a list of backends,
  controls dispatchable functions that return graphs such as
  nx.from_pandas_edgelist and nx.empty_graph. When one of these functions is
  called, the first backend listed in this backend_priority config that
  implements this function will be used and will return a backend graph. When
  this backend graph is passed to other dispatchable NetworkX functions, it
  will use the backend implementation if it exists or raise by default unless
  nx.config.fallback_to_nx is True (default is False). Using this configuration
  avoids creating NetworkX graphs, which subsequently avoids the need to
  convert to and cache backend graphs as when using
  nx.config.backend_priority.algos, but possible downsides are that the backend
  graph may not behave the same as a NetworkX graph and the backend may not
  implement all algorithms that you use, which may break your workflow.

* ``nx.config.backend_priority.classes``
  (``NETWORKX_BACKEND_PRIORITY_CLASSES`` env var), a list of backends,
  controls graph classes. For example, this allows ``nx.Graph(data)`` to
  create a backend graph. Advantages and disadvantages of this are similar
  to ``nx.config.backend_priority.generators`` (see above).

* ``nx.config.fallback_to_nx`` (``NETWORKX_FALLBACK_TO_NX`` env var), a boolean
  (default False), controls what happens when a backend graph is passed to a
  dispatchable function that is not implemented by that backend. The default
  behavior when False is to raise. If True, then the backend graph will be
  converted (and cached by default) to a NetworkX graph and will run with the
  default NetworkX implementation. Enabling this configuration can allow
  workflows to complete if the backend does not implement all algorithms used
  by the workflow, but a possible downside is that it may require converting
  the input backend graph to a NetworkX graph, which may be expensive. If a
  backend graph is duck-type compatible as a NetworkX graph, then the backend
  may choose not to convert to a NetworkX graph and use the incoming graph
  as-is.

* ``nx.config.cache_converted_graphs`` (``NETWORKX_CACHE_CONVERTED_GRAPHS`` env
  var), a boolean (default True), controls whether graph conversions are cached
  to G.__networkx_cache__ or not. Caching can improve performance by avoiding
  repeated conversions, but it uses more memory.

.. note:: Backends *should* follow the NetworkX backend naming convention. For
   example, if a backend is named ``parallel`` and specified using
   ``backend=parallel`` or ``NETWORKX_BACKEND_PRIORITY=parallel``, the package
   installed is ``nx-parallel``, and we would use ``import nx_parallel`` if we
   were to import the backend package directly.

Backends are encouraged to document how they recommend to be used and whether
their graph types are duck-type compatible as NetworkX graphs. If backend
graphs are NetworkX-compatible and you want your workflow to automatically
"just work" with a backend--converting and caching if necessary--then use all
of the above configurations. Automatically converting graphs is opt-in, and
configuration gives the user control.

Examples:
---------

Use the ``cugraph`` backend for every algorithm function it supports. This will
allow for fall back to the default NetworkX implementations for algorithm calls
not supported by cugraph because graph generator functions are still returning
NetworkX graphs.

.. code-block:: bash

   bash> NETWORKX_BACKEND_PRIORITY=cugraph python my_networkx_script.py

Explicitly use the ``parallel`` backend for a function call.

.. code-block:: python

    nx.betweenness_centrality(G, k=10, backend="parallel")

Explicitly use the ``parallel`` backend for a function call by passing an
instance of the backend graph type to the function.

.. code-block:: python

   H = nx_parallel.ParallelGraph(G)
   nx.betweenness_centrality(H, k=10)

Explicitly use the ``parallel`` backend and pass additional backend-specific
arguments. Here, ``get_chunks`` is an argument unique to the ``parallel``
backend.

.. code-block:: python

   nx.betweenness_centrality(G, k=10, backend="parallel", get_chunks=get_chunks)

Automatically dispatch the ``cugraph`` backend for all NetworkX algorithms and
generators, and allow the backend graph object returned from generators to be
passed to NetworkX functions the backend does not support.

.. code-block:: bash

   bash> NETWORKX_BACKEND_PRIORITY_ALGOS=cugraph \\
         NETWORKX_BACKEND_PRIORITY_GENERATORS=cugraph \\
         NETWORKX_FALLBACK_TO_NX=True \\
         python my_networkx_script.py

How does this work?
-------------------

If you've looked at functions in the NetworkX codebase, you might have seen the
``@nx._dispatchable`` decorator on most of the functions. This decorator allows the NetworkX
function to dispatch to the corresponding backend function if available. When the decorated
function is called, it first checks for a backend to run the function, and if no appropriate
backend is specified or available, it runs the NetworkX version of the function.

Backend Keyword Argument
^^^^^^^^^^^^^^^^^^^^^^^^

When a decorated function is called with the ``backend`` kwarg provided, it checks
if the specified backend is installed, and loads it. Next it checks whether to convert
input graphs by first resolving the backend of each input graph by looking
for an attribute named ``__networkx_backend__`` that holds the backend name for that
graph type. If all input graphs backend matches the ``backend`` kwarg, the backend's
function is called with the original inputs. If any of the input graphs do not match
the ``backend`` kwarg, they are converted to the backend graph type before calling.
Exceptions are raised if any step is not possible, e.g. if the backend does not
implement this function.

Finding a Backend
^^^^^^^^^^^^^^^^^

When a decorated function is called without a ``backend`` kwarg, it tries to find a
dispatchable backend function.
The backend type of each input graph parameter is resolved (using the
``__networkx_backend__`` attribute) and if they all agree, that backend's function
is called if possible. Otherwise the backends listed in the config ``backend_priority``
are considered one at a time in order. If that backend supports the function and
can convert the input graphs to its backend type, that backend function is called.
Otherwise the next backend is considered.

During this process, the backends can provide helpful information to the dispatcher
via helper methods in the backend's interface. Backend methods ``can_run`` and
``should_run`` are used by the dispatcher to determine whether to use the backend
function. If the number of nodes is small, it might be faster to run the NetworkX
version of the function. This is how backends can provide info about whether to run.

Falling Back to NetworkX
^^^^^^^^^^^^^^^^^^^^^^^^

If none of the backends are appropriate, we "fall back" to the NetworkX function.
That means we resolve the backends of all input graphs and if all are NetworkX
graphs we call the NetworkX function. If any are not NetworkX graphs, we raise
an exception unless the `fallback_to_nx` config is set. If it is, we convert all
graph types to NetworkX graph types before calling the NetworkX function.

Functions that mutate the graph
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any function decorated with the option that indicates it mutates the graph goes through
a slightly different path to automatically find backends. These functions typically
generate a graph, or add attributes or change the graph structure. The config
`backend_priority.generators` holds a list of backend names similar to the config
`backend_priority`. The process is similar for finding a matching backend. Once found,
the backend function is called and a backend graph is returned (instead of a NetworkX
graph). You can then use this backend graph in any function supported by the backend.
And you can use it for functions not supported by the backend if you set the config
`fallback_to_nx` to allow it to convert the backend graph to a NetworkX graph before
calling the function.

Optional keyword arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^

Backends can add optional keyword parameters to NetworkX functions to allow you to
control aspects of the backend algorithm. Thus the function signatures can be extended
beyond the NetworkX function signature. For example, the ``parallel`` backend might
have a parameter to specify how many CPUs to use. These parameters are collected
by the dispatchable decorator code at the start of the function call and used when
calling the backend function.

Existing Backends
^^^^^^^^^^^^^^^^^

NetworkX does not know all the backends that have been created.  In fact, the
NetworkX library does not need to know that a backend exists for it to work. As
long as the backend package creates the ``entry_point``, and provides the
correct interface, it will be called when the user requests it using one of the
three approaches described above. Some backends have been working with the
NetworkX developers to ensure smooth operation.

Refer to the :doc:`/backends` section to see a list of available backends known
to work with the current stable release of NetworkX.

.. _introspect:

Introspection and Logging
-------------------------
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
but introspection can be helpful by describing *when* and *how* to evolve your workflow
to meet your needs. If you have suggestions for how to improve introspection, please
`let us know <https://github.com/networkx/networkx/issues/new>`_!

Docs for backend developers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating a custom backend
-------------------------

1.  Defining a ``BackendInterface`` object:

    Note that the ``BackendInterface`` doesn't need to be a class. It can be an
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
          implemented by the backend, ``can_run`` and ``should_run`` are assumed to
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
            It is the name passed in the ``backend`` kwarg and must be a valid Python identifier.
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
    a string with the entry point name, which must be a valid Python identifier::

        class BackendGraph:
            __networkx_backend__ = "backend_name"
            ...

    Backend graph objects are also required to implement the methods ``is_directed()`` and
    ``is_multigraph()``. These methods return boolean values indicating the type of the graph:

    - ``is_directed()`` should return True if the graph is directed, and False otherwise.
    - ``is_multigraph()`` should return True if the graph allows multiple (parallel) edges
      between node pairs, and False otherwise.

    These methods are used by NetworkX utilities such as the ``@not_implemented_for`` decorator
    to determine whether a graph meets certain type constraints and to raise an error if the
    function is not applicable to that graph type.

    .. note::

       Decorators such as ``@not_implemented_for`` in networkx are applied prior to dispatching.
       Backend implementations can assume that graph-type constraints have
       already been validated.

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

.. automodule:: networkx.utils.backends

.. autosummary::
   :toctree: generated/

   _dispatchable
