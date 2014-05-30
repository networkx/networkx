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

6. The functions that the implement flow algorithms (i.e., :samp:`preflow_push`,
   :samp:`edmonds_karp`, :samp:`shortest_augmenting_path` and
   :samp:`ford_fulkerson`) are not imported to the base NetworkX namespace. You
   have to explicitly import them from the flow package:

>>> from networkx.algorithms.flow import (ford_fulkerson, preflow_push,
...        edmonds_karp, shortest_augmenting_path)


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

>>> flow_value = nx.max_flow(G, 0, 6)
>>> cut_value = nx.min_cut(G, 0, 6)
>>> flow_value == cut_value
True
>>> flow_value, flow_dict = nx.ford_fulkerson(G, 0, 6)

With NetworkX 1.9:

>>> from networkx.algorithms.flow import (ford_fulkerson, preflow_push,
...        edmonds_karp, shortest_augmenting_path)
>>> flow_value = nx.maximum_flow_value(G, 0, 6)
>>> cut_value = nx.minimum_cut_value(G, 0, 6)
>>> flow_value == cut_value
True
>>> # Legacy: this returns the exact same output than ford_fulkerson in 1.8.1
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6, flow_func=ford_fulkerson)
>>> # We strongly recommend to use the new algorithms:
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6)
>>> # If no flow_func is passed as argument, the default flow_func
>>> # (preflow-push) is used. Therefore this is the same than:
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6, flow_func=preflow_push)
>>> # You can also use alternative maximum flow algorithms:
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6, flow_func=shortest_augmenting_path)
>>> flow_value, flow_dict = nx.maximum_flow(G, 0, 6, flow_func=edmonds_karp)

Miscellaneous changes
---------------------

* The functions in the components package such as :samp:`connected_components`,
  :samp:`connected_components_subgraph` now return generators instead of lists.
  To recover the earlier behavior, use :samp:`list(connected_components(G))`.
