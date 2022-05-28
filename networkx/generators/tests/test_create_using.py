import networkx as nx
import pytest


@pytest.mark.parametrize(
    "generator, kwargs",
    [
        (nx.fast_gnp_random_graph, {"n": 20, "p": 0.2, "directed": False}),
        (nx.fast_gnp_random_graph, {"n": 20, "p": 0.2, "directed": True}),
        (nx.gnp_random_graph, {"n": 20, "p": 0.2, "directed": False}),
        (nx.gnp_random_graph, {"n": 20, "p": 0.2, "directed": True}),
        (nx.dense_gnm_random_graph, {"n": 30, "m": 4}),
        (nx.gnm_random_graph, {"n": 30, "m": 4, "directed": False}),
        (nx.gnm_random_graph, {"n": 30, "m": 4, "directed": True}),
        (nx.newman_watts_strogatz_graph, {"n": 50, "k": 5, "p": 0.1}),
        (nx.watts_strogatz_graph, {"n": 50, "k": 5, "p": 0.1}),
        (nx.connected_watts_strogatz_graph, {"n": 50, "k": 5, "p": 0.1}),
        (nx.random_regular_graph, {"d": 5, "n": 20}),
        (nx.barabasi_albert_graph, {"n": 40, "m": 3}),
        (nx.dual_barabasi_albert_graph, {"n": 40, "m1": 3, "m2": 2, "p": 0.1}),
        (nx.extended_barabasi_albert_graph, {"n": 40, "m": 3, "p": 0.1, "q": 0.2}),
        (nx.powerlaw_cluster_graph, {"n": 40, "m": 3, "p": 0.1}),
        (nx.random_lobster, {"n": 40, "p1": 0.1, "p2": 0.2}),
        (nx.random_shell_graph, {"constructor": [(10, 20, 0.8), (20, 40, 0.8)]}),
        (nx.random_powerlaw_tree, {"n": 10, "seed": 14, "tries": 1}),
        (nx.random_kernel_graph, {"n": 10, "kernel_integral": lambda u, w, z: z - w}),
    ],
)
def test_create_using(generator, kwargs):
    class DummyGraph(nx.Graph):
        pass

    class DummyDiGraph(nx.DiGraph):
        pass

    create_using = DummyDiGraph if kwargs.get("directed") else DummyGraph
    graph = generator(**kwargs, create_using=create_using)
    assert isinstance(graph, create_using)
