import pytest

from networkx.algorithms.components import is_strongly_connected
from networkx.algorithms.connectivity import strong_connectivity_augmentation
from networkx.algorithms import condensation, source, sink, isolate, disjoint_union
from networkx.classes import Graph, MultiGraph, MultiDiGraph, DiGraph
from networkx.exception import NetworkXNotImplemented
from networkx.generators.classic import path_graph, balanced_tree, cycle_graph, complete_graph
from networkx.generators.random_graphs import fast_gnp_random_graph

from typing import Set




def arcs_for_augmentation(G: DiGraph) -> int:
    """ Bounds the number of arcs needed to make G strongly connected

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph.

    Returns
    -------
    ints
        A lower and an upper bound on the number of arcs needed to add to G
        to make G strongly connected
    Notes
    -----
    For upper and lower bound on augmenting arcs see
    Theorem 2 in Eswaran and Tarjan's algorithm https://epubs.siam.org/doi/abs/10.1137/0205044
    """
    G_condensation = condensation(G)

    isolated = set(isolate.isolates(G_condensation))
    sources = set(source.sources(G_condensation)) - isolated
    sinks = set(sink.sinks(G_condensation)) - isolated
    s: int = len(sources)
    t: int = len(sinks)
    q: int = len(isolated)

    if s + t + q > 1:
        return max(s, t) + q
    else:  # obviously s > 0 iff t > 0, thus s == t == 0
        return 0


def is_correctly_augmented(G: DiGraph()) -> bool:
    """Returns if eswaran_tarjan augments G and the augmenting set is minimal

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph.

    Returns
    -------
    correct : bool
       True if eswaran_tarjan augments eswaran_tarjan and is a minimal such set
       according to the lower bound by Eswaran and Tarjan

    Notes
    -----
    For upper and lower bound see
    Theorem 2 in Eswaran and Tarjan's algorithm https://epubs.siam.org/doi/abs/10.1137/0205044
    """

    G = G.copy()
    A = strong_connectivity_augmentation.eswaran_tarjan(G)
    n = arcs_for_augmentation(G)
    G.add_edges_from(A)
    return is_strongly_connected(G) and (len(A) == n)


