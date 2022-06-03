"""Maximum common subgraph test suite.

"""

import itertools

import pytest

import networkx as nx


class TestMaxCommonSubgraph:
    def test_selfloop_exception(self):
        # Self-loops are not yet supported
        G0 = nx.Graph()
        G0.add_edge(1, 1)
        G1 = nx.Graph()
        for algorithm in (
            nx.max_common_induced_subgraph,
            nx.weak_modular_product_mcis,
            nx.ismags_mcis,
        ):
            with pytest.raises(nx.exception.NetworkXNotImplemented):
                algorithm(G0, G1)
            with pytest.raises(nx.exception.NetworkXNotImplemented):
                algorithm(G1, G0)
        with pytest.raises(nx.exception.NetworkXNotImplemented):
            nx.common_induced_subgraph(G0, G1, 0)
        with pytest.raises(nx.exception.NetworkXNotImplemented):
            nx.common_induced_subgraph(G1, G0, 0)

    def test_digraph_exception(self):
        G0 = nx.Graph()
        G1 = nx.DiGraph()
        for algorithm in (
            nx.max_common_induced_subgraph,
            nx.weak_modular_product_mcis,
            nx.ismags_mcis,
        ):
            with pytest.raises(nx.exception.NetworkXNotImplemented):
                algorithm(G0, G1)
            with pytest.raises(nx.exception.NetworkXNotImplemented):
                algorithm(G1, G0)
        with pytest.raises(nx.exception.NetworkXNotImplemented):
            nx.common_induced_subgraph(G0, G1, 0)
        with pytest.raises(nx.exception.NetworkXNotImplemented):
            nx.common_induced_subgraph(G1, G0, 0)

    def test_multigraph_exception(self):
        G0 = nx.Graph()
        G1 = nx.MultiGraph()
        for algorithm in (
            nx.max_common_induced_subgraph,
            nx.weak_modular_product_mcis,
            nx.ismags_mcis,
        ):
            with pytest.raises(nx.exception.NetworkXNotImplemented):
                algorithm(G0, G1)
            with pytest.raises(nx.exception.NetworkXNotImplemented):
                algorithm(G1, G0)
        with pytest.raises(nx.exception.NetworkXNotImplemented):
            nx.common_induced_subgraph(G0, G1, 0)
        with pytest.raises(nx.exception.NetworkXNotImplemented):
            nx.common_induced_subgraph(G1, G0, 0)

    def test_None_edge_label_exception(self):
        G0 = nx.Graph()
        G1 = nx.Graph()
        G0.add_edge(0, 1, label=1)
        G1.add_edge(0, 1, label=2)
        edge_label = lambda d: None if d["label"] == 1 else 1
        for algorithm in (
            nx.max_common_induced_subgraph,
            nx.weak_modular_product_mcis,
            nx.ismags_mcis,
        ):
            with pytest.raises(ValueError):
                algorithm(G0, G1, edge_label=edge_label)
            with pytest.raises(ValueError):
                algorithm(G1, G0, edge_label=edge_label)
        with pytest.raises(ValueError):
            nx.common_induced_subgraph(G0, G1, 1, edge_label=edge_label)
        with pytest.raises(ValueError):
            nx.common_induced_subgraph(G1, G0, 1, edge_label=edge_label)

    def test_missing_node_label_exception(self):
        G0 = nx.Graph()
        G1 = nx.Graph()
        G0.add_node(1)
        for algorithm in (
            nx.max_common_induced_subgraph,
            nx.weak_modular_product_mcis,
            nx.ismags_mcis,
        ):
            with pytest.raises(KeyError):
                algorithm(G0, G1, node_label="missing_key")
            with pytest.raises(KeyError):
                algorithm(G1, G0, node_label="missing_key")
        with pytest.raises(KeyError):
            nx.common_induced_subgraph(G0, G1, 1, node_label="missing_key")
        with pytest.raises(KeyError):
            nx.common_induced_subgraph(G1, G0, 1, node_label="missing_key")

    def test_missing_edge_label_exception(self):
        G0 = nx.Graph()
        G1 = nx.Graph()
        G0.add_edge(0, 1, label=1)
        for algorithm in (
            nx.max_common_induced_subgraph,
            nx.weak_modular_product_mcis,
            nx.ismags_mcis,
        ):
            with pytest.raises(KeyError):
                algorithm(G0, G1, edge_label="missing_key")
            with pytest.raises(KeyError):
                algorithm(G1, G0, edge_label="missing_key")
        with pytest.raises(KeyError):
            nx.common_induced_subgraph(G0, G1, 1, edge_label="missing_key")
        with pytest.raises(KeyError):
            nx.common_induced_subgraph(G1, G0, 1, edge_label="missing_key")

    def test_unsupported_connected_exception(self):
        G0 = nx.Graph()
        G1 = nx.Graph()
        with pytest.raises(TypeError):
            # Check that connected keyword is unsupported
            nx.weak_modular_product_mcis(G0, G1, connected=True)
        with pytest.raises(TypeError):
            # Check that connected keyword is unsupported
            nx.ismags_mcis(G0, G1, connected=True)

    def test_mcis(self):
        G0 = nx.path_graph(4)
        G1 = nx.complete_graph(4)
        generate_and_check_mcis(G0, G1, 2)
        generate_and_check_mcis(G0, G1, 2)

    def test_mcis_with_letters_for_nodes(self):
        G0 = nx.path_graph(4)
        mapping0 = {0: "a", 1: "b", 2: "c", 3: "d"}
        nx.relabel_nodes(G0, mapping0, copy=False)
        G1 = nx.complete_graph(4)
        mapping1 = {0: "Z", 1: "Y", 2: "X", 3: "W"}
        nx.relabel_nodes(G1, mapping1, copy=False)
        generate_and_check_mcis(G0, G1, 2)

    def test_mcis_empty_graph(self):
        for i in range(6):
            G0 = nx.empty_graph(i)
            G1 = nx.complete_graph(4)
            generate_and_check_mcis(G0, G1, 1 if i else 0)

    def test_connected_mcis(self):
        G0 = nx.path_graph(5)
        G1 = nx.empty_graph(5)
        G1.add_edge(0, 1)
        G1.add_edge(3, 4)
        generate_and_check_mcis(G0, G1, 2, connected=True)

    def test_decision_problem(self):
        G0 = nx.path_graph(3)
        G1 = nx.complete_graph(3)
        assert nx.common_induced_subgraph(G0, G1, 3) is None
        assert nx.common_induced_subgraph(G1, G0, 3) is None
        assert len(nx.common_induced_subgraph(G0, G1, 2)) == 2
        assert len(nx.common_induced_subgraph(G1, G0, 2)) == 2

    def test_node_labelled_mcis(self):
        G0 = nx.Graph()
        G1 = nx.Graph()
        G0.add_node(0, label="a")
        G0.add_node(1, label="b")
        G1.add_node(0, label="x")
        G1.add_node(1, label="y")
        generate_and_check_mcis(G0, G1, 2)
        fun = lambda node_data: node_data["label"]
        generate_and_check_mcis(G0, G0, 2, node_label=fun)
        generate_and_check_mcis(G0, G0, 2, node_label="label")
        generate_and_check_mcis(G0, G1, 0, node_label=fun)
        generate_and_check_mcis(G0, G1, 0, node_label="label")
        G1.add_node(2, label="a")
        generate_and_check_mcis(G0, G1, 1, node_label=fun)
        generate_and_check_mcis(G0, G1, 1, node_label="label")
        G1.add_node(3, label="b")
        generate_and_check_mcis(G0, G1, 2, node_label=fun)
        generate_and_check_mcis(G0, G1, 2, node_label="label")

    def test_edge_labelled_mcis(self):
        G0 = nx.empty_graph(3)
        G1 = nx.empty_graph(3)
        G0.add_edge(0, 1, label="a")
        G0.add_edge(0, 2, label="b")
        G1.add_edge(0, 1, label="x")
        G1.add_edge(0, 2, label="y")
        fun = lambda edge_data: edge_data["label"]
        generate_and_check_mcis(G0, G1, 2, edge_label=fun)
        generate_and_check_mcis(G0, G1, 2, edge_label="label")
        G0.add_edge(1, 2, label="c")
        generate_and_check_mcis(G0, G1, 1, edge_label=fun)
        generate_and_check_mcis(G0, G1, 1, edge_label="label")
        generate_and_check_mcis(G0, G0, 3, edge_label=fun)
        generate_and_check_mcis(G0, G0, 3, edge_label="label")

    def test_weak_modular_product_graph(self):
        G0 = nx.Graph()
        G1 = nx.Graph()
        G0.add_node(0, label="a")
        G0.add_node(1, label="b")
        G0.add_node(2, label="b")
        G1.add_node(0, label="b")
        G1.add_node(1, label="a")
        G1.add_node(2, label="a")
        G0.add_edge(0, 2, label="x")
        G1.add_edge(0, 1, label="x")
        node_fun = lambda node_data: node_data["label"]
        edge_fun = lambda edge_data: edge_data["label"]
        G = nx.algorithms.maximum_common_subgraph.maximum_common_induced_subgraph.weak_modular_product_graph(
            G0, G1, node_fun, edge_fun
        )
        assert len(G.nodes()) == 4
        assert len(G.edges()) == 2


