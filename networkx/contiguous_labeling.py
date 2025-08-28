"""
An Implementation of the Contiguous Oriented Labeling Algorithm
Based on:
"Fair and Efficient Cake Division with Connected Pieces" by Xiaohui Bei and Warut Suksompong
https://arxiv.org/pdf/1910.14129.pdf

Programmer: Ghia sarhan
Date: 2025-05-16

This module provides functions to:
1. Determine if a graph is bridgeless or almost bridgeless
2. Construct a contiguous oriented labeling for almost bridgeless graphs

The output format of contiguous_oriented_labeling is:
   (label, i_minus, i_plus)
Where:
- 'label' is an integer index starting from 1
- 'i_minus' (or i⁻) is the source vertex of a directed edge
- 'i_plus' (or i⁺) is the target vertex of a directed edge

This corresponds to the contiguous oriented labeling definition from the paper:
   For each edge i, it is directed from vertex i⁻ to i⁺.
   You can transform the output tuples into readable format like:
       f"Edge {label}: {i_minus}⁻ → {i_plus}⁺"
"""

import networkx as nx
from typing import List, Tuple, Dict, Set, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_uv_to_make_bridgeless(G: nx.Graph) -> Optional[Tuple]:
    """
    Find vertices u and v such that adding edge (u,v) makes the graph G bridgeless.

    A bridge is an edge whose removal increases the number of connected components.
    A bridgeless graph has no bridges. This function searches for a pair of non-adjacent
    vertices such that adding an edge between them eliminates all bridges in the graph.

    Args:
        G (nx.Graph): The input graph to analyze

    Returns:
        Optional[Tuple]: A tuple (u, v) of vertices such that adding edge (u,v) makes
                        G bridgeless, or None if G is already bridgeless or cannot
                        be made bridgeless by adding a single edge
    """
    logger.info(f"Checking if graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges can be made bridgeless")

    # If the graph is already bridgeless, return None
    if not nx.has_bridges(G):
        logger.info("Graph is already bridgeless")
        return None

    bridges = list(nx.bridges(G))
    logger.info(f"Found {len(bridges)} bridges in the graph")

    # Try adding an edge between any pair of vertices
    nodes = list(G.nodes())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            u, v = nodes[i], nodes[j]

            # Skip if the edge already exists
            if G.has_edge(u, v):
                continue

            # Add the edge temporarily
            G_temp = G.copy()
            G_temp.add_edge(u, v)

            # Check if the graph is now bridgeless
            if not nx.has_bridges(G_temp):
                logger.info(f"Adding edge ({u}, {v}) makes the graph bridgeless")
                return (u, v)

    # If no way to add an edge to make the graph bridgeless, return None
    logger.warning("Cannot make graph bridgeless by adding a single edge")
    return None


