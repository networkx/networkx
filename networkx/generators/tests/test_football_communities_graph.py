import numpy as np

import networkx as nx

# List of edges between communities
EDGES_TO_ADD = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 0),
    (0, 6),
    (1, 7),
    (2, 8),
    (3, 9),
    (4, 10),
    (5, 11),
    (6, 12),
    (7, 12),
    (8, 13),
    (9, 13),
    (10, 14),
    (11, 14),
    (7, 15),
    (8, 16),
    (9, 17),
    (10, 18),
    (11, 19),
    (6, 20),
    (15, 16),
    (17, 18),
    (19, 20),
    (15, 21),
    (16, 22),
    (17, 23),
    (18, 24),
    (19, 25),
    (20, 26),
    (12, 27),
    (13, 28),
    (14, 29),
    (21, 30),
    (22, 31),
    (28, 32),
    (23, 33),
    (24, 34),
    (29, 35),
    (25, 36),
    (26, 37),
    (27, 38),
    (21, 31),
    (22, 32),
    (28, 33),
    (23, 34),
    (24, 35),
    (29, 36),
    (25, 37),
    (26, 38),
    (27, 30),
    (30, 39),
    (31, 40),
    (32, 41),
    (33, 42),
    (34, 43),
    (35, 44),
    (36, 45),
    (37, 46),
    (38, 47),
    (39, 47),
    (41, 42),
    (44, 45),
    (39, 48),
    (40, 48),
    (40, 49),
    (41, 49),
    (42, 50),
    (43, 50),
    (43, 51),
    (44, 51),
    (45, 52),
    (46, 52),
    (46, 53),
    (47, 53),
    (48, 54),
    (49, 55),
    (50, 56),
    (51, 57),
    (52, 58),
    (53, 59),
    (54, 55),
    (55, 56),
    (56, 57),
    (57, 58),
    (58, 59),
    (59, 54),
]

EDGE_SET = set(EDGES_TO_ADD) | {(b, a) for (a, b) in EDGES_TO_ADD}


# Test the number of nodes
def test_number_of_nodes():
    for n in range(1, 10):
        for p_in in np.arange(0, 1.01, 0.2):
            for p_out in np.arange(0, 1.01, 0.2):
                G = nx.football_communities_graph(n, p_in, p_out, seed=42)
                assert len(G) == n * 60


# Test internal edges when p_in = 1
def test_internal_full():
    for n in range(1, 10):
        for p_out in np.arange(0, 1.01, 0.2):
            G = nx.football_communities_graph(n, 1.0, p_out, seed=42)
            communities = G.graph["communities"]

            for nodes in communities.values():
                sub = G.subgraph(nodes)
                assert sub.number_of_edges() == n * (n - 1) // 2


# Test internal edges when p_in = 0
def test_internal_zero():
    for n in range(1, 10):
        for p_out in np.arange(0, 1.01, 0.2):
            G = nx.football_communities_graph(n, 0.0, p_out, seed=42)
            communities = G.graph["communities"]

            for nodes in communities.values():
                sub = G.subgraph(nodes)
                assert sub.number_of_edges() == 0


# Test edges between neighboring communities when p_out = 1
def test_inter_full():
    for n in range(1, 10):
        for p_in in np.arange(0, 1.01, 0.2):
            G = nx.football_communities_graph(n, p_in, 1.0, seed=42)
            communities = G.graph["communities"]

            for c1, c2 in EDGES_TO_ADD:
                count = 0
                for u in communities[c1]:
                    for v in communities[c2]:
                        if G.has_edge(u, v):
                            count += 1

                assert count == n * n


# Test edges between neighboring communities when p_out = 0
def test_inter_zero():
    for n in range(1, 10):
        for p_in in np.arange(0, 1.01, 0.2):
            G = nx.football_communities_graph(n, p_in, 0.0, seed=42)
            communities = G.graph["communities"]

            for c1, c2 in EDGES_TO_ADD:
                for u in communities[c1]:
                    for v in communities[c2]:
                        assert not G.has_edge(u, v)


# Test absence of edges between non-neighboring communities
def test_no_edges_between_non_neighbors():
    for n in range(1, 10):
        G = nx.football_communities_graph(n, 0.0, 1.0, seed=42)
        communities = G.graph["communities"]

        for c1 in range(60):
            for c2 in range(c1 + 1, 60):
                if (c1, c2) in EDGE_SET:
                    continue

                for u in communities[c1]:
                    for v in communities[c2]:
                        assert not G.has_edge(u, v)
