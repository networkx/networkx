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

NetworkX supports third-party backends which can improve performance and add functionality.

## Using backends

There are multiple ways to use NetworkX backends.

```{code-cell}
import networkx as nx
G = nx.Graph()
```

By definition, a {class}`Graph` is a collection of nodes (vertices) along with
identified pairs of nodes (called edges, links, etc). In NetworkX, nodes can
be any {py:term}`hashable` object e.g., a text string, an image, an XML object,
another Graph, a customized node object, etc.

```{note}
Python's `None` object is not allowed to be used as a node. It
determines whether optional function arguments have been assigned in many
functions.
```
