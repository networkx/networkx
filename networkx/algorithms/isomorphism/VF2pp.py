import collections

import networkx as nx
from networkx.algorithms.isomorphism.VF2pp_helpers.candidates import find_candidates
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.node_ordering import matching_order
from networkx.algorithms.isomorphism.VF2pp_helpers.state import (
    restore_state,
    update_state,
)


def VF2pp(G1, G2, G1_labels, G2_labels):
    try:
        mapping = next(VF2pp_solver(G1, G2, G1_labels, G2_labels))
        return mapping
    except StopIteration:
        return None


def VF2pp_solver(G1, G2, G1_labels, G2_labels):
    """Implementation of the VF2++ algorithm.

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.

    Returns
    -------
    Node mapping, if the two graphs are isomorphic. None otherwise.
    """
    if not G1 and not G2:
        return False
    if not precheck(G1, G2, G1_labels, G2_labels):
        return False

    graph_params, state_params, node_order, stack = initialize_VF2pp(
        G1, G2, G1_labels, G2_labels
    )
    matching_node = 1
    mapping = state_params.mapping

    while stack:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)
        except StopIteration:
            stack.pop()
            matching_node -= 1
            if stack:
                restore_state(stack, graph_params, state_params)
            continue

        if feasibility(current_node, candidate, graph_params, state_params):
            if len(mapping) == G2.number_of_nodes() - 1:
                mapping.update({current_node: candidate})
                yield state_params.mapping

            update_state(
                current_node,
                candidate,
                matching_node,
                node_order,
                stack,
                graph_params,
                state_params,
            )
            matching_node += 1


def precheck(G1, G2, G1_labels, G2_labels):
    """Checks if all the pre-requisites are satisfied before calling the isomorphism solver.

    Notes
    -----
    Before trying to create the mapping between the nodes of the two graphs, we must check if:
    1. The two graphs have equal number of nodes
    2. The degree sequences in the two graphs are identical
    3. The two graphs have the same label distribution. For example, if G1 has orange nodes but G2 doesn't, there's no
    point in proceeding to create a mapping.

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.
    """
    if G1.order() != G2.order():
        return False
    if sorted(d for n, d in G1.degree()) != sorted(d for n, d in G2.degree()):
        return False

    G1_nodes_per_label = {
        label: len(nodes) for label, nodes in nx.utils.groups(G1_labels).items()
    }

    if any(
        label not in G1_nodes_per_label or G1_nodes_per_label[label] != len(nodes)
        for label, nodes in nx.utils.groups(G2_labels).items()
    ):
        return False

    return True


def initialize_VF2pp(G1, G2, G1_labels, G2_labels):
    """Initializes all the necessary parameters for VF2++

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively

    Returns
    -------
    graph_params: namedtuple
        Contains all the Graph-related parameters:

        G1,G2
        G1_labels,G2_labels: dict

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
    """
    GraphParameters = collections.namedtuple(
        "GraphParameters", ["G1", "G2", "G1_labels", "G2_labels"]
    )
    StateParameters = collections.namedtuple(
        "StateParameters",
        ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
    )

    graph_params = GraphParameters(G1, G2, G1_labels, G2_labels)
    state_params = StateParameters(
        dict(), dict(), set(), set(G1.nodes()), set(), set(G2.nodes())
    )

    node_order = matching_order(G1, G2, G1_labels, G2_labels)

    starting_node = node_order[0]
    candidates = find_candidates(starting_node, graph_params, state_params)
    stack = [(starting_node, iter(candidates))]

    return graph_params, state_params, node_order, stack


def prepare_next(stack, node_order, state_params):
    """Sets VF2++ after yielding the first mapping, so it can continue producing different mappings.
    stack: list
        Stack of the DFS, containing a node and its candidates

    node_order: list
        Contains the ordered nodes of G1, as obtained by the preprocessing

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
    """
    entering_node, _ = stack.pop()
    node_order.appendleft(entering_node)
    popped_node1, _ = stack[-1]
    popped_node2 = state_params.mapping[popped_node1]
    state_params.mapping.pop(popped_node1)
    state_params.reverse_mapping.pop(popped_node2)
