from copy import deepcopy

import networkx as nx

__all__ = ["bidirected_to_unobserved_confounder"]


def bidirected_to_unobserved_confounder(
    G,
    directed_edge_name="directed",
    bidirected_edge_name="bidirected",
    uc_label="Unobserved Confounders",
):
    """Convert all bidirected edges to unobserved confounders.

    Parameters
    ----------
    G : MixedEdgeGraph
        A causal graph with bidirected edges.
    directed_edge_name : str
        The name of the graph representing directed edges in ``G``.
    bidirected_edge_name : str
        The name of the graph representing bidirected edges in ``G``.
    uc_label : str
        The ``label`` of the unobserved variables that are added in.

    Returns
    -------
    G_copy : DiGraph
        A networkx DiGraph that is a fully specified DAG with unobserved
        variables added in place of bidirected edges.

    Notes
    -----
    This converts bidirected to unobserved confounding variables, that are unobserved
    nodes that have a directed edge pointing to the two variables that were connected
    with a bidirected edge.

    .. warning: This does not work for graphs with undirected edges yet.
    """
    if not isinstance(G, nx.MixedEdgeGraph):
        raise RuntimeError(
            "converting bidirected to confounders should only be run on a MixedEdgeGraph."
        )
    uc_label = "Unobserved Confounders"
    G_copy = nx.DiGraph()
    G_copy.add_nodes_from((n, deepcopy(d)) for n, d in G.nodes.items())
    G_copy.graph = deepcopy(G.graph)

    # add directed edges in
    G_copy.add_edges_from(G.get_graphs(edge_type=directed_edge_name).edges)

    # for every bidirected edge, add a new node
    bidirected_sub_graph = G.get_graphs(edge_type=bidirected_edge_name)
    for idx, latent_edge in enumerate(bidirected_sub_graph.edges):
        G_copy.add_node(f"U{idx}", label=uc_label, observed="no")

        # then add edges from the new UC to the nodes
        G_copy.add_edge(f"U{idx}", latent_edge[0])
        G_copy.add_edge(f"U{idx}", latent_edge[1])

    return G_copy
