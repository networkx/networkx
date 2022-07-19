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
    covered_neighbors = {
        nbr for nbr in graph_params.G1[u] if nbr in state_params.mapping
    }
    if len(covered_neighbors) == 0:
        return {
            node
            for node in graph_params.G2.nodes()
            if node not in state_params.reverse_mapping
            and graph_params.G2.degree[node] == graph_params.G1.degree[u]
            and graph_params.G2_labels[node] == graph_params.G1_labels[u]
            and len(
                [
                    nbr2
                    for nbr2 in graph_params.G2[node]
                    if nbr2 in state_params.reverse_mapping
                ]
            )
            == 0
        }

    G2_uncovered_neighborhoods = []
    for neighbor1 in covered_neighbors:
        current_neighborhood = set()
        for neighbor2 in graph_params.G2[state_params.mapping[neighbor1]]:
            current_neighborhood.add(neighbor2)
        G2_uncovered_neighborhoods.append(current_neighborhood)

    common_nodes = set.intersection(*G2_uncovered_neighborhoods)
    candidates = {
        node
        for node in common_nodes
        if graph_params.G1_labels[u] == graph_params.G2_labels[node]
        and graph_params.G1.degree[u] == graph_params.G2.degree[node]
    }

    return candidates
