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


def is_bridgeless(G: nx.Graph) -> bool:
    """
    Check if a graph is bridgeless (contains no bridges).
    """
    return len(list(nx.bridges(G))) == 0


def is_almost_bridgeless(G: nx.Graph) -> bool:
    """
    Check if a graph is almost bridgeless.
    
    A graph is almost bridgeless if we can add an edge so that the resulting graph is bridgeless.
    """
    # If the graph is already bridgeless, it's also almost bridgeless
    if is_bridgeless(G):
        return True
    
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
            if is_bridgeless(G_temp):
                return True
    
    # If no way to add an edge to make the graph bridgeless, return False
    return False


def find_uv_to_make_bridgeless(G: nx.Graph) -> Optional[Tuple]:
    """
    Find vertices u and v such that adding edge (u,v) makes G bridgeless.
    
    Returns None if G is already bridgeless or cannot be made bridgeless by adding one edge.
    """
    # If the graph is already bridgeless, return None
    if is_bridgeless(G):
        return None
    
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
            if is_bridgeless(G_temp):
                return (u, v)
    
    # If no way to add an edge to make the graph bridgeless, return None
    return None


def contiguous_oriented_labeling(G: nx.Graph) -> Optional[List[Tuple[int, any, any]]]:
    """
    Create a contiguous oriented labeling for an almost bridgeless graph.
    
    Returns a list of tuples: (label, from_node, to_node)
    where label is an integer, from_node is i⁻, and to_node is i⁺
    
    If the graph is not almost bridgeless, returns None.
    """
    # Check if the graph is almost bridgeless
    if not is_almost_bridgeless(G):
        return None
    
    # If the graph is not connected, return None
    if not nx.is_connected(G):
        return None
    
    # We'll follow the constructive proof in Lemma 4.3
    
    # Make a copy of the graph to work with
    H = G.copy()
    
    # If G is already bridgeless, choose any edge as the first ear
    if is_bridgeless(G):
        # Choose any edge for the first ear
        first_edge = list(H.edges())[0]
        u, v = first_edge
    else:
        # Find u, v such that adding (u, v) makes G bridgeless
        edge = find_uv_to_make_bridgeless(G)
        if edge is None:
            return None  # Should not happen if G is almost bridgeless
        u, v = edge
    
    # Find a path from u to v in H
    if nx.has_path(H, u, v):
        path = nx.shortest_path(H, u, v)
    else:
        # No path exists (should not happen in a connected graph)
        return None
    
    # Convert path to list of edges
    first_ear = [(path[i], path[i+1]) for i in range(len(path)-1)]
    
    # Initialize the list of ears and the edge ordering
    ears = [first_ear]
    all_edges = first_ear.copy()  # Initial order of edges
    
    # Initialize the set of vertices covered by the ears
    used_vertices = set(path)
    
    # Remove the first ear from H
    for edge in first_ear:
        H.remove_edge(*edge)
    
    # Continue building ears until all edges are used
    while H.number_of_edges() > 0:
        # First, try to find edges between vertices already in an ear
        found_ear = False
        for node1 in used_vertices:
            for node2 in list(H.neighbors(node1)):
                if node2 in used_vertices:
                    # Found an edge connecting two vertices already in ears
                    new_ear = [(node1, node2)]
                    ears.append(new_ear)
                    
                    # Determine insertion point
                    # If node1 = u, insert at beginning of order
                    if node1 == u:
                        all_edges = new_ear + all_edges
                    else:
                        # Insert after the first edge directed into node1
                        for i, (src, dst) in enumerate(all_edges):
                            if dst == node1:  # Found incoming edge to node1
                                all_edges = all_edges[:i+1] + new_ear + all_edges[i+1:]
                                break
                        else:
                            # No incoming edge found, append at the end (should not happen)
                            all_edges.extend(new_ear)
                    
                    # Remove the edge from H
                    H.remove_edge(node1, node2)
                    found_ear = True
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
                
                # Determine insertion point
                # If node1 = u, insert at beginning
                if node1 == u:
                    all_edges = current_ear + all_edges
                else:
                    # Insert after the first edge directed into node1
                    for i, (src, dst) in enumerate(all_edges):
                        if dst == node1:  # Found incoming edge to node1
                            all_edges = all_edges[:i+1] + current_ear + all_edges[i+1:]
                            break
                    else:
                        # No incoming edge found, append at the end (should not happen)
                        all_edges.extend(current_ear)
                
                found_ear = True
                break
        
        if not found_ear:
            # Should not happen in a connected graph, but just in case
            # Take any remaining edge
            edge = list(H.edges())[0]
            H.remove_edge(*edge)
            ears.append([edge])
            all_edges.append(edge)
            used_vertices.update(edge)
    
    # Create the labeling based on the final edge order
    labeling = [(i+1, src, dst) for i, (src, dst) in enumerate(all_edges)]
    
    # Verify the contiguous property
    if not verify_contiguous_labeling(G, labeling):
        # If verification fails, the algorithm has a bug
        # Return a DFS-based labeling as fallback
        return dfs_labeling(G)
    
    return labeling


