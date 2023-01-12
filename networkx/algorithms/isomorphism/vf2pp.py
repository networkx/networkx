"""
***************
VF2++ Algorithm
***************

An implementation of the VF2++ algorithm for Graph Isomorphism testing.

The simplest interface to use this module is to call:

`vf2pp_is_isomorphic`: to check whether two graphs are isomorphic.
`vf2pp_isomorphism`: to obtain the node mapping between two graphs,
in case they are isomorphic.
`vf2pp_all_isomorphisms`: to generate all possible mappings between two graphs,
if isomorphic.

Introduction
------------
The VF2++ algorithm, follows a similar logic to that of VF2, while also
introducing new easy-to-check cutting rules and determining the optimal access
order of nodes. It is also implemented in a non-recursive manner, which saves
both time and space, when compared to its previous counterpart.

The optimal node ordering is obtained after taking into consideration both the
degree but also the label rarity of each node.
This way we place the nodes that are more likely to match, first in the order,
thus examining the most promising branches in the beginning.
The rules also consider node labels, making it easier to prune unfruitful
branches early in the process.

Examples
--------

Suppose G1 and G2 are Isomorphic Graphs. Verification is as follows:

Without node labels:

>>> import networkx as nx
>>> G1 = nx.path_graph(4)
>>> G2 = nx.path_graph(4)
>>> nx.vf2pp_is_isomorphic(G1, G2, node_label=None)
True
>>> nx.vf2pp_isomorphism(G1, G2, node_label=None)
{1: 1, 2: 2, 0: 0, 3: 3}

With node labels:

>>> G1 = nx.path_graph(4)
>>> G2 = nx.path_graph(4)
>>> mapped = {1: 1, 2: 2, 3: 3, 0: 0}
>>> nx.set_node_attributes(G1, dict(zip(G1, ["blue", "red", "green", "yellow"])), "label")
>>> nx.set_node_attributes(G2, dict(zip([mapped[u] for u in G1], ["blue", "red", "green", "yellow"])), "label")
>>> nx.vf2pp_is_isomorphic(G1, G2, node_label="label")
True
>>> nx.vf2pp_isomorphism(G1, G2, node_label="label")
{1: 1, 2: 2, 0: 0, 3: 3}

"""
import collections

import networkx as nx

__all__ = ["vf2pp_isomorphism", "vf2pp_is_isomorphic", "vf2pp_all_isomorphisms"]

_GraphParameters = collections.namedtuple(
    "_GraphParameters",
    [
        "G1",
        "G2",
        "G1_degree",
        "G2_degree",
        "G1_labels",
        "G2_labels",
        "G1_by_label",
        "G2_by_label",
        "G2_by_degree",
    ],
)

_StateParameters = collections.namedtuple(
    "_StateParameters",
    [
        "mapping",
        "reverse_mapping",
        "T1",
        "T1_in",
        "T1_tilde",
        "T1_tilde_in",
        "T2",
        "T2_in",
        "T2_tilde",
        "T2_tilde_in",
    ],
)


def vf2pp_isomorphism(G1, G2, node_label=None, default_label=None):
    """Return an isomorphic mapping between `G1` and `G2` if it exists.

    Parameters
    ----------
    G1, G2 : NetworkX graph
        The two graphs to check for isomorphism.

    node_label : str (default=None)
        The name of the node attribute to be used when comparing nodes.
        The default is `None`, meaning node attributes are not considered
        in the comparison. Any node that doesn't have the `node_label`
        attribute is asssigned the label given by `default_label` instead.

    default_label : scalar (default=None)
        Default label value used when no node attribute is found for a node.

    Returns
    -------
    dict or None
        Isomorphism between the nodes in `G1` and `G2`.
        `None` if the two graphs are not isomorphic.
    """
    try:
        mapping = next(vf2pp_all_isomorphisms(G1, G2, node_label, default_label))
        return mapping
    except StopIteration:
        return None


def vf2pp_is_isomorphic(G1, G2, node_label=None, default_label=None):
    """Examines whether G1 and G2 are isomorphic.

    Parameters
    ----------
    G1, G2 : NetworkX graph
        The two graphs to check for isomorphism.

    node_label : str (default=None)
        The name of the node attribute to be used when comparing nodes.
        The default is `None`, meaning node attributes are not considered
        in the comparison. Any node that doesn't have the `node_label`
        attribute is asssigned the label given by `default_label` instead.

    default_label : scalar (default=None)
        Default label value used when no node attribute is found for a node.

    Returns
    -------
    bool
        True if the two graphs are isomorphic. False otherwise.
    """
    if vf2pp_isomorphism(G1, G2, node_label, default_label) is not None:
        return True
    return False


