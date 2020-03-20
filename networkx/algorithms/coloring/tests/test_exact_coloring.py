"""Exact coloring unit tests"""

import networkx as nx
import pytest
import itertools
from networkx.algorithms.coloring.tests.test_coloring \
    import verify_length, verify_coloring


class TestExactColoring:
    fixed_graphs = [
                    (2, nx.generators.small.cubical_graph()),
                    (2, nx.generators.small.desargues_graph()),
                    (2, nx.generators.small.heawood_graph()),
                    (2, nx.generators.small.moebius_kantor_graph()),
                    (2, nx.generators.small.pappus_graph()),
                    (3, nx.generators.small.bull_graph()),
                    (3, nx.generators.small.diamond_graph()),
                    (3, nx.generators.small.dodecahedral_graph()),
                    (3, nx.generators.small.frucht_graph()),
                    (3, nx.generators.small.octahedral_graph()),
                    (3, nx.generators.small.petersen_graph()),
                    (3, nx.generators.small.truncated_cube_graph()),
                    (3, nx.generators.small.truncated_tetrahedron_graph()),
                    (3, nx.generators.small.tutte_graph()),
                    (4, nx.generators.small.chvatal_graph()),
                    (4, nx.generators.small.icosahedral_graph()),
                    (4, nx.generators.small.hoffman_singleton_graph()),
                    (4, nx.generators.small.house_x_graph()),
                    (4, nx.generators.small.tetrahedral_graph()),
                    (5, nx.generators.classic.lollipop_graph(5, 3)),
                    (6, nx.generators.classic.lollipop_graph(6, 6))
                    ]

    disjoint_components = []
    for f in fixed_graphs[-3:]:
        for g in fixed_graphs[-5:-2]:
            for h in fixed_graphs[-7:-4]:
                disjoint_components.append(
                        (
                            max(f[0], g[0], h[0]),
                            nx.disjoint_union_all([f[1], g[1], h[1]])
                        )
                    )

    generated_graphs = [(2, nx.star_graph(n)) for n in range(1, 7)]\
        + [(2, nx.path_graph(n)) for n in range(2, 7)]\
        + [(1, nx.empty_graph(n)) for n in range(1, 7)]\
        + [(2, nx.ladder_graph(n)) for n in range(2, 7)]\
        + [(n, nx.complete_graph(n)) for n in range(0, 60)]\
        + [(2, nx.cycle_graph(n * 2)) for n in range(1, 7)]\
        + [(n, nx.mycielski_graph(n)) for n in range(1, 5)]\
        + [(2, tree) for tree in nx.nonisomorphic_trees(7)]\
        + [(n, nx.barbell_graph(n, n)) for n in range(3, 10)]\
        + [(3, nx.cycle_graph(n * 2 + 1)) for n in range(1, 7)]\
        + [(4 if n % 2 == 0 else 3, nx.wheel_graph(n)) for n in range(3, 30)]\
        + [(2, nx.generators.lattice.hypercube_graph(n)) for n in range(1, 4)]\
        + list(itertools.chain.from_iterable(
            [
                (r, nx.turan_graph(n, r)) for r in range(1, n + 1)
            ] for n in range(1, 7)))\
        + list(itertools.chain.from_iterable(
            [
                (r, nx.windmill_graph(n, r)) for r in range(2, n * 2)
            ] for n in range(1, 7)))

    @pytest.mark.parametrize(
                            "expected_chromatic_number, test_graph",
                            fixed_graphs
                            )
    def test_fixed_graphs(self, expected_chromatic_number, test_graph):
        coloring = nx.coloring.exact_color(test_graph)
        assert verify_length(coloring, expected_chromatic_number)
        assert verify_coloring(test_graph, coloring)

    @pytest.mark.parametrize(
                            "expected_chromatic_number, test_graph",
                            generated_graphs
                            )
    def test_generated_graphs(self, expected_chromatic_number, test_graph):
        coloring = nx.coloring.exact_color(test_graph)
        assert verify_length(coloring, expected_chromatic_number)
        assert verify_coloring(test_graph, coloring)

    @pytest.mark.parametrize(
                            "expected_chromatic_number, test_graph",
                            disjoint_components
                            )
    def test_disjoint_graphs(self, expected_chromatic_number, test_graph):
        coloring = nx.coloring.exact_color(test_graph)
        assert verify_length(coloring, expected_chromatic_number)
        assert verify_coloring(test_graph, coloring)