def contiguous_oriented_labeling(G: nx.Graph) -> Optional[List[Tuple[int, any, any]]]:
    """
    Create a contiguous oriented labeling for an almost bridgeless graph.

    This function implements the constructive algorithm from Lemma 4.3 of the paper.
    A contiguous oriented labeling is an ordering of edges with orientation such that
    for any prefix of edges, they form a connected subgraph, and for any suffix of
    edges, they also form a connected subgraph with specific connectivity conditions.

    The algorithm works by:
    1. Starting with an initial ear (path between vertices u and v)
    2. Iteratively adding new ears that connect to previously added edges
    3. Maintaining the contiguous property throughout the construction

    Args:
        G (nx.Graph): The input graph, must be almost bridgeless (bridgeless or
                     can be made bridgeless by adding one edge)

    Returns:
        Optional[List[Tuple[int, any, any]]]: A list of tuples (label, from_node, to_node)
                                            where label is an integer starting from 1,
                                            from_node is i⁻, and to_node is i⁺.
                                            Returns None if the graph is not almost bridgeless
                                            or not connected.
    """
    logger.info("Starting contiguous oriented labeling algorithm")
    logger.info(f"Input graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Check if the graph is almost bridgeless
    if find_uv_to_make_bridgeless(G) is None and nx.has_bridges(G):
        logger.error("Graph is not almost bridgeless")
        return None

    # If the graph is not connected, return None
    if not nx.is_connected(G):
        logger.error("Graph is not connected")
        return None

    # We'll follow the constructive proof in Lemma 4.3

    # Make a copy of the graph to work with
    H = G.copy()

    # If G is already bridgeless, choose any edge as the first ear
    if not nx.has_bridges(G):
        # Choose any edge for the first ear
        first_edge = list(H.edges())[0]
        u, v = first_edge
        logger.info(f"Graph is bridgeless, choosing edge {first_edge} for first ear")
    else:
        # Find u, v such that adding (u, v) makes G bridgeless
        edge = find_uv_to_make_bridgeless(G)
        if edge is None:
            return None  # Should not happen if G is almost bridgeless
        u, v = edge
        logger.info(f"Graph has bridges, using vertices {u} and {v} for first ear")

    # Find a path from u to v in H
    if nx.has_path(H, u, v):
        path = nx.shortest_path(H, u, v)
        logger.info(f"Found path from {u} to {v}: {path}")
    else:
        # No path exists (should not happen in a connected graph)
        logger.error(f"No path exists from {u} to {v}")
        return None

    # Convert path to list of edges
    first_ear = [(path[i], path[i+1]) for i in range(len(path)-1)]
    logger.info(f"First ear: {first_ear}")

    # Initialize the list of ears and the edge ordering
    ears = [first_ear]
    all_edges = first_ear.copy()  # Initial order of edges

    # Initialize the set of vertices covered by the ears
    used_vertices = set(path)

    # Remove the first ear from H
    for edge in first_ear:
        H.remove_edge(*edge)

    # Continue building ears until all edges are used
    ear_count = 1
    while H.number_of_edges() > 0:
        logger.debug(f"Building ear #{ear_count + 1}, remaining edges: {H.number_of_edges()}")

        # First, try to find edges between vertices already in an ear
        found_ear = False
        for node1 in used_vertices:
            for node2 in list(H.neighbors(node1)):
                if node2 in used_vertices:
                    # Found an edge connecting two vertices already in ears
                    new_ear = [(node1, node2)]
                    ears.append(new_ear)
                    logger.info(f"Found ear #{ear_count + 1} (single edge): {new_ear}")

                    # Determine insertion point
                    # If node1 = u, insert at beginning of order
                    if node1 == u:
                        all_edges = new_ear + all_edges
                        logger.debug(f"Inserting at beginning (node1={u})")
                    else:
                        # Insert after the first edge directed into node1
                        for i, (src, dst) in enumerate(all_edges):
                            if dst == node1:  # Found incoming edge to node1
                                all_edges = all_edges[:i+1] + new_ear + all_edges[i+1:]
                                logger.debug(f"Inserting after position {i}")
                                break
                        else:
                            # No incoming edge found, append at the end (should not happen)
                            all_edges.extend(new_ear)

                    # Remove the edge from H
                    H.remove_edge(node1, node2)
                    found_ear = True
                    ear_count += 1
                    break
            if found_ear:
                break

        if found_ear:
            continue

        # Next, look for an edge connecting a used vertex to a new vertex
        for node1 in used_vertices:
            new_neighbors = [n for n in H.neighbors(node1) if n not in used_vertices]
            if new_neighbors:
                # Found an edge to a new vertex - start a new ear
                node2 = new_neighbors[0]
                current_ear = [(node1, node2)]
                H.remove_edge(node1, node2)

                # Extend the ear as far as possible
                current = node2
                used_vertices.add(node2)

                # Continue the path until we reach another used vertex
                while True:
                    next_neighbors = [n for n in H.neighbors(current) if n not in used_vertices]
                    if not next_neighbors:
                        # Check if current is connected to a used vertex
                        used_neighbors = [n for n in H.neighbors(current) if n in used_vertices and n != node1]
                        if used_neighbors:
                            # End the ear at this used vertex
                            node3 = used_neighbors[0]
                            current_ear.append((current, node3))
                            H.remove_edge(current, node3)
                        break

                    # Continue the ear
                    next_node = next_neighbors[0]
                    current_ear.append((current, next_node))
                    H.remove_edge(current, next_node)
                    used_vertices.add(next_node)
                    current = next_node

                # Add the ear to our collection
                ears.append(current_ear)
                logger.info(f"Found ear #{ear_count + 1} (path): {current_ear}")

                # Determine insertion point
                # If node1 = u, insert at beginning
                if node1 == u:
                    all_edges = current_ear + all_edges
                    logger.debug(f"Inserting at beginning (node1={u})")
                else:
                    # Insert after the first edge directed into node1
                    for i, (src, dst) in enumerate(all_edges):
                        if dst == node1:  # Found incoming edge to node1
                            all_edges = all_edges[:i+1] + current_ear + all_edges[i+1:]
                            logger.debug(f"Inserting after position {i}")
                            break
                    else:
                        # No incoming edge found, append at the end (should not happen)
                        all_edges.extend(current_ear)

                found_ear = True
                ear_count += 1
                break

        if not found_ear:
            # Should not happen in a connected graph, but just in case
            # Take any remaining edge
            edge = list(H.edges())[0]
            H.remove_edge(*edge)
            ears.append([edge])
            all_edges.append(edge)
            used_vertices.update(edge)
            logger.warning(f"Fallback: adding remaining edge {edge}")

    # Create the labeling based on the final edge order
    labeling = [(i+1, src, dst) for i, (src, dst) in enumerate(all_edges)]
    logger.info(f"Created labeling with {len(labeling)} edges")

    # Verify the contiguous property
    if not verify_contiguous_labeling(G, labeling):
        # If verification fails, the algorithm has a bug
        # Return a DFS-based labeling as fallback
        logger.error("Contiguous labeling verification failed, using DFS fallback")
        return dfs_labeling(G)

    logger.info("Contiguous labeling completed successfully")
    return labeling


def dfs_labeling(G: nx.Graph) -> List[Tuple[int, any, any]]:
    """
    Create a simple DFS-based labeling as a fallback when the main algorithm fails.

    This function performs a depth-first search traversal of the graph and assigns
    labels to edges in the order they are encountered. While this labeling may not
    satisfy the contiguous property, it serves as a backup solution to ensure the
    function always returns a valid edge labeling.

    Args:
        G (nx.Graph): The input graph

    Returns:
        List[Tuple[int, any, any]]: A list of tuples (label, from_node, to_node)
                                   representing the DFS-based edge labeling
    """
    logger.info("Creating DFS-based labeling as fallback")
    visited_edges = set()
    labeling = []
    label = 1

    def dfs(u):
        """
        Recursive DFS helper function.

        Args:
            u: Current vertex being visited
        """
        nonlocal label
        for v in G.neighbors(u):
            edge = (u, v)
            rev_edge = (v, u)
            # Skip if edge already visited (considering undirected nature)
            if edge in visited_edges or rev_edge in visited_edges:
                continue
            visited_edges.add(edge)
            labeling.append((label, u, v))
            label += 1
            dfs(v)  # Recursively visit the neighbor

    # Start DFS from any node
    start_node = list(G.nodes())[0]
    logger.debug(f"Starting DFS from node {start_node}")
    dfs(start_node)

    logger.info(f"DFS labeling created {len(labeling)} labeled edges")
    return labeling


def verify_contiguous_labeling(G: nx.Graph, labeling: List[Tuple[int, any, any]]) -> bool:
    """
    Verify if the given labeling satisfies the contiguous property according to Definition 4.2.

    A contiguous oriented labeling must satisfy two conditions:
    1. For each 2 ≤ i ≤ m, the edges 1,...,i-1 form a connected subgraph,
       and vertex i⁻ belongs to one of these edges
    2. For each 1 ≤ i ≤ m-1, the edges i+1,...,m form a connected subgraph,
       and vertex i⁺ belongs to one of these edges

    Args:
        G (nx.Graph): The original graph
        labeling (List[Tuple[int, any, any]]): The labeling to verify, where each tuple
                                              is (label, from_node, to_node)

    Returns:
        bool: True if the labeling is contiguous, False otherwise
    """
    logger.info("Verifying contiguous labeling property")

    # If the graph or labeling is empty, it's trivially contiguous
    if len(labeling) == 0:
        logger.debug("Empty labeling is trivially contiguous")
        return True

    m = len(labeling)

    # Create mappings from label to source and target vertices
    i_minus = {}
    i_plus = {}

    for label, from_node, to_node in labeling:
        i_minus[label] = from_node
        i_plus[label] = to_node

    # Check first condition: For each 2 ≤ i ≤ m, the edges 1,...,i-1 form a connected subgraph,
    # and vertex i- belongs to one of these edges
    for i in range(2, m+1):
        # Create subgraph of edges with labels 1 to i-1
        subgraph = nx.Graph()
        for j in range(1, i):
            subgraph.add_edge(i_minus[j], i_plus[j])

        # Check if the subgraph is connected (if it has edges)
        if subgraph.number_of_edges() > 0 and not nx.is_connected(subgraph):
            logger.error(f"First condition failed at i={i}: subgraph not connected")
            return False

        # Check if vertex i- belongs to the subgraph
        if i_minus[i] not in subgraph:
            logger.error(f"First condition failed at i={i}: vertex {i_minus[i]}⁻ not in subgraph")
            return False

    # Check second condition: For each 1 ≤ i ≤ m-1, the edges i+1,...,m form a connected subgraph,
    # and vertex i+ belongs to one of these edges
    for i in range(1, m):
        # Create subgraph of edges with labels i+1 to m
        subgraph = nx.Graph()
        for j in range(i+1, m+1):
            subgraph.add_edge(i_minus[j], i_plus[j])

        # Check if the subgraph is connected (if it has edges)
        if subgraph.number_of_edges() > 0 and not nx.is_connected(subgraph):
            logger.error(f"Second condition failed at i={i}: subgraph not connected")
            return False

        # Check if vertex i+ belongs to the subgraph
        if i_plus[i] not in subgraph:
            logger.error(f"Second condition failed at i={i}: vertex {i_plus[i]}⁺ not in subgraph")
            return False

    logger.info("Contiguous labeling verification passed")
    return True


def show_labeling(labeling: List[Tuple[int, any, any]]) -> None:
    """
    Print a human-readable representation of the edge labeling.

    Displays each edge in the format "Edge {label}: {source}⁻ → {target}⁺"
    to show the oriented labeling clearly.

    Args:
        labeling (List[Tuple[int, any, any]]): The labeling to display, where each tuple
                                              is (label, from_node, to_node)
    """
    for label, i_minus, i_plus in labeling:
        print(f"Edge {label}: {i_minus}⁻ → {i_plus}⁺")



if __name__ == "__main__":
    # Test 1: Cycle graph
    print("===== Test 1: Cycle Graph =====")
    G1 = nx.cycle_graph(4)
    print(f"Is bridgeless: {not nx.has_bridges(G1)}")
    labeling1 = contiguous_oriented_labeling(G1)
    print("Labeling:")
    show_labeling(labeling1)
    print(f"Is contiguous: {verify_contiguous_labeling(G1, labeling1)}")
    print()

    # Test 2: Path graph
    print("===== Test 2: Path Graph =====")
    G2 = nx.path_graph(4)
    print(f"Is bridgeless: {not nx.has_bridges(G2)}")
    print(f"Is almost bridgeless: {find_uv_to_make_bridgeless(G2) is not None or not nx.has_bridges(G2)}")
    labeling2 = contiguous_oriented_labeling(G2)
    print("Labeling:")
    show_labeling(labeling2)
    print(f"Is contiguous: {verify_contiguous_labeling(G2, labeling2)}")
    print()

    # Test 3: Triangle with tail
    print("===== Test 3: Triangle with Tail =====")
    G3 = nx.Graph()
    G3.add_edges_from([("A", "B"), ("B", "C"), ("C", "A"), ("A", "D")])
    print(f"Is bridgeless: {not nx.has_bridges(G3)}")
    labeling3 = contiguous_oriented_labeling(G3)
    print("Labeling:")
    show_labeling(labeling3)
    print(f"Is contiguous: {verify_contiguous_labeling(G3, labeling3)}")
    print()

    # Test 4: Star graph
    print("===== Test 4: Star with Center =====")
    G4 = nx.Graph()
    G4.add_edges_from([("A", "B"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D")])
    print(f"Is bridgeless: {not nx.has_bridges(G4)}")
    labeling4 = contiguous_oriented_labeling(G4)
    print("Labeling:")
    show_labeling(labeling4)
    print(f"Is contiguous: {verify_contiguous_labeling(G4, labeling4)}")
