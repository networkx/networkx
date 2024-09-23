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

NetworkX supports third-party backends to improve performance and add functionality.  Through runtime dispatching, NetworkX directs function calls to backends if available, or falls back to the default Python implementation if not. This approach allows users to create graph analysis workflows that are both optimized for a particular environment yet still portable across systems, without requiring code changes.  Common examples of backends include GPU accelerators, graph database adapters, efficient implementations based on linear algebra, and more.

## Installing backends

Backends are Python packages installed in the same environment as NetworkX, where installation procedures typically follow standard Python package conventions but may vary based on the individual backend.  Backend Python packages usually support installation from source and using `pip` with packages available from the Python Package Index (PyPI), but may also include support for `conda` and other package managers.  Consult the documentation for the specific backend to find out more.

## Using backends

Once installed, there are three way in which NetworkX will dispatch a function call to a backend, varying from simply setting an environment variable to
The most straightforward of which requires users to simply set an environment variable and run their existing, unmodified application, where NetworkX will dispatch function calls to the one or more backends that provide them, or fall back to the default Python implementation automatically if not supported.

### Assigning backend priority
NETWORKX_BACKEND_PRIORITY
nx.config.backend_priority

```{code-cell}
import networkx as nx
G = nx.Graph()
```

```{note}
NetworkX includes debug logging calls using Python's standard logging mechanism that can be enabled to help users understand when and how backends are being used.
<example of how to enable>
```

### backend= kwarg

```{code-cell}
import networkx as nx
G = nx.Graph()
```

### Type-based dispatching to backends

```{code-cell}
import networkx as nx
G = nx.Graph()
```

## Creating NetworkX backends


By definition, a {class}`Graph` is a collection of nodes (vertices) along with
identified pairs of nodes (called edges, links, etc). In NetworkX, nodes can
be any {py:term}`hashable` object e.g., a text string, an image, an XML object,
another Graph, a customized node object, etc.

```{note}
Python's `None` object is not allowed to be used as a node. It
determines whether optional function arguments have been assigned in many
functions.
```
