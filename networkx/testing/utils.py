from networkx.utils import nodes_equal, edges_equal, graphs_equal

__all__ = [
    "assert_nodes_equal",
    "assert_edges_equal",
    "assert_graphs_equal",
    "almost_equal",
]


def almost_equal(x, y, places=7):
    import warnings

    warnings.warn(
        (
            "`almost_equal` is deprecated and will be removed in version 3.0.\n"
            "Use `pytest.approx` instead.\n"
        ),
        DeprecationWarning,
    )
    return round(abs(x - y), places) == 0


def assert_nodes_equal(nodes1, nodes2):
    assert nodes_equal(nodes1, nodes2)


def assert_edges_equal(edges1, edges2):
    assert edges_equal(edges1, edges2)


def assert_graphs_equal(graph1, graph2):
    assert graphs_equal(graph1, graph2)
