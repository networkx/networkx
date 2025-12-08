Shortest Paths
==============

The shortest path problem involves finding a path between two nodes in a graph
such that the total distance is minimized. In unweighted graphs this means
finding the path with the fewest number of edges. In weighted graphs it is the
path with minimum sum of weights associated to the path edges.

This problem definition applies for both undirected and directed graphs. In
undirected graphs, edges can be traversed in any direction. In directed graphs
edges can only be followed in their defined direction, and the path must respect
those constraints. For more details on graph types and their properties, see
:ref:`graph types <classes>`.

NetworkX provides a unified interface for shortest paths weighted and unweighted,
directed and undirected. Other variants of the shortest path problem such as all
pairs of shortest paths are also supported.

To specify that a graph is weighted, the user must provide a weight for the edges by
using the ``weight`` parameter. This can be either a string holding the name of an edge
attribute or a function that returns the weight of an edge. If no weight is
specified, the graph is treated as unweighted. In the case ``weight`` is
specified, but the edge does not have the specified attribute, the edge is
treated as having a weight of :math:`1`.

 >>> import networkx as nx
 >>>
 >>> # Create an undirected weighted graph
 >>> G = nx.Graph()
 >>> G.add_edge("A", "B", weight=4)
 >>> G.add_edge("A", "C", weight=2)
 >>> G.add_edge("B", "C", weight=5)
 >>> G.add_edge("B", "D", weight=10)
 >>> G.add_edge("C", "E", weight=3)
 >>> G.add_edge("E", "D", weight=4)
 >>> G.add_edge("D", "F", weight=11)
 >>>
 >>> # Compute shortest path from A to F considering weights
 >>> weighted_path = nx.shortest_path(G, source="A", target="F", weight="weight")
 >>> print(weighted_path)
 ['A', 'C', 'E', 'D', 'F']
 >>> # Compute shortest path length from A to F ignoring weights
 >>> unweighted_path = nx.shortest_path(G, source="A", target="F")
 >>> print(unweighted_path)
 ['A', 'B', 'D', 'F']

Algorithms
----------

Depending on the type of graph and problem, different algorithms can perform
better than others. The table below summarizes the algorithms NetworkX supports
and their typical time complexities. Here, :math:`V` is the number of nodes and
:math:`E` is the number of edges in the graph.

+----------------------+-------------+--------------------+---------------------------+------------------------------------+
| Algorithm            | Weighted    | Query Type         | Time Complexity           | Recommended for                    |
|                      | Supported?  |                    |                           |                                    |
+======================+=============+====================+===========================+====================================+
| Breadth–First Search | Unweighted  | Single-source,     | :math:`O(V + E)`          | Fastest choice for unweighted      |
| (BFS)                | Only        | Single-pair        |                           | graphs; shortest path in hops      |
+----------------------+-------------+--------------------+---------------------------+------------------------------------+
| |dijkstra|           | Yes, both   | Single-source,     | :math:`O((V + E) \log V)` | General-purpose choice for         |
|                      |             | Single-pair        |                           | non-negative weights               |
+----------------------+-------------+--------------------+---------------------------+------------------------------------+
| Bellman–Ford         | Yes, both   | Single-source,     | :math:`O(VE)`             | Graphs with negative edge weights  |
|                      |             | Single-pair        |                           |                                    |
+----------------------+-------------+--------------------+---------------------------+------------------------------------+
| Floyd–Warshall       | Yes, both   | All-pairs          | :math:`O(V^3)`            | Dense graphs or when all-pairs     |
|                      |             |                    |                           | shortest paths are needed          |
+----------------------+-------------+--------------------+---------------------------+------------------------------------+
| Johnson              | Yes, both   | All-pairs          | :math:`O(V(V + E) \log V)`| All-pairs shortest paths with      |
|                      |             |                    |                           | negative weights                   |
+----------------------+-------------+--------------------+---------------------------+------------------------------------+

