def find_candidates(u, graph_params, state_params):
    """Given node u of G1, finds the candidates of u from G2.

    Parameters
    ----------
    u: Graph node
        The node from G1 for which to find the candidates from G2.

    graph_params: namedtuple
        Contains all the Graph-related parameters:

        G1,G2: NetworkX Graph or MultiGraph instances.
            The two graphs to check for isomorphism or monomorphism

        G1_labels,G2_labels: dict
            The label of every node in G1 and G2 respectively

    state_params: namedtuple
        Contains all the State-related parameters:

        mapping: dict
            The mapping as extended so far. Maps nodes of G1 to nodes of G2

        reverse_mapping: dict
            The reverse mapping as extended so far. Maps nodes from G2 to nodes of G1. It's basically "mapping" reversed

        T1, T2: set
            Ti contains uncovered neighbors of covered nodes from Gi, i.e. nodes that are not in the mapping, but are
            neighbors of nodes that are.

        T1_out, T2_out: set
            Ti_out contains all the nodes from Gi, that are neither in the mapping nor in Ti

    Returns
    -------
    candidates: set
        The nodes from G2 which are candidates for u.
    """
    G1, G2, G1_labels, _, _, nodes_of_G2Labels, G2_nodes_of_degree = graph_params
    mapping, reverse_mapping, _, _, _, _ = state_params

    covered_neighbors = [nbr for nbr in G1[u] if nbr in mapping]
    if not covered_neighbors:
        return {
            node
            for node in G2.nodes()
            if node not in reverse_mapping
            and all(nbr2 not in reverse_mapping for nbr2 in G2[node])
        }.intersection(
            *[nodes_of_G2Labels[G1_labels[u]], G2_nodes_of_degree[G1.degree[u]]]
        )

    nbr1 = covered_neighbors[0]
    common_nodes = {nbr2 for nbr2 in G2[mapping[nbr1]]}

    for nbr1 in covered_neighbors[1:]:
        common_nodes.intersection_update(G2[mapping[nbr1]])

    return {node for node in common_nodes if node not in reverse_mapping}.intersection(
        *[nodes_of_G2Labels[G1_labels[u]], G2_nodes_of_degree[G1.degree[u]]]
    )
