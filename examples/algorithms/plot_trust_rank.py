"""
=========
TrustRank
=========

`TrustRank`_ is an algorithm designed to compute trust scores for nodes in a graph.
It is particularly useful in applications like web spam detection, where certain
nodes (web pages) are known to be trustworthy, and the goal is to propagate trust
to other nodes based on the graph structure.

.. _TrustRank: https://en.wikipedia.org/wiki/TrustRank

How TrustRank Relies on PageRank:
---------------------------------
TrustRank uses the personalization feature of PageRank to bias the ranking towards
a set of "seed nodes." These seed nodes are considered trustworthy and are assigned
higher initial scores in the personalization vector. The algorithm then propagates
trust through the graph using the same iterative process as PageRank.

Key Steps:

1. Define a set of seed nodes that are considered trustworthy.
2. Create a personalization vector where seed nodes are assigned equal trust,
   and non-seed nodes are assigned zero.
3. Run the PageRank algorithm with the personalization vector to compute trust
   scores for all nodes.
"""

import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph([(1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 1), (5, 6)])

# Define seed nodes (trusted nodes)
seed_nodes = {1, 3}

# Use a personalization vector to assign trust values to seed nodes.
# Seed nodes can have equal trust or custom values, while non-seed nodes are
# assigned zero trust.
trust = {n: 1.0 / len(seed_nodes) if n in seed_nodes else 0 for n in G.nodes}

# Compute TrustRank using PageRank with personalization
trust_rank = nx.pagerank(G, alpha=0.85, personalization=trust)

pos = nx.spring_layout(G, seed=2771)
node_sizes = [trust_rank[n] * 5000 for n in G]

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
plt.show()
