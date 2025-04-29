"""Functions for computing communities based on centrality notions."""

import networkx as nx

__all__ = ["girvan_newman"]


@nx._dispatchable(preserve_edge_attrs="most_valuable_edge")
def girvan_newman(G, most_valuable_edge=None, component_wise_computing=False):
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

    component_wise_computing : bool
        If component_wise_computing is True, the edge to remove is selected by:
        1. Local Selection: Select a candidate edge to remove from the subgraph of each connected component of G.
        2. Global Selection: Select a single edge from all candidate edges.

        In this scenario, the function most_valuable_edge should return a tuple of `(*edge_to_remove, metric)`, such that
        it is possible to compute the `metric` of each candidate.
        Note that the Global Selection phase will select the candidate edge with the highest `metric`.

    Returns
    -------
    iterator
        Iterator over tuples of sets of nodes in `G`. Each set of node
        is a community, each tuple is a sequence of communities at a
        particular level of the algorithm.

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
        ([0, 1], [2, 3], [4, 5, 6, 7])

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
        ([0, 1], [2, 3], [4, 5, 6, 7])
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

    # If no function is provided for computing the most valuable edge,
    # use the edge betweenness centrality.
    if most_valuable_edge is None:
        if component_wise_computing:

            def most_valuable_edge(G):
                """Returns the edge with the highest betweenness centrality
                in the graph `G`.
                """
                # We have guaranteed that the graph is non-empty, so this
                # dictionary will never be empty.
                betweenness = nx.edge_betweenness_centrality(G, normalized=False)
                edge_highest_centrality = max(betweenness, key=betweenness.get)
                return edge_highest_centrality, betweenness[edge_highest_centrality]
        else:

            def most_valuable_edge(G):
                """Returns the edge with the highest betweenness centrality
                in the graph `G`.
                """
                # We have guaranteed that the graph is non-empty, so this
                # dictionary will never be empty.
                betweenness = nx.edge_betweenness_centrality(G)
                return max(betweenness, key=betweenness.get)

    # The copy of G here must include the edge weight data.
    g = G.copy().to_undirected()

    # Self-loops must be removed because their removal has no effect on
    # the connected components of the graph.
    g.remove_edges_from(nx.selfloop_edges(g))

    # Initialize the cache of all connected components if we are doing component wise computing
    if component_wise_computing:
        current_components = list(nx.connected_components(g))
        candidates = {g.subgraph(c).copy(): None for c in current_components}

    while g.number_of_edges() > 0:
        if component_wise_computing:
            yield _without_most_central_edges_component_wise(
                g, most_valuable_edge, candidates
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


def _without_most_central_edges_component_wise(G, most_valuable_edge, candidates):
    """Returns the connected components of the graph that results from
    repeatedly removing the most "valuable" edge in the graph.

    Each connected component generates the most "valuable" edge in its own subgraph as a candidate,
    and a single most "valuable" edge is selected from the candidates.
    This allows for potential parallel computing.

    `G` must be a non-empty graph. This function modifies the graph `G`
    in-place; that is, it removes edges on the graph `G`.

    `most_valuable_edge` is a function that takes the graph `G` as input
    (or a subgraph with one or more edges of `G` removed) and returns an
    edge. That edge will be removed and this process will be repeated
    until the number of connected components in the graph increases.

    """

    # Loop until there is a component split
    while True:
        optimal_centrality = None
        global_optimal_edge = None
        affected_subgraph = None

        # Obtain a candidate edge from each subgraph
        for sg in candidates:
            if sg.number_of_edges() == 0:
                continue

            # If the (candidate_edge, centrality) of the current subgraph is not recorded, compute it
            if candidates[sg] is None:
                edge_value_result = most_valuable_edge(sg)
                assert (
                    isinstance(edge_value_result, tuple)
                    and len(edge_value_result) == 2
                    and isinstance(edge_value_result[0], tuple)
                    and len(edge_value_result[0]) == 2
                ), (
                    "If component_wise computing is True, most_valuable_edge must return a tuple (most valuable edge, value of most valuable edge)"
                )

                candidate_edge, centrality = edge_value_result
                candidates[sg] = (candidate_edge, centrality)
            # Otherwise, read from cache
            else:
                candidate_edge, centrality = candidates[sg]

            # Update globally most valuable edge and the affected subgraph
            if optimal_centrality is None or centrality > optimal_centrality:
                optimal_centrality = centrality
                global_optimal_edge = candidate_edge
                affected_subgraph = sg

        # Select globally most valuable edge, remove edge from main graph and component
        G.remove_edge(*global_optimal_edge)
        affected_subgraph.remove_edge(*global_optimal_edge)

        # Set the cache to None, such that the candidate edge and centrality will be recomputed for this subgraph in the next iteration
        candidates[affected_subgraph] = None

        # Check if removing the global_optimal_edge results in the affected subgraph being split
        new_comps = list(nx.connected_components(affected_subgraph))
        if len(new_comps) > 1:
            # Update cache: replace the affected (split) subgraph with the newly generated subgraphs
            del candidates[affected_subgraph]

            for new_comp in new_comps:
                candidates[G.subgraph(new_comp).copy()] = None

            return tuple(map(set, [sg.nodes() for sg in candidates]))
