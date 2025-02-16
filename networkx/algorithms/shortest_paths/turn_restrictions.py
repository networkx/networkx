"""
Compute the shortest paths and path lengths between nodes in the graph,
taking turn restrictions into account.
"""

from heapq import heappush, heappop
from itertools import count
import networkx as nx

__all___ = ["shortest_path_with_turn_restrictions"]


def shortest_path_with_turn_restrictions(
    G, source, target, restricted, weight="length"
):
    """
    Single-source shortest path between two nodes accounting for turn restrictions.

    Parameters
    ----------
    G : NetworkX graph

    source : node
        Starting node for path

    target : node
        Ending node for path

    restricted : function
        Accepts exactly 5 inputs: the origin node, the through node, the exit
        node, the edge attribute dictionary for the in edge, and the edge
        attribute dictionary for the out edge. Returns a boolean, True if the
        turn is restricted and cannot be used, False if the turn can be used.

    weight : string (default = "length")
        If a string, use this edge attribute as the edge weight.
        Any edge attribute not present defaults to 1.

    Returns
    -------
    (length, path) : (number, list)
        The length of the shortest path, and the nodes involved in a shortest path
        from the source to the target.

    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.

    NetworkXNoPath
        If no path exists between source and target.

    Notes
    -----
    Based on the algorithm in Gutiérrez, E., & Medaglia, A. L. (2007). Labeling
    algorithm for the shortest path problem with turn prohibitions with
    application to large-scale road networks. Annals of Operations
    Research, 157(1), 169–182. doi:10.1007/s10479-007-0198-9
    """
    if source not in G:
        raise nx.NodeNotFound(f"{source} not in G")

    if target not in G:
        raise nx.NetworkXNoPath(f"{target} not in G")

    if source == target:
        return (0, [source])

    G_succ = G._succ if G.is_directed() else G._adj
    # Graphs without parallel edges have (u, v) edge keys.
    # MultiGraphs have (u, v, key) edge keys.
    _single_edges = len(next(iter(G.edges))) == 2

    push = heappush
    pop = heappop
    dist = {}  # dictionary of distances to end of edges
    seen = set()  # edges we've processed
    pred = {}  # predecessor edges
    # fringe is heapq with 3-tuples (distance,c,edge)
    # use the count c to avoid comparing nodes (may not be able to)
    c = count()
    fringe = []
    for v, edges in G_succ[source].items():
        if _single_edges:
            edges = [((source, v), edges)]
        else:
            edges = [((source, v, e), attrs) for (e, attrs) in edges.items()]
        for uv_edge, attrs in edges:
            cost = attrs.get(weight, 1)
            if cost is None:
                continue
            push(fringe, (cost, next(c), uv_edge))
            dist[uv_edge] = cost

    while fringe:
        (_, _, uv_edge) = pop(fringe)
        if uv_edge in seen:
            continue  # already searched this edge
        seen.add(uv_edge)
        (u, v) = uv_edge[:2]
        uv_edge_attrs = G.edges[uv_edge]
        if v == target:
            path = [u, v]
            p = pred.get(uv_edge)
            while p:
                u = p[0]
                path.insert(0, u)
                p = pred.get(p)
            return (dist[uv_edge], path)

        for w, edges in G_succ[v].items():
            if _single_edges:
                edges = [((v, w), edges)]
            else:
                edges = [((v, w, e), attrs) for (e, attrs) in edges.items()]
            for (vw_edge, attrs) in edges:
                if vw_edge in seen:
                    continue
                cost = attrs.get(weight, 1)
                if cost is None:
                    continue
                if restricted(u, v, w, uv_edge_attrs, attrs):
                    continue
                vw_cost = dist[uv_edge] + cost
                if vw_edge not in dist or vw_cost < dist[vw_edge]:
                    push(fringe, (vw_cost, next(c), vw_edge))
                    dist[vw_edge] = vw_cost
                    pred[vw_edge] = uv_edge

    raise nx.NetworkXNoPath(f"G has no path from {source} to {target}")
