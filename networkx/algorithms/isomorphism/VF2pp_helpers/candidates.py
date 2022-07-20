def find_candidates(u, graph_params, state_params):
    """Given a node u of G1, finds the candidates of u from G2.

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.

    u: int
        The node from G1 for which to find the candidates from G2.

    mapping: dict
        The mapping as extended so far. Maps nodes of G1 to nodes of G2.

    reverse_mapping: dict
        The reverse mapping as extended so far. Maps nodes from G2 to nodes of G1. It's basically "mapping" reversed.

    Returns
    -------
    candidates: set
        The nodes from G2 which are candidates for u.
    """
    G1, G2, G1_labels, G2_labels = graph_params
    mapping, reverse_mapping, T1, T1_out, T2, T2_out = state_params

    covered_neighbors = [nbr for nbr in G1[u] if nbr in mapping]
    if not covered_neighbors:
        return {
            node
            for node in G2.nodes()
            if node not in reverse_mapping
            and G2.degree[node] == G1.degree[u]
            and G2_labels[node] == G1_labels[u]
            and not {nbr2 for nbr2 in G2[node] if nbr2 in reverse_mapping}
        }

    nbr1 = covered_neighbors[0]
    current_neighborhood = {nbr2 for nbr2 in G2[mapping[nbr1]]}
    common_nodes = current_neighborhood.copy()

    for nbr1 in covered_neighbors[1:]:
        current_neighborhood = {nbr2 for nbr2 in G2[mapping[nbr1]]}
        common_nodes.intersection_update(current_neighborhood)

    common_nodes.intersection_update(
        {
            node
            for node in common_nodes
            if G1_labels[u] == G2_labels[node] and G1.degree[u] == G2.degree[node]
        }
    )
    return common_nodes