class Teststrong_connectivity_augmentation:

    def test_directed(self):
        # Testing on directed graph, no exception expected
        exception = False
        try:
            strong_connectivity_augmentation.eswaran_tarjan(DiGraph())
        except:
            exception = True
        assert not exception

    def test_wrong_graph_type(self):
        # Testing on unsupported graph types, exception networkx.NetworkXNotImplemented expected
        with pytest.raises(NetworkXNotImplemented):
            strong_connectivity_augmentation.eswaran_tarjan(Graph())
        with pytest.raises(NetworkXNotImplemented):
            strong_connectivity_augmentation.eswaran_tarjan(MultiGraph())
        with pytest.raises(NetworkXNotImplemented):
            strong_connectivity_augmentation.eswaran_tarjan(MultiDiGraph())

    def test_output_format(self):
        # tests the type of the output on an elementary case. Expected a set of tuples of
        # length 2. We only test the most trivial case in so as not to depend
        # on the correctness of the implementation.

        G = DiGraph()
        assert isinstance(strong_connectivity_augmentation.eswaran_tarjan(G), Set)
        G.add_edge(0, 1)
        result = strong_connectivity_augmentation.eswaran_tarjan(G)
        assert isinstance(strong_connectivity_augmentation.eswaran_tarjan(G), Set)
        element = result.pop()
        assert isinstance(element, tuple)
        assert len(element) == 2

    def test_empty(self):
        # Testing on empty digraph, empty set expected.
        assert strong_connectivity_augmentation.eswaran_tarjan(DiGraph()) == set()

    def test_trivial(self):
        # Testing digraph with one vertex, empty set expected.
        assert strong_connectivity_augmentation.eswaran_tarjan(complete_graph(1, DiGraph())) == set()

    def test_directed_path_joins_ends(self):
        # Testing if called on directed path,
        # expected
        for i in range(2, 11):
            assert strong_connectivity_augmentation.eswaran_tarjan(path_graph(i, DiGraph())) == {(i - 1, 0)}

    """
    --------------------
    The following tests test the correct behaviour on corner cases
    in regard to s, t, p, q as defined in eswaran_tarjan
    --------------------
    """

    def test_A_critical_q_null_p_eq_st(self):
        # tests correct behaviour if q = 0 and p = s = t
        G = DiGraph()
        for i in range(0, 5):
            G.add_edge(2 * i, 2 * i + 1)
        assert is_correctly_augmented(G)

    def test_A_critical_q_null_p_lower_s_eq_t(self):
        # tests correct behaviour if q = 0 and p < s = t
        # To test this, we test in on a "crossroad" graph G
        # E(G) = {(a, m), (m, b), (c, m), (d, m)}
        # We test both if p + 1 = s = t and if the difference if bigger
        # and also if the underlying undirected graph is not connected
        G = DiGraph()
        G.add_edges_from({('a', 'm'), ('m', 'b'), ('c', 'm'), ('m', 'd')})
        assert is_correctly_augmented(G)

        H = DiGraph()
        H.add_edges_from({('a', 'm'), ('m', 'b'), ('c', 'm'), ('m', 'd'),
                          ('e', 'm'), ('m', 'f')})
        assert is_correctly_augmented(H)

        G = disjoint_union(G, H)
        assert is_correctly_augmented(G)

    def test_A_critical_q_null_p_lower_s_lower_t(self):
        # tests correct behaviour if q = 0 and p < s < t.
        # We extend our crossroad graph by extending the central cross
        # one vertex to each side. As previously, we test
        # if s + 1 = t and if the difference is bigger.
        # We also test correct behaviour on reversed graph.
        G = DiGraph()
        G.add_edges_from({('a', 'p'), ('p', 'm'), ('m', 'n'),
                          ('n', 'b'), ('n', 'c'), ('d', 'q'),
                          ('q', 'm'), ('m', 'o'), ('o', 'e')})
        assert is_correctly_augmented(G)
        G.add_edges_from({('o', 'f')})
        assert is_correctly_augmented(G)
        G = G.reverse()
        assert is_correctly_augmented(G)

    def test_A_critical_q_notnull_stp_null(self):
        # tests correct behaviour if q != 0 and 0 = p = s = t.
        # This will be done using generating number of graphs where
        # no two vertices are connected. G will have both, even and odd number
        # of vertices.
        n = 1
        for i in range(5):
            G: DiGraph = DiGraph()
            G.add_nodes_from({j for j in range(2 ** i + n)})
            n = n + 1
            assert is_correctly_augmented(G)

    def test_A_critical_q_notnull_p_eq_st_not_null(self):
        # tests correct behaviour if q != 0, 0 < p = s = t
        # To test this, we will test cases when p, s, t = {1, 2}
        # and q = {0, 1}
        G = DiGraph()
        G.add_node(0)
        H = path_graph(2, DiGraph())
        G = disjoint_union(G, H)
        assert is_correctly_augmented(G)

        H = path_graph(3, DiGraph())
        G = disjoint_union(G, H)
        assert is_correctly_augmented(G)

        H = DiGraph()
        H.add_node(0)
        G = disjoint_union(G, H)
        assert is_correctly_augmented(G)

    def test_A_critical_q_notnull_p_lower_s_eq_t(self):
        # tests correct behaviour if q != 0 and p < s = t
        # To test this, we test in on a "crossroad" graph G
        # E(G) = {(a, m), (m, b), (c, m), (d, m)}
        # We test both if p + 1 = s = t and if the difference if bigger
        # and also if the underlying undirected graph is not connected
        G = DiGraph()
        G.add_nodes_from({0})

        G.add_edges_from({('a', 'm'), ('m', 'b'), ('c', 'm'), ('m', 'd')})
        assert is_correctly_augmented(G)

        H = DiGraph()
        H.add_edges_from({('a', 'm'), ('m', 'b'), ('c', 'm'), ('m', 'd'),
                          ('e', 'm'), ('m', 'f')})
        assert is_correctly_augmented(H)

        G = disjoint_union(G, H)
        assert is_correctly_augmented(G)

        H.clear()
        H.add_nodes_from({0})
        G = disjoint_union(G, H)
        assert is_correctly_augmented(G)

    def test_A_critical_q_notnull_p_lower_s_lower_t(self):
        # tests correct behaviour if q = 0 and p < s < t.
        # We extend our crossroad graph by extending the central cross
        # one vertex to each side. As previously, we test
        # if s + 1 = t and if the difference is bigger.
        # Moreover, we test adding 1 resp. 2 isolated vertices.
        G = DiGraph()
        G.add_edges_from({('a', 'p'), ('p', 'm'), ('m', 'n'),
                          ('n', 'b'), ('n', 'c'), ('d', 'q'),
                          ('q', 'm'), ('m', 'o'), ('o', 'e')})
        assert is_correctly_augmented(G)
        G.add_edges_from({('o', 'f')})
        assert is_correctly_augmented(G)

        G.add_node(0)
        assert is_correctly_augmented(G)

        G.add_node(1)
        assert is_correctly_augmented(G)

    """
    --------------------
    End of testing corner cases regarding s, t, p, q
    --------------------
    """

    def test_tree_and_reversed(self):
        # Testing correct behaviour on trees, expecting to connect all leaves and one
        # leaf with root.
        for i in range(0, 5):
            G: DiGraph = balanced_tree(2, i, create_using=DiGraph)
            assert is_correctly_augmented(G)
            G = G.reverse()
            assert is_correctly_augmented(G)

    def test_several_disjoint_strongly_connected_components(self):
        # tests a correct behaviour of connecting isolated vertices when
        # there are more mutually disjoint strongly connected components,
        # this tests correct choice of representative and connecting only
        # isolated vertices.
        n = 0
        for i in range(0, 5):
            G: DiGraph = DiGraph()
            for j in range(2 ** i + n):
                C = cycle_graph(i + 2, create_using=DiGraph())
                G = disjoint_union(G, C)
            n = n + 1
            assert is_correctly_augmented(G)

    def test_random_graphs(self):
        # tests behaviour on (small) random graphs of different density.
        # Used to catch graph instances not caught in previous tests,
        # for which special tests should be created afterwards.
        for i in range(1, 100):
            p = 0.199
            while p < 1:
                G = fast_gnp_random_graph(i, p, directed=True)
                assert is_correctly_augmented(G)
                p += 0.2
