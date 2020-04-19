"""Functions for computing and verifying regular graphs."""
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['is_regular', 'is_k_regular', 'k_factor']


def is_regular(G):
    """Determines whether the graph ``G`` is a regular graph.

    A regular graph is a graph where each vertex has the same degree. A
    regular digraph is a graph where the indegree and outdegree of each
    vertex are equal.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    bool
        Whether the given graph or digraph is regular.

    """
    n1 = nx.utils.arbitrary_element(G)
    if not G.is_directed():
        d1 = G.degree(n1)
        return all(d1 == d for _, d in G.degree)
    else:
        d_in = G.in_degree(n1)
        in_regular = all(d_in == d for _, d in G.in_degree)
        d_out = G.out_degree(n1)
        out_regular = all(d_out == d for _, d in G.out_degree)
        return in_regular and out_regular


@not_implemented_for('directed')
def is_k_regular(G, k):
    """Determines whether the graph ``G`` is a k-regular graph.

    A k-regular graph is a graph where each vertex has degree k.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    bool
        Whether the given graph is k-regular.

    """
    return all(d == k for n, d in G.degree)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def k_factor(G, k, matching_weight='weight'):
    """Compute a k-factor of G

    A k-factor of a graph is a spanning k-regular subgraph.

    Parameters
    ----------
    G : NetworkX graph
      Undirected graph

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight.
       Used for finding the max-weighted perfect matching.
       If key not found, uses 1 as weight.

    Returns
    -------
    G2 : NetworkX graph
        A k-factor of G

    References
    ----------
    .. [1] "An algorithm for computing simple k-factors.",
       Meijer, Henk, Yurai Núñez-Rodríguez, and David Rappaport,
       Information processing letters, 2009.
    """

    from networkx.algorithms.matching import max_weight_matching
    from networkx.algorithms.matching import is_perfect_matching

    class LargeKGadget:
        def __init__(self, k, degree, node):
            self.original = node
            self.k = k
            self.degree = degree

            self.outer_vertices = [(node, x) for x in range(degree)]
            self.core_vertices = [(node, x + degree)
                                  for x in range(degree - k)]

        def replace_node(self, g):
            adj_view = g[self.original]
            neighbors = list(adj_view.keys())
            edge_attrs = list(adj_view.values())
            for (outer, neighbor, edge_attrs) in \
                    zip(self.outer_vertices, neighbors, edge_attrs):
                g.add_node(outer)
                g.add_edge(outer, neighbor, **edge_attrs)
            for core in self.core_vertices:
                g.add_node(core)
                for outer in self.outer_vertices:
                    g.add_edge(core, outer)
            g.remove_node(self.original)

        def restore_node(self, g):
            g.add_node(self.original)
            for outer in self.outer_vertices:
                adj_view = g[outer]
                for neighbor, edge_attrs in list(adj_view.items()):
                    if neighbor not in self.core_vertices:
                        g.add_edge(self.original, neighbor, **edge_attrs)
                        break
            g.remove_nodes_from(self.outer_vertices)
            g.remove_nodes_from(self.core_vertices)

    class SmallKGadget:
        def __init__(self, k, degree, node):
            self.original = node
            self.k = k
            self.degree = degree

            self.outer_vertices = [(node, x) for x in range(degree)]
            self.inner_vertices = [(node, x + degree) for x in range(degree)]
            self.core_vertices = [(node, x + 2 * degree) for x in range(k)]

        def replace_node(self, g):
            adj_view = g[self.original]
            for (outer, inner, (neighbor, edge_attrs)) in \
                    zip(
                        self.outer_vertices,
                        self.inner_vertices,
                        list(adj_view.items())):
                g.add_node(outer)
                g.add_node(inner)
                g.add_edge(outer, inner)
                g.add_edge(outer, neighbor, **edge_attrs)
            for core in self.core_vertices:
                g.add_node(core)
                for inner in self.inner_vertices:
                    g.add_edge(core, inner)
            g.remove_node(self.original)

        def restore_node(self, g):
            g.add_node(self.original)
            for outer in self.outer_vertices:
                adj_view = g[outer]
                for neighbor, edge_attrs in adj_view.items():
                    if neighbor not in self.core_vertices:
                        g.add_edge(self.original, neighbor, **edge_attrs)
                        break
            g.remove_nodes_from(self.outer_vertices)
            g.remove_nodes_from(self.inner_vertices)
            g.remove_nodes_from(self.core_vertices)

    # Step 1
    if any(d < k for _, d in G.degree):
        raise nx.NetworkXUnfeasible(
            "Graph contains a vertex with degree less than k")
    g = G.copy()

    # Step 2
    gadgets = []
    for node, degree in list(g.degree):
        if k < degree / 2.:
            gadget = SmallKGadget(k, degree, node)
        else:
            gadget = LargeKGadget(k, degree, node)
        gadget.replace_node(g)
        gadgets.append(gadget)

    # Step 3
    matching = max_weight_matching(
        g, maxcardinality=True, weight=matching_weight)

    # Step 4
    if not is_perfect_matching(g, matching):
        raise nx.NetworkXUnfeasible("No perfect matching exists for graph")

    for edge in g.edges():
        if edge not in matching and (edge[1], edge[0]) not in matching:
            g.remove_edge(edge[0], edge[1])

    for gadget in gadgets:
        gadget.restore_node(g)

    return g
