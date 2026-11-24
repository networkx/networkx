"""Functions for computing communities based on centrality notions."""

import networkx as nx
from networkx.algorithms.centrality.betweenness import (
    _single_source_dijkstra_path_basic,
    _single_source_shortest_path_basic,
)

__all__ = ["girvan_newman"]


@nx._dispatchable(preserve_edge_attrs="most_valuable_edge")
def girvan_newman(
    G, most_valuable_edge=None, most_valuable_edge_metric=None, weight=None
):
    """Finds communities in a graph using the Girvan–Newman method.

    Parameters
    ----------
    G : NetworkX graph

    most_valuable_edge : function
        Function that takes a graph as input and outputs an edge. The
        edge returned by this function will be recomputed and removed at
        each iteration of the algorithm.

        If not specified, the edge with the highest
        :func:`networkx.edge_betweenness_centrality` will be used.

    most_valuable_edge_metric : function
        Function that takes a graph as input and outputs a tuple of `(*edge_to_remove, metric)`.

        If this function is defined, the edge to remove is selected by:
        1. Local Selection: Select a candidate edge to remove from the subgraph of
        each connected component of G.
        2. Global Selection: Select a single edge from all candidate edges,
        based on the metric of each edge returned by `most_valuable_edge_metric`

        Note that the Global Selection phase will select the candidate edge with the highest `metric`.

    weight : string, optional (default= None)
        If None, all edge weights are considered equal.
        Weights are used to calculate weighted shortest paths, so they are
        interpreted as distances.


    Note
    --------
    If none of `most_valuable_edge` and `most_valuable_edge_metric` is defined,
    this function removes the edge with the highest betweenness centrality.

    Returns
    -------
    iterator
        Iterator over tuples of sets of nodes in `G`. Each set of node
        is a community, each tuple is a sequence of communities at a
        particular level of the algorithm.

    Raises
    ------
    NetworkXError
        If `most_valuable_edge_metric` is defined but does not return
        a tuple of format `(edge, metric)`, where `edge` is a tuple
        of two nodes.

    Examples
    --------
    To get the first pair of communities::

        >>> G = nx.path_graph(10)
        >>> comp = nx.community.girvan_newman(G)
        >>> tuple(sorted(c) for c in next(comp))
        ([0, 1, 2, 3, 4], [5, 6, 7, 8, 9])

    To get only the first *k* tuples of communities, use
    :func:`itertools.islice`::

        >>> import itertools
        >>> G = nx.path_graph(8)
        >>> k = 2
        >>> comp = nx.community.girvan_newman(G)
        >>> for communities in itertools.islice(comp, k):
        ...     print(tuple(sorted(c) for c in communities))
        ...
        ([0, 1, 2, 3], [4, 5, 6, 7])
        ([0, 1, 2, 3], [4, 5], [6, 7])

    To stop getting tuples of communities once the number of communities
    is greater than *k*, use :func:`itertools.takewhile`::

        >>> import itertools
        >>> G = nx.path_graph(8)
        >>> k = 4
        >>> comp = nx.community.girvan_newman(G)
        >>> limited = itertools.takewhile(lambda c: len(c) <= k, comp)
        >>> for communities in limited:
        ...     print(tuple(sorted(c) for c in communities))
        ...
        ([0, 1, 2, 3], [4, 5, 6, 7])
        ([0, 1, 2, 3], [4, 5], [6, 7])
        ([0, 1], [2, 3], [4, 5], [6, 7])

    To just choose an edge to remove based on the weight::

        >>> from operator import itemgetter
        >>> G = nx.path_graph(10)
        >>> edges = G.edges()
        >>> nx.set_edge_attributes(G, {(u, v): v for u, v in edges}, "weight")
        >>> def heaviest(G):
        ...     u, v, w = max(G.edges(data="weight"), key=itemgetter(2))
        ...     return (u, v)
        ...
        >>> comp = nx.community.girvan_newman(G, most_valuable_edge=heaviest)
        >>> tuple(sorted(c) for c in next(comp))
        ([0, 1, 2, 3, 4, 5, 6, 7, 8], [9])

    To utilize edge weights when choosing an edge with, for example, the
    highest betweenness centrality::

        >>> from networkx import edge_betweenness_centrality as betweenness
        >>> def most_central_edge(G):
        ...     centrality = betweenness(G, weight="weight")
        ...     return max(centrality, key=centrality.get)
        ...
        >>> G = nx.path_graph(10)
        >>> comp = nx.community.girvan_newman(G, most_valuable_edge=most_central_edge)
        >>> tuple(sorted(c) for c in next(comp))
        ([0, 1, 2, 3, 4], [5, 6, 7, 8, 9])

    To specify a different ranking algorithm for edges, use the
    `most_valuable_edge` keyword argument::

        >>> from networkx import edge_betweenness_centrality
        >>> from random import random
        >>> def most_central_edge(G):
        ...     centrality = edge_betweenness_centrality(G)
        ...     max_cent = max(centrality.values())
        ...     # Scale the centrality values so they are between 0 and 1,
        ...     # and add some random noise.
        ...     centrality = {e: c / max_cent for e, c in centrality.items()}
        ...     # Add some random noise.
        ...     centrality = {e: c + random() for e, c in centrality.items()}
        ...     return max(centrality, key=centrality.get)
        ...
        >>> G = nx.path_graph(10)
        >>> comp = nx.community.girvan_newman(G, most_valuable_edge=most_central_edge)

    Notes
    -----
    The Girvan–Newman algorithm detects communities by progressively
    removing edges from the original graph. The algorithm removes the
    "most valuable" edge, traditionally the edge with the highest
    betweenness centrality, at each step. As the graph breaks down into
    pieces, the tightly knit community structure is exposed and the
    result can be depicted as a dendrogram.

    """

    # If the graph is already empty, simply return its connected
    # components.
    if G.number_of_edges() == 0:
        yield tuple(nx.connected_components(G))
        return

    # Determine which computation approach to adopt
    component_wise_computing = False
    fast_betweenness_centrality = False
    if most_valuable_edge is None and most_valuable_edge_metric is None:
        fast_betweenness_centrality = True
    elif most_valuable_edge_metric:
        component_wise_computing = True

    # The copy of G here must include the edge weight data.
    g = G.copy().to_undirected()

    # Self-loops must be removed because their removal has no effect on
    # the connected components of the graph.
    g.remove_edges_from(nx.selfloop_edges(g))

    if fast_betweenness_centrality:
        betweenness_cache = BetweennessCache(g, weight=weight)
    # Initialize the cache of all connected components if we are doing component wise computing
    elif component_wise_computing:
        current_components = list(nx.connected_components(g))
        candidates = {g.subgraph(c).copy(): None for c in current_components}

    while g.number_of_edges() > 0:
        if fast_betweenness_centrality:
            yield _without_most_central_edges_betweenness(betweenness_cache)
        elif component_wise_computing:
            yield _without_most_central_edges_component_wise(
                g, most_valuable_edge_metric, candidates
            )
        else:
            yield _without_most_central_edges(g, most_valuable_edge)


