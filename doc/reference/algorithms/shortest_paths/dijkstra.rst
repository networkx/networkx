Dijkstra's Algorithm
====================

Dijkstra's algorithm is a classical algorithm for finding the shortest paths
from a single source node to all other nodes in a weighted graph with
non-negative edge weights. It was conceived by Edsger W. Dijkstra in 1956 and
is widely used in routing, network optimization, and pathfinding problems.

Because Dijkstra's algorithm works only with non-negative edge weights,
alternative algorithms such as Bellman-Ford or Johnson's algorithm are used
for graphs with negative weights. For a general overview of the shortest path
problem see :doc:`/reference/algorithms/shortest_paths`.

Problem Definition
------------------
Given a weighted graph $G = (V, E)$ and a source node $s \in V$, compute the
shortest-path distances $d(s, v)$ from $s$ to every node $v \in V$, where each
edge $(u, v) \in E$ has a non-negative weight $w(u, v)$. Optionally, the
algorithm can also produce the actual shortest paths.

Algorithm
---------
Dijkstra's algorithm is a greedy, iterative algorithm. The main idea is to
incrementally build a set of nodes with known shortest distances, selecting at
each step the node with the smallest tentative distance. At each step, the
tentative distance of the selected node becomes final, as no shorter path to it
can be found.

A key operation in Dijkstra's algorithm is **edge relaxation**. When a node is
selected, the algorithm examines all of its outgoing edges and checks whether
reaching a neighboring node through it would yield a shorter path than the one
currently known. If so, the tentative distance of that neighbor is updated.

Through repeated relaxation of edges, the algorithm gradually refines the
shortest-path estimates until all distances are finalized. The procedure can be
summarized in three main stages: **initialization**, **iteration**, and
**termination**, as outlined below.

**Initialization**

1. Assign source node $s$ a tentative distance value of $0$
   ($dist[s] = 0$).
2. Optionally, initialize a $predecessor$ dict to reconstruct shortest
   paths.

At this point, all nodes are considered **unvisited** and no shortest distance
is considered **final**.

**Iteration**

While there are unvisited nodes:

1. Select the unvisited node $u$ with the smallest tentative distance.
2. Mark $u$ as visited. A visited node will not be checked again because
   this is the shortest path to get to it. Distance to $u$ is now
   considered **final**.
3. **Edge relaxation**. For each neighbor $v$ of $u$:

   * Compute alternative distance: $alt = dist[u] + w(u, v)$
   * If $alt < dist[v]$, update $dist[v] = alt$ and set $predecessor[v] = u$.

**Termination**

The algorithm terminates when all nodes have been visited. The final distances
represent the shortest paths from the source to every reachable node. Shortest
paths can be reconstructed by following predecessor dict backward from each
target node to the source.

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

We can compute the shortest path from ``A`` to all nodes by doing:

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
results in a time complexity of :math:`O(|V|^2)`, while a binary heap reduces it to
:math:`O((|V| + |E|) \log |V|)`. Using a Fibonacci heap further improves the
complexity to :math:`O(|V| \log |V| + |E|)`. The space complexity of the algorithm is
:math:`O(|V| + |E|)`, which accounts for storing the graph representation as well as
the distance and predecessor information.

In practice, Fibonacci heaps have a higher constant overhead compared to binary
heaps, which can make them slower for typical problem sizes despite their
better asymptotic performance. NetworkX's implementation of Dijkstra's
algorithm uses a Python built-in binary heap.

Available Functions
-------------------

.. automodule:: networkx.algorithms.shortest_paths.weighted
   :no-index:
.. autosummary::

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
