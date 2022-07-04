class State:
    def __init__(self, G1, G2, u, node_order, mapping, reverse_mapping):
        self.u = u
        self.node_order = node_order
        self.mapping = mapping
        self.reverse_mapping = reverse_mapping

        self.T1 = {nbr for node in mapping for nbr in G1[node] if nbr not in mapping}
        self.T2 = {nbr for node in reverse_mapping for nbr in G2[node] if nbr not in reverse_mapping}

        self.T1_out = {n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in self.T1}
        self.T2_out = {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in self.T2}


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
            T1.add(popped_node1)
            is_added = True
            break

    # Case where the node does not exist in neither the mapping nor T1. By deffinition it should belong to T1_out
    if not is_added:
        T1_out.add(popped_node1)

    is_added = False
    for nbr in G2[popped_node2]:
        if nbr in reverse_mapping:
            T2.add(popped_node2)
            break

    if not is_added:
        T2_out.add(popped_node2)

    return T1, T2, T1_out, T2_out