import random
import time
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import check_feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.state import update_Tinout, restore_Tinout
from networkx.algorithms.isomorphism.VF2pp_helpers.candidates import find_candidates


def isomorphic_VF2pp(G1, G2, G1_labels, G2_labels, node_order):
    mapping, reverse_mapping = dict(), dict()
    T1, T2 = set(), set()
    T1_out, T2_out = set(G1.nodes()), set(G2.nodes())
    visited = set()
    # todo: add unit tests
    starting_node = node_order.pop(0)  # todo: examine if we can keep track of the node using a pointer
    candidates = find_candidates(G1, G2, G1_labels, G2_labels, starting_node, mapping, reverse_mapping)
    stack = [(starting_node, iter(candidates))]

    while True:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)
            if candidate not in visited and check_feasibility(current_node, candidate, G1, G2, G1_labels, G2_labels,
                                                              mapping, reverse_mapping, T1, T1_out, T2, T2_out):
                visited.add(candidate)

                # Update the mapping and Ti/Ti_out
                mapping.update({current_node: candidate})
                reverse_mapping.update({candidate: current_node})
                T1, T2, T1_out, T2_out = update_Tinout(G1, G2, T1, T2, T1_out, T2_out, current_node, candidate, mapping,
                                                       reverse_mapping)
                # Feasibile pair found, extend mapping and descent to the DFS tree searching for another feasible pair
                if not node_order:
                    break

                next_node = node_order.pop(0)
                candidates = find_candidates(G1, G2, G1_labels, G2_labels, next_node, mapping, reverse_mapping)
                stack.append((next_node, iter(candidates)))

        except StopIteration:
            # Restore the previous state of the algorithm
            entering_node, _ = stack.pop()  # The node to be returned to the ordering
            node_order.insert(0, entering_node)  # todo: replace with collections.deque
            if not stack:
                break

            popped_node1, _ = stack[-1]
            popped_node2 = mapping[popped_node1]
            mapping.pop(popped_node1)
            reverse_mapping.pop(popped_node2)
            visited.remove(popped_node2)

            T1, T2, T1_out, T2_out = restore_Tinout(G1, G2, T1, T2, T1_out, T2_out, popped_node1, popped_node2, mapping,
                                                    reverse_mapping)

    if len(mapping) == G1.number_of_nodes():
        return mapping
    return False
