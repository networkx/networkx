import math

import pytest

import networkx as nx
from networkx.algorithms.tree.mst import EdgePartition


def _sum_weights(edgelist):
    # Works for (u,v,d) and (u,v,k,d); defaults to weight=1 if absent
    total = 0
    for e in edgelist:
        d = e[-1] if isinstance(e[-1], dict) else {}
        total += d.get("weight", 1)
    return total


def test_equivalence_simple_graph():
    G = nx.cycle_graph(6)
    # give a non-uniform extra edge
    G.add_edge(0, 3, weight=2)
    # baseline
    e_std = list(nx.minimum_spanning_edges(G, algorithm="kruskal", data=True))
    # optimized
    e_opt = list(nx.minimum_spanning_edges(G, algorithm="kruskal_opt", data=True))

    assert len(e_opt) == len(e_std)
    assert _sum_weights(e_opt) == _sum_weights(e_std)


def test_equivalence_random_graph_seeded():
    # Deterministic random graph
    G = nx.gnp_random_graph(80, 0.07, seed=7)
    for u, v in G.edges():
        # simple deterministic weights
        G[u][v]["weight"] = ((u + 3 * v) % 11) + 1

    e_std = list(nx.minimum_spanning_edges(G, algorithm="kruskal", data=True))
    e_opt = list(nx.minimum_spanning_edges(G, algorithm="kruskal_opt", data=True))

    assert len(e_opt) == len(e_std)
    assert _sum_weights(e_opt) == _sum_weights(e_std)


def test_multigraph_keys_and_data():
    M = nx.MultiGraph()
    # parallel edges with different weights
    M.add_edge(0, 1, key="a", weight=5)
    M.add_edge(0, 1, key="b", weight=1)
    M.add_edge(1, 2, key="x", weight=3)
    M.add_edge(0, 2, key="y", weight=4)

    e_std = list(
        nx.minimum_spanning_edges(M, algorithm="kruskal", keys=True, data=True)
    )
    e_opt = list(
        nx.minimum_spanning_edges(M, algorithm="kruskal_opt", keys=True, data=True)
    )

    assert len(e_opt) == len(e_std)
    assert _sum_weights(e_opt) == _sum_weights(e_std)


def test_ignore_nan_behavior():
    G = nx.Graph()
    G.add_edge(0, 1, weight=1)
    G.add_edge(1, 2, weight=math.nan)
    G.add_edge(0, 2, weight=5)

    # Without ignore_nan: both should raise
    with pytest.raises(ValueError):
        list(nx.minimum_spanning_edges(G, algorithm="kruskal_opt", data=True))
    with pytest.raises(ValueError):
        list(nx.minimum_spanning_edges(G, algorithm="kruskal", data=True))

    # With ignore_nan=True: parity on weight and edge count
    e_std = list(
        nx.minimum_spanning_edges(G, algorithm="kruskal", data=True, ignore_nan=True)
    )
    e_opt = list(
        nx.minimum_spanning_edges(
            G, algorithm="kruskal_opt", data=True, ignore_nan=True
        )
    )
    assert len(e_opt) == len(e_std)
    assert _sum_weights(e_opt) == _sum_weights(e_std)


def test_partition_included_excluded_respected():
    G = nx.Graph()
    # Make a small diamond: 0-1-2 and 0-2, plus 1-3, 2-3
    G.add_edge(0, 1, weight=10)
    G.add_edge(1, 2, weight=1)
    G.add_edge(0, 2, weight=2)
    G.add_edge(1, 3, weight=1)
    G.add_edge(2, 3, weight=1)

    # Tag edges with a partition: force (0,2) INCLUDED, forbid (0,1)
    G[0][2]["part"] = EdgePartition.INCLUDED
    G[0][1]["part"] = EdgePartition.EXCLUDED

    e_std = list(
        nx.minimum_spanning_edges(
            G, algorithm="kruskal", data=True, ignore_nan=False, weight="weight"
        )
    )  # default does not look at our custom "part" key

    e_std_part = list(
        nx.minimum_spanning_edges(
            G,
            algorithm="kruskal",
            data=True,
            ignore_nan=False,
            weight="weight",
            # tell the backend which attribute carries the partition labels
            # (this is how kruskal_mst_edges supports partitions)
            # In minimum_spanning_edges, there's no 'partition' kwarg, but the underlying
            # kruskal backend reads it if present on edges and the name is passed through
            # via partition_spanning_tree or by calling kruskal directly. So here we call
            # kruskal directly to test parity with our opt backend.
        )
    )

    # To directly exercise partition behavior, call the backends explicitly:
    from networkx.algorithms.tree.mst import kruskal_mst_edges as KSTD
    from networkx.algorithms.tree.mst import kruskal_mst_edges_opt as KOPT

    e_kstd = list(
        KSTD(G, True, weight="weight", keys=True, data=True, partition="part")
    )
    e_kopt = list(
        KOPT(G, True, weight="weight", keys=True, data=True, partition="part")
    )

    # INCLUDED must appear, EXCLUDED must not
    assert any((u, v) == (0, 2) or (v, u) == (0, 2) for u, v, *_ in e_kopt)
    assert all((u, v) != (0, 1) and (v, u) != (0, 1) for u, v, *_ in e_kopt)

    # Parity with stock kruskal + partition
    assert len(e_kopt) == len(e_kstd)
    assert _sum_weights(e_kopt) == _sum_weights(e_kstd)


def test_directed_not_implemented():
    DG = nx.DiGraph()
    DG.add_edge(0, 1, weight=1)
    with pytest.raises(nx.NetworkXNotImplemented):
        list(nx.minimum_spanning_edges(DG, algorithm="kruskal_opt"))


def test_maximum_spanning_edges_parity():
    G = nx.gnp_random_graph(30, 0.15, seed=11)
    for u, v in G.edges():
        G[u][v]["weight"] = ((u * 17 + v * 31) % 13) + 1

    e_std = list(nx.maximum_spanning_edges(G, algorithm="kruskal", data=True))
    e_opt = list(nx.maximum_spanning_edges(G, algorithm="kruskal_opt", data=True))

    assert len(e_opt) == len(e_std)
    assert _sum_weights(e_opt) == _sum_weights(e_std)
