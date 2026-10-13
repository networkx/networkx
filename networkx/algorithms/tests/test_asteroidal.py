import pytest

import networkx as nx


@pytest.mark.parametrize(
    ("graph", "expected"),
    [
        (nx.cycle_graph(6), False),
        (nx.path_graph(6), True),
        (nx.complete_graph(2), True),
        (nx.petersen_graph(), False),
        (nx.complete_graph(6), True),
        (nx.line_graph(nx.complete_graph(6)), False),
        (nx.empty_graph(10), True),
    ],
)
def test_is_at_free(graph, expected):
    assert nx.is_at_free(graph) == expected


@pytest.mark.parametrize("ast_fn", [nx.is_at_free, nx.find_asteroidal_triple])
@pytest.mark.parametrize("graph_type", [nx.DiGraph, nx.MultiDiGraph])
def test_asteroidal_not_implemented(ast_fn, graph_type):
    with pytest.raises(nx.NetworkXNotImplemented, match="not implemented for directed"):
        ast_fn(graph_type())
