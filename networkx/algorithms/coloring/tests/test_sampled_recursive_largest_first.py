"""sampled recursive largest first test suite.

"""
import pytest

import networkx as nx

is_coloring = nx.algorithms.coloring.equitable_coloring.is_coloring


# --------------------------------------------------------------------------
# Basic tests
# For each basic graph, specify the number of expected colors.
BASIC_TEST_CASES = {
    nx.Graph(): 0,
    nx.path_graph([1]): 1,
    nx.Graph([(1, 2)]): 2,
    nx.Graph([(1, 2), (2, 3), (4, 5), (5, 6)]): 2,
    nx.cycle_graph(3): 3,
}


# ############################  tests ############################
@pytest.mark.parametrize("graph, n_colors", list(BASIC_TEST_CASES.items()))
@pytest.mark.parametrize("n_searches", [10, 100, 1_000, 10_000])
def test_basic_case(graph, n_colors, n_searches):
    coloring = nx.coloring.sampled_rlf_color(graph, n_searches=n_searches)
    assert verify_length(coloring, n_colors)
    assert verify_coloring(graph, coloring)


def test_bad_inputs():
    graph = nx.path_graph([1])
    pytest.raises(
        TypeError,
        nx.coloring.sampled_rlf_color,
        graph,
        n_searches="invalid search",
    )


def test_invalid_graph():
    graph = nx.DiGraph([(1, 2), (2, 3), (4, 5), (5, 6)])
    pytest.raises(
        nx.NetworkXNotImplemented, nx.coloring.sampled_rlf_color, graph, n_searches=10
    )


#  ############################  Utility functions ############################
def verify_coloring(graph, coloring):
    for node in graph.nodes():
        if node not in coloring:
            return False

        color = coloring[node]
        for neighbor in graph.neighbors(node):
            if coloring[neighbor] == color:
                return False

    return True


def verify_length(coloring, expected):
    return len(set(coloring.values())) == expected
