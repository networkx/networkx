from copy import deepcopy
from itertools import permutations

import pytest

import networkx as nx

from .local_structure_oracles import directed_oracle, weighted_closure_oracle


def test_undirected_closure_and_reciprocal_reduction():
    for G in nx.graph_atlas_g():
        reciprocal = G.to_directed()
        values = nx.closure(G)
        assert nx.closure(reciprocal) == pytest.approx(values)
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


@pytest.mark.parametrize("G", [nx.MultiGraph(), nx.MultiDiGraph()])
def test_multigraphs_rejected(G):
    with pytest.raises(nx.NetworkXNotImplemented):
        nx.closure(G)


def test_binary_total_against_endpoint_oracle():
    arcs = list(permutations(range(4), 2))
    for mask in range(1 << len(arcs)):
        G = nx.DiGraph()
        G.add_nodes_from(range(4))
        G.add_edges_from(e for bit, e in enumerate(arcs) if mask >> bit & 1)
        values = nx.closure(G)
        for v in G:
            assert values[v] == pytest.approx(directed_oracle(G, v)["total"])


def test_closure_contracts():
    G = nx.DiGraph([("ego", (1, 2)), ((1, 2), 7), ("ego", 7)])
    values = nx.closure(G)
    G.add_edge("ego", "ego", w=1e100)
    assert nx.closure(G) == values
    assert nx.closure(G, weight="w") == pytest.approx(values)
    assert nx.closure(G, (1, 2)) == values[(1, 2)]
    assert nx.closure(G, ["ego", "unknown"]) == {"ego": values["ego"]}
    assert nx.average_closure(G, "ego") == values["ego"]
    assert nx.average_closure(nx.Graph()) == 0
    assert nx.average_closure(nx.path_graph(3), count_zeros=False) == 0
    nx.set_edge_attributes(G, 0, "w")
    assert set(nx.closure(G, weight="w").values()) == {0.0}
    for value in [-1, float("nan"), float("inf"), "one"]:
        H = nx.Graph([(0, 1, {"w": value})])
        with pytest.raises(ValueError, match="finite nonnegative"):
            nx.closure(H, weight="w")
