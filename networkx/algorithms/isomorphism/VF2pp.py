import collections

import networkx as nx
from networkx.algorithms.isomorphism.VF2pp_helpers.candidates import find_candidates
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.node_ordering import matching_order
from networkx.algorithms.isomorphism.VF2pp_helpers.state import (
    restore_Tinout,
    update_Tinout,
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

    mapping, reverse_mapping = dict(), dict()
    T1, T2 = set(), set()
    T1_out, T2_out = set(G1.nodes()), set(G2.nodes())
    visited = set()

    node_order = matching_order(G1, G2, G1_labels, G2_labels)
    node_order = collections.deque(node_order)

    starting_node = node_order.popleft()
    candidates = find_candidates(
        G1, G2, G1_labels, G2_labels, starting_node, mapping, reverse_mapping
    )
    stack = [(starting_node, iter(candidates))]

    while True:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)
            if candidate not in visited and feasibility(
                current_node,
                candidate,
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
            ):
                visited.add(candidate)

                # Update the mapping and Ti/Ti_out
                mapping.update({current_node: candidate})
                reverse_mapping.update({candidate: current_node})
                update_Tinout(
                    G1,
                    G2,
                    T1,
                    T2,
                    T1_out,
                    T2_out,
                    current_node,
                    candidate,
                    mapping,
                    reverse_mapping,
                )
                # Feasibile pair found, extend mapping and descent to the DFS tree searching for another feasible pair
                if not node_order:
                    break

                next_node = node_order.popleft()
                candidates = find_candidates(
                    G1, G2, G1_labels, G2_labels, next_node, mapping, reverse_mapping
                )
                stack.append((next_node, iter(candidates)))

        except StopIteration:
            # Restore the previous state of the algorithm
            entering_node, _ = stack.pop()  # The node to be returned to the ordering
            node_order.appendleft(entering_node)
            if not stack:
                break

            popped_node1, _ = stack[-1]
            popped_node2 = mapping[popped_node1]
            mapping.pop(popped_node1)
            reverse_mapping.pop(popped_node2)
            visited.remove(popped_node2)

            restore_Tinout(
                G1,
                G2,
                T1,
                T2,
                T1_out,
                T2_out,
                popped_node1,
                popped_node2,
                mapping,
                reverse_mapping,
            )

    if len(mapping) == G1.number_of_nodes():
        return True, mapping
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
