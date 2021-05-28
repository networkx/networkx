import networkx as nx
import random


def rearrange_edge_nodes(G: nx.Graph, seed=None) -> nx.Graph:
    r = random.Random(seed)
    if len(G.nodes) > 2 and len(G.edges) > 1:
        edge = r.choice(tuple(G.edges))
        node_1 = r.choice(tuple(G.nodes))
        node_2 = r.choice([n for n in tuple(G.nodes) if n != node_1])
        G_temp = G.copy()
        G_temp.remove_edge(*edge)
        G_temp.add_edge(node_1, node_2)
        return G_temp
    else:
        raise ValueError("Graph must have more than two nodes & one edge")


def test_simulated_annealing():
    G = nx.random_internet_as_graph(4, seed=42)
    R = nx.algorithms.cluster.transitivity
    args = (G, R, rearrange_edge_nodes)
    kwargs = dict(n_iter=10)
    (m, nG) = nx.algorithms.rewiring.simulated_annealing_optimize(*args, **kwargs)
    assert m == 1.0
    assert list(nG.edges) == [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4)]
