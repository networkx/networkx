from copy import deepcopy
from itertools import permutations

import pytest

import networkx as nx

from .local_structure_oracles import directed_oracle, weighted_closure_oracle

PATTERNS = ("total", "source", "target", "head", "mid", "end", "cyclic")


@pytest.mark.parametrize("n", [3, 4])
def test_all_binary_digraphs_against_orientation_oracle(n):
    arcs = list(permutations(range(n), 2))
    for mask in range(1 << len(arcs)):
        G = nx.DiGraph()
        G.add_nodes_from(range(n))
        G.add_edges_from(e for bit, e in enumerate(arcs) if mask >> bit & 1)
        actual = {p: nx.directed_closure(G, pattern=p) for p in PATTERNS}
        reversed_graph = G.reverse(copy=False)
        reversal = {
            "total": "total",
            "source": "target",
            "target": "source",
            "head": "end",
            "end": "head",
            "mid": "mid",
            "cyclic": "cyclic",
        }
        for v in G:
            expected = directed_oracle(G, v)
            for p in PATTERNS:
                assert actual[p][v] == pytest.approx(expected[p]), (mask, v, p)
            assert actual["total"][v] == pytest.approx(
                (actual["source"][v] + actual["target"][v]) / 2
            )
        for p in PATTERNS:
            assert nx.directed_closure(reversed_graph, pattern=p) == pytest.approx(
                actual[reversal[p]]
            )


def test_undirected_closure_and_reciprocal_reduction():
    for G in nx.graph_atlas_g():
        reciprocal = G.to_directed()
        values = nx.closure(G)
        assert nx.directed_closure(reciprocal) == pytest.approx(values)
        for v in G:
            denom = sum(G.degree(j) - 1 for j in G[v])
            expected = 2 * nx.triangles(G, v) / denom if denom else 0
            assert values[v] == pytest.approx(expected)


@pytest.mark.parametrize("directed", [False, True])
def test_weighted_total_against_independent_paths(directed):
    for seed in range(15):
        G = nx.gnp_random_graph(6, 0.55, seed=seed, directed=directed)
        for index, (u, v) in enumerate(G.edges()):
            if index % 3:  # Also exercise the default weight of one.
                G[u][v]["w"] = (index % 7) / 3
        before = deepcopy(G)
        actual = nx.closure(G, weight="w")
        for v in G:
            assert actual[v] == pytest.approx(weighted_closure_oracle(G, v, "w"))
        assert nx.utils.graphs_equal(G, before)
        nx.set_edge_attributes(G, 1, "w")
        assert nx.closure(G, weight="w") == pytest.approx(nx.closure(G))


def test_contracts_loops_labels_and_averaging():
    G = nx.DiGraph([("a", (1, 2)), ((1, 2), 7), ("a", 7)])
    base = nx.closure(G)
    G.add_edge("a", "a", w=1e100)
    assert nx.closure(G) == base
    assert nx.closure(G, weight="w") == pytest.approx(base)
    assert nx.closure(G, (1, 2)) == base[(1, 2)]
    assert nx.closure(G, ["a", "missing"]) == {"a": base["a"]}
    assert nx.average_closure(G, "a") == base["a"]
    assert nx.average_directed_closure(G, ["a"], pattern="head") == nx.directed_closure(
        G, "a", pattern="head"
    )
    for p in PATTERNS:
        assert nx.directed_closure(G, pattern=p) == nx.directed_closure(
            nx.DiGraph([(u, v) for u, v in G.edges() if u != v]), pattern=p
        )
    assert nx.closure(nx.Graph()) == {}
    assert nx.average_closure(nx.Graph()) == 0
    assert nx.average_closure(nx.path_graph(3), count_zeros=False) == 0
    assert nx.average_directed_closure(nx.DiGraph(), count_zeros=False) == 0
    nx.set_edge_attributes(G, 0, "w")
    assert set(nx.closure(G, weight="w").values()) == {0.0}
    with pytest.raises(nx.NetworkXError):
        nx.closure(G, 999)


@pytest.mark.parametrize("G", [nx.MultiGraph(), nx.MultiDiGraph()])
def test_multigraphs_rejected(G):
    with pytest.raises(nx.NetworkXNotImplemented):
        nx.closure(G)


def test_unsupported_patterns_and_weights():
    with pytest.raises(nx.NetworkXNotImplemented):
        nx.directed_closure(nx.Graph())
    with pytest.raises(ValueError, match="pattern"):
        nx.directed_closure(nx.DiGraph(), pattern="typo")
    for p in PATTERNS[1:]:
        with pytest.raises(nx.NetworkXNotImplemented, match="Weighted"):
            nx.directed_closure(nx.DiGraph(), weight="w", pattern=p)
    for value in (-1, float("nan"), float("inf"), "1", 1j):
        G = nx.DiGraph([(0, 1, {"w": value})])
        with pytest.raises(ValueError, match="finite nonnegative"):
            nx.closure(G, weight="w")