def generate_and_check_mcis(G0, G1, expected_size, **kwargs):
    sizes = set()
    for G, H in [(G0, G1), (G1, G0)]:
        for algorithm in (
            nx.max_common_induced_subgraph,
            nx.weak_modular_product_mcis,
            nx.ismags_mcis,
        ):
            if (
                algorithm in [nx.weak_modular_product_mcis, nx.ismags_mcis]
                and "connected" in kwargs
                and kwargs["connected"]
            ):
                continue
            mcis = algorithm(G, H, **kwargs)
            check_common_induced_subgraph(mcis, G, H, expected_size, **kwargs)
            sizes.add(len(mcis))
        if expected_size is not None:
            cis = nx.common_induced_subgraph(G, H, expected_size, **kwargs)
            check_common_induced_subgraph(cis, G, H, expected_size, **kwargs)
            cis = nx.common_induced_subgraph(H, G, expected_size, **kwargs)
            check_common_induced_subgraph(cis, H, G, expected_size, **kwargs)
            assert nx.common_induced_subgraph(G, H, expected_size + 1, **kwargs) is None
            assert nx.common_induced_subgraph(H, G, expected_size + 1, **kwargs) is None
    assert len(sizes) == 1


def check_common_induced_subgraph(
    mcis, G0, G1, expected_size=None, connected=False, node_label=None, edge_label=None
):
    # Vertices should be in G0 and G1
    for v in mcis.keys():
        assert v in G0.nodes()
    for v in mcis.values():
        assert v in G1.nodes()

    # At most one vertex of G0 should map to any vertex of G1
    assert len(set(mcis.values())) == len(mcis.values())

    # Node labels should match
    if node_label is not None:
        for v, w in mcis.items():
            if callable(node_label):
                assert node_label(G0.nodes[v]) == node_label(G1.nodes[w])
            else:
                assert G0.nodes[v][node_label] == G1.nodes[w][node_label]

    # The isomorphism should preserve edges and non-edges
    for (v, w), (v_, w_) in itertools.combinations(mcis.items(), 2):
        assert G0.has_edge(v, v_) == G1.has_edge(w, w_)

    # The isomorphism should preserve edge labels
    if edge_label is not None:
        for (v, w), (v_, w_) in itertools.combinations(mcis.items(), 2):
            if G0.has_edge(v, v_):
                if callable(edge_label):
                    assert edge_label(G0.edges[v, v_]) == edge_label(G1.edges[w, w_])
                else:
                    assert G0.edges[v, v_][edge_label] == G1.edges[w, w_][edge_label]

    if connected:
        assert nx.is_connected(nx.subgraph(G0, mcis.keys()))

    if expected_size is not None:
        assert len(mcis) == expected_size
