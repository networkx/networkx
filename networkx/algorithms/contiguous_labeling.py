"""
An Implementation of the Contiguous Oriented Labeling Algorithm
Based on:
"Fair and Efficient Cake Division with Connected Pieces" by Xiaohui Bei and Warut Suksompong
https://arxiv.org/pdf/1910.14129.pdf

Programmer: Ghia sarhan
Date: 2025-05-16
"""

import networkx as nx
from typing import List, Tuple, Dict, Set, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def find_uv_to_make_bridgeless(G: nx.Graph) -> Optional[Tuple[Any, Any]]:
    """
    Find vertices u and v such that adding edge (u,v) makes the graph G bridgeless.
    """
    logger.info(
        f"Checking if graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges can be made bridgeless"
    )

    if not nx.has_bridges(G):
        logger.info("Graph is already bridgeless")
        return None

    bridges = list(nx.bridges(G))
    logger.info(f"Found {len(bridges)} bridges in the graph")

    nodes = list(G.nodes())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            u, v = nodes[i], nodes[j]
            if G.has_edge(u, v):
                continue

            G_temp = G.copy()
            G_temp.add_edge(u, v)

            if not nx.has_bridges(G_temp):
                logger.info(f"Adding edge ({u}, {v}) makes the graph bridgeless")
                return (u, v)

    logger.warning("Cannot make graph bridgeless by adding a single edge")
    return None


