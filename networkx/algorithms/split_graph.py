import networkx as nx
from networkx.algorithms.clique import find_cliques

__all__ = ["is_split_graph", "is_complete_split_graph"]


def is_split_graph(G: nx.Graph) -> bool:
    """
    Returns True if G is a split graph.
    A graph is split if it is chordal and its complement is also chordal.
    """
    return nx.is_chordal(G) and nx.is_chordal(nx.complement(G))


def is_complete_split_graph(G: nx.Graph) -> bool:
    """
    Returns True if G is a complete split graph.

    Checks:
    1. The graph is split.
    2. There exists a max clique and an independent set partition.
    3. The independent set is connected to every vertex in the clique minus the lowest-degree vertex.
    """
    if G.number_of_nodes() == 0:
        return True

    if not is_split_graph(G):
        return False

    # Pick one maximum clique
    cliques = list(find_cliques(G))
    max_clique = max(cliques, key=len)
    clique_set = set(max_clique)
    rest = set(G.nodes) - clique_set

    # 1. Remaining nodes must form an independent set
    if any(G.has_edge(u, v) for u in rest for v in rest if u != v):
        return False

    # 2. Remove lowest-degree vertex in the clique
    if len(clique_set) > 1:
        to_remove = min(clique_set, key=G.degree)
        clique_reduced = clique_set - {to_remove}
    else:
        clique_reduced = set()

    # 3. Each node in rest must connect to every vertex in reduced clique
    if all(all(G.has_edge(u, v) for v in clique_reduced) for u in rest):
        return True

    return False
