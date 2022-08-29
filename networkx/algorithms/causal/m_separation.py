import networkx as nx

__all__ = ["m_separated"]


def m_separated(
    G, x, y, z, bidirected_edge_name="bidirected", directed_edge_name="directed"
):
    """Check m-separation among 'x' and 'y' given 'z' in mixed-edge causal graph G.

    This algorithm wraps ``networkx.algorithms.d_separated``, but
    allows one to pass in a ``ADMG`` instance instead.

    It first converts all bidirected edges into explicit unobserved
    confounding nodes in an explicit ``networkx.DiGraph``, which then
    calls ``networkx.algorithms.d_separated`` to determine d-separation.
    This inherently increases the runtime cost if there are many
    bidirected edges, because many nodes must be added.

    Parameters
    ----------
    G : mixed-edge-graph
        Mixed edge causal graph.
    x : set
        First set of nodes in ``G``.
    y : set
        Second set of nodes in ``G``.
    z : set
        Set of conditioning nodes in ``G``. Can be empty set.

    Returns
    -------
    b : bool
        A boolean that is true if ``x`` is m-separated from ``y`` given ``z`` in ``G``.

    See Also
    --------
    d_separated

    Notes
    -----
    This wraps the networkx implementation, which only allows DAGs. Since
    ``ADMG`` is not represented.
    """
    if not isinstance(G, nx.MixedEdgeGraph):
        raise RuntimeError(
            "m-separation should only be run on a MixedEdgeGraph. If "
            'you have a directed graph, use "d_separated" function instead.'
        )
    if any(
        edge_type not in G.edge_types
        for edge_type in [bidirected_edge_name, directed_edge_name]
    ):
        raise RuntimeError(
            f"m-separation only works on nx with directed and bidirected edges. "
            f"Your graph passed in has the following edge types: {G.edge_types}, whereas "
            f"the function is expecting directed edges named {directed_edge_name} and "
            f"bidirected edges named {bidirected_edge_name}."
        )
    if any(
        edge_type not in [bidirected_edge_name, directed_edge_name]
        for edge_type in G.edge_types
    ):
        raise RuntimeError(
            f"m-separation should only be run on mixed-edge graphs with directed edges "
            f"named {directed_edge_name} and bidirected edges named {bidirected_edge_name}."
        )

    # get the full graph by converting bidirected edges into latent confounders
    # and keeping the directed edges
    explicit_G = nx.bidirected_to_unobserved_confounder(
        G, bidirected_edge_name=bidirected_edge_name
    )

    # Convert the graph to a directed graph;
    # At this point, it should be a valid DAG if the original graph was acyclic
    explicit_G = explicit_G.to_directed()

    # get all unobserved confounders
    uc_nodes = {
        node for node, label in explicit_G.nodes(data="label") if label is not None
    }

    # make sure there are always conditioned on the conditioning set
    assert all(uc_node not in z for uc_node in uc_nodes)
    return nx.d_separated(explicit_G, x, y, z)
