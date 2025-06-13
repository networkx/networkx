import networkx as nx
from networkx.exception import NetworkXError

__all__ = ["is_perfect_graph"]


def is_perfect_graph(G, *, max_cycle_length=None):
    """Return True if G is a perfect graph, else False.

    According to the Strong Perfect Graph Theorem, a graph is perfect
    if and only if neither it nor its complement contains an induced
    odd cycle of length at least 5.

    Parameters
    ----------
    G : NetworkX graph
        The graph to check.

    max_cycle_length : int or None (default: None)
        Maximum length of odd holes/antiholes to check. If None, checks
        up to number of nodes in G.

    Returns
    -------
    bool
        True if G is perfect, False otherwise.

    Notes
    -----
    This implementation uses the Strong Perfect Graph Theorem.
    """

    if max_cycle_length is None:
        max_cycle_length = G.number_of_nodes()

    if max_cycle_length > 12:
        import warnings

        warnings.warn(
            f"Checking for induced odd holes up to length {max_cycle_length} may be slow on large graphs.",
            RuntimeWarning,
        )

    def has_induced_odd_hole(graph):
        """Check for any induced odd cycle (hole) of length ≥5."""
        nodes = list(graph.nodes)
        n = len(nodes)

        for i in range(n):
            for j in range(i + 1, n):
                try:
                    paths = list(
                        nx.all_simple_paths(
                            graph, nodes[i], nodes[j], cutoff=max_cycle_length
                        )
                    )
                except nx.NetworkXNoPath:
                    continue

                for path in paths:
                    if len(path) < 5 or len(path) % 2 == 0:
                        continue

                    # Check if this forms a cycle
                    if graph.has_edge(path[-1], path[0]):
                        cycle_nodes = path
                        subG = graph.subgraph(cycle_nodes)

                        # Induced means only edges in the cycle
                        if subG.number_of_edges() == len(cycle_nodes):
                            return True
        return False

    if has_induced_odd_hole(G):
        return False

    if has_induced_odd_hole(nx.complement(G)):
        return False

    return True
