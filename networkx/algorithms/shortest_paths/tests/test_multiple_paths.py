import pytest

import networkx as nx


class TestMultiplePaths:
    def test_shortest_paths_bhandari(self):
        G = nx.DiGraph()
        edges = [
            ("s", "a", 1),
            ("s", "c", 4),
            ("a", "b", 1),
            ("b", "c", 1),
            ("s", "b", 4),
            ("a", "t", 6),
            ("b", "t", 5),
            ("c", "t", 1),
        ]
        G.add_weighted_edges_from(edges)
        paths_1 = nx.multiple_paths(G, "s", "t", 1)
        paths_2 = nx.multiple_paths(G, "s", "t", 2)
        paths_3 = nx.multiple_paths(G, "s", "t", 3)
        assert paths_1 == [["s", "a", "b", "c", "t"]]
        assert paths_2 == [["s", "c", "t"], ["s", "a", "b", "t"]]
        assert paths_3 == [["s", "c", "t"], ["s", "a", "t"], ["s", "b", "t"]]
        for k in range(4, 7):
            paths_k = nx.multiple_paths(G, "s", "t", k)
            assert paths_k == [["s", "c", "t"], ["s", "a", "t"], ["s", "b", "t"]]

    def test_shortest_paths_suurballe(self):
        G = nx.DiGraph()
        edges = [
            ("s", "a", 1),
            ("s", "c", 4),
            ("a", "b", 1),
            ("b", "c", 1),
            ("s", "b", 4),
            ("a", "t", 6),
            ("b", "t", 5),
            ("c", "t", 1),
        ]
        G.add_weighted_edges_from(edges)
        paths_1 = nx.multiple_paths(G, "s", "t", 1, "suurballe")
        paths_2 = nx.multiple_paths(G, "s", "t", 2, "suurballe")
        paths_3 = nx.multiple_paths(G, "s", "t", 3, "suurballe")
        assert paths_1 == [["s", "a", "b", "c", "t"]]
        assert paths_2 == [["s", "c", "t"], ["s", "a", "b", "t"]]
        assert paths_3 == [["s", "c", "t"], ["s", "a", "t"], ["s", "b", "t"]]
        for k in range(4, 7):
            paths_k = nx.multiple_paths(G, "s", "t", k, "suurballe")
            assert paths_k == [["s", "c", "t"], ["s", "a", "t"], ["s", "b", "t"]]

    def test_shortest_paths_2_bhandari(self):
        G = nx.DiGraph()
        edges = [
            ("s", "a", 3),
            ("s", "b", 2),
            ("s", "d", 8),
            ("a", "c", 1),
            ("a", "d", 4),
            ("b", "e", 5),
            ("c", "t", 5),
            ("d", "t", 1),
            ("g", "t", 7),
            ("a", "e", 6),
            ("e", "g", 2),
            ("g", "b", 3),
        ]
        G.add_weighted_edges_from(edges)
        paths_1 = nx.multiple_paths(G, "s", "t", 1)
        paths_2 = nx.multiple_paths(G, "s", "t", 2)
        paths_3 = nx.multiple_paths(G, "s", "t", 3)
        assert paths_1 == [["s", "a", "d", "t"]]
        assert paths_2 == [["s", "d", "t"], ["s", "a", "c", "t"]] or paths_2 == [
            ["s", "a", "c", "t"],
            ["s", "d", "t"],
        ]
        assert paths_3 == [
            ["s", "d", "t"],
            ["s", "a", "c", "t"],
            ["s", "b", "e", "g", "t"],
        ] or paths_3 == [
            ["s", "a", "c", "t"],
            ["s", "d", "t"],
            ["s", "b", "e", "g", "t"],
        ]

    def test_shortest_paths_2_suurballe(self):
        G = nx.DiGraph()
        edges = [
            ("s", "a", 3),
            ("s", "b", 2),
            ("s", "d", 8),
            ("a", "c", 1),
            ("a", "d", 4),
            ("b", "e", 5),
            ("c", "t", 5),
            ("d", "t", 1),
            ("g", "t", 7),
            ("a", "e", 6),
            ("e", "g", 2),
            ("g", "b", 3),
        ]
        G.add_weighted_edges_from(edges)
        paths_1 = nx.multiple_paths(G, "s", "t", 1, "suurballe")
        paths_2 = nx.multiple_paths(G, "s", "t", 2, "suurballe")
        paths_3 = nx.multiple_paths(G, "s", "t", 3, "suurballe")
        assert paths_1 == [["s", "a", "d", "t"]]
        assert paths_2 == [["s", "d", "t"], ["s", "a", "c", "t"]] or paths_2 == [
            ["s", "a", "c", "t"],
            ["s", "d", "t"],
        ]
        assert paths_3 == [
            ["s", "d", "t"],
            ["s", "a", "c", "t"],
            ["s", "b", "e", "g", "t"],
        ] or paths_3 == [
            ["s", "a", "c", "t"],
            ["s", "d", "t"],
            ["s", "b", "e", "g", "t"],
        ]

    def test_shortest_path_bhandari_3(self):
        G = nx.DiGraph()
        edges = [
            ("a", "d", 1),
            ("a", "b", 1),
            ("d", "c", 6),
            ("b", "c", 1),
            ("c", "z", 1),
            ("b", "e", 4),
            ("e", "z", 1),
        ]
        G.add_weighted_edges_from(edges)
        paths_1 = nx.multiple_paths(G, "a", "z", 1)
        paths_2 = nx.multiple_paths(G, "a", "z", 2)
        assert paths_1 == [["a", "b", "c", "z"]]
        assert paths_2 == [["a", "b", "e", "z"], ["a", "d", "c", "z"]]

    def test_shortest_path_suurballe_3(self):
        G = nx.DiGraph()
        edges = [
            ("a", "d", 1),
            ("a", "b", 1),
            ("d", "c", 6),
            ("b", "c", 1),
            ("c", "z", 1),
            ("b", "e", 4),
            ("e", "z", 1),
        ]
        G.add_weighted_edges_from(edges)
        paths_1 = nx.multiple_paths(G, "a", "z", 1, "suurballe")
        paths_2 = nx.multiple_paths(G, "a", "z", 2, "suurballe")
        assert paths_1 == [["a", "b", "c", "z"]]
        assert paths_2 == [["a", "b", "e", "z"], ["a", "d", "c", "z"]]

    def test_bhandari(self):
        G = nx.DiGraph()
        edges = [
            ("s", "a", 1),
            ("a", "s", 1),
            ("s", "b", 1),
            ("b", "s", 1),
            ("a", "t", 1),
            ("t", "a", 1),
            ("b", "t", 1),
            ("t", "b", 1),
        ]
        G.add_weighted_edges_from(edges)
        dp_lst = nx.multiple_paths(G, "s", "t", 2)
        assert ["s", "a", "t"] in dp_lst
        assert ["s", "b", "t"] in dp_lst

    def test_suurballe(self):
        G = nx.DiGraph()
        edges = [
            ("s", "a", 1),
            ("a", "s", 1),
            ("s", "b", 1),
            ("b", "s", 1),
            ("a", "t", 1),
            ("t", "a", 1),
            ("b", "t", 1),
            ("t", "b", 1),
        ]
        G.add_weighted_edges_from(edges)
        dp_lst = nx.multiple_paths(G, "s", "t", 2, "suurballe")
        assert ["s", "a", "t"] in dp_lst
        assert ["s", "b", "t"] in dp_lst

    def test_bhandari_not_directed(self):
        G = nx.Graph()
        edges = [("s", "a", 1), ("s", "b", 1), ("a", "t", 1), ("b", "t", 1)]
        G.add_weighted_edges_from(edges)
        paths_2 = nx.multiple_paths(G, "s", "t", 2)
        assert paths_2 == [["s", "a", "t"], ["s", "b", "t"]] or paths_2 == [
            ["s", "b", "t"],
            ["s", "a", "t"],
        ]

    def test_suurballe_not_directed(self):
        G = nx.Graph()
        edges = [("s", "a", 1), ("s", "b", 1), ("a", "t", 1), ("b", "t", 1)]
        G.add_weighted_edges_from(edges)
        paths_2 = nx.multiple_paths(G, "s", "t", 2, "suurballe")
        assert paths_2 == [["s", "a", "t"], ["s", "b", "t"]] or paths_2 == [
            ["s", "b", "t"],
            ["s", "a", "t"],
        ]

    def test_bhandari_negative_weight_1(self):
        test_graph = nx.DiGraph()
        edges = [
            ("A", "B", 4),
            ("A", "C", -2),
            ("B", "C", -3),
            ("B", "D", 2),
            ("C", "D", 2),
            ("D", "E", 1),
            ("C", "E", 4),
        ]
        test_graph.add_weighted_edges_from(edges)
        path_1 = nx.multiple_paths(test_graph, "A", "E", 1)
        path_2 = nx.multiple_paths(test_graph, "A", "E", 2)
        assert path_1 == [["A", "C", "D", "E"]]
        # sum of both paths is 6, 2 valid options
        assert path_2 == [["A", "C", "E"], ["A", "B", "C", "D", "E"]] or path_2 == [
            ["A", "C", "D", "E"],
            ["A", "B", "C", "E"],
        ]

    def test_bhandari_negative_weight_2(self):
        test_graph = nx.DiGraph()
        edges = [
            ("A", "B", 4),
            ("A", "C", 2),
            ("B", "C", -3),
            ("B", "D", 2),
            ("C", "D", 2),
            ("D", "E", 1),
            ("C", "E", 4),
        ]
        test_graph.add_weighted_edges_from(edges)
        path_1 = nx.multiple_paths(test_graph, "A", "E", 1)
        path_2 = nx.multiple_paths(test_graph, "A", "E", 2)
        assert path_1 == [["A", "B", "C", "D", "E"]]
        # sum of both paths is 10, 3 valid options
        assert (
            path_2 == [["A", "B", "C", "D", "E"], ["A", "C", "E"]]
            or path_2 == [["A", "B", "C", "E"], ["A", "C", "D", "E"]]
            or path_2 == [["A", "C", "D", "E"], ["A", "B", "C", "E"]]
        )

    def test_bhandari_negative_multidigraph(self):
        test_graph = nx.MultiDiGraph()
        edges = [
            ("A", "B", 1),
            ("A", "B", 2),
            ("B", "D", 4),
            ("B", "C", 3),
            ("C", "D", 2),
            ("A", "C", -1),
        ]
        test_graph.add_weighted_edges_from(edges)
        path_1 = nx.multiple_paths(test_graph, "A", "D", 1)
        path_2 = nx.multiple_paths(test_graph, "A", "D", 2)
        assert path_1 == [["A", "C", "D"]]
        assert path_2 == [["A", "C", "D"], ["A", "B", "D"]]