def vf2pp_all_isomorphisms(G1, G2, node_label=None, default_label=None):
    """Yields all the possible mappings between G1 and G2.

    Parameters
    ----------
    G1, G2 : NetworkX graph
        The two graphs to check for isomorphism.

    node_label : str (default=None)
        The name of the node attribute to be used when comparing nodes.
        The default is `None`, meaning node attributes are not considered
        in the comparison. Any node that doesn't have the `node_label`
        attribute is asssigned the label given by `default_label` instead.

    default_label : scalar (default=None)
        Default label value used when no node attribute is found for a node.

    Yields
    ------
    dict
        Isomorphism between the nodes in `G1` and `G2`.
    """
    N1, N2 = len(G1), len(G2)
    if N1 != N2:
        return "G1 and G2 have different number of nodes, so no isomorphism"
    if N1 == 0:
        return "G1 and G2 have no nodes, so no isomorphism"

    # Initialize parameters and cache information about degree and labels
    gparams, sparams = _initialize_parameters(G1, G2, node_label, default_label)

    # Check that degree sequences match
    if sorted(gparams.G1_degree.values()) != sorted(gparams.G2_degree.values()):
        return "G1 and G2 have different degree sequences, so no isomorphism"

    # Check if G1 and G2 have the same number of nodes per label
    for label, nodes in gparams.G2_by_label.items():
        if label not in gparams.G1_by_label:
            return f"Label {label} in G2 is not in G1, so no isomorphism"
        if len(gparams.G1_by_label[label]) != len(nodes):
            return f"Number of nodes labeled {label} differs, so no isomorphism"

    # Calculate the optimal node ordering
    node_order = _matching_order(gparams)

    # set convenience names
    if G1.is_directed():
        find_candidates = _find_candidates_Di
        restore_Tinout = _restore_Tinout_Di
    else:
        find_candidates = _find_candidates
        restore_Tinout = _restore_Tinout
    mapping = sparams.mapping
    reverse_mapping = sparams.reverse_mapping

    # Initialize the stack
    current_node = node_order[0]
    candidates = iter(find_candidates(current_node, gparams, sparams))
    stack = [(current_node, candidates)]
    # Index of the next node from the order, currently being examined
    matching_node = 1

    while stack:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)
        except StopIteration:
            # If no remaining candidates, return to a previous state, and follow another branch
            stack.pop()
            matching_node -= 1
            if stack:
                # Pop the previously added u-v pair, and look for a different candidate _v for u
                popped_node1, _ = stack[-1]
                popped_node2 = mapping[popped_node1]
                mapping.pop(popped_node1)
                reverse_mapping.pop(popped_node2)
                restore_Tinout(popped_node1, popped_node2, gparams, sparams)
            continue

        if _feasibility(current_node, candidate, gparams, sparams):
            # Terminate if mapping is extended to its full
            if len(mapping) == G2.number_of_nodes() - 1:
                cp_mapping = mapping.copy()
                cp_mapping[current_node] = candidate
                yield cp_mapping
                continue

            # Feasibility rules pass, so extend the mapping and update the parameters
            mapping[current_node] = candidate
            reverse_mapping[candidate] = current_node
            _update_Tinout(current_node, candidate, gparams, sparams)
            # Append the next node and its candidates to the stack
            current_node = node_order[matching_node]
            cands = iter(find_candidates(current_node, gparams, sparams))
            stack.append((current_node, cands))
            matching_node += 1


# TODO: correct and unify the namedtuple descriptions in the doc_strings
def _initialize_parameters(G1, G2, node_label=None, default_label=-1):
    """Initializes all the necessary parameters for VF2++

    Parameters
    ----------
    G1, G2 : NetworkX graph
        The two graphs to check for isomorphism or monomorphism

    node_label : str (default=None)
        The name of the node attribute to be used when comparing nodes.
        The default is `None`, meaning node attributes are not considered
        in the comparison. Any node that doesn't have the `node_label`
        attribute is asssigned the label given by `default_label` instead.

    default_label : scalar (default=None)
        Default label value used when no node attribute is found for a node.

    Returns
    -------
    graph_params: namedtuple
        Contains all the Graph-related parameters:

        G1, G2 : graphs
        G1_labels, G2_labels : dict

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
            The map as extended so far. Maps nodes of G1 to nodes of G2

    """
    G1_labels = dict(G1.nodes(data=node_label, default=default_label))
    G2_labels = dict(G2.nodes(data=node_label, default=default_label))

    # Create the degree dicts based on graph type
    if G1.is_directed():
        G1_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(G1.in_degree, G1.out_degree)
        }
        G2_degree = {
            n: (in_degree, out_degree)
            for (n, in_degree), (_, out_degree) in zip(G2.in_degree, G2.out_degree)
        }
    else:
        G1_degree = dict(G1.degree)
        G2_degree = dict(G2.degree)

    graph_params = _GraphParameters(
        G1,
        G2,
        G1_degree,
        G2_degree,
        G1_labels,
        G2_labels,
        nx.utils.groups(G1_labels),  # G1_by_label,
        nx.utils.groups(G2_labels),  # G2_by_label,
        nx.utils.groups(G2_degree),  # G2_by_degree,
    )

    state_params = _StateParameters(
        {},  # mapping
        {},  # reverse_mapping
        set(),  # T1,
        set(),  # T1_in,
        set(G1),  # T1_tilde,
        set(),  # T1_tilde_in,
        set(),  # T2,
        set(),  # T2_in,
        set(G2),  # T2_tilde,
        set(),  # T2_tilde_in,
    )

    return graph_params, state_params


