"""Functions for computing communities based on centrality notions."""

from heapq import heappop, heappush

import networkx as nx
from networkx.algorithms.centrality.betweenness import (
    _edge_betweenness_centrality,
    edge_betweenness_centrality,
)

__all__ = ["girvan_newman"]


@nx._dispatchable(preserve_edge_attrs="most_valuable_edge")
def girvan_newman(G, most_valuable_edge=None):
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

    With the default edge ranking, only the connected component affected
    by an edge removal needs its betweenness recomputed. Contributions in
    other components remain unchanged. Global normalization and the original
    node and edge order are retained, including ties. A custom
    ``most_valuable_edge`` function continues to receive the whole graph.

    References
    ----------
    .. [1] M. Girvan and M. E. J. Newman, "Community structure in social and
       biological networks," PNAS 99, 7821-7826 (2002).
       https://doi.org/10.1073/pnas.122653799
       https://arxiv.org/abs/cond-mat/0112110

    """
    # If the graph is already empty, simply return its connected
    # components.
    if G.number_of_edges() == 0:
        yield tuple(nx.connected_components(G))
        return
    # The copy of G here must include the edge weight data.
    g = G.copy().to_undirected()
    # Self-loops must be removed because their removal has no effect on
    # the connected components of the graph.
    g.remove_edges_from(nx.selfloop_edges(g))
    if most_valuable_edge is None:
        if type(g) in (nx.Graph, nx.MultiGraph) and _can_cache_betweenness():
            # Until a connected graph splits, no component can be reused.
            # Keep the original path and defer cache setup until the caller
            # actually requests a further level of the hierarchy.
            if g.number_of_edges() and nx.number_connected_components(g) == 1:
                yield _without_most_central_edges(g, _most_central_edge)
            if _can_cache_betweenness() and not any(edge in g for edge in g.edges()):
                yield from _girvan_newman_components(g)
                return

        # Keep public dispatch and custom graph behavior on the original path.
        # The current betweenness accumulator also combines node and edge keys;
        # when these collide, do not change that behavior by separating them.
        most_valuable_edge = _most_central_edge
    while g.number_of_edges() > 0:
        yield _without_most_central_edges(g, most_valuable_edge)


def _can_cache_betweenness():
    priorities = nx.config.backend_priority
    return nx.edge_betweenness_centrality is edge_betweenness_centrality and not any(
        priorities.get(name, priorities.algos)
        for name in (
            "edge_betweenness_centrality",
            "connected_components",
            "number_connected_components",
            "node_connected_component",
        )
    )


def _most_central_edge(G):
    betweenness = nx.edge_betweenness_centrality(G)
    return max(betweenness, key=betweenness.get)


def _girvan_newman_components(G):
    """Remove highest-betweenness edges, reusing unaffected components.

    ``G`` is the private undirected copy with self-loops already removed.
    A heap holds one candidate per component, ordered by its globally
    normalized score and then its position in the original edge iteration.
    No source contributions are subtracted or incrementally reaccumulated.
    """
    edge_order = {edge: index for index, edge in enumerate(G.edges)}
    if not edge_order:
        return
    node_order = {node: index for index, node in enumerate(G)}
    components = {}
    candidates = []
    normalization_size = len(G)

    def add_component(nodes):
        # An induced subgraph view can iterate a small node set in set order.
        # These are entire components, so their adjacency dictionaries have
        # no outside neighbors and can be shared without filtering. Only the
        # outer mappings are copied, in the original source order.
        ordered_nodes = sorted(nodes, key=node_order.__getitem__)
        identifier = node_order[ordered_nodes[0]]
        if len(ordered_nodes) == 1:
            # Isolates are needed only when yielding the full partition.
            components[identifier] = set(ordered_nodes)
            return identifier
        component = nx.graphviews.generic_graph_view(G)
        component._node = {node: G._node[node] for node in ordered_nodes}
        component._adj = {node: G._adj[node] for node in ordered_nodes}
        components[identifier] = component
        return identifier

    def add_candidate(identifier, component):
        if len(component) == 1:
            return
        betweenness = _edge_betweenness_centrality(
            component, normalization_size=normalization_size
        )
        edge = max(betweenness, key=betweenness.get)
        heappush(
            candidates,
            (-betweenness[edge], edge_order[edge], identifier, edge),
        )

    pending = [add_component(nodes) for nodes in nx.connected_components(G)]
    while candidates or pending:
        # A generator caller can change backend configuration between levels.
        # Fall back before evaluating another level under the new policy.
        if not _can_cache_betweenness():
            while G.number_of_edges() > 0:
                yield _without_most_central_edges(G, _most_central_edge)
            return
        for identifier in pending:
            add_candidate(identifier, components[identifier])
        pending = []
        if not candidates:
            return
        _, _, identifier, edge = heappop(candidates)
        component = components[identifier]
        G.remove_edge(*edge)
        reachable = nx.node_connected_component(component, edge[0])
        if len(reachable) == len(component):
            pending.append(identifier)
            continue

        # One edge removal splits one connected component into exactly two.
        # The untouched components keep both their scores and heap entries.
        del components[identifier]
        left = add_component(reachable)
        right = add_component(set(component).difference(reachable))
        yield tuple(set(components[key]) for key in sorted(components))
        # Do not calculate the next level unless the caller requests it.
        pending.extend((left, right))


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
