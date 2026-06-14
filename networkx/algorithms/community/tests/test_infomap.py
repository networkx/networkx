import pytest

import networkx as nx
from networkx.algorithms.community import infomap_communities

# Infomap is not implemented by networkx, so only run the substantive tests for
# backends that implement it.
no_backends_for_infomap = (
    "not set(nx.config.backend_priority.algos) & infomap_communities.backends"
)


def test_infomap_with_nx_backend():
    G = nx.karate_club_graph()
    with pytest.raises(NotImplementedError):
        nx.community.infomap_communities(G, backend="networkx")


@pytest.mark.skipif(no_backends_for_infomap)
def test_valid_partition():
    G = nx.karate_club_graph()
    partition = nx.community.infomap_communities(G)
    assert nx.community.is_partition(G, partition)


@pytest.mark.skipif(no_backends_for_infomap)
def test_labels_preserved():
    G = nx.karate_club_graph()
    partition = nx.community.infomap_communities(G)
    assert set().union(*partition) == set(G.nodes())


@pytest.mark.skipif(no_backends_for_infomap)
def test_directed():
    # Infomap is flow-based and supports directed graphs.
    G = nx.gnc_graph(50, seed=42)
    partition = nx.community.infomap_communities(G)
    assert nx.community.is_partition(G, partition)


@pytest.mark.skipif(no_backends_for_infomap)
def test_isolated_nodes():
    G = nx.karate_club_graph()
    G.add_node("isolated")
    partition = nx.community.infomap_communities(G)
    assert {"isolated"} in partition


@pytest.mark.skipif(no_backends_for_infomap)
def test_weight_param():
    G = nx.karate_club_graph()
    nx.set_edge_attributes(
        G, {edge: i * i for i, edge in enumerate(G.edges)}, name="foo"
    )
    partition_none = nx.community.infomap_communities(G, weight=None, seed=2)
    partition_foo = nx.community.infomap_communities(G, weight="foo", seed=2)

    assert nx.community.is_partition(G, partition_none)
    assert nx.community.is_partition(G, partition_foo)


@pytest.mark.skipif(no_backends_for_infomap)
def test_seed_reproducible():
    G = nx.karate_club_graph()
    p1 = nx.community.infomap_communities(G, seed=42)
    p2 = nx.community.infomap_communities(G, seed=42)
    assert sorted(map(sorted, p1)) == sorted(map(sorted, p2))
