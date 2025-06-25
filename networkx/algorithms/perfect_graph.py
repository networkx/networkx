import networkx as nx

__all__ = ["is_perfect_graph"]


def is_perfect_graph(G):
    """Return True if G is a perfect graph, else False.

    According to the Strong Perfect Graph Theorem, a graph is perfect
    if and only if neither it nor its complement contains an induced
    odd cycle of length at least 5.
    """

    def has_induced_odd_hole(graph):
        nodes = list(graph.nodes)
        n = len(nodes)
        for i in range(n):
            for j in range(i + 1, n):
                try:
                    paths = nx.all_simple_paths(graph, nodes[i], nodes[j], cutoff=n)
                except nx.NetworkXNoPath:
                    continue
                for path in paths:
                    if len(path) < 5 or len(path) % 2 == 0:
                        continue
                    if graph.has_edge(path[-1], path[0]):
                        cycle_nodes = path
                        subG = graph.subgraph(cycle_nodes)
                        if subG.number_of_edges() == len(cycle_nodes):
                            return True
        return False

    if has_induced_odd_hole(G):
        return False
    if has_induced_odd_hole(nx.complement(G)):
        return False
    return True
