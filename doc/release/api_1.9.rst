*********************************
Version 1.9 notes and API changes
*********************************

This page reflects API changes from NetworkX 1.8 to NetworkX 1.9.

Please send comments and questions to the networkx-discuss mailing list:
<http://groups.google.com/group/networkx-discuss>.

Flow package
------------

The flow package (:samp:`networkx.algorithms.flow`) is completely rewritten
with backward *incompatible* changes. It introduces a new interface to flow
algorithms. Existing code that uses the flow package will not work unmodified
with NetworkX 1.9.

Main changes
============

1. We added two new maximum flow algorithms (:samp:`preflow_push` and
   :samp:`shortest_augmenting_path`) and rewrote the Edmonds–Karp algorithm in
   :samp:`flow_fulkerson` which is now in :samp:`edmonds_karp`.
   `@ysitu <https://github.com/ysitu>`_ contributed implementations of all new
   maximum flow algorithms. The legacy Edmonds–Karp algorithm implementation in
   :samp:`ford_fulkerson` is still available but will be removed in the next
   release.

2. All maximum flow algorithm implementations (including the legacy
   :samp:`ford_fulkerson`) output now a residual network (i.e., a
   :samp:`DiGraph`) after computing the maximum flow. See :samp:`maximum_flow`
   documentation for the details on the conventions that NetworkX uses for
   defining a residual network.

3. We removed the old :samp:`max_flow` and :samp:`min_cut` functions. The main
   entry points to flow algorithms are now the functions :samp:`maximum_flow`,
   :samp:`maximum_flow_value`, :samp:`minimum_cut` and
   :samp:`minimum_cut_value`, which have new parameters that control maximum
   flow computation: :samp:`flow_func` for specifying the algorithm that will
   do the actual computation (it accepts a function as argument that implements
   a maximum flow algorithm), :samp:`cutoff` for suggesting a maximum flow
   value at which the algorithm stops, :samp:`value_only` for stopping the
   computation as soon as we have the value of the flow, and :samp:`residual`
   that accepts as argument a residual network to be reused in repeated maximum
   flow computation.

4. All flow algorithms are required to accept arguments for these parameters
   but may selectively ignored the inapplicable ones. For instance,
   :samp:`preflow_push` algorithm can stop after the preflow phase without
   computing a maximum flow if we only need the flow value, but both
   :samp:`edmonds_karp` and :samp:`shortest_augmenting_path` always compute a
   maximum flow to obtain the flow value.

5. The new function :samp:`minimum_cut` returns the cut value and a node
   partition that defines the minimum cut. The function
   :samp:`minimum_cut_value` returns only the value of the cut, which is what
   the removed :samp:`min_cut` function used to return before 1.9.

6. The functions that implement flow algorithms (i.e., :samp:`preflow_push`,
   :samp:`edmonds_karp`, :samp:`shortest_augmenting_path` and
   :samp:`ford_fulkerson`) are not imported to the base NetworkX namespace. You
   have to explicitly import them from the flow package:

>>> from networkx.algorithms.flow import (ford_fulkerson, preflow_push,
...        edmonds_karp, shortest_augmenting_path)  # doctest: +SKIP


7. We also added a capacity-scaling minimum cost flow algorithm:
   :samp:`capacity_scaling`. It supports :samp:`MultiDiGraph` and disconnected
   networks.

Examples
========

Below are some small examples illustrating how to obtain the same output than in
NetworkX 1.8.1 using the new interface to flow algorithms introduced in 1.9:

>>> import networkx as nx
>>> G = nx.icosahedral_graph()
>>> nx.set_edge_attributes(G, 'capacity', 1)

With NetworkX 1.8:

>>> flow_value = nx.max_flow(G, 0, 6)  # doctest: +SKIP
>>> cut_value = nx.min_cut(G, 0, 6)  # doctest: +SKIP
>>> flow_value == cut_value  # doctest: +SKIP
True
>>> flow_value, flow_dict = nx.ford_fulkerson(G, 0, 6)  # doctest: +SKIP

With NetworkX 1.9:

>>> from networkx.algorithms.flow import (ford_fulkerson, preflow_push,
...        edmonds_karp, shortest_augmenting_path)  # doctest: +SKIP
>>> flow_value = nx.maximum_flow_value(G, 0, 6)  # doctest: +SKIP
>>> cut_value = nx.minimum_cut_value(G, 0, 6)  # doctest: +SKIP
>>> flow_value == cut_value  # doctest: +SKIP
True
>>> # Legacy: this returns the exact same output than ford_fulkerson in 1.8.1
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6, flow_func=ford_fulkerson)  # doctest: +SKIP
>>> # We strongly recommend to use the new algorithms:
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6)  # doctest: +SKIP
>>> # If no flow_func is passed as argument, the default flow_func
>>> # (preflow-push) is used. Therefore this is the same than:
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6, flow_func=preflow_push)  # doctest: +SKIP
>>> # You can also use alternative maximum flow algorithms:
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6, flow_func=shortest_augmenting_path)  # doctest: +SKIP
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6, flow_func=edmonds_karp)  # doctest: +SKIP

