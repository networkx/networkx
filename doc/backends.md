---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Backends

```{currentmodule} networkx
```

NetworkX supports third-party backends to improve performance and add functionality.  Through runtime dispatching, NetworkX directs function calls to backends if available, or falls back to the default Python implementation if not.  The vast majority of functions in the NetworkX library are "dispatchable", meaning NetworkX will attempt to dispatch calls to those functions if an enabled backend supports them.  This approach allows users to create graph analysis workflows that are both optimized for a particular environment yet still portable to different systems, without requiring code changes.  Common examples of backends include GPU accelerators, graph database adapters, efficient linear algebra-based implementations, parallel processing implementations, and more.

## Installing backends

Backends are Python packages installed in the same environment as NetworkX, where installation procedures typically follow standard Python package conventions but may vary based on the individual backend.  Backend Python packages usually support installation from source and using `pip` with packages available from the Python Package Index (PyPI), but may also include support for `conda` and other package managers.  Consult the documentation for the specific backend to find out more.

## Using backends

There are three ways users can run with backends in their NetworkX application:
* Automatic dispatch - adding the backend name to the prioritized list of backends for NetworkX to use whenever a dispatchable function is called
* Explicit dispatch - explicitly specifying the backend to use for a dispatchable NetworkX function with the `backend=` keyword argument
* Type-based dispatch - instantiating a backend graph type and passing that to a dispatchable NetworkX function

### Automatic dispatch

Possibly the easiest way to incorporate backends into a NetworkX application is through automatic dispatch.  Automatic dispatch does not require users to modify their code when using backends, allowing for "portable" NetworkX applications.  Through automatic dispatch, a user can run NetworkX code with backeds optimized for one particular system, then share the same code with other users that may not have any backends or a different set of backends optimized for a different system.

Automatic dispath is enabled by simply setting an environment variable, or NetworkX configuration, to a list of at least one installed backend.  If more than one backend is to be used, then the list should be ordered based on the desired priority which NetworkX should use in the event multiple backends implement the same function.  If a NetworkX function is called which none of the specified backends implement, NetworkX will automatically fall back to the default python-based implementation.

```{code-cell}
bash> NETWORKX_BACKEND_PRIORITY=gpu_accelerator python my_nx_app.py
```

```{code-cell}
import networkx as nx
nx.config.backend_priority = ["gpu_accelerator"]
```

```{note}
NetworkX includes debug logging calls using Python's standard logging mechanism that can be enabled to help users understand when and how backends are being used.
<example of how to enable>
```

### Explicit dispatch

```{code-cell}
import networkx as nx
G = nx.karate_club_graph()

pagerank_results = nx.pagerank(G, backend="fast_backend")
```

### Type-based dispatch

```{code-cell}
import networkx as nx

# This code requires the db_backend backend to be installed
import db_backend
G = db_backend.Graph(graph_name="team_project1", server="dbserver", port="1234")

# The remaining code is standard NetworkX
pagerank_results = nx.pagerank(G)
```

## Creating NetworkX backends

See the section on "backends" in the Reference docs.

## Other use cases for backends

Adding functionality (extra options, etc.) to existing NetworkX functions, adding new functions to NetworkX (requires a NetworkX update), prototype alternate implementations.