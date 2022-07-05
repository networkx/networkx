import random
import time
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms.isomorphism.VF2pp_helpers.feasibility import check_feasibility
from networkx.algorithms.isomorphism.VF2pp_helpers.node_ordering import matching_order
from networkx.algorithms.isomorphism.VF2pp_helpers.state import State, update_Tinout, restore_Tinout
from networkx.algorithms.isomorphism.VF2pp_helpers.candidates import find_candidates


def isomorphic_VF2pp(G1, G2, G1_labels, G2_labels, node_order):
    mapping, reverse_mapping = dict(), dict()
    T1, T2 = set(), set()
    T1_out, T2_out = set(G1.nodes()), set(G2.nodes())
    visited = set()

    starting_node = node_order.pop(0)
    candidates = find_candidates(G1, G2, G1_labels, G2_labels, starting_node, mapping, reverse_mapping)
    stack = [(starting_node, iter(candidates), node_order)]

    while stack:
        current_node, candidate_nodes, order = stack[-1]
        # print(f"Current: {current_node}, candidates: {find_candidates(G1, G2, G1_labels, G2_labels, current_node, mapping, reverse_mapping)}")

        try:
            candidate = next(candidate_nodes)
            # print(f"Candidate of {current_node}: {candidate}")

            if check_feasibility(current_node, candidate, G1, G2, G1_labels, G2_labels, mapping, reverse_mapping, T1,
                                 T1_out, T2, T2_out) and candidate not in visited:
                visited.add(candidate)
                # print(f"{current_node}-{candidate} feasible")

                # Update the mapping and Ti/Ti_out
                mapping.update({current_node: candidate})
                reverse_mapping.update({candidate: current_node})
                T1, T2, T1_out, T2_out = update_Tinout(G1, G2, T1, T2, T1_out, T2_out, current_node, candidate, mapping,
                                                       reverse_mapping)
                # print(f"m: {mapping}")

                # Feasibile pair found, extend mapping and descent to the DFS tree searching for another feasible pair
                next_order = [n for n in order]
                if len(next_order) == 0:
                    break

                next_node = next_order.pop(0)
                candidates = find_candidates(G1, G2, G1_labels, G2_labels, next_node, mapping, reverse_mapping)
                stack.append((next_node, iter(candidates), next_order))

        except StopIteration:
            # Restore the previous state of the algorithm
            stack.pop()
            if len(stack) == 0:
                break

            node1_to_pop, _, _ = stack[-1]
            node2_to_pop = mapping[node1_to_pop]
            mapping.pop(node1_to_pop)
            reverse_mapping.pop(node2_to_pop)
            visited.remove(node2_to_pop)  # todo: do we need this?
            # print(f"popping {node1_to_pop}-{node2_to_pop}")
            # node_order.insert(0, node1_to_pop)

            T1, T2, T1_out, T2_out = restore_Tinout(G1, G2, T1, T2, T1_out, T2_out, node1_to_pop, node2_to_pop, mapping,
                                                    reverse_mapping)

    if len(mapping) == G1.number_of_nodes():
        return mapping
    return False
