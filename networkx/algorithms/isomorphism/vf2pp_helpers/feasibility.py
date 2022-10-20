import networkx as nx


def _feasibility(node1, node2, graph_params, state_params):
    """Given a candidate pair of nodes u and v from G1 and G2 respectively, checks if it's feasible to extend the
    mapping, i.e. if u and v can be matched.

    Notes
    -----
    This function performs all the necessary checking by applying both consistency and cutting rules.

    Parameters
    ----------
    node1, node2: Graph node
        The candidate pair of nodes being checked for matching

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
    True if all checks are successful, False otherwise.
    """
    G1 = graph_params.G1

    if _cut_PT(node1, node2, graph_params, state_params):
        return False

    if G1.is_multigraph():
        if not _consistent_PT(node1, node2, graph_params, state_params):
            return False

    return True


def _cut_PT(u, v, graph_params, state_params):
    """Implements the cutting rules for the ISO problem.

    Parameters
    ----------
    u, v: Graph node
        The two candidate nodes being examined.

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

    Returns
    -------
    True if we should prune this branch, i.e. the node pair failed the cutting checks. False otherwise.
    """
    G1, G2, G1_labels, G2_labels, _, _, _ = graph_params
    (
        _,
        _,
        T1,
        T1_in,
        T1_tilde,
        _,
        T2,
        T2_in,
        T2_tilde,
        _,
    ) = state_params

    u_labels_predecessors, v_labels_predecessors = {}, {}
    if G1.is_directed():
        u_labels_predecessors = nx.utils.groups(
            {n1: G1_labels[n1] for n1 in G1.pred[u]}
        )
        v_labels_predecessors = nx.utils.groups(
            {n2: G2_labels[n2] for n2 in G2.pred[v]}
        )

        if set(u_labels_predecessors.keys()) != set(v_labels_predecessors.keys()):
            return True

    u_labels_successors = nx.utils.groups({n1: G1_labels[n1] for n1 in G1[u]})
    v_labels_successors = nx.utils.groups({n2: G2_labels[n2] for n2 in G2[v]})

    # if the neighbors of u, do not have the same labels as those of v, NOT feasible.
    if set(u_labels_successors.keys()) != set(v_labels_successors.keys()):
        return True

    for label, G1_nbh in u_labels_successors.items():
        G2_nbh = v_labels_successors[label]

        if G1.is_multigraph():
            # Check for every neighbor in the neighborhood, if u-nbr1 has same edges as v-nbr2
            u_nbrs_edges = sorted(G1.number_of_edges(u, x) for x in G1_nbh)
            v_nbrs_edges = sorted(G2.number_of_edges(v, x) for x in G2_nbh)
            if any(
                u_nbr_edges != v_nbr_edges
                for u_nbr_edges, v_nbr_edges in zip(u_nbrs_edges, v_nbrs_edges)
            ):
                return True

        if len(T1.intersection(G1_nbh)) != len(T2.intersection(G2_nbh)):
            return True
        if len(T1_tilde.intersection(G1_nbh)) != len(T2_tilde.intersection(G2_nbh)):
            return True
        if G1.is_directed() and len(T1_in.intersection(G1_nbh)) != len(
            T2_in.intersection(G2_nbh)
        ):
            return True

    if not G1.is_directed():
        return False

    for label, G1_pred in u_labels_predecessors.items():
        G2_pred = v_labels_predecessors[label]

        if G1.is_multigraph():
            # Check for every neighbor in the neighborhood, if u-nbr1 has same edges as v-nbr2
            u_pred_edges = sorted(G1.number_of_edges(u, x) for x in G1_pred)
            v_pred_edges = sorted(G2.number_of_edges(v, x) for x in G2_pred)
            if any(
                u_nbr_edges != v_nbr_edges
                for u_nbr_edges, v_nbr_edges in zip(u_pred_edges, v_pred_edges)
            ):
                return True

        if len(T1.intersection(G1_pred)) != len(T2.intersection(G2_pred)):
            return True
        if len(T1_tilde.intersection(G1_pred)) != len(T2_tilde.intersection(G2_pred)):
            return True
        if len(T1_in.intersection(G1_pred)) != len(T2_in.intersection(G2_pred)):
            return True

    return False


def _consistent_PT(u, v, graph_params, state_params):
    """Checks the consistency of extending the mapping using the current node pair.

    Parameters
    ----------
    u, v: Graph node
        The two candidate nodes being examined.

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
    True if the pair passes all the consistency checks successfully. False otherwise.
    """
    G1, G2 = graph_params.G1, graph_params.G2
    mapping, reverse_mapping = state_params.mapping, state_params.reverse_mapping

    for neighbor in G1[u]:
        if neighbor in mapping:
            if G1.number_of_edges(u, neighbor) != G2.number_of_edges(
                v, mapping[neighbor]
            ):
                return False

    for neighbor in G2[v]:
        if neighbor in reverse_mapping:
            if G1.number_of_edges(u, reverse_mapping[neighbor]) != G2.number_of_edges(
                v, neighbor
            ):
                return False

    if not G1.is_directed():
        return True

    for predecessor in G1.pred[u]:
        if predecessor in mapping:
            if G1.number_of_edges(u, predecessor) != G2.number_of_edges(
                v, mapping[predecessor]
            ):
                return False

    for predecessor in G2.pred[v]:
        if predecessor in reverse_mapping:
            if G1.number_of_edges(
                u, reverse_mapping[predecessor]
            ) != G2.number_of_edges(v, predecessor):
                return False

    return True