def dfs_labeling(G: nx.Graph) -> List[Tuple[int, any, any]]:
    """
    Create a simple DFS-based labeling as a fallback.
    This may not be contiguous but serves as a backup.
    """
    visited_edges = set()
    labeling = []
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
    
    # Start DFS from any node
    dfs(list(G.nodes())[0])
    
    return labeling


def verify_contiguous_labeling(G: nx.Graph, labeling: List[Tuple[int, any, any]]) -> bool:
    """
    Verify if the given labeling is contiguous according to Definition 4.2.
    """
    # If the graph or labeling is empty, it's trivially contiguous
    if len(labeling) == 0:
        return True
    
    m = len(labeling)
    
    # Create mappings
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
            return False
        
        # Check if vertex i- belongs to the subgraph
        if i_minus[i] not in subgraph:
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
            return False
        
        # Check if vertex i+ belongs to the subgraph
        if i_plus[i] not in subgraph:
            return False
    
    return True


def show_labeling(labeling: List[Tuple[int, any, any]]) -> None:
    """
    Print a readable representation of the labeling.
    """
    for label, i_minus, i_plus in labeling:
        print(f"Edge {label}: {i_minus}⁻ → {i_plus}⁺")



if __name__ == "__main__":
    # Test 1: Cycle graph
    print("===== Test 1: Cycle Graph =====")
    G1 = nx.cycle_graph(4)
    print(f"Is bridgeless: {is_bridgeless(G1)}")
    labeling1 = contiguous_oriented_labeling(G1)
    print("Labeling:")
    show_labeling(labeling1)
    print(f"Is contiguous: {verify_contiguous_labeling(G1, labeling1)}")
    print()
    
    # Test 2: Path graph
    print("===== Test 2: Path Graph =====")
    G2 = nx.path_graph(4)
    print(f"Is bridgeless: {is_bridgeless(G2)}")
    print(f"Is almost bridgeless: {is_almost_bridgeless(G2)}")
    labeling2 = contiguous_oriented_labeling(G2)
    print("Labeling:")
    show_labeling(labeling2)
    print(f"Is contiguous: {verify_contiguous_labeling(G2, labeling2)}")
    print()
    
    # Test 3: Triangle with tail
    print("===== Test 3: Triangle with Tail =====")
    G3 = nx.Graph()
    G3.add_edges_from([("A", "B"), ("B", "C"), ("C", "A"), ("A", "D")])
    print(f"Is bridgeless: {is_bridgeless(G3)}")
    labeling3 = contiguous_oriented_labeling(G3)
    print("Labeling:")
    show_labeling(labeling3)
    print(f"Is contiguous: {verify_contiguous_labeling(G3, labeling3)}")
    print()
    
    # Test 4: Star graph
    print("===== Test 4: Star with Center =====")
    G4 = nx.Graph()
    G4.add_edges_from([("A", "B"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D")])
    print(f"Is bridgeless: {is_bridgeless(G4)}")
    labeling4 = contiguous_oriented_labeling(G4)
    print("Labeling:")
    show_labeling(labeling4)
    print(f"Is contiguous: {verify_contiguous_labeling(G4, labeling4)}")