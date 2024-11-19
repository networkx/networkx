import pytest
import networkx as nx
from networkx.algorithms import bipartite
from networkx.algorithms.bipartite import color, is_bipartite, sets


class TestBipartiteBasic:
    def test_is_bipartite(self):
        assert bipartite.is_bipartite(nx.path_graph(4))
        assert bipartite.is_bipartite(nx.DiGraph([(1, 0)]))
        assert not bipartite.is_bipartite(nx.complete_graph(3))

    def test_bipartite_color(self):
        G = nx.path_graph(4)
        c = bipartite.color(G)
        assert c == {0: 1, 1: 0, 2: 1, 3: 0}

    def test_not_bipartite_color(self):
        with pytest.raises(nx.NetworkXError):
            c = bipartite.color(nx.complete_graph(4))

    def test_relaxed_color(self):
        # Test relaxed coloring on non-bipartite graph
        G = nx.cycle_graph(3)  # Odd cycle, not bipartite
        c = bipartite.color(G, relaxed=True)
        # Check that colors are assigned
        assert all(color in {0, 1} for color in c.values())

        # Test relaxed coloring on disconnected graph with mixed components
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 0)])  # Non-bipartite component
        G.add_edges_from([(3, 4), (4, 5)])  # Bipartite component
        c = bipartite.color(G, relaxed=True)
        # Check that all nodes are colored
        assert len(c) == 6
        assert all(color in {0, 1} for color in c.values())

    def test_relaxed_is_bipartite(self):
        # Test with mixed graph (both bipartite and non-bipartite components)
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 0)])  # Non-bipartite triangle
        G.add_edges_from([(3, 4), (4, 5)])  # Bipartite path
        assert not bipartite.is_bipartite(G)  # Should fail without relaxed
        assert bipartite.is_bipartite(G, relaxed=True)  # Should pass with relaxed

    def test_relaxed_sets(self):
        # Test with disconnected graph
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3)])  # Path graph
        G.add_edges_from([(4, 5), (5, 6)])  # Another component
        X, Y = bipartite.sets(G, relaxed=True)
        assert isinstance(X, set) and isinstance(Y, set)
        assert X.union(Y) == set(G.nodes())
        assert X.intersection(Y) == set()

        # Test with non-bipartite component
        G.add_edges_from([(7, 8), (8, 9), (9, 7)])  # Add triangle
        X, Y = bipartite.sets(G, relaxed=True)
        assert isinstance(X, set) and isinstance(Y, set)
        assert X.union(Y) == set(G.nodes())

    def test_bipartite_directed(self):
        G = bipartite.random_graph(10, 10, 0.1, directed=True)
        assert bipartite.is_bipartite(G)

    def test_bipartite_sets(self):
        G = nx.path_graph(4)
        X, Y = bipartite.sets(G)
        assert X == {0, 2}
        assert Y == {1, 3}

    def test_bipartite_sets_directed(self):
        G = nx.path_graph(4)
        D = G.to_directed()
        X, Y = bipartite.sets(D)
        assert X == {0, 2}
        assert Y == {1, 3}

    def test_bipartite_sets_given_top_nodes(self):
        G = nx.path_graph(4)
        top_nodes = [0, 2]
        X, Y = bipartite.sets(G, top_nodes)
        assert X == {0, 2}
        assert Y == {1, 3}

    def test_bipartite_sets_disconnected(self):
        with pytest.raises(nx.AmbiguousSolution):
            G = nx.path_graph(4)
            G.add_edges_from([(5, 6), (6, 7)])
            X, Y = bipartite.sets(G)

    def test_is_bipartite_node_set(self):
        G = nx.path_graph(4)

        with pytest.raises(nx.AmbiguousSolution):
            bipartite.is_bipartite_node_set(G, [1, 1, 2, 3])

        assert bipartite.is_bipartite_node_set(G, [0, 2])
        assert bipartite.is_bipartite_node_set(G, [1, 3])
        assert not bipartite.is_bipartite_node_set(G, [1, 2])
        G.add_edge(10, 20)
        assert bipartite.is_bipartite_node_set(G, [0, 2, 10])
        assert bipartite.is_bipartite_node_set(G, [0, 2, 20])
        assert bipartite.is_bipartite_node_set(G, [1, 3, 10])
        assert bipartite.is_bipartite_node_set(G, [1, 3, 20])

    def test_bipartite_density(self):
        G = nx.path_graph(5)
        X, Y = bipartite.sets(G)
        density = len(list(G.edges())) / (len(X) * len(Y))
        assert bipartite.density(G, X) == density
        D = nx.DiGraph(G.edges())
        assert bipartite.density(D, X) == density / 2.0
        assert bipartite.density(nx.Graph(), {}) == 0.0

    def test_bipartite_degrees(self):
        G = nx.path_graph(5)
        X = {1, 3}
        Y = {0, 2, 4}
        u, d = bipartite.degrees(G, Y)
        assert dict(u) == {1: 2, 3: 2}
        assert dict(d) == {0: 1, 2: 2, 4: 1}

    def test_bipartite_weighted_degrees(self):
        G = nx.path_graph(5)
        G.add_edge(0, 1, weight=0.1, other=0.2)
        X = {1, 3}
        Y = {0, 2, 4}
        u, d = bipartite.degrees(G, Y, weight="weight")
        assert dict(u) == {1: 1.1, 3: 2}
        assert dict(d) == {0: 0.1, 2: 2, 4: 1}
        u, d = bipartite.degrees(G, Y, weight="other")
        assert dict(u) == {1: 1.2, 3: 2}
        assert dict(d) == {0: 0.2, 2: 2, 4: 1}

    def test_color_partial_bicoloring_disconnected(self):
        # Tests color function with a disconnected, non-bipartite graph and relaxed=True
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 0)])  # non-bipartite component
        G.add_edges_from([(3, 4)])  # bipartite component
        colors = bipartite.color(G, relaxed=True)
        assert all(color in {0, 1} for color in colors.values())

    def test_bipartite_density_edge_cases(self):
        # Tests density calculation on different edge cases
        G_empty = nx.Graph()
        assert bipartite.density(G_empty, set()) == 0.0

        G_single = nx.Graph()
        G_single.add_node(0)
        assert bipartite.density(G_single, {0}) == 0.0

    def test_bipartite_degrees_weighted(self):
        # Tests weighted degrees with custom weights
        G = nx.Graph()
        G.add_edge(0, 1, weight=0.1)
        G.add_edge(1, 2, weight=0.9)
        G.add_edge(0, 2, weight=0.4)
        X, Y = bipartite.sets(G, top_nodes={0})
        u, d = bipartite.degrees(G, X, weight="weight")
        assert u[1] == pytest.approx(1.0)
        assert d[0] == pytest.approx(0.5)
        assert d[2] == pytest.approx(1.3)

    def test_is_bipartite_node_set_with_duplicates(self):
        # Tests is_bipartite_node_set with duplicate nodes in input
        G = nx.path_graph(4)
        with pytest.raises(nx.AmbiguousSolution):
            bipartite.is_bipartite_node_set(G, [0, 0, 1, 2])

    def test_sets_with_disconnected_non_bipartite_component(self):
        # Tests sets function with disconnected graph and relaxed=True
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (3, 4), (4, 5)])
        G.add_edge(6, 7)
        X, Y = bipartite.sets(G, relaxed=True)
        assert X.union(Y) == set(G.nodes())
        assert X.isdisjoint(Y)

    def test_isolated_nodes(self):
        # Graph with isolated nodes
        G = nx.Graph()
        G.add_edges_from([(0, 1), (2, 3)])
        G.add_node(4)  # Isolated node
        assert bipartite.is_bipartite(G)
        c = bipartite.color(G)
        assert c[4] == 0  # Default color for isolates

    def test_large_bipartite(self):
        # Large complete bipartite graph
        G = nx.complete_bipartite_graph(100, 200)
        assert bipartite.is_bipartite(G)
        X, Y = bipartite.sets(G)
        assert len(X) == 100 and len(Y) == 200

    def test_directed_with_loops(self):
        # Directed graph with self-loops
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 0), (2, 2)])  # Self-loop on node 2
        assert not bipartite.is_bipartite(G)

    def test_density_computation(self):
        # Test density for complete bipartite graph
        G = nx.complete_bipartite_graph(3, 2)
        X = {0, 1, 2}  # Top set
        assert bipartite.density(G, X) == 1.0
