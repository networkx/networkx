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