Connectivity package
--------------------

The flow-based connecitivity and cut algorithms from the connectivity
package (:samp:`networkx.algorithms.connectivity`) are adapted to take
advantage of the new interface to flow algorithms. As a result, flow-based
connectivity algorithms are up to 10x faster than in NetworkX 1.8 for some
problems, such as sparse networks with highly skewed degree distributions.
A few backwards *incompatible* changes were introduced.

* The functions for local connectivity and cuts accept now
  arguments for the new parameters defined for the flow interface:
  :samp:`flow_func` for defining the algorithm that will perform the
  underlying maximum flow computations, :samp:`residual` that accepts
  as argument a residual network to be reused in repeated maximum
  flow computations, and :samp:`cutoff` for defining a maximum flow
  value at which the underlying maximum flow algorithm stops. The big
  speed improvement with respect to 1.8 comes mainly from the reuse
  of the residual network and the use of :samp:`cutoff`.

* We removed the flow-based local connectivity and cut functions from
  the base namespace. Now they have to be explicitly imported from the
  connectivity package. The main entry point to flow-based connectivity
  and cut functions are the functions :samp:`edge_connectivity`,
  :samp:`node_connectivity`, :samp:`minimum_edge_cut`, and
  :samp:`minimum_node_cut`. All these functions accept a couple of nodes
  as optional arguments for computing local connectivity and cuts.

* We improved the auxiliary network for connectivity functions: The node
  mapping dict needed for node connectivity and minimum node cuts is now a
  graph attribute of the auxiliary network. Thus we removed the
  :samp:`mapping` parameter from the local versions of connectivity and cut
  functions. We also changed the parameter name for the auxuliary digraph
  from :samp:`aux_digraph` to :samp:`auxiliary`.

* We changed the name of the function :samp:`all_pairs_node_connectiviy_matrix`
  to :samp:`all_pairs_node_connectivity`. This function now returns a dictionary
  instead of a NumPy 2D array. We added a new parameter :samp:`nbunch` for
  computing node connectivity only among pairs of nodes in :samp:`nbunch`.

* A :samp:`stoer_wagner` function is added to the connectivity package
  for computing the weighted minimum cuts of undirected graphs using
  the Stoer–Wagner algorithm. This algorithm is not based on maximum flows.
  Several heap implementations are also added in the utility package
  (:samp:`networkx.utils`) for use in this function.
  :class:`BinaryHeap` is recommended over :class:`PairingHeap` for Python
  implementations without optimized attribute accesses (e.g., CPython)
  despite a slower asymptotic running time. For Python implementations
  with optimized attribute accesses (e.g., PyPy), :class:`PairingHeap`
  provides better performance.

Other new functionalities
-------------------------

* A :samp:`disperson` function is added in the centrality package
  (:samp:`networkx.algorithms.centrality`) for computing the dispersion of
  graphs.

* A community package (:samp:`networkx.generators.community`) is added for
  generating community graphs.

* An :samp:`is_semiconnected` function is added in the connectivity package
  (:samp:`networkx.algorithms.connectivity`) for recognizing semiconnected
  graphs.

* The :samp:`eulerian_circuit` function in the Euler package
  (:samp:`networkx.algorithm.euler`) is changed to use a linear-time algorithm.

* A :samp:`non_edges` function in added in the function package
  (:samp:`networkx.functions`) for enumerating nonexistent edges between
  existing nodes of graphs.

* The linear algebra package (:samp:`networkx.linalg`) is changed to use SciPy
  sparse matrices.

* Functions :samp:`algebraic_connectivity`, :samp:`fiedler_vector` and
  :samp:`spectral_ordering` are added in the linear algebra package
  (:samp:`networkx.linalg`) for computing the algebraic connectivity, Fiedler
  vectors and spectral orderings of undirected graphs.

* A link prediction package (:samp:`networkx.algorithms.link_prediction`) is
  added to provide link prediction-related functionalities.

* Write Support for the graph6 and sparse6 formats is added in the read/write
  package (:samp:`networx.readwrite`).

* A :samp:`goldberg_radzik` function is added in the shortest path package
  (:samp:`networkx.algorithms.shortest_paths`) for computing shortest paths
  using the Goldberg–Radzik algorithm.

* A tree package (:samp:`networkx.tree`) is added to provide tree recognition
  functionalities.

* A context manager :samp:`reversed` is added in the utility package
  (:samp:`networkx.utils`) for temporary in-place reversal of graphs.

Miscellaneous changes
---------------------

* The functions in the components package
  (:samp:`networkx.algorithms.components`) such as :samp:`connected_components`,
  :samp:`connected_components_subgraph` now return generators instead of lists.
  To recover the earlier behavior, use :samp:`list(connected_components(G))`.

* JSON helpers in the JSON graph package (:samp:`networkx.readwrite.json_graph`)
  are removed. Use functions from the standard library (e.g.,
  :samp:`json.dumps`) instead.

* Support for Python 3.1 is dropped. Basic support is added for Jython 2.7 and
  IronPython 2.7, although they remain not officially supported.

* Numerous reported issues are fixed.