The **query type** determines whether the algorithm computes shortest paths
from one node to all others (single-source), between two specified nodes
(single-pair), or between all pairs of nodes (all-pairs). For example, BFS,
|dijkstra|, and Bellman–Ford are commonly used for single-source
or single-pair queries, while Floyd–Warshall and Johnson are designed for
all-pairs shortest paths.

Single-source algorithms can be adapted to single-pair queries by stopping
once the target node is reached (same time complexity). They can also be
extended to multi-source queries by running the algorithm from all starting
nodes. In which case, the time complexity increases by a factor equal to the
number of sources (:math:`V`).

When the query is restricted to a single pair of nodes, bidirectional variants
of some algorithms can be applied to improve efficiency. In NetworkX, both
bidirectional breadth–first search and bidirectional
|dijkstra| are available.

A less common query type is the single-target shortest path, where the goal is
to find paths from all nodes to a given target. This can be computed by
reversing the graph and running a single-source shortest path algorithm from
the target node.

To make these choices easier, NetworkX provides a **simplified interface** that
automatically selects the most suitable algorithm based on the query type.

Simplified Interface
--------------------

When using the simplified interface, NetworkX picks the algorithm that best
suits the use-case. The selection is primarly based on the type of query and
the specified method ("unweighted", "dijkstra", or "bellman-ford").

The type of shortest path query depends on whether ``source`` and ``target``
are specified. When those parameters are ``None``, the type of query
corresponds to all sources or all targets respectively. For example, specifying
``source`` alone means that the query is from the specified source to all
possible vertex targets in the graph. Not passing both ``source`` and ``target``
represents the all pairs shortest path query.

+------------------+------------------+---------------------------------------------+
| ``source``       | ``target``       | Query Type                                  |
+==================+==================+=============================================+
| ``None``         | ``None``         | All pairs shortest paths                    |
+------------------+------------------+---------------------------------------------+
| specified        | ``None``         | From source to all reachable nodes          |
+------------------+------------------+---------------------------------------------+
| ``None``         | specified        | From all nodes that can reach the target    |
+------------------+------------------+---------------------------------------------+
| specified        | specified        | Single source–target shortest path          |
+------------------+------------------+---------------------------------------------+

By default, the simplified interface uses Breadth–First Search for unweighted
graphs and |dijkstra| for weighted graphs (``weight`` parameter is not ``None``).

The default algorithm can be overridden to select Bellman-Ford by specifying
the ``method`` parameter to be "bellman-ford". Algorithms other than
|dijkstra|, Bellman-Ford and Breadth–First Search are not
supported in the simplified interface.

For the case of single-pair queries (both ``source`` and ``target`` specified),
bidirectional variants of |dijkstra| and BFS are used when
those methods are selected.


Simplified Interface Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: networkx.algorithms.shortest_paths.generic
.. autosummary::
   :toctree: generated/

   shortest_path
   all_shortest_paths
   all_pairs_all_shortest_paths
   single_source_all_shortest_paths
   shortest_path_length
   average_shortest_path_length
   has_path


Advanced Interface
------------------

.. automodule:: networkx.algorithms.shortest_paths.unweighted
.. autosummary::
   :toctree: generated/

   single_source_shortest_path
   single_source_shortest_path_length
   single_target_shortest_path
   single_target_shortest_path_length
   bidirectional_shortest_path
   all_pairs_shortest_path
   all_pairs_shortest_path_length
   predecessor

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

   bellman_ford_path
   bellman_ford_path_length
   single_source_bellman_ford
   single_source_bellman_ford_path
   single_source_bellman_ford_path_length
   all_pairs_bellman_ford_path
   all_pairs_bellman_ford_path_length
   bellman_ford_predecessor_and_distance

   negative_edge_cycle
   find_negative_cycle
   goldberg_radzik
   johnson


Dense Graphs
------------

.. automodule:: networkx.algorithms.shortest_paths.dense
.. autosummary::
   :toctree: generated/

   floyd_warshall
   floyd_warshall_predecessor_and_distance
   floyd_warshall_numpy
   reconstruct_path


A* Algorithm
------------

