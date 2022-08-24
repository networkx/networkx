import utils

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import vf2pp_mapping


class TestMultiGraphISOVF2pp:
    def test_both_graphs_empty(self):
        G = nx.MultiGraph()
        H = nx.MultiGraph()

        m = vf2pp_mapping(G, H, None)
        assert not m

    def test_first_graph_empty(self):
        G = nx.MultiGraph()
        H = nx.MultiGraph([(0, 1)])
        m = vf2pp_mapping(G, H, None)
        assert not m

    def test_second_graph_empty(self):
        G = nx.MultiGraph([(0, 1)])
        H = nx.MultiGraph()
        m = vf2pp_mapping(G, H, None)
        assert not m

    def test_custom_multigraph1_same_labels(self):
        G1 = nx.MultiGraph()

        mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
        edges1 = [
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 4),
            (1, 4),
            (2, 3),
            (2, 6),
            (2, 6),
            (3, 4),
            (3, 4),
            (5, 1),
            (5, 1),
            (5, 2),
            (5, 2),
        ]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        utils.assign_labels(G1, G2, mapped, same=True)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Transfer the 2-clique to the right side of G1
        G1.remove_edges_from([(2, 6), (2, 6)])
        G1.add_edges_from([(3, 6), (3, 6)])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Delete an edges, making them symmetrical, so the position of the 2-clique doesn't matter
        G2.remove_edge(mapped[1], mapped[4])
        G1.remove_edge(1, 4)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Add self-loops
        G1.add_edges_from([(5, 5), (5, 5), (1, 1)])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Compensate in G2
        G2.add_edges_from(
            [(mapped[1], mapped[1]), (mapped[4], mapped[4]), (mapped[4], mapped[4])]
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

    def test_custom_multigraph1_different_labels(self):
        G1 = nx.MultiGraph()

        mapped = {1: "A", 2: "B", 3: "C", 4: "D", 5: "Z", 6: "E"}
        edges1 = [
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 4),
            (1, 4),
            (2, 3),
            (2, 6),
            (2, 6),
            (3, 4),
            (3, 4),
            (5, 1),
            (5, 1),
            (5, 2),
            (5, 2),
        ]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        utils.assign_labels(G1, G2, mapped)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Re-structure G1, maintaining the degree sequence
        G1.remove_edge(1, 4)
        G1.add_edge(1, 5)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Restructure G2, making it isomorphic to G1
        G2.remove_edge("A", "D")
        G2.add_edge("A", "Z")
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Add edge from node to itself
        G1.add_edges_from([(6, 6), (6, 6), (6, 6)])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Same for G2
        G2.add_edges_from([("E", "E"), ("E", "E"), ("E", "E")])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

    def test_custom_multigraph2_same_labels(self):
        G1 = nx.MultiGraph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [
            (1, 2),
            (1, 2),
            (1, 5),
            (1, 5),
            (1, 5),
            (5, 6),
            (2, 3),
            (2, 3),
            (2, 4),
            (3, 4),
            (3, 4),
            (4, 5),
            (4, 5),
            (4, 5),
            (2, 7),
            (2, 7),
            (2, 7),
        ]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        utils.assign_labels(G1, G2, mapped, same=True)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Obtain two non-somorphic subgraphs from the graph
        G2.remove_edges_from([(mapped[1], mapped[2]), (mapped[1], mapped[2])])
        G2.add_edge(mapped[1], mapped[4])
        H1 = nx.MultiGraph(G1.subgraph([2, 3, 4, 7]))
        H2 = nx.MultiGraph(G2.subgraph([mapped[1], mapped[4], mapped[5], mapped[6]]))

        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert not m

        # Make them isomorphic
        H1.remove_edge(3, 4)
        H1.add_edges_from([(2, 3), (2, 4), (2, 4)])
        H2.add_edges_from([(mapped[5], mapped[6]), (mapped[5], mapped[6])])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Remove triangle edge
        H1.remove_edges_from([(2, 3), (2, 3), (2, 3)])
        H2.remove_edges_from([(mapped[5], mapped[4])] * 3)
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Change the edge orientation such that H1 is rotated H2
        H1.remove_edges_from([(2, 7), (2, 7)])
        H1.add_edges_from([(3, 4), (3, 4)])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Add extra edges maintaining degree sequence, but in a non-symmetrical manner
        H2.add_edge(mapped[5], mapped[1])
        H1.add_edge(3, 4)
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert not m

    def test_custom_multigraph2_different_labels(self):
        G1 = nx.MultiGraph()

        mapped = {1: "A", 2: "C", 3: "D", 4: "E", 5: "G", 7: "B", 6: "F"}
        edges1 = [
            (1, 2),
            (1, 2),
            (1, 5),
            (1, 5),
            (1, 5),
            (5, 6),
            (2, 3),
            (2, 3),
            (2, 4),
            (3, 4),
            (3, 4),
            (4, 5),
            (4, 5),
            (4, 5),
            (2, 7),
            (2, 7),
            (2, 7),
        ]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        utils.assign_labels(G1, G2, mapped)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Re-structure G1
        G1.remove_edge(2, 7)
        G1.add_edge(5, 6)

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Same for G2
        G2.remove_edge("B", "C")
        G2.add_edge("G", "F")

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Delete node from G1 and G2, keeping them isomorphic
        G1.remove_node(3)
        G2.remove_node("D")
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Change G1 edges
        G1.remove_edge(1, 2)
        G1.remove_edge(2, 7)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Make G2 identical to G1, but with different edge orientation and different labels
        G2.add_edges_from([("A", "C"), ("C", "E"), ("C", "E")])
        G2.remove_edges_from(
            [("A", "G"), ("A", "G"), ("F", "G"), ("E", "G"), ("E", "G")]
        )

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Make all labels the same, so G1 and G2 are also isomorphic
        for n1, n2 in zip(G1.nodes(), G2.nodes()):
            G1.nodes[n1]["label"] = "blue"
            G2.nodes[n2]["label"] = "blue"

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

    def test_custom_multigraph3_same_labels(self):
        G1 = nx.MultiGraph()

        mapped = {1: 9, 2: 8, 3: 7, 4: 6, 5: 3, 8: 5, 9: 4, 7: 1, 6: 2}
        edges1 = [
            (1, 2),
            (1, 3),
            (1, 3),
            (2, 3),
            (2, 3),
            (3, 4),
            (4, 5),
            (4, 7),
            (4, 9),
            (4, 9),
            (4, 9),
            (5, 8),
            (5, 8),
            (8, 9),
            (8, 9),
            (5, 6),
            (6, 7),
            (6, 7),
            (6, 7),
            (5, 2),
        ]
        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        utils.assign_labels(G1, G2, mapped, same=True)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Connect nodes maintaining symmetry
        G1.add_edges_from([(6, 9), (7, 8), (5, 8), (4, 9), (4, 9)])
        G2.add_edges_from(
            [
                (mapped[6], mapped[8]),
                (mapped[7], mapped[9]),
                (mapped[5], mapped[8]),
                (mapped[4], mapped[9]),
                (mapped[4], mapped[9]),
            ]
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Make isomorphic
        G1.add_edges_from([(6, 8), (6, 8), (7, 9), (7, 9), (7, 9)])
        G2.add_edges_from(
            [
                (mapped[6], mapped[8]),
                (mapped[6], mapped[9]),
                (mapped[7], mapped[8]),
                (mapped[7], mapped[9]),
                (mapped[7], mapped[9]),
            ]
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Connect more nodes
        G1.add_edges_from([(2, 7), (2, 7), (3, 6), (3, 6)])
        G2.add_edges_from(
            [
                (mapped[2], mapped[7]),
                (mapped[2], mapped[7]),
                (mapped[3], mapped[6]),
                (mapped[3], mapped[6]),
            ]
        )
        G1.add_node(10)
        G2.add_node("Z")
        G1.nodes[10]["label"] = "blue"
        G2.nodes["Z"]["label"] = "blue"

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Connect the newly added node, to opposite sides of the graph
        G1.add_edges_from([(10, 1), (10, 5), (10, 8), (10, 10), (10, 10)])
        G2.add_edges_from(
            [
                ("Z", mapped[1]),
                ("Z", mapped[4]),
                ("Z", mapped[9]),
                ("Z", "Z"),
                ("Z", "Z"),
            ]
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # We connected the new node to opposite sides, so G1 must be symmetrical to G2. Re-structure them to be so
        G1.remove_edges_from([(1, 3), (4, 9), (4, 9), (7, 9)])
        G2.remove_edges_from(
            [
                (mapped[1], mapped[3]),
                (mapped[4], mapped[9]),
                (mapped[4], mapped[9]),
                (mapped[7], mapped[9]),
            ]
        )
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Get two subgraphs that are not isomorphic but are easy to make
        H1 = nx.Graph(G1.subgraph([2, 3, 4, 5, 6, 7, 10]))
        H2 = nx.Graph(
            G2.subgraph(
                [mapped[4], mapped[5], mapped[6], mapped[7], mapped[8], mapped[9], "Z"]
            )
        )

        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert not m

        # Restructure both to make them isomorphic
        H1.add_edges_from([(10, 2), (10, 6), (3, 6), (2, 7), (2, 6), (3, 7)])
        H2.add_edges_from(
            [("Z", mapped[7]), (mapped[6], mapped[9]), (mapped[7], mapped[8])]
        )
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Remove one self-loop in H2
        H2.remove_edge("Z", "Z")
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert not m

        # Compensate in H1
        H1.remove_edge(10, 10)
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

    def test_custom_multigraph3_different_labels(self):
        G1 = nx.MultiGraph()

        mapped = {1: 9, 2: 8, 3: 7, 4: 6, 5: 3, 8: 5, 9: 4, 7: 1, 6: 2}
        edges1 = [
            (1, 2),
            (1, 3),
            (1, 3),
            (2, 3),
            (2, 3),
            (3, 4),
            (4, 5),
            (4, 7),
            (4, 9),
            (4, 9),
            (4, 9),
            (5, 8),
            (5, 8),
            (8, 9),
            (8, 9),
            (5, 6),
            (6, 7),
            (6, 7),
            (6, 7),
            (5, 2),
        ]

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        utils.assign_labels(G1, G2, mapped)

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Delete edge maintaining isomorphism
        G1.remove_edge(4, 9)
        G2.remove_edge(4, 6)

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Change edge orientation such that G1 mirrors G2
        G1.add_edges_from([(4, 9), (1, 2), (1, 2)])
        G1.remove_edges_from([(1, 3), (1, 3)])
        G2.add_edges_from([(3, 5), (7, 9)])
        G2.remove_edge(8, 9)

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Make all labels the same, so G1 and G2 are also isomorphic
        for n1, n2 in zip(G1.nodes(), G2.nodes()):
            G1.nodes[n1]["label"] = "blue"
            G2.nodes[n2]["label"] = "blue"

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        G1.add_node(10)
        G2.add_node("Z")
        G1.nodes[10]["label"] = "green"
        G2.nodes["Z"]["label"] = "green"

        # Add different number of edges between the new nodes and themselves
        G1.add_edges_from([(10, 10), (10, 10)])
        G2.add_edges_from([("Z", "Z")])

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Make the number of self-edges equal
        G1.remove_edge(10, 10)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Connect the new node to the graph
        G1.add_edges_from([(10, 3), (10, 4)])
        G2.add_edges_from([("Z", 8), ("Z", 3)])

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Remove central node
        G1.remove_node(4)
        G2.remove_node(3)
        G1.add_edges_from([(5, 6), (5, 6), (5, 7)])
        G2.add_edges_from([(1, 6), (1, 6), (6, 2)])

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

    def test_custom_multigraph4_same_labels(self):
        G1 = nx.MultiGraph()
        edges1 = [
            (1, 2),
            (1, 2),
            (2, 2),
            (2, 3),
            (3, 8),
            (3, 8),
            (3, 4),
            (4, 5),
            (4, 5),
            (4, 5),
            (4, 6),
            (3, 6),
            (3, 6),
            (6, 6),
            (8, 7),
            (7, 7),
            (8, 9),
            (9, 9),
            (8, 9),
            (8, 9),
            (5, 9),
            (10, 11),
            (11, 12),
            (12, 13),
            (11, 13),
            (10, 10),
            (10, 11),
            (11, 13),
        ]

        mapped = {
            1: "n",
            2: "m",
            3: "l",
            4: "j",
            5: "k",
            6: "i",
            7: "g",
            8: "h",
            9: "f",
            10: "b",
            11: "a",
            12: "d",
            13: "e",
        }

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        utils.assign_labels(G1, G2, mapped, same=True)

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Add extra but corresponding edges to both graphs
        G1.add_edges_from([(2, 2), (2, 3), (2, 8), (3, 4)])
        G2.add_edges_from([("m", "m"), ("m", "l"), ("m", "h"), ("l", "j")])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Obtain subgraphs
        H1 = nx.MultiGraph(G1.subgraph([2, 3, 4, 6, 10, 11, 12, 13]))
        H2 = nx.MultiGraph(
            G2.subgraph(
                [
                    mapped[2],
                    mapped[3],
                    mapped[8],
                    mapped[9],
                    mapped[10],
                    mapped[11],
                    mapped[12],
                    mapped[13],
                ]
            )
        )

        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert not m

        # Make them isomorphic
        H2.remove_edges_from(
            [(mapped[3], mapped[2]), (mapped[9], mapped[8]), (mapped[2], mapped[2])]
        )
        H2.add_edges_from([(mapped[9], mapped[9]), (mapped[2], mapped[8])])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Re-structure the disconnected sub-graph
        H1.remove_node(12)
        H2.remove_node(mapped[12])
        H1.add_edge(13, 13)
        H2.add_edge(mapped[13], mapped[13])

        # Connect the two disconnected components, forming a single graph
        H1.add_edges_from([(3, 13), (6, 11)])
        H2.add_edges_from([(mapped[8], mapped[10]), (mapped[2], mapped[11])])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Change orientation of self-loops in one graph, maintaining the degree sequence
        H1.remove_edges_from([(2, 2), (3, 6)])
        H1.add_edges_from([(6, 6), (2, 3)])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert not m

    def test_custom_multigraph4_different_labels(self):
        G1 = nx.MultiGraph()
        edges1 = [
            (1, 2),
            (1, 2),
            (2, 2),
            (2, 3),
            (3, 8),
            (3, 8),
            (3, 4),
            (4, 5),
            (4, 5),
            (4, 5),
            (4, 6),
            (3, 6),
            (3, 6),
            (6, 6),
            (8, 7),
            (7, 7),
            (8, 9),
            (9, 9),
            (8, 9),
            (8, 9),
            (5, 9),
            (10, 11),
            (11, 12),
            (12, 13),
            (11, 13),
        ]

        mapped = {
            1: "n",
            2: "m",
            3: "l",
            4: "j",
            5: "k",
            6: "i",
            7: "g",
            8: "h",
            9: "f",
            10: "b",
            11: "a",
            12: "d",
            13: "e",
        }

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)

        utils.assign_labels(G1, G2, mapped)

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m == mapped

        # Add extra but corresponding edges to both graphs
        G1.add_edges_from([(2, 2), (2, 3), (2, 8), (3, 4)])
        G2.add_edges_from([("m", "m"), ("m", "l"), ("m", "h"), ("l", "j")])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m == mapped

        # Obtain isomorphic subgraphs
        H1 = nx.MultiGraph(G1.subgraph([2, 3, 4, 6]))
        H2 = nx.MultiGraph(G2.subgraph(["m", "l", "j", "i"]))

        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Delete the 3-clique, keeping only the path-graph. Also, H1 mirrors H2
        H1.remove_node(4)
        H2.remove_node("j")
        H1.remove_edges_from([(2, 2), (2, 3), (6, 6)])
        H2.remove_edges_from([("l", "i"), ("m", "m"), ("m", "m")])

        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert not m

        # Assign the same labels so that mirroring means isomorphic
        for n1, n2 in zip(H1.nodes(), H2.nodes()):
            H1.nodes[n1]["label"] = "red"
            H2.nodes[n2]["label"] = "red"

        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Leave only one node with self-loop
        H1.remove_nodes_from([3, 6])
        H2.remove_nodes_from(["m", "l"])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Remove one self-loop from H1
        H1.remove_edge(2, 2)
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert not m

        # Same for H2
        H2.remove_edge("i", "i")
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Compose H1 with the disconnected sub-graph of G1. Same for H2
        S1 = nx.compose(H1, nx.MultiGraph(G1.subgraph([10, 11, 12, 13])))
        S2 = nx.compose(H2, nx.MultiGraph(G2.subgraph(["a", "b", "d", "e"])))

        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

        # Connect the two components
        S1.add_edges_from([(13, 13), (13, 13), (2, 13)])
        S2.add_edges_from([("a", "a"), ("a", "a"), ("i", "e")])
        m = vf2pp_mapping(H1, H2, node_labels="label")
        assert m

    def test_custom_multigraph5_same_labels(self):
        G1 = nx.MultiGraph()

        edges1 = [
            (1, 5),
            (1, 2),
            (1, 4),
            (2, 3),
            (2, 6),
            (3, 4),
            (3, 7),
            (4, 8),
            (5, 8),
            (5, 6),
            (6, 7),
            (7, 8),
        ]
        mapped = {1: "a", 2: "h", 3: "d", 4: "i", 5: "g", 6: "b", 7: "j", 8: "c"}

        G1.add_edges_from(edges1)
        G2 = nx.relabel_nodes(G1, mapped)
        utils.assign_labels(G1, G2, mapped, same=True)

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Add multiple edges and self-loops, maintaining isomorphism
        G1.add_edges_from(
            [(1, 2), (1, 2), (3, 7), (8, 8), (8, 8), (7, 8), (2, 3), (5, 6)]
        )
        G2.add_edges_from(
            [
                ("a", "h"),
                ("a", "h"),
                ("d", "j"),
                ("c", "c"),
                ("c", "c"),
                ("j", "c"),
                ("d", "h"),
                ("g", "b"),
            ]
        )

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Make G2 to be the rotated G1
        G2.remove_edges_from(
            [
                ("a", "h"),
                ("a", "h"),
                ("d", "j"),
                ("c", "c"),
                ("c", "c"),
                ("j", "c"),
                ("d", "h"),
                ("g", "b"),
            ]
        )
        G2.add_edges_from(
            [
                ("d", "i"),
                ("a", "h"),
                ("g", "b"),
                ("g", "b"),
                ("i", "i"),
                ("i", "i"),
                ("b", "j"),
                ("d", "j"),
            ]
        )

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

    def test_disconnected_multigraph_all_same_labels(self):
        G1 = nx.MultiGraph()
        G1.add_nodes_from([i for i in range(10)])
        G1.add_edges_from([(i, i) for i in range(10)])

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        G2 = nx.relabel_nodes(G1, mapped)

        for n in G1.nodes():
            G1.nodes[n]["label"] = "blue"
            G2.nodes[n]["label"] = "blue"

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Add self-loops to non-mapped nodes. Should be the same, as the graph is disconnected.
        G1.add_edges_from([(i, i) for i in range(5, 8)] * 3)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Compensate in G2
        G2.add_edges_from([(i, i) for i in range(0, 3)] * 3)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

        # Add one more self-loop in G2
        G2.add_edges_from([(0, 0), (1, 1), (1, 1)])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Compensate in G1
        G1.add_edges_from([(5, 5), (7, 7), (7, 7)])
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m

    def test_disconnected_multigraph_all_different_labels(self):
        G1 = nx.MultiGraph()
        G1.add_nodes_from([i for i in range(10)])
        G1.add_edges_from([(i, i) for i in range(10)])

        mapped = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        G2 = nx.relabel_nodes(G1, mapped)

        utils.assign_labels(G1, G2, mapped)

        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
        assert m == mapped

        # Add self-loops to non-mapped nodes. Now it is not the same, as there are different labels
        G1.add_edges_from([(i, i) for i in range(5, 8)] * 3)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Add self-loops to non mapped nodes in G2 as well
        G2.add_edges_from([(mapped[i], mapped[i]) for i in range(0, 3)] * 7)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Add self-loops to mapped nodes in G2
        G2.add_edges_from([(mapped[i], mapped[i]) for i in range(5, 8)] * 3)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert not m

        # Add self-loops to G1 so that they are even in both graphs
        G1.add_edges_from([(i, i) for i in range(0, 3)] * 7)
        m = vf2pp_mapping(G1, G2, node_labels="label")
        assert m
