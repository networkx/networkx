def _find_candidates(
    u, graph_params, state_params, G1_degree
):  # todo: make the 4th argument the degree of u
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

        T1_tilde, T2_tilde: set
            Ti_tilde contains all the nodes from Gi, that are neither in the mapping nor in Ti

    Returns
    -------
    candidates: set
        The nodes from G2 which are candidates for u.
    """
    G1, G2, G1_labels, _, _, nodes_of_G2Labels, G2_nodes_of_degree = graph_params
    mapping, reverse_mapping, _, _, _, _, _, _, T2_tilde, _ = state_params

    covered_neighbors = [nbr for nbr in G1[u] if nbr in mapping]
    if not covered_neighbors:
        candidates = set(nodes_of_G2Labels[G1_labels[u]])
        candidates.intersection_update(G2_nodes_of_degree[G1_degree[u]])
        candidates.intersection_update(T2_tilde)
        candidates.difference_update(reverse_mapping)
        if G1.is_multigraph():
            candidates.difference_update(
                {
                    node
                    for node in candidates
                    if G1.number_of_edges(u, u) != G2.number_of_edges(node, node)
                }
            )
        return candidates

    nbr1 = covered_neighbors[0]
    common_nodes = set(G2[mapping[nbr1]])

    for nbr1 in covered_neighbors[1:]:
        common_nodes.intersection_update(G2[mapping[nbr1]])

    common_nodes.difference_update(reverse_mapping)
    common_nodes.intersection_update(G2_nodes_of_degree[G1_degree[u]])
    common_nodes.intersection_update(nodes_of_G2Labels[G1_labels[u]])
    if G1.is_multigraph():
        common_nodes.difference_update(
            {
                node
                for node in common_nodes
                if G1.number_of_edges(u, u) != G2.number_of_edges(node, node)
            }
        )
    return common_nodes


def _find_candidates_Di(u, graph_params, state_params, G1_degree):
    G1, G2, G1_labels, _, _, nodes_of_G2Labels, G2_nodes_of_degree = graph_params
    mapping, reverse_mapping, _, _, _, _, _, _, T2_tilde, _ = state_params

    covered_successors = [succ for succ in G1[u] if succ in mapping]
    covered_predecessors = [pred for pred in G1.pred[u] if pred in mapping]

    if not (covered_successors or covered_predecessors):
        candidates = set(nodes_of_G2Labels[G1_labels[u]])
        candidates.intersection_update(G2_nodes_of_degree[G1_degree[u]])
        candidates.intersection_update(T2_tilde)
        candidates.difference_update(reverse_mapping)
        if G1.is_multigraph():
            candidates.difference_update(
                {
                    node
                    for node in candidates
                    if G1.number_of_edges(u, u) != G2.number_of_edges(node, node)
                }
            )
        return candidates

    if covered_successors:
        succ1 = covered_successors[0]
        common_nodes = set(G2.pred[mapping[succ1]])

        for succ1 in covered_successors[1:]:
            common_nodes.intersection_update(G2.pred[mapping[succ1]])
    else:
        pred1 = covered_predecessors.pop()
        common_nodes = set(G2[mapping[pred1]])

    for pred1 in covered_predecessors:
        common_nodes.intersection_update(G2[mapping[pred1]])

    common_nodes.difference_update(reverse_mapping)
    common_nodes.intersection_update(G2_nodes_of_degree[G1_degree[u]])
    common_nodes.intersection_update(nodes_of_G2Labels[G1_labels[u]])
    if G1.is_multigraph():
        common_nodes.difference_update(
            {
                node
                for node in common_nodes
                if G1.number_of_edges(u, u) != G2.number_of_edges(node, node)
            }
        )
    return common_nodes