def _matching_order(graph_params):
    """The node ordering as introduced in VF2++.

    Notes
    -----
    Taking into account the structure of the Graph and the node labeling, the nodes are placed in an order such that,
    most of the unfruitful/infeasible branches of the search space can be pruned on high levels, significantly
    decreasing the number of visited states. The premise is that, the algorithm will be able to recognize
    inconsistencies early, proceeding to go deep into the search tree only if it's needed.

    Parameters
    ----------
    graph_params: namedtuple
        Contains:

            G1,G2: NetworkX Graph or MultiGraph instances.
                The two graphs to check for isomorphism or monomorphism.

            G1_labels,G2_labels: dict
                The label of every node in G1 and G2 respectively.

    Returns
    -------
    node_order: list
        The ordering of the nodes.
    """
    G1, G2, G1_degree, _, G1_labels, _, _, nodes_of_G2Labels, _ = graph_params
    if not G1 and not G2:
        return {}

    if G1.is_directed():
        G1 = G1.to_undirected(as_view=True)

    V1_unordered = set(G1)
    label_rarity = {label: len(nodes) for label, nodes in nodes_of_G2Labels.items()}
    used_degrees = {node: 0 for node in G1}
    node_order = []

    while V1_unordered:
        max_rarity = min(label_rarity[G1_labels[x]] for x in V1_unordered)
        rarest_nodes = [
            n for n in V1_unordered if label_rarity[G1_labels[n]] == max_rarity
        ]
        max_node = max(rarest_nodes, key=G1.degree)

        for dlevel_nodes in nx.bfs_layers(G1, max_node):
            nodes_to_add = dlevel_nodes.copy()
            while nodes_to_add:
                max_used_degree = max(used_degrees[n] for n in nodes_to_add)
                max_used_degree_nodes = [
                    n for n in nodes_to_add if used_degrees[n] == max_used_degree
                ]
                max_degree = max(G1_degree[n] for n in max_used_degree_nodes)
                max_degree_nodes = [
                    n for n in max_used_degree_nodes if G1_degree[n] == max_degree
                ]
                next_node = min(
                    max_degree_nodes, key=lambda x: label_rarity[G1_labels[x]]
                )

                node_order.append(next_node)
                for node in G1.neighbors(next_node):
                    used_degrees[node] += 1

                nodes_to_add.remove(next_node)
                label_rarity[G1_labels[next_node]] -= 1
                V1_unordered.discard(next_node)

    return node_order


def _find_candidates(u, graph_params, state_params):
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
    G1, G2, G1_degree, _, G1_labels, _, _, G2_by_label, G2_by_degree = graph_params
    mapping, reverse_mapping, _, _, _, _, _, _, T2_tilde, _ = state_params

    covered_neighbors = [nbr for nbr in G1[u] if nbr in mapping]
    if not covered_neighbors:
        candidates = set(G2_by_label[G1_labels[u]])
        candidates.intersection_update(G2_by_degree[G1_degree[u]])
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
    common_nodes.intersection_update(G2_by_degree[G1_degree[u]])
    common_nodes.intersection_update(G2_by_label[G1_labels[u]])
    if G1.is_multigraph():
        common_nodes.difference_update(
            {
                node
                for node in common_nodes
                if G1.number_of_edges(u, u) != G2.number_of_edges(node, node)
            }
        )
    return common_nodes


