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

Backends need not be listed here in order to work, and there may be many
backends that NetworkX developers don't know about. You should be able to
install the backend, enable the backend using the `backend=...` keyword arg,
the `NETWORKX_BACKEND_PRIORITY` environment variable, or the config setting
`nx.config.backend_priority="..."` as described in the
[Tutorial](#using-networkx-backends).

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
*  - [nx-arangodb](https://github.com/arangodb/nx-arangodb)
   - Seamlessly adds ArangoDB as a persistence layer to NetworkX graphs
*  - [nx-neptune](https://github.com/awslabs/nx-neptune)
   - Seamlessly offload computation workloads to AWS Neptune Analytics service
```