def _without_most_central_edges(G, most_valuable_edge):
    """Returns the connected components of the graph that results from
    repeatedly removing the most "valuable" edge in the graph.

    `G` must be a non-empty graph. This function modifies the graph `G`
    in-place; that is, it removes edges on the graph `G`.

    `most_valuable_edge` is a function that takes the graph `G` as input
    (or a subgraph with one or more edges of `G` removed) and returns an
    edge. That edge will be removed and this process will be repeated
    until the number of connected components in the graph increases.

    """
    original_num_components = nx.number_connected_components(G)
    num_new_components = original_num_components
    while num_new_components <= original_num_components:
        edge = most_valuable_edge(G)
        G.remove_edge(*edge)
        new_components = tuple(nx.connected_components(G))
        num_new_components = len(new_components)
    return new_components


def _without_most_central_edges_component_wise(
    G, most_valuable_edge_metric, candidates
):
    """Returns the connected components of the graph that results from
    repeatedly removing the most "valuable" edge in the graph.

    Each connected component generates the most "valuable" edge in its own subgraph as a candidate,
    and a single most "valuable" edge is selected from the candidates.
    This allows for potential parallel computing.

    `G` must be a non-empty graph. This function modifies the graph `G`
    in-place; that is, it removes edges on the graph `G`.

    `most_valuable_edge_metric` is a function that takes a subgraph of `G`
    and returns a candidate edge from this subgraph and a comparable metric.
    The candidate edge with the highest metric will be removed from `G`.
    This process loops until the number of connected components in the graph increases.

    """

    # Loop until there is a component split
    while True:
        edge_metric = {}

        # Obtain a candidate edge from each subgraph
        for sg in candidates:
            if sg.number_of_edges() == 0:
                continue

            # If the (candidate_edge, metric) of the current subgraph is not recorded, compute it
            if candidates[sg] is None:
                edge_value_result = most_valuable_edge_metric(sg)
                if not (
                    isinstance(edge_value_result, tuple)
                    and len(edge_value_result) == 2
                    and isinstance(edge_value_result[0], tuple)
                    and len(edge_value_result[0]) == 2
                ):
                    raise nx.NetworkXError(
                        "If component_wise computing is True, most_valuable_edge_metric must return a tuple (most valuable edge, value of most valuable edge)"
                    )

                candidate_edge, metric = edge_value_result
                candidates[sg] = (candidate_edge, metric)
            # Otherwise, read from cache
            else:
                candidate_edge, metric = candidates[sg]

            edge_metric[(candidate_edge, sg)] = metric

        # Select globally most valuable edge and the affected subgraph
        global_optimal_edge, affected_subgraph = max(
            edge_metric,
            key=lambda edge_sg: (
                round(edge_metric[edge_sg], 8),
                max(edge_sg[0]),
                min(edge_sg[0]),
            ),
        )

        # Select globally most valuable edge, remove edge from main graph and component
        G.remove_edge(*global_optimal_edge)
        affected_subgraph.remove_edge(*global_optimal_edge)

        # Set the cache to None, such that the candidate edge
        # and centrality will be recomputed for this subgraph in the next iteration
        candidates[affected_subgraph] = None

        # Check if removing the global_optimal_edge results in the affected subgraph being split
        new_comps = list(nx.connected_components(affected_subgraph))
        if len(new_comps) > 1:
            # Update cache: replace the affected (split) subgraph with the newly generated subgraphs
            del candidates[affected_subgraph]

            for new_comp in new_comps:
                candidates[G.subgraph(new_comp).copy()] = None

            return tuple([set(sg.nodes()) for sg in candidates])


