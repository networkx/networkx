"""Exact coloring unit tests"""

import networkx as nx
import pytest
import itertools
from networkx.algorithms.coloring.tests.test_coloring import verify_length, verify_coloring


class TestColoring:

    graphs = [
        (3, nx.generators.small.petersen_graph()),
    ]\
    + [(2, nx.cycle_graph(n * 2)) for n in range(1, 7)]\
    + [(n, nx.complete_graph(n)) for n in range(0, 30)]\
    + [(3, nx.cycle_graph(n * 2 + 1)) for n in range(1, 7)]\
    + [(4 if n % 2 == 0 else 3, nx.wheel_graph(n)) for n in range(3, 30)]\
    + [(n, nx.mycielski_graph(n)) for n in range(1, 5)]\
    + list(itertools.chain.from_iterable([(r, nx.turan_graph(n, r)) for r in range(1, n+1)] for n in range(1, 7)))\


    @pytest.mark.parametrize("expected_chromatic_number,test_graph", graphs)
    def test_graphs(self, expected_chromatic_number, test_graph):
        coloring = nx.coloring.exact_color(test_graph)
        assert verify_length(coloring, expected_chromatic_number)
        assert verify_coloring(test_graph, coloring)
