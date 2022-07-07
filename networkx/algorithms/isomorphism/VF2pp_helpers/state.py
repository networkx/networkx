def update_Tinout(G1, G2, T1, T2, T1_out, T2_out, new_node1, new_node2, mapping, reverse_mapping):
    # This function should be called right after the feasibility is established and node1 is mapped to node2.
    uncovered_neighbors_G1 = {nbr for nbr in G1[new_node1] if nbr not in mapping}
    uncovered_neighbors_G2 = {nbr for nbr in G2[new_node2] if nbr not in reverse_mapping}

    # Add the uncovered neighbors of node1 and node2 in T1 and T2 respectively
    T1.discard(new_node1)
    T2.discard(new_node2)
    T1 = T1.union(uncovered_neighbors_G1)
    T2 = T2.union(uncovered_neighbors_G2)

    # todo: maybe check this twice just to make sure
    T1_out.discard(new_node1)
    T2_out.discard(new_node2)
    T1_out = T1_out - uncovered_neighbors_G1
    T2_out = T2_out - uncovered_neighbors_G2

    return T1, T2, T1_out, T2_out


def restore_Tinout(G1, G2, T1, T2, T1_out, T2_out, popped_node1, popped_node2, mapping, reverse_mapping):
    # If the node we want to remove from the mapping, has at least one covered neighbor, add it to T1.
    is_added = False
    for nbr in G1[popped_node1]:
        if nbr in mapping:
            T1.add(popped_node1)  # if a neighbor of the excluded node1 is in the mapping, keep node1 in T1
            is_added = True
        else:  # check if its neighbor has another connection with a covered node. If not, only then exclude it from T1
            if any(nbr2 in mapping for nbr2 in G1[nbr]):
                continue
            T1.discard(nbr)
            T1_out.add(nbr)

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

    return T1, T2, T1_out, T2_out