def _without_most_central_edges_betweenness(betweenness_cache):
    original_num_components = len(betweenness_cache.current_components)
    num_new_components = original_num_components

    # Cut edge until the component is split
    while num_new_components <= original_num_components:
        # Select edge to remove with largest betweenness centrality
        edge_to_remove = betweenness_cache.select_edge_to_remove()
        betweenness_cache.remove_edge(edge_to_remove)

        # The new components after removing edge
        components = betweenness_cache.current_components
        num_new_components = len(components)

    return betweenness_cache.current_components


class BetweennessCache:
    def __init__(self, G, weight=None):
        self.G = G
        self.weight = weight

        # Caches
        # For consistency, edges are recorded in ascending order when used as key
        self.edge_betweenness = {
            tuple(sorted(edge)): 0.0 for edge in list(self.G.edges())
        }
        self.edge_sources = {
            tuple(sorted(edge)): set() for edge in list(self.G.edges())
        }  # edge_sources[edge] = {nodes which has shortest paths that go through edge}
        self.node_contributions = dict.fromkeys(
            self.G.nodes(), 0.0
        )  # contribution of a node to each edge's centrality
        self.current_components = tuple(nx.connected_components(self.G))

        # Initial full betweenness calculation
        for node in self.G.nodes():
            S, P, sigma, _ = self._compute_shortest_path(node)

            self.node_contributions[node] = self._compute_node_contributions(
                S, P, sigma
            )
            for edge, score in self.node_contributions[node].items():
                self.edge_betweenness[edge] += score / 2
                self.edge_sources[edge].add(node)

    def select_edge_to_remove(self):
        return max(
            self.edge_betweenness,
            key=lambda edge: (
                round(self.edge_betweenness[edge], 8),
                max(edge),
                min(edge),
            ),
        )

    def remove_edge(
        self,
        edge_to_remove,
    ):
        """Update betweenness after edge removal using cached contributions."""
        self.G.remove_edge(*edge_to_remove)

        affected_nodes = self.edge_sources[edge_to_remove]
        del self.edge_betweenness[edge_to_remove]
        del self.edge_sources[edge_to_remove]

        component_split = False

        for node in affected_nodes:
            # Remove old contribution
            for edge, score in self.node_contributions[node].items():
                if edge == edge_to_remove:
                    continue
                self.edge_betweenness[edge] -= score / 2
                self.edge_sources[edge].remove(node)

            # Recompute shortest paths and contributions
            S, P, sigma, D = self._compute_shortest_path(node)
            self.node_contributions[node] = self._compute_node_contributions(
                S, P, sigma
            )

            # Add new contribution
            for edge, score in self.node_contributions[node].items():
                self.edge_betweenness[edge] += score / 2
                self.edge_sources[edge].add(node)

            # Determines whether there is a component split
            # check if removing this edge blocks the affected nodes
            # from reaching either end point
            if edge_to_remove[0] not in D or edge_to_remove[1] not in D:
                component_split = True

        # Update components if needed
        if component_split:
            self.current_components = tuple(nx.connected_components(self.G))

    def _compute_shortest_path(self, node):
        """Compute shortest path starting from a node"""
        if self.weight:
            S, P, sigma, D = _single_source_dijkstra_path_basic(
                self.G, node, self.weight
            )
        else:
            S, P, sigma, D = _single_source_shortest_path_basic(self.G, node)

        return S, P, sigma, D

    def _compute_node_contributions(self, S, P, sigma):
        """Precompute and cache contributions for all edges from a single source."""
        contributions = {}
        delta = dict.fromkeys(S, 0)

        while S:
            w = S.pop()
            coeff = (1 + delta[w]) / sigma[w]

            # Compute sigma(s, w | edge v-w) / sigma(s, w)
            for v in P[w]:
                edge = (v, w) if v < w else (w, v)
                contributions[edge] = sigma[v] * coeff
                delta[v] += sigma[v] * coeff

        return contributions
