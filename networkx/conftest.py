"""
Testing
=======

General guidelines for writing good tests:

- doctests always assume ``import networkx as nx`` so don't add that
- prefer pytest fixtures over classes with setup methods.
- use the ``@pytest.mark.parametrize``  decorator
- use ``pytest.importorskip`` for numpy, scipy, pandas, and matplotlib b/c of PyPy.
  and add the module to the relevant entries below.

"""
import sys
import warnings

import pytest

import networkx


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    # Allow pluggable backends to add markers to tests when
    # running in auto-conversion test mode
    networkx.classes.backends._mark_tests(items)

    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


# TODO: The warnings below need to be dealt with, but for now we silence them.
@pytest.fixture(autouse=True)
def set_warnings():
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message="literal_stringizer is deprecated",
    )
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message="literal_destringizer is deprecated",
    )
    # create_using for scale_free_graph
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, message="The create_using argument"
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, message="nx.nx_pydot"
    )
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message="\n\nThe `attrs` keyword argument of node_link",
    )


@pytest.fixture(autouse=True)
def add_nx(doctest_namespace):
    doctest_namespace["nx"] = networkx


# What dependencies are installed?

try:
    import numpy

    has_numpy = True
except ImportError:
    has_numpy = False

try:
    import scipy

    has_scipy = True
except ImportError:
    has_scipy = False

try:
    import matplotlib

    has_matplotlib = True
except ImportError:
    has_matplotlib = False

try:
    import pandas

    has_pandas = True
except ImportError:
    has_pandas = False

try:
    import pygraphviz

    has_pygraphviz = True
except ImportError:
    has_pygraphviz = False

try:
    import pydot

    has_pydot = True
except ImportError:
    has_pydot = False

try:
    import sympy

    has_sympy = True
except ImportError:
    has_sympy = False


# List of files that pytest should ignore

collect_ignore = []

needs_numpy = [
    "algorithms/approximation/traveling_salesman.py",
    "algorithms/centrality/current_flow_closeness.py",
    "algorithms/node_classification.py",
    "algorithms/non_randomness.py",
    "algorithms/shortest_paths/dense.py",
    "linalg/bethehessianmatrix.py",
    "linalg/laplacianmatrix.py",
    "utils/misc.py",
]
needs_scipy = [
    "algorithms/approximation/traveling_salesman.py",
    "algorithms/assortativity/correlation.py",
    "algorithms/assortativity/mixing.py",
    "algorithms/assortativity/pairs.py",
    "algorithms/bipartite/matrix.py",
    "algorithms/bipartite/spectral.py",
    "algorithms/centrality/current_flow_betweenness.py",
    "algorithms/centrality/current_flow_betweenness_subset.py",
    "algorithms/centrality/eigenvector.py",
    "algorithms/centrality/katz.py",
    "algorithms/centrality/second_order.py",
    "algorithms/centrality/subgraph_alg.py",
    "algorithms/communicability_alg.py",
    "algorithms/link_analysis/hits_alg.py",
    "algorithms/link_analysis/pagerank_alg.py",
    "algorithms/node_classification.py",
    "algorithms/similarity.py",
    "convert_matrix.py",
    "drawing/layout.py",
    "generators/spectral_graph_forge.py",
    "linalg/algebraicconnectivity.py",
    "linalg/attrmatrix.py",
    "linalg/bethehessianmatrix.py",
    "linalg/graphmatrix.py",
    "linalg/modularitymatrix.py",
    "linalg/spectrum.py",
    "utils/rcm.py",
]
needs_matplotlib = ["drawing/nx_pylab.py"]
needs_pandas = ["convert_matrix.py"]
needs_pygraphviz = ["drawing/nx_agraph.py"]
needs_pydot = ["drawing/nx_pydot.py"]
needs_sympy = ["algorithms/polynomials.py"]

if not has_numpy:
    collect_ignore += needs_numpy
if not has_scipy:
    collect_ignore += needs_scipy
if not has_matplotlib:
    collect_ignore += needs_matplotlib
if not has_pandas:
    collect_ignore += needs_pandas
if not has_pygraphviz:
    collect_ignore += needs_pygraphviz
if not has_pydot:
    collect_ignore += needs_pydot
if not has_sympy:
    collect_ignore += needs_sympy
