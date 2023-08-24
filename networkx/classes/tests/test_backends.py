import pickle

import pytest

import networkx as nx

pytest.importorskip("scipy")
pytest.importorskip("numpy")


def test_dispatch_kwds_vs_args():
    G = nx.path_graph(4)
    nx.pagerank(G)
    nx.pagerank(G=G)
    with pytest.raises(TypeError):
        nx.pagerank()


def test_pickle():
    for name, func in nx.utils.backends._registered_algorithms.items():
        assert pickle.loads(pickle.dumps(func)) is func
    assert pickle.loads(pickle.dumps(nx.inverse_line_graph)) is nx.inverse_line_graph
