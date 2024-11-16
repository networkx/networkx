import networkx as nx
from networkx.algorithms.bipartite import color
from networkx.utils import not_implemented_for

__all__ = ["get_top_nodes"]


@not_implemented_for("directed")
def get_top_nodes(G: nx.Graph) -> list:
    """
    Helper function to get top nodes, of a bipartite graph,
    when used with `hopcroft_karp_matching` as `hopcroft_karp_matching`
    can raise an exception when the input is disconnected
    bipartite graph
    """
    assert nx.is_bipartite(G), "Graph must be bipartite"
    top_nodes = []
    graph_coloring = color(G)
    for node in G.nodes:
        if graph_coloring[node] == 0:
            top_nodes.append(node)

    return top_nodes
