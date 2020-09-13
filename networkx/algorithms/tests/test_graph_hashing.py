import pytest
import networkx as nx


def _relabel_graph(G, f=lambda x: -1 * x):
    """
    relabels graph nodes by a given relabeling function on integers.
    By default it flips the sign of the labels (Note this is a self-inverse).
    Returns the relabeled graph, with the original left intact.
    """
    return nx.relabel_nodes(G, {u: f(u) for u in G.nodes()})


def _relabel_dict(dic, f=lambda x: -1 * x):
    """
    relabels dictionary keys by a given relabeling function on integers.
    By default it flips the sign of the labels (Note this is a self-inverse).
    Returns the relabeled dictionary, with the original left intact.
    """
    return {f(k): v for k, v in dic.items()}


class TestFullGraphHash:
    """Unit tests for the :func:`~networkx.weisfeiler_lehman_graph_hash` function"""

    def test_empty_graph_hash(self):
        """
        empty graphs should give hashes regardless of other params
        """
        G1 = nx.empty_graph()
        G2 = nx.empty_graph()

        h1 = nx.weisfeiler_lehman_graph_hash(G1)
        h2 = nx.weisfeiler_lehman_graph_hash(G2)
        h3 = nx.weisfeiler_lehman_graph_hash(G2, edge_attr="edge_attr1")
        h4 = nx.weisfeiler_lehman_graph_hash(G2, node_attr="node_attr1")
        h5 = nx.weisfeiler_lehman_graph_hash(
            G2, edge_attr="edge_attr1", node_attr="node_attr1"
        )
        h6 = nx.weisfeiler_lehman_graph_hash(G2, iterations=10)

        assert h1 == h2
        assert h1 == h3
        assert h1 == h4
        assert h1 == h5
        assert h1 == h6

    def test_directed(self):
        """
        A directed graph with no bi-directional edges should yield different a graph hash
        to the same graph taken as undirected if there are no hash collisions.
        """
        r = 10
        for i in range(r):
            G_directed = nx.gn_graph(10 + r, seed=100 + i)
            G_undirected = nx.to_undirected(G_directed)

            h_directed = nx.weisfeiler_lehman_subgraph_hashes(G_directed)
            h_undirected = nx.weisfeiler_lehman_subgraph_hashes(G_undirected)

            assert h_directed != h_undirected

    def test_isomorphic(self):
        """
        graph hashes should be invariant to node-relabeling (when the output is reindexed
        by the same mapping)
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G1 = nx.erdos_renyi_graph(n, p * i, seed=200 + i)
            G2 = _relabel_graph(G1)

            g1_hash = nx.weisfeiler_lehman_graph_hash(G1)
            g2_hash = nx.weisfeiler_lehman_graph_hash(G2)

            assert g1_hash == g2_hash

    def test_isomorphic_edge_attr(self):
        """
        Isomorphic graphs with differing edge attributes should yield different graph
        hashes if the 'edge_attr' argument is supplied and populated in the graph,
        and there are no hash collisions.
        The output should still be invariant to node-relabeling
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G1 = nx.erdos_renyi_graph(n, p * i, seed=300 + i)

            for a, b in G1.edges:
                G1[a][b]["edge_attr1"] = f"{a}-{b}-1"
                G1[a][b]["edge_attr2"] = f"{a}-{b}-2"

            g1_hash_with_edge_attr1 = nx.weisfeiler_lehman_graph_hash(
                G1, edge_attr="edge_attr1"
            )
            g1_hash_with_edge_attr2 = nx.weisfeiler_lehman_graph_hash(
                G1, edge_attr="edge_attr2"
            )
            g1_hash_no_edge_attr = nx.weisfeiler_lehman_graph_hash(G1, edge_attr=None)

            assert g1_hash_with_edge_attr1 != g1_hash_no_edge_attr
            assert g1_hash_with_edge_attr2 != g1_hash_no_edge_attr
            assert g1_hash_with_edge_attr1 != g1_hash_with_edge_attr2

            G2 = _relabel_graph(G1)

            g2_hash_with_edge_attr1 = nx.weisfeiler_lehman_graph_hash(
                G2, edge_attr="edge_attr1"
            )
            g2_hash_with_edge_attr2 = nx.weisfeiler_lehman_graph_hash(
                G2, edge_attr="edge_attr2"
            )

            assert g1_hash_with_edge_attr1 == g2_hash_with_edge_attr1
            assert g1_hash_with_edge_attr2 == g2_hash_with_edge_attr2

    def test_missing_edge_attr(self):
        """
        If the 'edge_attr' argument is supplied but is missing from an edge in the graph,
        we should raise a KeyError
        """
        G = nx.Graph()
        G.add_edges_from([(1, 2, {"edge_attr1": "a"}), (1, 3, {})])
        pytest.raises(
            KeyError, nx.weisfeiler_lehman_graph_hash, G, edge_attr="edge_attr1"
        )

    def test_isomorphic_node_attr(self):
        """
        Isomorphic graphs with differing node attributes should yield different graph
        hashes if the 'node_attr' argument is supplied and populated in the graph, and
        there are no hash collisions.
        The output should still be invariant to node-relabeling
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G1 = nx.erdos_renyi_graph(n, p * i, seed=400 + i)

            for u in G1.nodes():
                G1.nodes[u]["node_attr1"] = f"{u}-1"
                G1.nodes[u]["node_attr2"] = f"{u}-2"

            g1_hash_with_node_attr1 = nx.weisfeiler_lehman_graph_hash(
                G1, node_attr="node_attr1"
            )
            g1_hash_with_node_attr2 = nx.weisfeiler_lehman_graph_hash(
                G1, node_attr="node_attr2"
            )
            g1_hash_no_node_attr = nx.weisfeiler_lehman_graph_hash(G1, node_attr=None)

            assert g1_hash_with_node_attr1 != g1_hash_no_node_attr
            assert g1_hash_with_node_attr2 != g1_hash_no_node_attr
            assert g1_hash_with_node_attr1 != g1_hash_with_node_attr2

            G2 = _relabel_graph(G1)

            g2_hash_with_node_attr1 = nx.weisfeiler_lehman_graph_hash(
                G2, node_attr="node_attr1"
            )
            g2_hash_with_node_attr2 = nx.weisfeiler_lehman_graph_hash(
                G2, node_attr="node_attr2"
            )

            assert g1_hash_with_node_attr1 == g2_hash_with_node_attr1
            assert g1_hash_with_node_attr2 == g2_hash_with_node_attr2

    def test_missing_node_attr(self):
        """
        If the 'node_attr' argument is supplied but is missing from a node in the graph,
        we should raise a KeyError
        """
        G = nx.Graph()
        G.add_nodes_from([(1, {"node_attr1": "a"}), (2, {})])
        G.add_edges_from([(1, 2), (2, 3), (3, 1), (1, 4)])
        pytest.raises(
            KeyError, nx.weisfeiler_lehman_graph_hash, G, node_attr="node_attr1"
        )

    def test_isomorphic_edge_attr_and_node_attr(self):
        """
        Isomorphic graphs with differing node attributes should yield different graph
        hashes if the 'node_attr' and 'edge_attr' argument is supplied and populated in
        the graph, and there are no hash collisions.
        The output should still be invariant to node-relabeling
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G1 = nx.erdos_renyi_graph(n, p * i, seed=500 + i)

            for u in G1.nodes():
                G1.nodes[u]["node_attr1"] = f"{u}-1"
                G1.nodes[u]["node_attr2"] = f"{u}-2"

            for a, b in G1.edges:
                G1[a][b]["edge_attr1"] = f"{a}-{b}-1"
                G1[a][b]["edge_attr2"] = f"{a}-{b}-2"

            g1_hash_edge1_node1 = nx.weisfeiler_lehman_graph_hash(
                G1, edge_attr="edge_attr1", node_attr="node_attr1"
            )
            g1_hash_edge2_node2 = nx.weisfeiler_lehman_graph_hash(
                G1, edge_attr="edge_attr2", node_attr="node_attr2"
            )
            g1_hash_edge1_node2 = nx.weisfeiler_lehman_graph_hash(
                G1, edge_attr="edge_attr1", node_attr="node_attr2"
            )
            g1_hash_no_attr = nx.weisfeiler_lehman_graph_hash(G1)

            assert g1_hash_edge1_node1 != g1_hash_no_attr
            assert g1_hash_edge2_node2 != g1_hash_no_attr
            assert g1_hash_edge1_node1 != g1_hash_edge2_node2
            assert g1_hash_edge1_node2 != g1_hash_edge2_node2
            assert g1_hash_edge1_node2 != g1_hash_edge1_node1

            G2 = _relabel_graph(G1)

            g2_hash_edge1_node1 = nx.weisfeiler_lehman_graph_hash(
                G2, edge_attr="edge_attr1", node_attr="node_attr1"
            )
            g2_hash_edge2_node2 = nx.weisfeiler_lehman_graph_hash(
                G2, edge_attr="edge_attr2", node_attr="node_attr2"
            )

            assert g1_hash_edge1_node1 == g2_hash_edge1_node1
            assert g1_hash_edge2_node2 == g2_hash_edge2_node2

    def test_digest_size(self):
        """
        The hash string lengths should be as expected for a variety of graphs and
        digest sizes
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G = nx.erdos_renyi_graph(n, p * i, seed=1000 + i)

            h16 = nx.weisfeiler_lehman_graph_hash(G)
            h32 = nx.weisfeiler_lehman_graph_hash(G, digest_size=32)

            assert h16 != h32
            assert len(h16) == 16 * 2
            assert len(h32) == 32 * 2


class TestSubgraphHashes:
    """Unit tests for the :func:`~networkx.weisfeiler_lehman_hash_subgraphs` function"""

    @staticmethod
    def is_subiteration(a, b):
        """
        returns True if that each hash sequence in 'a' is a prefix for
        the corresponding sequence indexed by the same node in 'b'.
        """
        return all(b[node][: len(hashes)] == hashes for node, hashes in a.items())

    @staticmethod
    def hexdigest_sizes_correct(a, digest_size):
        """
        returns True if all hex digest sizes are the expected length in a node:subgraph-hashes
        dictionary. Hex digest string length == 2 * bytes digest length since each pair of hex
        digits encodes 1 byte (https://docs.python.org/3/library/hashlib.html)
        """
        hexdigest_size = digest_size * 2
        list_digest_sizes_correct = lambda l: all(len(x) == hexdigest_size for x in l)
        return all(list_digest_sizes_correct(hashes) for hashes in a.values())

    def test_empty_graph(self):
        """ "
        empty graphs should give empty dict subgraph hashes regardless of other params
        """
        G = nx.empty_graph()

        subgraph_hashes1 = nx.weisfeiler_lehman_subgraph_hashes(G)
        subgraph_hashes2 = nx.weisfeiler_lehman_subgraph_hashes(
            G, edge_attr="edge_attr"
        )
        subgraph_hashes3 = nx.weisfeiler_lehman_subgraph_hashes(
            G, node_attr="edge_attr"
        )
        subgraph_hashes4 = nx.weisfeiler_lehman_subgraph_hashes(G, iterations=2)
        subgraph_hashes5 = nx.weisfeiler_lehman_subgraph_hashes(G, digest_size=64)

        assert subgraph_hashes1 == dict()
        assert subgraph_hashes2 == dict()
        assert subgraph_hashes3 == dict()
        assert subgraph_hashes4 == dict()
        assert subgraph_hashes5 == dict()

    def test_directed(self):
        """
        A directed graph with no bi-directional edges should yield different subgraph hashes
        to the same graph taken as undirected, if all hashes don't collide.
        """
        r = 10
        for i in range(r):
            G_directed = nx.gn_graph(10 + r, seed=100 + i)
            G_undirected = nx.to_undirected(G_directed)

            directed_subgraph_hashes = nx.weisfeiler_lehman_subgraph_hashes(G_directed)
            undirected_subgraph_hashes = nx.weisfeiler_lehman_subgraph_hashes(
                G_undirected
            )

            assert directed_subgraph_hashes != undirected_subgraph_hashes

    def test_isomorphic(self):
        """
        the subgraph hashes should be invariant to node-relabeling when the output is reindexed
        by the same mapping and all hashes don't collide.
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G1 = nx.erdos_renyi_graph(n, p * i, seed=200 + i)
            G2 = _relabel_graph(G1)

            g1_subgraph_hashes = nx.weisfeiler_lehman_subgraph_hashes(G1)
            g2_subgraph_hashes = nx.weisfeiler_lehman_subgraph_hashes(G2)

            assert g1_subgraph_hashes == _relabel_dict(g2_subgraph_hashes)

    def test_isomorphic_edge_attr(self):
        """
        Isomorphic graphs with differing edge attributes should yield different subgraph
        hashes if the 'edge_attr' argument is supplied and populated in the graph, and
        all hashes don't collide.
        The output should still be invariant to node-relabeling
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G1 = nx.erdos_renyi_graph(n, p * i, seed=300 + i)

            for a, b in G1.edges:
                G1[a][b]["edge_attr1"] = f"{a}-{b}-1"
                G1[a][b]["edge_attr2"] = f"{a}-{b}-2"

            g1_hash_with_edge_attr1 = nx.weisfeiler_lehman_subgraph_hashes(
                G1, edge_attr="edge_attr1"
            )
            g1_hash_with_edge_attr2 = nx.weisfeiler_lehman_subgraph_hashes(
                G1, edge_attr="edge_attr2"
            )
            g1_hash_no_edge_attr = nx.weisfeiler_lehman_subgraph_hashes(
                G1, edge_attr=None
            )

            assert g1_hash_with_edge_attr1 != g1_hash_no_edge_attr
            assert g1_hash_with_edge_attr2 != g1_hash_no_edge_attr
            assert g1_hash_with_edge_attr1 != g1_hash_with_edge_attr2

            G2 = _relabel_graph(G1)

            g2_hash_with_edge_attr1 = nx.weisfeiler_lehman_subgraph_hashes(
                G2, edge_attr="edge_attr1"
            )
            g2_hash_with_edge_attr2 = nx.weisfeiler_lehman_subgraph_hashes(
                G2, edge_attr="edge_attr2"
            )

            assert g1_hash_with_edge_attr1 == _relabel_dict(g2_hash_with_edge_attr1)
            assert g1_hash_with_edge_attr2 == _relabel_dict(g2_hash_with_edge_attr2)

    def test_missing_edge_attr(self):
        """
        If the 'edge_attr' argument is supplied but is missing from an edge in the graph,
        we should raise a KeyError
        """
        G = nx.Graph()
        G.add_edges_from([(1, 2, {"edge_attr1": "a"}), (1, 3, {})])
        pytest.raises(
            KeyError, nx.weisfeiler_lehman_subgraph_hashes, G, edge_attr="edge_attr1"
        )

    def test_isomorphic_node_attr(self):
        """
        Isomorphic graphs with differing node attributes should yield different subgraph
        hashes if the 'node_attr' argument is supplied and populated in the graph, and
        all hashes don't collide.
        The output should still be invariant to node-relabeling
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G1 = nx.erdos_renyi_graph(n, p * i, seed=400 + i)

            for u in G1.nodes():
                G1.nodes[u]["node_attr1"] = f"{u}-1"
                G1.nodes[u]["node_attr2"] = f"{u}-2"

            g1_hash_with_node_attr1 = nx.weisfeiler_lehman_subgraph_hashes(
                G1, node_attr="node_attr1"
            )
            g1_hash_with_node_attr2 = nx.weisfeiler_lehman_subgraph_hashes(
                G1, node_attr="node_attr2"
            )
            g1_hash_no_node_attr = nx.weisfeiler_lehman_subgraph_hashes(
                G1, node_attr=None
            )

            assert g1_hash_with_node_attr1 != g1_hash_no_node_attr
            assert g1_hash_with_node_attr2 != g1_hash_no_node_attr
            assert g1_hash_with_node_attr1 != g1_hash_with_node_attr2

            G2 = _relabel_graph(G1)

            g2_hash_with_node_attr1 = nx.weisfeiler_lehman_subgraph_hashes(
                G2, node_attr="node_attr1"
            )
            g2_hash_with_node_attr2 = nx.weisfeiler_lehman_subgraph_hashes(
                G2, node_attr="node_attr2"
            )

            assert g1_hash_with_node_attr1 == _relabel_dict(g2_hash_with_node_attr1)
            assert g1_hash_with_node_attr2 == _relabel_dict(g2_hash_with_node_attr2)

    def test_missing_node_attr(self):
        """
        If the 'node_attr' argument is supplied but is missing from a node in the graph,
        we should raise a KeyError
        """
        G = nx.Graph()
        G.add_nodes_from([(1, {"node_attr1": "a"}), (2, {})])
        G.add_edges_from([(1, 2), (2, 3), (3, 1), (1, 4)])
        pytest.raises(
            KeyError, nx.weisfeiler_lehman_subgraph_hashes, G, node_attr="node_attr1"
        )

    def test_isomorphic_edge_attr_and_node_attr(self):
        """
        Isomorphic graphs with differing node attributes should yield different subgraph
        hashes if the 'node_attr' and 'edge_attr' argument is supplied and populated in
        the graph, and all hashes don't collide
        The output should still be invariant to node-relabeling
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G1 = nx.erdos_renyi_graph(n, p * i, seed=500 + i)

            for u in G1.nodes():
                G1.nodes[u]["node_attr1"] = f"{u}-1"
                G1.nodes[u]["node_attr2"] = f"{u}-2"

            for a, b in G1.edges:
                G1[a][b]["edge_attr1"] = f"{a}-{b}-1"
                G1[a][b]["edge_attr2"] = f"{a}-{b}-2"

            g1_hash_edge1_node1 = nx.weisfeiler_lehman_subgraph_hashes(
                G1, edge_attr="edge_attr1", node_attr="node_attr1"
            )
            g1_hash_edge2_node2 = nx.weisfeiler_lehman_subgraph_hashes(
                G1, edge_attr="edge_attr2", node_attr="node_attr2"
            )
            g1_hash_edge1_node2 = nx.weisfeiler_lehman_subgraph_hashes(
                G1, edge_attr="edge_attr1", node_attr="node_attr2"
            )
            g1_hash_no_attr = nx.weisfeiler_lehman_subgraph_hashes(G1)

            assert g1_hash_edge1_node1 != g1_hash_no_attr
            assert g1_hash_edge2_node2 != g1_hash_no_attr
            assert g1_hash_edge1_node1 != g1_hash_edge2_node2
            assert g1_hash_edge1_node2 != g1_hash_edge2_node2
            assert g1_hash_edge1_node2 != g1_hash_edge1_node1

            G2 = _relabel_graph(G1)

            g2_hash_edge1_node1 = nx.weisfeiler_lehman_subgraph_hashes(
                G2, edge_attr="edge_attr1", node_attr="node_attr1"
            )
            g2_hash_edge2_node2 = nx.weisfeiler_lehman_subgraph_hashes(
                G2, edge_attr="edge_attr2", node_attr="node_attr2"
            )

            assert g1_hash_edge1_node1 == _relabel_dict(g2_hash_edge1_node1)
            assert g1_hash_edge2_node2 == _relabel_dict(g2_hash_edge2_node2)

    def test_iteration_depth(self):
        """
        All nodes should have the correct number of subgraph hashes in the output when
        using degree as initial node labels
        Subsequent iteration depths for the same graph should be additive for each node
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G = nx.erdos_renyi_graph(n, p * i, seed=600 + i)

            depth3 = nx.weisfeiler_lehman_subgraph_hashes(G, iterations=3)
            depth4 = nx.weisfeiler_lehman_subgraph_hashes(G, iterations=4)
            depth5 = nx.weisfeiler_lehman_subgraph_hashes(G, iterations=5)

            assert all(len(hashes) == 3 for hashes in depth3.values())
            assert all(len(hashes) == 4 for hashes in depth4.values())
            assert all(len(hashes) == 5 for hashes in depth5.values())

            assert TestSubgraphHashes.is_subiteration(depth3, depth4)
            assert TestSubgraphHashes.is_subiteration(depth4, depth5)
            assert TestSubgraphHashes.is_subiteration(depth3, depth5)

    def test_iteration_depth_edge_attr(self):
        """
        All nodes should have the correct number of subgraph hashes in the output when
        setting initial node labels empty and using an edge attribute when aggregating
        neighborhoods.
        Subsequent iteration depths for the same graph should be additive for each node
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G = nx.erdos_renyi_graph(n, p * i, seed=700 + i)

            for a, b in G.edges:
                G[a][b]["edge_attr1"] = f"{a}-{b}-1"

            depth3 = nx.weisfeiler_lehman_subgraph_hashes(
                G, edge_attr="edge_attr1", iterations=3
            )
            depth4 = nx.weisfeiler_lehman_subgraph_hashes(
                G, edge_attr="edge_attr1", iterations=4
            )
            depth5 = nx.weisfeiler_lehman_subgraph_hashes(
                G, edge_attr="edge_attr1", iterations=5
            )

            assert all(len(hashes) == 3 for hashes in depth3.values())
            assert all(len(hashes) == 4 for hashes in depth4.values())
            assert all(len(hashes) == 5 for hashes in depth5.values())

            assert TestSubgraphHashes.is_subiteration(depth3, depth4)
            assert TestSubgraphHashes.is_subiteration(depth4, depth5)
            assert TestSubgraphHashes.is_subiteration(depth3, depth5)

    def test_iteration_depth_node_attr(self):
        """
        All nodes should have the correct number of subgraph hashes in the output when
        setting initial node labels to an attribute.
        Subsequent iteration depths for the same graph should be additive for each node
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G = nx.erdos_renyi_graph(n, p * i, seed=800 + i)

            for u in G.nodes():
                G.nodes[u]["node_attr1"] = f"{u}-1"

            depth3 = nx.weisfeiler_lehman_subgraph_hashes(
                G, node_attr="node_attr1", iterations=3
            )
            depth4 = nx.weisfeiler_lehman_subgraph_hashes(
                G, node_attr="node_attr1", iterations=4
            )
            depth5 = nx.weisfeiler_lehman_subgraph_hashes(
                G, node_attr="node_attr1", iterations=5
            )

            assert all(len(hashes) == 3 for hashes in depth3.values())
            assert all(len(hashes) == 4 for hashes in depth4.values())
            assert all(len(hashes) == 5 for hashes in depth5.values())

            assert TestSubgraphHashes.is_subiteration(depth3, depth4)
            assert TestSubgraphHashes.is_subiteration(depth4, depth5)
            assert TestSubgraphHashes.is_subiteration(depth3, depth5)

    def test_iteration_depth_node_edge_attr(self):
        """
        All nodes should have the correct number of subgraph hashes in the output when
        setting initial node labels to an attribute and also using an edge attribute when
        aggregating neighborhoods.
        Subsequent iteration depths for the same graph should be additive for each node
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G = nx.erdos_renyi_graph(n, p * i, seed=900 + i)

            for u in G.nodes():
                G.nodes[u]["node_attr1"] = f"{u}-1"

            for a, b in G.edges:
                G[a][b]["edge_attr1"] = f"{a}-{b}-1"

            depth3 = nx.weisfeiler_lehman_subgraph_hashes(
                G, edge_attr="edge_attr1", node_attr="node_attr1", iterations=3
            )
            depth4 = nx.weisfeiler_lehman_subgraph_hashes(
                G, edge_attr="edge_attr1", node_attr="node_attr1", iterations=4
            )
            depth5 = nx.weisfeiler_lehman_subgraph_hashes(
                G, edge_attr="edge_attr1", node_attr="node_attr1", iterations=5
            )

            assert all(len(hashes) == 3 for hashes in depth3.values())
            assert all(len(hashes) == 4 for hashes in depth4.values())
            assert all(len(hashes) == 5 for hashes in depth5.values())

            assert TestSubgraphHashes.is_subiteration(depth3, depth4)
            assert TestSubgraphHashes.is_subiteration(depth4, depth5)
            assert TestSubgraphHashes.is_subiteration(depth3, depth5)

    def test_digest_size(self):
        """
        The hash string lengths should be as expected for a variety of graphs and
        digest sizes
        """
        n, r = 100, 10
        p = 1.0 / r
        for i in range(1, r + 1):
            G = nx.erdos_renyi_graph(n, p * i, seed=1000 + i)

            digest_size16_hashes = nx.weisfeiler_lehman_subgraph_hashes(G)
            digest_size32_hashes = nx.weisfeiler_lehman_subgraph_hashes(
                G, digest_size=32
            )

            assert digest_size16_hashes != digest_size32_hashes

            assert TestSubgraphHashes.hexdigest_sizes_correct(digest_size16_hashes, 16)
            assert TestSubgraphHashes.hexdigest_sizes_correct(digest_size32_hashes, 32)
