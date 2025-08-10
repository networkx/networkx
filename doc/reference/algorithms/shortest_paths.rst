Shortest Paths
==============
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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