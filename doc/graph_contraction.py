import networkx as nx

def contract_graph_nodes(G, node1, node2):
    """
    Contract two nodes in a graph and handle link weights correctly.
    """
    if G.has_edge(node1, node2):
        weight = G.edges[node1, node2].get('weight', 1)
        print(f"Contracting nodes {node1} and {node2} with weight {weight}")

        # Contract node2 into node1
        contracted_graph = nx.contracted_nodes(G, node1, node2, self_loops=False)

        # Check for invalid or negative weights
        for u, v, data in contracted_graph.edges(data=True):
            if data.get('weight', 1) < 0:
                print(f"Invalid link weight detected between {u} and {v}. Adjusting...")
                contracted_graph[u][v]['weight'] = max(data['weight'], 0)  # Fix weight if needed

        return contracted_graph
    else:
        raise ValueError(f"No edge between {node1} and {node2} to contract.")

# Example usage
if __name__ == "__main__":
    G = nx.Graph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('B', 'C', weight=2)
    G.add_edge('A', 'C', weight=3)

    print("Original Graph:")
    print(G.edges(data=True))

    contracted_G = contract_graph_nodes(G, 'A', 'B')

    print("Contracted Graph:")
    print(contracted_G.edges(data=True))