.. automodule:: networkx.algorithms.shortest_paths.astar
.. autosummary::
   :toctree: generated/

   astar_path
   astar_path_length

Notes on Multi-Target Shortest Path Queries
-------------------------------------------

NetworkX does not currently provide a built-in function to compute the shortest
path from a single source to the *nearest* node in a set of multiple targets:

.. math::

   \min_{t \in \text{targets}} \mathrm{distance}(s, t)


This type of query is useful in applications like navigation, facility location,
or emergency response planning. You can implement it efficiently using a
**sentinel node trick**, which transforms the problem into a standard
single-target query.

**Note:** If modifying the original graph is not desirable, use
:meth:`Graph.copy <networkx.Graph.copy>` to operate on a duplicate.

Sentinel Node trick for Multi-Target Queries
--------------------------------------------

To find the shortest path from a source node :math:`s` to the nearest of several
target nodes :math:`\{t_1, t_2, \ldots, t_k\}`, you can:

#. Add a **sentinel node** :math:`T` to your graph.
#. Connect each target node :math:`t_i` to :math:`T` with an edge of **zero cost** (for weighted graphs).
#. Run a shortest path algorithm from the source node :math:`s` to the sentinel node :math:`T`.
#. Recover the actual target by inspecting the path just before :math:`T`.

This approach works with all shortest path algorithms supported in NetworkX,
including Dijkstra's algorithm and Breadth-First Search (for unweighted graphs).

It also works for multi-source queries, where you want to find the shortest path
from any node in a set of sources to the nearest target. In that case, you run a
multi-source shortest path algorithm (such as :meth:`multi_source_dijkstra
<networkx.algorithms.shortest_paths.weighted.multi_source_dijkstra>`) from the
set of sources to the sentinel node, and then recover the closest source and
target by inspecting the resulting path as before.

To obtain the true distance to the closest target, you may need to adjust the
result returned by the shortest path algorithm. In **weighted graphs**, **no
adjustment is needed** because the added edges have zero weight. In **unweighted
graphs**, however, the extra edge to the sentinel contributes a **distance of
one**, so you should **subtract one** from the total to get the correct distance
to the closest target.

Example
^^^^^^^

Adding sentinel node in-place and calling shortest path functions::

    >>> import networkx as nx

    >>> # Create a simple path graph: A - B - C - D - E
    >>> G = nx.Graph()
    >>> G.add_edge('A', 'B', weight=1)
    >>> G.add_edge('B', 'C', weight=1)
    >>> G.add_edge('C', 'D', weight=1)
    >>> G.add_edge('D', 'E', weight=1)

    >>> # Suppose we're at source node 'A'
    >>> source = 'A'
    >>> # And we want the closest of targets 'C', 'D', or 'E'
    >>> targets = {'C', 'D', 'E'}

    >>> # Add a sentinel node connected to each target with weight 0
    >>> sentinel = '_sentinel_'
    >>> G.add_node(sentinel)
    >>> for target in targets:
    >>>     G.add_edge(target, sentinel, weight=0)

    >>> # Compute shortest path from source to sentinel
    >>> path = nx.shortest_path(
            G,
            source=source,
            target=sentinel,
            weight='weight'
         )
    >>> # Compute the true distance
    >>> # No adjustment needed because added edges have zero weight
    >>> distance = nx.shortest_path_length(
            G,
            source=source,
            target=sentinel,
            weight='weight'
         )

    >>> # The real closest target is the node before the sentinel
    >>> closest_target = path[-2]

    >>> print("Shortest path to closest target:", path[:-1])  # exclude sentinel
    >>> print("Closest target:", closest_target)
    >>> print("Distance:", distance)
    Shortest path to closest target: ['A', 'B', 'C']
    Closest target: C
    Distance: 2

    >>> # Clean up (optional)
    >>> G.remove_node(sentinel) # we restore graph
    >>> list(G)
    ['A', 'B', 'C', 'D', 'E']


See Also
--------

.. toctree::
   :maxdepth: 1

   shortest_paths/dijkstra
