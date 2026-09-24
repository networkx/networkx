"""Basic algorithms for searching the nodes of a graph by uniform cost."""
import networkx as nx
from heapq import heappush, heappop
from networkx.algorithms.shortest_paths.weighted import _weight_function

__all__ = ['ucs_edges']


def ucs_edges(G, source, weight='weight'):
    """Iterate over edges by least total path cost (UCS).

    Perform a uniform-cost-search over the nodes of G and yield
    the edges in order.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Specify starting node for uniform-cost search and return edges in
       the component reachable from source.

    Returns
    -------
    edges: generator
       A generator of edges in the uniform-cost-search.

    Examples
    --------
    >>> g = nx.Graph()
    >>> g.add_nodes_from(['A','B','C','D','E','F','G'])
    >>> g.add_edges_from([('A','B', {'weight': 5}), ('A','C', {'weight': 2}), ('D','B', {'weight': 9}), ('E','B', {'weight': 6}), ('C','F', {'weight': 4}), ('C','G', {'weight': 10})])
    >>> list(nx.ucs_edges(g, source='A'))
    [('A', 'C'), ('A', 'B'), ('C', 'F'), ('B', 'E'), ('C', 'G'), ('B', 'D')]

    Notes
    -----
    The implementation of this function is adapted from `Wikipedia`_.

    .. _Wikipedia: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Practical_optimizations_and_infinite_graphs

    """
    if source not in G :
        msg = f"Source {source} is not in G"
        raise nx.NodeNotFound(msg)

    push = heappush
    pop = heappop
    visited = set()

    # The queue stores priority, node, cost to reach, and parent.
    # Uses Python heapq to keep in priority order.
    # Add a counter to the queue to prevent the underlying heap from
    # attempting to compare the nodes themselves. The hash breaks ties in the
    # priority and is guaranteed unique for all nodes in the graph.
    queue = [(0, source, None)]
    visited.add(source)

    while queue:
        # Pop the smallest item from queue.
        current_cost, current_node, parent = pop(queue)

        for neighbour in iter(G[current_node]):
            if neighbour in visited:
                continue
            neighbour_cost = G[current_node][neighbour][weight]
            push(queue, (neighbour_cost + current_cost, neighbour, current_node))
            visited.add(neighbour)

        if parent is not None:
            yield parent, current_node