def contiguous_oriented_labeling(G: nx.Graph) -> Optional[List[Tuple[int, Any, Any]]]:
    """
    Create a contiguous oriented labeling for an almost bridgeless graph.
    """

    # --- Handle edge cases ---
    if G.number_of_nodes() == 0:
        logger.warning("Empty graph: returning None")
        return None

    if G.number_of_nodes() == 1:
        logger.warning("Single node, no edges: returning None")
        return None

    if G.number_of_edges() == 1:
        u, v = list(G.edges())[0]
        logger.info(f"Single edge ({u}, {v}): returning trivial labeling")
        return [(1, u, v)]
    # ------------------------

    logger.info("Starting contiguous oriented labeling algorithm")
    logger.info(f"Input graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    if find_uv_to_make_bridgeless(G) is None and nx.has_bridges(G):
        logger.error("Graph is not almost bridgeless")
        return None

    if not nx.is_connected(G):
        logger.error("Graph is not connected")
        return None

    H = G.copy()

    if not nx.has_bridges(G):
        first_edge = list(H.edges())[0]
        u, v = first_edge
        logger.info(f"Graph is bridgeless, choosing edge {first_edge} for first ear")
    else:
        edge = find_uv_to_make_bridgeless(G)
        if edge is None:
            return None
        u, v = edge
        logger.info(f"Graph has bridges, using vertices {u} and {v} for first ear")

    if nx.has_path(H, u, v):
        path = nx.shortest_path(H, u, v)
        logger.info(f"Found path from {u} to {v}: {path}")
    else:
        logger.error(f"No path exists from {u} to {v}")
        return None

    first_ear = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    logger.info(f"First ear: {first_ear}")

    ears = [first_ear]
    all_edges = first_ear.copy()
    used_vertices = set(path)

    for edge in first_ear:
        H.remove_edge(*edge)

    ear_count = 1
    while H.number_of_edges() > 0:
        found_ear = False
        for node1 in used_vertices:
            for node2 in list(H.neighbors(node1)):
                if node2 in used_vertices:
                    new_ear = [(node1, node2)]
                    ears.append(new_ear)
                    logger.info(f"Found ear #{ear_count + 1} (single edge): {new_ear}")

                    if node1 == u:
                        all_edges = new_ear + all_edges
                    else:
                        for i, (src, dst) in enumerate(all_edges):
                            if dst == node1:
                                all_edges = all_edges[: i + 1] + new_ear + all_edges[i + 1 :]
                                break
                        else:
                            all_edges.extend(new_ear)

                    H.remove_edge(node1, node2)
                    found_ear = True
                    ear_count += 1
                    break
            if found_ear:
                break

        if found_ear:
            continue

        for node1 in used_vertices:
            new_neighbors = [n for n in H.neighbors(node1) if n not in used_vertices]
            if new_neighbors:
                node2 = new_neighbors[0]
                current_ear = [(node1, node2)]
                H.remove_edge(node1, node2)
                current = node2
                used_vertices.add(node2)

                while True:
                    next_neighbors = [n for n in H.neighbors(current) if n not in used_vertices]
                    if not next_neighbors:
                        used_neighbors = [n for n in H.neighbors(current) if n in used_vertices and n != node1]
                        if used_neighbors:
                            node3 = used_neighbors[0]
                            current_ear.append((current, node3))
                            H.remove_edge(current, node3)
                        break

                    next_node = next_neighbors[0]
                    current_ear.append((current, next_node))
                    H.remove_edge(current, next_node)
                    used_vertices.add(next_node)
                    current = next_node

                ears.append(current_ear)
                logger.info(f"Found ear #{ear_count + 1} (path): {current_ear}")

                if node1 == u:
                    all_edges = current_ear + all_edges
                else:
                    for i, (src, dst) in enumerate(all_edges):
                        if dst == node1:
                            all_edges = all_edges[: i + 1] + current_ear + all_edges[i + 1 :]
                            break
                    else:
                        all_edges.extend(current_ear)

                found_ear = True
                ear_count += 1
                break

        if not found_ear:
            edge = list(H.edges())[0]
            H.remove_edge(*edge)
            ears.append([edge])
            all_edges.append(edge)
            used_vertices.update(edge)

    labeling = [(i + 1, src, dst) for i, (src, dst) in enumerate(all_edges)]
    logger.info(f"Created labeling with {len(labeling)} edges")

    if not verify_contiguous_labeling(G, labeling):
        logger.error("Contiguous labeling verification failed, using DFS fallback")
        return dfs_labeling(G)

    logger.info("Contiguous labeling completed successfully")
    return labeling


def dfs_labeling(G: nx.Graph) -> List[Tuple[int, Any, Any]]:
    """
    DFS fallback labeling.
    """
    visited_edges = set()
    labeling: List[Tuple[int, Any, Any]] = []
    label = 1

    def dfs(u):
        nonlocal label
        for v in G.neighbors(u):
            edge = (u, v)
            rev_edge = (v, u)
            if edge in visited_edges or rev_edge in visited_edges:
                continue
            visited_edges.add(edge)
            labeling.append((label, u, v))
            label += 1
            dfs(v)

    start_node = list(G.nodes())[0]
    dfs(start_node)
    return labeling


def verify_contiguous_labeling(G: nx.Graph, labeling: List[Tuple[int, Any, Any]]) -> bool:
    """
    Verify contiguous property.
    """
    if len(labeling) == 0:
        return True

    m = len(labeling)
    i_minus: Dict[int, Any] = {}
    i_plus: Dict[int, Any] = {}

    for label, from_node, to_node in labeling:
        i_minus[label] = from_node
        i_plus[label] = to_node

    for i in range(2, m + 1):
        subgraph = nx.Graph()
        for j in range(1, i):
            subgraph.add_edge(i_minus[j], i_plus[j])
        if subgraph.number_of_edges() > 0 and not nx.is_connected(subgraph):
            return False
        if i_minus[i] not in subgraph:
            return False

    for i in range(1, m):
        subgraph = nx.Graph()
        for j in range(i + 1, m + 1):
            subgraph.add_edge(i_minus[j], i_plus[j])
        if subgraph.number_of_edges() > 0 and not nx.is_connected(subgraph):
            return False
        if i_plus[i] not in subgraph:
            return False

    return True


def show_labeling(labeling: Optional[List[Tuple[int, Any, Any]]]) -> None:
    """
    Print a labeling in human-readable format.
    """
    if labeling is None:
        print("No labeling")
        return
    for label, i_minus, i_plus in labeling:
        print(f"Edge {label}: {i_minus}⁻ → {i_plus}⁺")


if __name__ == "__main__":
    print("===== Test 1: Cycle Graph =====")
    G1 = nx.cycle_graph(4)
    print(f"Is bridgeless: {not nx.has_bridges(G1)}")
    labeling1 = contiguous_oriented_labeling(G1)
    show_labeling(labeling1)
    if labeling1 is not None:
        print(f"Is contiguous: {verify_contiguous_labeling(G1, labeling1)}")
    print()

    print("===== Test 2: Path Graph =====")
    G2 = nx.path_graph(4)
    print(f"Is bridgeless: {not nx.has_bridges(G2)}")
    print(f"Is almost bridgeless: {find_uv_to_make_bridgeless(G2) is not None or not nx.has_bridges(G2)}")
    labeling2 = contiguous_oriented_labeling(G2)
    show_labeling(labeling2)
    if labeling2 is not None:
        print(f"Is contiguous: {verify_contiguous_labeling(G2, labeling2)}")
    print()

    print("===== Test 3: Triangle with Tail =====")
    G3 = nx.Graph()
    G3.add_edges_from([("A", "B"), ("B", "C"), ("C", "A"), ("A", "D")])
    print(f"Is bridgeless: {not nx.has_bridges(G3)}")
    labeling3 = contiguous_oriented_labeling(G3)
    show_labeling(labeling3)
    if labeling3 is not None:
        print(f"Is contiguous: {verify_contiguous_labeling(G3, labeling3)}")
    print()

    print("===== Test 4: Star graph =====")
    G4 = nx.Graph()
    G4.add_edges_from([("A", "B"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D")])
    print(f"Is bridgeless: {not nx.has_bridges(G4)}")
    labeling4 = contiguous_oriented_labeling(G4)
    show_labeling(labeling4)
    if labeling4 is not None:
        print(f"Is contiguous: {verify_contiguous_labeling(G4, labeling4)}")