def _find_candidates_Di(u, graph_params, state_params):
    G1, G2, G1_degree, _, G1_labels, _, _, G2_by_label, G2_by_degree = graph_params
    mapping, reverse_mapping, _, _, _, _, _, _, T2_tilde, _ = state_params

    covered_successors = [succ for succ in G1[u] if succ in mapping]
    covered_predecessors = [pred for pred in G1.pred[u] if pred in mapping]

    if not (covered_successors or covered_predecessors):
        candidates = set(G2_by_label[G1_labels[u]])
        candidates.intersection_update(G2_by_degree[G1_degree[u]])
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
    common_nodes.intersection_update(G2_by_degree[G1_degree[u]])
    common_nodes.intersection_update(G2_by_label[G1_labels[u]])
    if G1.is_multigraph():
        common_nodes.difference_update(
            {
                node
                for node in common_nodes
                if G1.number_of_edges(u, u) != G2.number_of_edges(node, node)
            }
        )
    return common_nodes


def _feasibility(node1, node2, graph_params, state_params):
    """Check if a candidate pair of nodes can be matched

    node1 and node2 must be from G1 and G2 respectively.
    checks if it's feasible to extend the mapping using node1 -> node2.

    Notes
    -----
    This function applies both consistency and cutting rules.

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
    if _cut_PT(node1, node2, graph_params, state_params):
        return False

    if graph_params.G1.is_multigraph():
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
    G1, G2, _, _, G1_labels, G2_labels, _, _, _ = graph_params
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
    G1, G2 = graph_params.G1, graph_params.G2
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
    G1, G2 = graph_params.G1, graph_params.G2
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
    for neighbor in G1[popped_node1]:
        if neighbor in mapping:
            # if a neighbor of popped_node1 is in the mapping, keep popped_node1 in T1
            is_added = True
            T1.add(popped_node1)
        else:
            # check if neighbor connects with a covered node. If not, exclude it from T1
            if any(nbr in mapping for nbr in G1[neighbor]):
                continue
            T1.discard(neighbor)
            T1_tilde.add(neighbor)

    # If popped_node1 not present in the mapping nor T1, put into T1_tilde
    if not is_added:
        T1_tilde.add(popped_node1)

    is_added = False
    for neighbor in G2[popped_node2]:
        if neighbor in reverse_mapping:
            is_added = True
            T2.add(popped_node2)
        else:
            if any(nbr in reverse_mapping for nbr in G2[neighbor]):
                continue
            T2.discard(neighbor)
            T2_tilde.add(neighbor)

    if not is_added:
        T2_tilde.add(popped_node2)


# TODO:  reuse the dup loops in restore_Tinout. Maybe handle DiGraph and Graph too.
def _restore_Tinout_Di(popped_node1, popped_node2, graph_params, state_params):
    G1, G2 = graph_params.G1, graph_params.G2
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
            # if a neighbor of popped_node1 is in the mapping, keep popped_node1 in T1
            is_added = True
            T1_in.add(popped_node1)
        else:
            # check if neighbor connects with a covered node. If not, exclude it from T1
            if not any(pred in mapping for pred in G1.pred[successor]):
                T1.discard(successor)

            if not any(succ in mapping for succ in G1[successor]):
                T1_in.discard(successor)

            if not (successor in T1 or successor in T1_in):
                T1_tilde.add(successor)

    for predecessor in G1.pred[popped_node1]:
        if predecessor in mapping:
            # if a neighbor of popped_node1 is in the mapping, keep popped_node1 in T1
            is_added = True
            T1.add(popped_node1)
        else:
            # check if neighbor connects with a covered node. If not, exclude it from T1
            if not any(pred in mapping for pred in G1.pred[predecessor]):
                T1.discard(predecessor)

            if not any(succ in mapping for succ in G1[predecessor]):
                T1_in.discard(predecessor)

            if not (predecessor in T1 or predecessor in T1_in):
                T1_tilde.add(predecessor)

    # If popped_node1 not present in the mapping nor T1, put into T1_tilde
    if not is_added:
        T1_tilde.add(popped_node1)

    is_added = False
    for successor in G2[popped_node2]:
        if successor in reverse_mapping:
            is_added = True
            T2_in.add(popped_node2)
        else:
            if not any(pred in reverse_mapping for pred in G2.pred[successor]):
                T2.discard(successor)

            if not any(succ in reverse_mapping for succ in G2[successor]):
                T2_in.discard(successor)

            if not (successor in T2 or successor in T2_in):
                T2_tilde.add(successor)

    for predecessor in G2.pred[popped_node2]:
        if predecessor in reverse_mapping:
            is_added = True
            T2.add(popped_node2)
        else:
            if not any(pred in reverse_mapping for pred in G2.pred[predecessor]):
                T2.discard(predecessor)

            if not any(succ in reverse_mapping for succ in G2[predecessor]):
                T2_in.discard(predecessor)

            if not (predecessor in T2 or predecessor in T2_in):
                T2_tilde.add(predecessor)

    if not is_added:
        T2_tilde.add(popped_node2)
