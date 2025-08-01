"""
==========
TrustRank Algorithm
==========

TrustRank is an algorithm designed to compute trust scores for nodes in a graph.
It is particularly useful in applications like web spam detection, where certain nodes (web pages) are
known to be trustworthy, and the goal is to propagate trust to other nodes based on the graph structure.

How TrustRank Relies on PageRank:
---------------------------------
TrustRank uses the personalization feature of PageRank to bias the ranking towards a set of "seed nodes."
These seed nodes are considered trustworthy and are assigned higher initial scores in the personalization
vector. The algorithm then propagates trust through the graph using the same iterative process as PageRank.

Key Steps:
1. Define a set of seed nodes that are considered trustworthy.
2. Create a personalization vector where seed nodes are assigned equal trust, and non-seed nodes are assigned zero.
3. Run the PageRank algorithm with the personalization vector to compute trust scores for all nodes.

References
----------
.. [1] Gyongyi, Zoltan; Garcia-Molina, Hector (2004).
    "Combating Web Spam with TrustRank"
    http://ilpubs.stanford.edu:8090/770/1/2004-52.pdf
.. [2] Krishnan, Vijay; Raj, Rashmi
    "Web Spam Detection with Anti-Trust Rank"
    http://i.stanford.edu/~kvijay/krishnan-raj-airweb06.pdf
"""

import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
edges = [
    (1, 2),
    (1, 3),
    (2, 4),
    (3, 4),
    (3, 5),
    (4, 1),
    (5, 6),
]
G.add_edges_from(edges)

# Define seed nodes (trusted nodes)
seed_nodes = {1, 3}

# use personalization vector to assign equal trust to seed nodes
personalization = {n: 1.0 / len(seed_nodes) if n in seed_nodes else 0 for n in G.nodes}
"""
alternatively, you can use a dictionary with custom trust values:
personalization = {1: 0.7, 3: 0.3}
personalization.update({n: 0 for n in G.nodes if n not in seed_nodes})
"""

# Compute TrustRank using PageRank with personalization
trust_rank = nx.pagerank(G, alpha=0.85, personalization=personalization)

pos = nx.spring_layout(G)
node_sizes = [trust_rank[n] * 5000 for n in G.nodes]

plt.figure(figsize=(8, 6))
nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=node_sizes,
    node_color="skyblue",
    edge_color="gray",
    font_size=10,
)
plt.title("TrustRank Visualization")
plt.show()
