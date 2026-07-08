from itertools import combinations

import pytest

import networkx as nx

torch = pytest.importorskip("torch")
pytest.importorskip("torch_geometric")
pytest.importorskip("numpy")
pytest.importorskip("scipy")


def _fast_nocd_kwargs(**overrides):
    defaults = {
        "num_communities": 4,
        "epochs": 80,
        "eval_frequency": 20,
        "patience_epochs": 2,
        "hidden_dim": 32,
        "batch_size": 100,
        "seed": 0,
    }
    defaults.update(overrides)
    return defaults


def test_overlapping_k5_cover():
    G = nx.Graph()
    G.add_edges_from(combinations(range(5), 2))
    G.add_edges_from(combinations(range(2, 7), 2))
    comms = list(nx.community.nocd_communities(G, **_fast_nocd_kwargs()))
    assert nx.community.is_cover(G, comms)
    assert all(isinstance(c, frozenset) for c in comms)


def test_isolated_k5_cover():
    G = nx.Graph()
    G.add_edges_from(combinations(range(5), 2))
    G.add_edges_from(combinations(range(5, 10), 2))
    comms = list(nx.community.nocd_communities(G, **_fast_nocd_kwargs()))
    assert nx.community.is_cover(G, comms)


def test_karate_club_cover():
    G = nx.karate_club_graph()
    comms = list(
        nx.community.nocd_communities(G, **_fast_nocd_kwargs(num_communities=6))
    )
    assert nx.community.is_cover(G, comms)


def test_reproducible_with_seed():
    G = nx.karate_club_graph()
    kwargs = _fast_nocd_kwargs(num_communities=5, seed=42)
    a = set(nx.community.nocd_communities(G, **kwargs))
    b = set(nx.community.nocd_communities(G, **kwargs))
    assert a == b


def test_no_edges_raises():
    G = nx.Graph()
    G.add_node(0)
    with pytest.raises(nx.NetworkXError, match="at least one edge"):
        list(nx.community.nocd_communities(G, **_fast_nocd_kwargs()))


def test_bad_num_communities():
    G = nx.complete_graph(4)
    with pytest.raises(nx.NetworkXError, match="num_communities"):
        list(nx.community.nocd_communities(G, **_fast_nocd_kwargs(num_communities=0)))


def test_directed_converted_to_undirected():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    comms = list(nx.community.nocd_communities(G, **_fast_nocd_kwargs()))
    assert nx.community.is_cover(G, comms)
