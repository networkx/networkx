def _update_Tinout(new_node1, new_node2, graph_params, state_params):
    """Updates the Ti/Ti_out (i=1,2) when a new node pair u-v is added to the mapping.

    Notes
    -----
    This function should be called right after the feasibility checks are passed, and node1 is mapped to node2. The
    purpose of this function is to avoid brute force computing of Ti/Ti_out by iterating over all nodes of the graph
    and checking which nodes satisfy the necessary conditions. Instead, in every step of the algorithm we focus
    exclusively on the two nodes that are being added to the mapping, incrementally updating Ti/Ti_out.

    Parameters
    ----------
    new_node1, new_node2: Graph node
        The two new nodes, added to the mapping.

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
            Ti_out contains all the nodes from Gi, that are neither in the mapping nor in Ti
    """
    G1, G2, _, _, _, _, _ = graph_params
    (
        mapping,
        reverse_mapping,
        T1,
        T1_in,
        T1_tilde,
        T1_tilde_in,
        T2,
        T2_in,
        T2_tilde,
        T2_tilde_in,
    ) = state_params

    uncovered_successors_G1 = {succ for succ in G1[new_node1] if succ not in mapping}
    uncovered_successors_G2 = {
        succ for succ in G2[new_node2] if succ not in reverse_mapping
    }

    # Add the uncovered neighbors of node1 and node2 in T1 and T2 respectively
    T1.update(uncovered_successors_G1)
    T2.update(uncovered_successors_G2)
    T1.discard(new_node1)
    T2.discard(new_node2)

    T1_tilde.difference_update(uncovered_successors_G1)
    T2_tilde.difference_update(uncovered_successors_G2)
    T1_tilde.discard(new_node1)
    T2_tilde.discard(new_node2)

    if not G1.is_directed():
        return

    uncovered_predecessors_G1 = {
        pred for pred in G1.pred[new_node1] if pred not in mapping
    }
    uncovered_predecessors_G2 = {
        pred for pred in G2.pred[new_node2] if pred not in reverse_mapping
    }

    T1_in.update(uncovered_predecessors_G1)
    T2_in.update(uncovered_predecessors_G2)
    T1_in.discard(new_node1)
    T2_in.discard(new_node2)

    T1_tilde.difference_update(uncovered_predecessors_G1)
    T2_tilde.difference_update(uncovered_predecessors_G2)
    T1_tilde.discard(new_node1)
    T2_tilde.discard(new_node2)


def _restore_Tinout(popped_node1, popped_node2, graph_params, state_params):
    """Restores the previous version of Ti/Ti_out when a node pair is deleted from the mapping.

    Parameters
    ----------
    popped_node1, popped_node2: Graph node
        The two nodes deleted from the mapping.

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
            Ti_out contains all the nodes from Gi, that are neither in the mapping nor in Ti
    """
    # If the node we want to remove from the mapping, has at least one covered neighbor, add it to T1.
    G1, G2, _, _, _, _, _ = graph_params
    (
        mapping,
        reverse_mapping,
        T1,
        T1_in,
        T1_tilde,
        T1_tilde_in,
        T2,
        T2_in,
        T2_tilde,
        T2_tilde_in,
    ) = state_params

    is_added = False
    for successor in G1[popped_node1]:
        if successor in mapping:
            # if a neighbor of the excluded node1 is in the mapping, keep node1 in T1
            is_added = True
            if not G1.is_directed():
                T1.add(popped_node1)
                continue
            T1_in.add(popped_node1)
        else:
            # check if its neighbor has another connection with a covered node. If not, only then exclude it from T1
            if G1.is_directed() and not any(
                pred in mapping for pred in G1.pred[successor]
            ):
                T1.discard(successor)

            if not any(succ in mapping for succ in G1[successor]):
                if G1.is_directed():
                    T1_in.discard(successor)
                else:
                    T1.discard(successor)

            if successor not in T1:
                if not G1.is_directed():
                    T1_tilde.add(successor)
                else:
                    if successor not in T1_in:
                        T1_tilde.add(successor)

    if G1.is_directed():
        for predecessor in G1.pred[popped_node1]:
            if predecessor in mapping:
                # if a neighbor of the excluded node1 is in the mapping, keep node1 in T1
                is_added = True
                T1.add(popped_node1)
            else:
                # check if its neighbor has another connection with a covered node. If not, only then exclude it from T1
                if not any(pred in mapping for pred in G1.pred[predecessor]):
                    T1.discard(predecessor)

                if not any(succ in mapping for succ in G1[predecessor]):
                    T1_in.discard(predecessor)

                if not (predecessor in T1 or predecessor in T1_in):
                    T1_tilde.add(predecessor)

    # Case where the node is not present in neither the mapping nor T1. By deffinition it should belong to T1_tilde
    if not is_added:
        T1_tilde.add(popped_node1)

    is_added = False
    for successor in G2[popped_node2]:
        if successor in reverse_mapping:
            is_added = True
            if not G2.is_directed():
                T2.add(popped_node2)
                continue
            T2_in.add(popped_node2)
        else:
            if G2.is_directed() and not any(
                pred in reverse_mapping for pred in G2.pred[successor]
            ):
                T2.discard(successor)

            if not any(succ in reverse_mapping for succ in G2[successor]):
                if G2.is_directed():
                    T2_in.discard(successor)
                else:
                    T2.discard(successor)

            if successor not in T2:
                if not G2.is_directed():
                    T2_tilde.add(successor)
                else:
                    if successor not in T2_in:
                        T2_tilde.add(successor)

    if G2.is_directed():
        for predecessor in G2.pred[popped_node2]:
            if predecessor in reverse_mapping:
                # if a neighbor of the excluded node1 is in the mapping, keep node1 in T1
                is_added = True
                T2.add(popped_node2)
            else:
                # check if its neighbor has another connection with a covered node. If not, only then exclude it from T1
                if not any(pred in reverse_mapping for pred in G2.pred[predecessor]):
                    T2.discard(predecessor)

                if not any(succ in reverse_mapping for succ in G2[predecessor]):
                    T2_in.discard(predecessor)

                if not (predecessor in T2 or predecessor in T2_in):
                    T2_tilde.add(predecessor)

    if not is_added:
        T2_tilde.add(popped_node2)
