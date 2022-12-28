import pytest

import networkx as nx
from networkx.utils.misc import optional_package
from networkx.utils.parallel import NxParallel, chunks


def test_chunks():
    # Test dividing a list into a single chunk
    l = list(range(10))
    n = 1
    result = list(chunks(l, n))
    assert result == [(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,), (9,)]

    # Test dividing a list into multiple chunks
    l = list(range(10))
    n = 2
    result = list(chunks(l, n))
    assert result == [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]


@pytest.mark.parametrize(
    "backend",
    [
        "multiprocessing",
        "loky",
        "threading",
    ],
)
def test_NxParallel_init(backend):
    # Test initializing NxParallel with a supported backend
    nxp = NxParallel(backend=backend)
    assert nxp.backend == backend
    assert nxp.processes is not None

    # Test initializing NxParallel with a specified number of processes
    nxp = NxParallel(backend=backend, processes=4)
    assert nxp.backend == backend
    assert nxp.processes == 4

    if backend in ["multiprocessing", "loky", "threading"]:
        # Test initializing NxParallel with a specified number of processes
        nxp = NxParallel(backend=backend, processes=4)
        assert nxp.backend == backend
        assert nxp.processes == 4
    else:
        if backend == "dask":
            # Test initializing NxParallel with a required package that is not installed
            has_dask = optional_package(backend)[1]
            if not has_dask:
                with pytest.raises(ImportError):
                    nxp = NxParallel(backend=backend)
        elif backend == "ray":
            # Test initializing NxParallel with a required package that is not installed
            has_ray = optional_package(backend)[1]
            if not has_ray:
                with pytest.raises(ImportError):
                    nxp = NxParallel(backend=backend)
        elif backend == "ipyparallel":
            # Test initializing NxParallel with a required package that is not installed
            has_ipyparallel = optional_package(backend)[1]
            if not has_ipyparallel:
                with pytest.raises(ImportError):
                    nxp = NxParallel(backend=backend)


def test_unsupported_backend():
    # Test initializing NxParallel with an unsupported backend
    with pytest.raises(ValueError):
        nxp = NxParallel(backend="unsupported_backend")


def test_NxParallel_call():
    import time

    # Create an instance of the NxParallel class
    nxp = NxParallel(backend="multiprocessing", processes=4)

    G_ba = nx.barabasi_albert_graph(1000, 3)
    G_er = nx.gnp_random_graph(1000, 0.01)
    G_ws = nx.connected_watts_strogatz_graph(1000, 4, 0.1)

    def betweenness_centrality(G, parallel_callable=nxp):
        """Parallel betweenness centrality function"""
        node_divisor = parallel_callable.processes * 4
        node_chunks = list(chunks(G.nodes(), G.order() // node_divisor))
        num_chunks = len(node_chunks)
        iterable = zip(
            [G] * num_chunks,
            node_chunks,
            [list(G)] * num_chunks,
            [True] * num_chunks,
            [None] * num_chunks,
        )
        bt_sc = parallel_callable(nx.betweenness_centrality_subset, iterable)

        # Reduce the partial solutions
        bt_c = bt_sc[0]
        for bt in bt_sc[1:]:
            for n in bt:
                bt_c[n] += bt[n]
        return bt_c

    G_ba = nx.barabasi_albert_graph(1000, 3, seed=42)
    G_er = nx.gnp_random_graph(1000, 0.01, seed=42)
    G_ws = nx.connected_watts_strogatz_graph(1000, 4, 0.1, seed=42)
    for G in [G_ba, G_er, G_ws]:
        start = time.time()
        bt_parallel = betweenness_centrality(G, nxp)
        bt_parallel_time = time.time() - start

        start = time.time()
        bt_serial = nx.betweenness_centrality(G)
        bt_serial_time = time.time() - start

        assert bt_parallel == pytest.approx(bt_serial)
        assert bt_parallel_time < bt_serial_time
