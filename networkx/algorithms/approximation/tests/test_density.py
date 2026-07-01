import pytest

import networkx as nx
import networkx.algorithms.approximation as approx

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def close_cliques_example(d=12, D=300, h=24, k=2):
    """
    Hard example from Harb, Elfarouk, Kent Quanrud, and Chandra Chekuri.
    "Faster and scalable algorithms for densest subgraph and decomposition."
    Advances in Neural Information Processing Systems 35 (2022): 26966-26979.
    """
    Kh = nx.complete_graph(h)
    KdD = nx.complete_bipartite_graph(d, D)
    G = nx.disjoint_union_all([KdD] + [Kh for _ in range(k)])
    best_density = d * D / (d + D)  # of the complete bipartite graph
    return G, best_density, set(KdD.nodes)


@pytest.fixture(
    params=(
        "greedy++",
        pytest.param(
            "fista",
            marks=pytest.mark.skipif(not HAS_NUMPY, reason="fista requires numpy"),
        ),
    )
)
def method(request):
    return request.param


def _compute_density(family, n):
    if family == nx.star_graph:
        # The densest subgraph of a star network is the entire graph.
        # The peeling algorithm would peel all the vertices with degree 1,
        # and so should discover the densest subgraph in one iteration!
        return n / (n + 1), set(range(n + 1))
    elif family == nx.complete_graph:
        # The density of a complete graph network is the entire graph: C(n, 2)/n
        # where C(n, 2) is n*(n-1)//2. The peeling algorithm would find
        # the densest subgraph in one iteration!
        return (n - 1) / 2, set(range(n))
    elif family == nx.empty_graph:
        return 0, set()
    else:
        msg = f"unknown {family=} family"
        raise ValueError(msg)


@pytest.mark.parametrize("n", range(4, 7))
@pytest.mark.parametrize("iterations", (1, 3))
@pytest.mark.parametrize("family", (nx.star_graph, nx.complete_graph, nx.empty_graph))
def test_densest_subgraph(n, iterations, family, method):
    G = family(n)
    d, S = approx.densest_subgraph(G, iterations=iterations, method=method)
    correct_density, correct_subgraph_set = _compute_density(family, n)
    assert d == pytest.approx(correct_density)
    assert S == correct_subgraph_set


def test_greedy_plus_plus_close_cliques():
    G, best_density, densest_set = close_cliques_example()
    # NOTE: iterations=185 fails to ID the densest subgraph
    greedy_pp, S_pp = approx.densest_subgraph(G, iterations=186, method="greedy++")

    assert greedy_pp == pytest.approx(best_density)
    assert S_pp == densest_set


def test_fista_close_cliques():
    pytest.importorskip("numpy")
    G, best_density, best_set = close_cliques_example()
    # NOTE: iterations=12 fails to ID the densest subgraph
    density, dense_set = approx.densest_subgraph(G, iterations=13, method="fista")

    assert density == pytest.approx(best_density)
    assert dense_set == best_set


def bipartite_and_clique_example(d=5, D=200, k=2):
    """
    Hard example from: Boob, Digvijay, Yu Gao, Richard Peng, Saurabh Sawlani,
    Charalampos Tsourakakis, Di Wang, and Junxing Wang. "Flowless: Extracting
    densest subgraphs without flow computations." In Proceedings of The Web
    Conference 2020, pp. 573-583. 2020.
    """
    B = nx.complete_bipartite_graph(d, D)
    H = [nx.complete_graph(d + 2) for _ in range(k)]
    G = nx.disjoint_union_all([B] + H)

    best_density = d * D / (d + D)  # of the complete bipartite graph
    correct_one_round_density = (2 * d * D + (d + 1) * (d + 2) * k) / (
        2 * d + 2 * D + 2 * k * (d + 2)
    )
    best_subgraph = set(B.nodes)
    return G, best_density, best_subgraph, correct_one_round_density


def test_bipartite_and_clique_greedy_plus_plus_one_iter():
    G, _, _, correct_one_iter_density = bipartite_and_clique_example()
    one_round_density, S_one = approx.densest_subgraph(
        G, iterations=1, method="greedy++"
    )
    assert one_round_density == pytest.approx(correct_one_iter_density)
    assert S_one == set(G.nodes)


def test_bipartite_and_clique_ten_iter(method):
    G, best_density, best_subgraph, _ = bipartite_and_clique_example()
    ten_round_density, S_ten = approx.densest_subgraph(G, iterations=10, method=method)
    assert ten_round_density == pytest.approx(best_density)
    assert S_ten == best_subgraph


def test_fista_big_dataset():
    pytest.importorskip("numpy")
    G, best_density, best_subgraph = close_cliques_example(d=30, D=2000, h=60, k=20)

    # Note: iterations=12 fails to identify densest subgraph
    density, dense_set = approx.densest_subgraph(G, iterations=13, method="fista")

    assert density == pytest.approx(best_density)
    assert dense_set == best_subgraph


def test_densest_subgraph_self_loop(method):
    """Test that self-loops don't repeat calculations."""
    G = nx.complete_graph(7)
    G.add_edges_from([(0, 7), (7, 7)])
    # 7 is the lowest degree node, so it will be removed first.
    # However, it will be re-added as neighbor (due to the self-loop) and be skipped.

    density, dense_set = approx.densest_subgraph(G, method=method)
    assert density == pytest.approx(density)
    assert dense_set == dense_set


def test_densest_subgraph_invalid_iterations(method):
    """Test that `iterations < 1` raises."""
    with pytest.raises(ValueError, match="iterations must be"):
        approx.densest_subgraph(nx.complete_graph(3), iterations=0, method=method)


def test_densest_subgraph_invalid_method():
    """Test that `method` is validated."""
    with pytest.raises(ValueError, match="not a valid choice"):
        approx.densest_subgraph(nx.complete_graph(3), method="dummy")


@pytest.mark.parametrize("labels", ((1, 2, 3), ("a", "b", "c")))
def test_gh_8271(labels):
    """Test for graphs with nonstandard node labels."""
    pytest.importorskip("numpy")
    G = nx.complete_graph(labels)
    assert approx.densest_subgraph(G, method="fista") == (1, set(labels))
