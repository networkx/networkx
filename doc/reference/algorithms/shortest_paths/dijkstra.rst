Dijkstra's Algorithm
===================

Dijkstra's algorithm is a classical algorithm for finding the shortest paths
from a single source node to all other nodes in a weighted graph with
non-negative edge weights. It was conceived by Edsger W. Dijkstra in 1956
and is widely used in routing, network optimization, and pathfinding problems.

For a general overview in the shortest path problem see
`Shortest Paths <index.html>`_.

Problem Definition
------------------
Given a weighted graph G = (V, E) and a source vertex s ∈ V, compute the
shortest-path distances d(s, v) from s to every vertex v ∈ V, where each
edge (u, v) ∈ E has a non-negative weight w(u, v). Optionally, the algorithm
can also produce the actual shortest paths.

Algorithm
---------
Dijkstra's algorithm is a greedy, iterative algorithm. The main idea is to
incrementally build a set of nodes with known shortest distances,
selecting at each step the node with the smallest tentative distance.

**Initialization**

1. Assign every node a tentative distance value:
    * `dist[s] = 0` for the source
    * `dist[v] = ∞` for all other nodes
2. Initialize all nodes as unvisited.
3. Optionally, initialize a predecessor map to reconstruct shortest paths.

**Iteration**

While there are unvisited nodes:

1. Select the unvisited node u with the smallest tentative distance.
2. For each neighbor v of u:
    * Compute alternative distance: `alt = dist[u] + w(u, v)`
    * If `alt < dist[v]`, update `dist[v] = alt` and set `predecessor[v] = u`.
3. Mark u as visited. A visited node will not be checked again.

**Termination**

The algorithm terminates when all nodes have been visited, or when the smallest
tentative distance among unvisited nodes is infinity.

Example
-------
Consider the weighted graph:

.. code-block:: text

        (2)
    A ------- B
    |         |
   (1)       (3)
    |         |
    C ------- D
        (1)

We can compute the shortest path from ``A`` to all vertices by doing:

    >>> import networkx as nx
    >>> # Create a weighted graph
    >>> G = nx.Graph()
    >>> edges = [('A', 'B', 2), ('A', 'C', 1), ('B', 'D', 3), ('C', 'D', 1)]
    >>> G.add_weighted_edges_from(edges)
    >>> distances = nx.single_source_dijkstra_path_length(G, source='A')
    >>> print("Shortest distances from A:", distances)
    Shortest distances from A: {'A': 0, 'C': 1, 'B': 2, 'D': 2}

Complexity
----------

The time complexity of Dijkstra's algorithm depends on the data structure used
to select the node with the smallest tentative distance. Using a simple array
results in a time complexity of :math:`O(|V|^2)`, while a binary heap reduces
it to :math:`O((|V| + |E|) \log |V|)`. Using a Fibonacci heap further improves
the complexity to :math:`O(|V| \log |V| + |E|)`. The space complexity of the
algorithm is :math:`O(|V| + |E|)`, which accounts for storing the graph
representation as well as the distance and predecessor information.

In practice, Fibonacci heaps have a higher constant overhead compared to binary
heaps, which can make them slower for typical problem sizes despite their
better asymptotic performance. NetworkX's implementation of Dijkstra's
algorithm uses a Python built-in binary heap.

Limitations
-----------
Dijkstra's algorithm works only with non-negative edge weights and finds the
shortest-path tree from the source to all reachable nodes. For graphs that
contain negative edge weights, alternative algorithms such as Bellman-Ford or
Johnson’s algorithm are required.

Available Functions
-------------------

.. automodule:: networkx.algorithms.shortest_paths.weighted
.. autosummary::
   :toctree: generated/

   dijkstra_predecessor_and_distance
   dijkstra_path
   dijkstra_path_length
   single_source_dijkstra
   single_source_dijkstra_path
   single_source_dijkstra_path_length
   multi_source_dijkstra
   multi_source_dijkstra_path
   multi_source_dijkstra_path_length
   all_pairs_dijkstra
   all_pairs_dijkstra_path
   all_pairs_dijkstra_path_length
   bidirectional_dijkstra