import networkx as nx
from networkx.utils import py_random_state


def create_edges_between_communities(G, c1, c2, p, rng):
    """
    Add edges between two communities with probability p.
    """
    communities = G.graph["communities"]

    nodes1 = communities[c1]
    nodes2 = communities[c2]

    for u in nodes1:
        for v in nodes2:
            if rng.random() < p:
                G.add_edge(u, v)


@py_random_state(3)
def football_communities_graph(n_per_community=40, p_in=0.35, p_out=0.05, seed=None):
    """
    Generate a football-like graph with 60 communities.

    Parameters
    ----------
    n_per_community : int
        Number of nodes in each community.
    p_in : float
        Probability of edges inside communities.
    p_out : float
        Probability of edges between connected communities.
    seed : int, random state or None

    Returns
    -------
    G : NetworkX Graph
    """

    G = nx.Graph()
    communities = {}

    node_id = 0

    # =========================
    # Create communities
    # =========================
    for c in range(60):
        nodes = list(range(node_id, node_id + n_per_community))
        communities[c] = nodes

        for u in nodes:
            G.add_node(u, community=c)

        # internal edges
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if seed.random() < p_in:
                    G.add_edge(nodes[i], nodes[j])

        node_id += n_per_community

    G.graph["communities"] = communities

    # =========================
    # Community connections
    # =========================
    edges_to_add = [
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

    for c1, c2 in edges_to_add:
        create_edges_between_communities(G, c1, c2, p_out, seed)

    return G
