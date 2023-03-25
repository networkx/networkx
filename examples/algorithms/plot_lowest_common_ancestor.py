"""
==================
Lowest Common Ancestor
==================
This code serves as an illustration of how to work with graphs using the NetworkX framework. It specifically generates an 8 node binary tree and carries out several operations to determine the tree's nodes' lowest common ancestor (LCA).
"""
# Importing necessary libraries
import networkx as nx
import matplotlib.pyplot as plt

# Create a Directed Acyclic Graph with 8 nodes
graph = nx.DiGraph()
graph.add_nodes_from(["A", "B", "C", "D", "E", "F", "G", "H"])
graph.add_edge("A", "B")
graph.add_edge("A", "C")
graph.add_edge("B", "D")
graph.add_edge("B", "E")
graph.add_edge("C", "F")
graph.add_edge("C", "G")
graph.add_edge("D", "H")
graph.add_edge("E", "H")
graph.add_edge("F", "H")
graph.add_edge("G", "H")

# Find the lowest common ancestor of all possible pairs of nodes in the tree
all_pairs_lca = nx.all_pairs_lowest_common_ancestor(graph)
for pair, lca in all_pairs_lca:
    print(f"Lowest common ancestor of nodes {pair} is node {lca}")

# Find the lowest common ancestor of sets of pairs of nodes in the tree, The pairs argument can be used to limit the output to only the specified node pairings: In this example we find the lca between (A,D) AND (B,C) pairs only.
tree_lca = nx.tree_all_pairs_lowest_common_ancestor(
    graph, root="A", pairs=[("A", "D"), ("B", "C")]
)
for pair_set, lca in tree_lca:
    print(f"Lowest common ancestor of nodes {pair_set} is node {lca}")

# Find the lowest common ancestor of particular nodes, for example E and G in this tree
node_lca = nx.lowest_common_ancestor(graph, "E", "G")
print(f"Lowest common ancestor of nodes E and G is node {node_lca}")

# Visualize the graph with the lowest common ancestor of nodes E and G highlighted
pos = nx.spring_layout(graph)
fig, ax = plt.subplots()
nx.draw(graph, pos=pos, with_labels=True, ax=ax)
nx.draw_networkx_nodes(
    graph, pos=pos, nodelist=["E", "G"], node_color="r", node_size=500, ax=ax
)
nx.draw_networkx_nodes(
    graph, pos=pos, nodelist=[node_lca], node_color="g", node_size=500, ax=ax
)
nx.draw_networkx_labels(graph, pos=pos, labels={n: n for n in graph.nodes}, ax=ax)
plt.axis("off")
plt.show()
