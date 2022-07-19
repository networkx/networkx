def update_Tinout(new_node1, new_node2, graph_params, state_params):
    """Updates the Ti/Ti_out (i=1,2) when a new node pair u-v is added to the mapping.

    Notes
    -----
    This function should be called right after the feasibility checks are passed, and node1 is mapped to node2. The
    purpose of this function is to avoid brute force computing of Ti/Ti_out by iterating over all nodes of the graph
    and checking which nodes satisfy the necessary conditions. Instead, in every step of the algorithm we focus
    exclusively on the two nodes that are being added to the mapping, incrementally updating Ti/Ti_out.
    todo: explain how it works

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    T1, T2: set
        Ti contains uncovered neighbors of covered nodes from Gi, i.e. nodes that are not in the mapping, but are
        neighbors of nodes that are.

    T1_out, T2_out: set
        Ti_out contains all the nodes from Gi, that are neither in the mapping nor in Ti.

    new_node1, new_node2: int
        The two new nodes, added to the mapping.

    mapping: dict
        The mapping as extended so far. Maps nodes of G1 to nodes of G2.

    reverse_mapping: dict
        The reverse mapping as extended so far. Maps nodes from G2 to nodes of G1. It's basically "mapping" reversed.
    """
    G1, G2, _, _ = graph_params
    mapping, reverse_mapping, T1, T1_out, T2, T2_out = state_params

    uncovered_neighbors_G1 = {nbr for nbr in G1[new_node1] if nbr not in mapping}
    uncovered_neighbors_G2 = {
        nbr for nbr in G2[new_node2] if nbr not in reverse_mapping
    }

    # Add the uncovered neighbors of node1 and node2 in T1 and T2 respectively
    T1.discard(new_node1)
    T2.discard(new_node2)
    T1.update(uncovered_neighbors_G1)
    T2.update(uncovered_neighbors_G2)

    T1_out.discard(new_node1)
    T2_out.discard(new_node2)
    T1_out.difference_update(uncovered_neighbors_G1)
    T2_out.difference_update(uncovered_neighbors_G2)


def restore_Tinout(popped_node1, popped_node2, graph_params, state_params):
    """Restores the previous version of Ti/Ti_out when a node pair is deleted from the mapping.

    Notes
    -----
    todo: explain how it works

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    T1, T2: set
        Ti contains uncovered neighbors of covered nodes from Gi, i.e. nodes that are not in the mapping, but are
        neighbors of nodes that are.

    T1_out, T2_out: set
        Ti_out contains all the nodes from Gi, that are neither in the mapping nor in Ti.

    popped_node1, popped_node2: int
        The two nodes deleted from the mapping.

    mapping: dict
        The mapping as extended so far. Maps nodes of G1 to nodes of G2.

    reverse_mapping: dict
        The reverse mapping as extended so far. Maps nodes from G2 to nodes of G1. It's basically "mapping" reversed.
    """
    # If the node we want to remove from the mapping, has at least one covered neighbor, add it to T1.
    G1, G2, _, _ = graph_params
    mapping, reverse_mapping, T1, T1_out, T2, T2_out = state_params

    is_added = False
    for nbr in G1[popped_node1]:
        if nbr in mapping:
            T1.add(
                popped_node1
            )  # if a neighbor of the excluded node1 is in the mapping, keep node1 in T1
            is_added = True
        else:  # check if its neighbor has another connection with a covered node. If not, only then exclude it from T1
            if any(nbr2 in mapping for nbr2 in G1[nbr]):
                continue
            T1.discard(nbr)
            T1_out.add(nbr)  # todo: maybe split into two loops

    # Case where the node is not present in neither the mapping nor T1. By deffinition it should belong to T1_out
    if not is_added:
        T1_out.add(popped_node1)

    is_added = False
    for nbr in G2[popped_node2]:
        if nbr in reverse_mapping:
            T2.add(popped_node2)
            is_added = True
        else:
            if any(nbr2 in reverse_mapping for nbr2 in G2[nbr]):
                continue
            T2.discard(nbr)
            T2_out.add(nbr)

    if not is_added:
        T2_out.add(popped_node2)


def update_state(node, candidate, graph_params, state_params):
    state_params.mapping.update({node: candidate})
    state_params.reverse_mapping.update({candidate: node})
    update_Tinout(node, candidate, graph_params, state_params)


def restore_state(stack, visited, graph_params, state_params):
    popped_node1, _ = stack[-1]
    popped_node2 = state_params.mapping[popped_node1]
    state_params.mapping.pop(popped_node1)
    state_params.reverse_mapping.pop(popped_node2)
    visited.remove(popped_node2)

    restore_Tinout(popped_node1, popped_node2, graph_params, state_params)
