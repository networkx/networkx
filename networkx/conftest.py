import pytest
import networkx
import sys
import warnings


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
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
        message="literal_stringizer is deprecated*",
    )
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message="literal_destringizer is deprecated*",
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, message="is_string_like is deprecated*"
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, message="make_str is deprecated*"
    )
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message="context manager reversed is deprecated*",
    )
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message="This will return a generator in 3.0*",
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, message="betweenness_centrality_source*",
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, message="edge_betweeness*",
    )
    warnings.filterwarnings(
        "ignore",
        category=PendingDeprecationWarning,
        message="the matrix subclass is not the recommended way*",
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
    import yaml

    has_yaml = True
except ImportError:
    has_yaml = False

try:
    import pydot

    has_pydot = True
except ImportError:
    has_pydot = False

try:
    import ogr

    has_ogr = True
except ImportError:
    has_ogr = False


# List of files that pytest should ignore

collect_ignore = []

needs_numpy = [
    "algorithms/centrality/current_flow_closeness.py",
    "algorithms/node_classification/__init__.py",
    "algorithms/non_randomness.py",
    "algorithms/shortest_paths/dense.py",
    "linalg/bethehessianmatrix.py",
    "linalg/laplacianmatrix.py",
    "utils/misc.py",
]
needs_scipy = [
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
    "algorithms/node_classification/hmn.py",
    "algorithms/node_classification/lgc.py",
    "algorithms/similarity.py",
    "convert_matrix.py",
    "drawing/layout.py",
    "generators/spectral_graph_forge.py",
    "linalg/algebraicconnectivity.py",
    "linalg/attrmatrix.py",
    "linalg/graphmatrix.py",
    "linalg/modularitymatrix.py",
    "linalg/spectrum.py",
    "utils/rcm.py",
]
needs_matplotlib = ["drawing/nx_pylab.py"]
needs_pandas = ["convert_matrix.py"]
needs_yaml = ["readwrite/nx_yaml.py"]
needs_pygraphviz = ["drawing/nx_agraph.py"]
needs_pydot = ["drawing/nx_pydot.py"]
needs_ogr = ["readwrite/nx_shp.py"]

if not has_numpy:
    collect_ignore += needs_numpy
if not has_scipy:
    collect_ignore += needs_scipy
if not has_matplotlib:
    collect_ignore += needs_matplotlib
if not has_pandas:
    collect_ignore += needs_pandas
if not has_yaml:
    collect_ignore += needs_yaml
if not has_pygraphviz:
    collect_ignore += needs_pygraphviz
if not has_pydot:
    collect_ignore += needs_pydot
if not has_ogr:
    collect_ignore += needs_ogr

# FIXME:  This is to avoid errors on AppVeyor
if sys.platform.startswith("win"):
    collect_ignore += ["readwrite/graph6.py", "readwrite/sparse6.py"]
