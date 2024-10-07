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

The following backends are known to work with the current stable release of
NetworkX.

See the documentation for a particular backend for a description of
the NetworkX functions it provides, how to install it, and any special
backend-specific configurations it supports.

```{list-table}
:header-rows: 1
*  - Name
   - Description
*  - [nx-parallel](https://github.com/networkx/nx-parallel)
   - Parallelized implementations of various NetworkX functions using joblib
*  - [nx-cugraph](https://rapids.ai/nx-cugraph)
   - GPU acceleration using RAPIDS cuGraph and NVIDIA GPUs
*  - [nx-arangodb](https://nx-arangodb.readthedocs.io/en/latest/)
   - Seamlessly adds ArangoDB as a persistence layer to NetworkX graphs
```
