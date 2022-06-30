def find_candidates(G1, G2, G1_labels, G2_labels, u, state):
    if G1.degree[u] == 0:
        return {node for node in G2.nodes() if
                G2.degree[node] == 0 and G2_labels[node] == G1_labels[u] and node not in state.reverse_mapping}

    covered_neighbors = {nbr for nbr in G1[u] if nbr in state.mapping}
    if len(covered_neighbors) == 0:
        return {node for node in G2.nodes() if  # todo: add label check for every neighbor
                node not in state.reverse_mapping and G2.degree[node] == G1.degree[u] and len(
                    [nbr2 for nbr2 in G2[node] if nbr2 in state.reverse_mapping]) == 0}

    G2_uncovered_neighborhoods = []
    for neighbor1 in covered_neighbors:
        current_neighborhood = set()
        for neighbor2 in G2[state.mapping[neighbor1]]:
            current_neighborhood.add(neighbor2)
        G2_uncovered_neighborhoods.append(current_neighborhood)

    # for neighbor1 in G1[u]:
    #     current_neighborhood = set()
    #     if neighbor1 in state.mapping:
    #         for neighbor2 in G2[state.mapping[neighbor1]]:
    #             current_neighborhood.add(neighbor2)
    #     if len(current_neighborhood) > 0:
    #         G2_uncovered_neighborhoods.append(current_neighborhood)

    common_nodes = set.intersection(*G2_uncovered_neighborhoods)
    candidates = {node for node in common_nodes if G1_labels[u] == G2_labels[node] and G1.degree[u] == G2.degree[node]}

    return candidates
