import collections

import networkx as nx
from networkx.algorithms.isomorphism.VF2pp_helpers.candidates import find_candidates
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.node_ordering import matching_order
from networkx.algorithms.isomorphism.VF2pp_helpers.state import (
    restore_state,
    update_state,
)


def isomorphic_VF2pp(G1, G2, G1_labels, G2_labels):
    """Implementation of the VF2++ algorithm.

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.

    Returns
    -------
    True and the node mapping, if the two graphs are isomorphic. False and None otherwise.
    """
    if not G1 and not G2:
        return True, {}
    if not precheck(G1, G2, G1_labels, G2_labels):
        return False, None

    visited = set()
    graph_params, state_params, node_order, stack = initialize_VF2pp(
        G1, G2, G1_labels, G2_labels
    )

    while True:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)
            if candidate not in visited and feasibility(
                current_node, candidate, graph_params, state_params
            ):
                visited.add(candidate)
                update_state(current_node, candidate, graph_params, state_params)

                if not node_order:
                    break

                next_node = node_order.popleft()
                candidates = find_candidates(next_node, graph_params, state_params)
                stack.append((next_node, iter(candidates)))

        except StopIteration:
            # Restore the previous state of the algorithm
            entering_node, _ = stack.pop()  # The node to be returned to the ordering
            node_order.appendleft(entering_node)
            if not stack:
                break

            restore_state(stack, visited, graph_params, state_params)

    if len(state_params.mapping) == G1.number_of_nodes():
        return True, state_params.mapping
    return False, None


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

    nodes_per_label1 = {
        label: len(nodes) for label, nodes in nx.utils.groups(G1_labels).items()
    }
    nodes_per_label2 = {
        label: len(nodes) for label, nodes in nx.utils.groups(G2_labels).items()
    }

    if nodes_per_label1 != nodes_per_label2:
        return False

    return True


def initialize_VF2pp(G1, G2, G1_labels, G2_labels):
    mapping, reverse_mapping = dict(), dict()
    T1, T2 = set(), set()
    T1_out, T2_out = set(G1.nodes()), set(G2.nodes())

    GraphParameters = collections.namedtuple(
        "GraphParameters", ["G1", "G2", "G1_labels", "G2_labels"]
    )
    StateParameters = collections.namedtuple(
        "StateParameters",
        ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
    )

    graph_params = GraphParameters(G1, G2, G1_labels, G2_labels)
    state_params = StateParameters(mapping, reverse_mapping, T1, T1_out, T2, T2_out)

    node_order = matching_order(G1, G2, G1_labels, G2_labels)
    node_order = collections.deque(node_order)

    starting_node = node_order.popleft()
    candidates = find_candidates(starting_node, graph_params, state_params)
    stack = [(starting_node, iter(candidates))]

    return graph_params, state_params, node_order, stack
