"""
=========================================================================
Generating Node Feature Matrices and Diffusion Matrix Tensors from Graphs
=========================================================================

In this example, we show how two things:

1. How to obtain a node dataframe from NetworkX graphs
   using custom user-defined functions,
2. How to obtain an adjacency matrix/tensor from NetworkX graphs,
   using custom user-defined functions.

A tensor is a generalization of vectors & matrices
to arbitrary numbers of dimensions.
By convention, vectors are 1D, matrices are 2D,
and tensors are ND.
In the Python world, we refer to all of these as nD-arrays
(i.e. n-dimensional arrays).

This allows you to generate structured dataframes and xarray dataarrays
in a highly customized fashion.
The resulting data containers are highly compatible
with the rest of the PyData ecosystem,
and can easily be converted into NumPy arrays/tensors
to be fed into deep learning models.

An overview of the steps involved looks like this:

1. Create your graph with data attributes
1. Define functions to extract data.
    - For node DataFrames functions have signature:
    f(node, datadict) -> pd.Series.
    - For adjacency DataArray functions have signature: f(G) -> xr.DataArray.
    Use ``format_adjacency()`` to ease creation of the DataArray.
1. Call the relevant generate function
(``generate_node_dataframe`` or ``generate_adjacency_xarray``)

"""
import networkx as nx
import string
from random import choice
import pandas as pd
import numpy as np
from functools import partial
import xarray as xr


def make_graph():
    # Generate a graph
    G = nx.erdos_renyi_graph(n=20, p=0.1)

    # Add metadata to it:
    # - some arbitrary letter chosen from the English alphabet
    # - a random number chosen from the range(0,100)
    for node in G.nodes():
        G.nodes[node]["letter"] = choice(string.ascii_lowercase)
        G.nodes[node]["number"] = choice(range(100))
    return G


# %%
# Now, generate a node dataframe using a custom function.


def node_metadata(n, d):
    return pd.Series(d, name=n)


# %%
# We'll define a function that also transforms number by multiplying it by 10


def ten_times_number(n, d):
    return pd.Series({"10x_number": d["number"] * 10}, name=n)


# %%
# Now, generate node dataframe

G = make_graph()
funcs = [
    node_metadata,
    ten_times_number,
]
dataframe = nx.generate_node_dataframe(G, funcs)
assert set(dataframe.columns) == set(["letter", "number", "10x_number"])
assert set(dataframe.index) == set(G.nodes())

# %%
# We are now going to generate a graph's adjacency tensor.


def adjacency_power(G, n):
    A = np.asarray(nx.adjacency_matrix(G).todense())
    A = np.linalg.matrix_power(A, n)
    return nx.format_adjacency(G, A, name=f"adjacency_{n}")


def laplacian(G):
    A = np.asarray(nx.laplacian_matrix(G).todense())
    return nx.format_adjacency(G, A, name="laplacian_matrix")


G = make_graph()
adj_funcs = [
    partial(adjacency_power, n=1),
    partial(adjacency_power, n=2),
    partial(adjacency_power, n=3),
    laplacian,
]


adjacency_tensor = nx.generate_adjacency_xarray(G, adj_funcs)
assert isinstance(adjacency_tensor, xr.DataArray)
assert set(adjacency_tensor.dims) == set(["n1", "n2", "name"])
