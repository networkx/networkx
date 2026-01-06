"""
Motif counting using the ESU (Enumerate Subgraphs) algorithm.

This module implements motif counting for small connected subgraphs
using the ESU algorithm by Wernicke (2006).
"""

import networkx as nx

__all__ = ["count_motifs"]


@nx._dispatchable
def count_motifs(G, size=3):
    """Count occurrences of connected subgraph motifs using the ESU algorithm.

    Enumerates all connected induced subgraphs of a given size and counts
    their occurrences grouped by isomorphism class. Uses the ESU algorithm
    (Wernicke, 2006) which efficiently avoids duplicate counting through
    a tree-traversal structure.

    Parameters
    ----------
    G : NetworkX Graph or DiGraph
        The input graph.

    size : int, optional (default=3)
        The size (number of nodes) of motifs to count. Must be between 2 and 4.

    Returns
    -------
    motif_counts : dict
        A dictionary mapping canonical subgraph hashes (using Weisfeiler-Lehman
        graph hash) to their occurrence counts.

    Raises
    ------
    ValueError
        If size is less than 2 or greater than 4.

    Notes
    -----
    The ESU algorithm works by iterating through each node and extending
    subgraphs only through neighbors with higher indices. This ensures each
    connected subgraph is enumerated exactly once.

    The canonical labeling uses the Weisfeiler-Lehman graph hash which
    provides consistent identification of isomorphic subgraphs.

    For larger motif sizes (k > 4), the computation becomes exponentially
    expensive and is not recommended without specialized hardware.

    References
    ----------
    .. [1] Wernicke, S. (2006). Efficient Detection of Network Motifs.
       IEEE/ACM Transactions on Computational Biology and Bioinformatics,
       3(4), 347-359.

    Examples
    --------
    >>> G = nx.complete_graph(4)
    >>> motifs = nx.count_motifs(G, size=3)
    >>> sum(motifs.values())  # K4 has 4 triangles
    4

    >>> G = nx.path_graph(4)
    >>> motifs = nx.count_motifs(G, size=3)
    >>> sum(motifs.values())  # P4 has 2 connected 3-node subgraphs
    2

    See Also
    --------
    triadic_census : Count triads in a directed graph.
    weisfeiler_lehman_graph_hash : Compute canonical hash for graphs.
    """
    if size < 2:
        raise ValueError("Motif size must be at least 2")
    if size > 4:
        raise ValueError("Motif size must be at most 4 for performance reasons")

    if len(G) < size:
        return {}

    if G.number_of_edges() == 0:
        return {}

    counts: dict[str, int] = {}

    if not all(isinstance(n, int) for n in G.nodes()):
        node_mapping = {node: i for i, node in enumerate(G.nodes())}
        G = nx.relabel_nodes(G, node_mapping)

    nodes = sorted(G.nodes())

    def get_canonical_label(subgraph_nodes: set[int]) -> str:
        S = G.subgraph(subgraph_nodes).copy()
        return nx.weisfeiler_lehman_graph_hash(S)

    def get_neighbors(node: int) -> set[int]:
        neighbors: set[int] = set(G.neighbors(node))
        if G.is_directed():
            neighbors.update(G.predecessors(node))
        return neighbors

    def extend_subgraph(
        subgraph: set[int], extension: set[int], v_start: int, forbidden: set[int]
    ) -> None:
        if len(subgraph) == size:
            label = get_canonical_label(subgraph)
            counts[label] = counts.get(label, 0) + 1
            return

        ext_list = sorted(extension)
        for i, w in enumerate(ext_list):
            remaining = set(ext_list[i + 1 :])

            new_forbidden = forbidden | set(ext_list[: i + 1])

            w_neighbors = get_neighbors(w)
            new_neighbors = w_neighbors - subgraph - new_forbidden
            valid_new = {n for n in new_neighbors if n > v_start}

            new_extension = remaining | valid_new

            new_subgraph = subgraph | {w}
            extend_subgraph(new_subgraph, new_extension, v_start, new_forbidden)

    for v in nodes:
        initial_extension = {n for n in get_neighbors(v) if n > v}
        extend_subgraph({v}, initial_extension, v, {v})

    return counts
