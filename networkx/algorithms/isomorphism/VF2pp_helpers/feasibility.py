import networkx as nx
import collections


def check_feasibility(
    node1,
    node2,
    G1,
    G2,
    G1_labels,
    G2_labels,
    mapping,
    reverse_mapping,
    T1,
    T1_out,
    T2,
    T2_out,
    PT="ISO"
):
    """Given a candidate pair of nodes u and v from G1 and G2 respectively, checks if it's feasible to extend the
    mapping, i.e. if u and v can be matched.

    Notes
    -----
    This function performs all the necessary checking by applying both consistency and cutting rules.

    Parameters
    ----------
    node1,node2: int
        The two candidate nodes being checked.

    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.

    mapping: dict
        The mapping as extended so far. Maps nodes of G1 to nodes of G2.

    reverse_mapping: dict
        The reverse mapping as extended so far. Maps nodes from G2 to nodes of G1. It's basically "mapping" reversed.

    T1, T2: set
        Ti contains uncovered neighbors of covered nodes from Gi, i.e. nodes that are not in the mapping, but are
        neighbors of nodes that are.

    T1_out, T2_out: set
        Ti_out contains all the nodes from Gi, that are neither in the mapping nor in Ti.

    PT: string
        The problem type we are trying to solve. Values for PT are ("")

    Returns
    -------
    True if all checks are successful, False otherwise.
    """
    if G1.number_of_edges(node1, node1) != G2.number_of_edges(node2, node2):
        return False

    if cut_PT(
            G1,
            G2,
            G1_labels,
            G2_labels,
            node1,
            node2,
            T1,
            T1_out,
            T2,
            T2_out
    ):
        return False

    if not consistent_PT(G1, G2, node1, node2, mapping, reverse_mapping):
        return False

    return True


def cut_PT(
    G1, G2, G1_labels, G2_labels, u, v, T1, T1_out, T2, T2_out
):
    """Implements the cutting rules for the ISO problem.

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.

    u, v: int
        The two candidate nodes being examined.

    T1, T2: set
        Ti contains uncovered neighbors of covered nodes from Gi, i.e. nodes that are not in the mapping, but are
        neighbors of nodes that are.

    T1_out, T2_out: set
        Ti_out contains all the nodes from Gi, that are neither in the mapping nor in Ti.

    Returns
    -------
    True if we should prune this branch, i.e. the node pair failed the cutting checks. False otherwise.
    """
    u_neighbors_labels = {n1: G1_labels[n1] for n1 in G1[u]}
    u_labels_neighbors = collections.OrderedDict(
        sorted(nx.utils.groups(u_neighbors_labels).items())
    )

    v_neighbors_labels = {n2: G2_labels[n2] for n2 in G2[v]}
    v_labels_neighbors = collections.OrderedDict(
        sorted(nx.utils.groups(v_neighbors_labels).items())
    )
    # if the neighbors of u, do not have the same labels as those of v, NOT feasible.
    if set(u_labels_neighbors.keys()) != set(v_labels_neighbors.keys()):
        return True

    for labeled_nh1, labeled_nh2 in zip(
        u_labels_neighbors.values(), v_labels_neighbors.values()
    ):
        if len(T1.intersection(labeled_nh1)) != len(
            T2.intersection(labeled_nh2)
        ) or len(T1_out.intersection(labeled_nh1)) != len(
            T2_out.intersection(labeled_nh2)
        ):
            return True

    return False


def consistent_PT(G1, G2, u, v, mapping, reverse_mapping):
    """Checks the consistency of extending the mapping using the current node pair.

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    u, v: int
        The two candidate nodes being examined.

    mapping: dict
        The mapping as extended so far. Maps nodes of G1 to nodes of G2.

    reverse_mapping: dict
        The reverse mapping as extended so far. Maps nodes from G2 to nodes of G1. It's basically "mapping" reversed.

    Returns
    -------
    True if the pair passes all the consistency checks successfully. False otherwise.
    """
    # Check if every covered neighbor of u is mapped to every covered neighbor of v
    # Also check if there is the same number of edges between the candidates and their neighbors
    for neighbor in G1[u]:
        if neighbor in mapping:
            if mapping[neighbor] not in G2[v]:
                return False
            elif G1.number_of_edges(u, neighbor) != G2.number_of_edges(
                    v, mapping[neighbor]
            ):
                return False

    for neighbor in G2[v]:
        if neighbor in reverse_mapping:
            if reverse_mapping[neighbor] not in G1[u]:
                return False
            elif G1.number_of_edges(
                    u, reverse_mapping[neighbor]
            ) != G2.number_of_edges(v, neighbor):
                return False
    return True


